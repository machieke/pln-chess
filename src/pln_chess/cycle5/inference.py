"""Verified negative proofs and an explicit, conservative positive proof planner.

Native partial local support is diagnostic, never silently promoted to LegalMove.
The planner contains no probability arithmetic and no chess oracle.
"""
from dataclasses import dataclass,asdict,replace
from pathlib import Path
import copy,json,time
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime,TV,UNKNOWN,NativeError
from pln_chess.inference import classify
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle4.inference import infer_moves as reference,Cycle4Options
from pln_chess.cycle4.ontology import relation as old_relation
from pln_chess.cycle5.ontology import descriptors,FAMILIES
from pln_chess.cycle5.history import inspect as temporal_inspect,MODES
from pln_chess.cycle5.model import PremiseModel

@dataclass(frozen=True)
class Cycle5Options(Cycle4Options):
    temporal_mode:str='fen-only'
    temporal_evidence:dict|None=None
    suppress_families:tuple=()
    dependence_aware:bool=True
    def __post_init__(self):
        super().__post_init__()
        if type(self.dependence_aware) is not bool:raise ValueError('Invalid dependence policy')
        if self.temporal_mode not in MODES:raise ValueError('Unknown temporal mode')
        if set(self.suppress_families)-set(FAMILIES):raise ValueError('Unknown premise family')
        if self.temporal_evidence is not None and not isinstance(self.temporal_evidence,dict):raise ValueError('Temporal evidence must be an object')

class Session:
    def __init__(self,runtime,optimized=True,max_entries=50000):
        self.base=NativeSession(runtime,optimized,max_entries)
        self.premises=NativeSession(runtime,optimized,max_entries)

def infer_moves(position,checkpoint,options=None,runtime=None,selected_moves=None,session=None,optimized=True):
    started=time.perf_counter();options=options or Cycle5Options()
    if not isinstance(options,Cycle5Options):options=Cycle5Options(**asdict(options))
    runtime=runtime or Runtime(timeout=options.timeout_seconds)
    model=PremiseModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    if model.runtime_version!=runtime.version:raise ValueError('Model/runtime mismatch')
    position=Position.from_fen(position) if isinstance(position,str) else position
    moves=list(selected_moves) if selected_moves is not None else list(candidates(position))
    history=temporal_inspect(position,options.temporal_mode,options.temporal_evidence)
    if history['mode']=='event-backed' and history['status']=='structurally-consistent' and history['ep_truth_value']['confidence']>=.99:
        position=replace(position,history_known=True)
    session=session or Session(runtime,optimized,options.max_cache_entries)
    if not isinstance(session,Session):raise ValueError('Cycle 5 requires its scoped two-stage Session')
    base=model.base_model();suppressed=set(options.suppress_families)
    if not options.dependence_aware:base.training_report['dependence_aware']=False
    if suppressed:
        base=copy.deepcopy(base)
        targets={'geometry':{'GeometryObserved','LocalAdmissibility'},'destination':{'DestinationConflict','LocalAdmissibility'},
                 'ray':{'Obstruction','LocalAdmissibility'},'boundary':{'BoundaryConflict','LocalAdmissibility'},
                 'exposure':{'Attack'},'temporal':{'LocalAdmissibility'}}
        removed=set().union(*(targets[f] for f in suppressed))
        base.hypotheses={k:h for k,h in base.hypotheses.items() if h['target'] not in removed}
    # Detection uses the preregistered C4 floor. Raising display thresholds may
    # suppress a negative label but cannot reveal a hidden positive projection.
    base_options=Cycle4Options(max_native_invocations=options.max_native_invocations,timeout_seconds=options.timeout_seconds,
        max_proof_bytes=options.max_proof_bytes,max_cache_entries=options.max_cache_entries,
        castling_history_attested=history['mode']=='event-backed' and history['castle_truth_value']['confidence']>=.99)
    result=reference(position,base,base_options,runtime,moves,session.base,optimized)
    scope=digest([runtime.manifest,model.version,position.id,asdict(options),history['id']])
    session.premises.bind(scope);calls=session.premises.calls;hits=session.premises.hits
    nodes=[];traces={};beliefs={};paths={};items=result['candidates'];size=0
    remaining_nodes=options.max_native_invocations-result['scheduled_invocations']
    remaining_bytes=options.max_proof_bytes-result['proof_bytes_estimate']
    def node(op,expr,target,premises,ids,groups,rules):
        nonlocal size
        size+=len(expr)+len(json.dumps(premises))+len(json.dumps(ids))+256
        if len(nodes)>=remaining_nodes or size>remaining_bytes:raise OverflowError('Combined Cycle 4/5 proof budget exhausted')
        if time.perf_counter()-started>=options.timeout_seconds:raise OverflowError('Inference wall time budget exhausted')
        name=f'c5n{len(nodes)}';nodes.append((name,expr));traces[name]={'id':name,'operator':op,'native_expression':expr,'conclusion':target,
            'premises':premises,'evidence_ids':sorted(set(ids)),'dependence_groups':sorted(set(groups)),
            'matched_rule_ids':rules,'provenance':'native-derived'}
        return name
    error=None
    from pln_chess.observations import attack_observations
    pre_frames=attack_observations(position,position.turn)
    try:
        for move,item in zip(moves,items):
            o=descriptors(position,move,pre_frames);item['relative_neighborhood']=o['relative_neighborhood'];item['rule_hierarchy']=o['hierarchy']
            item['typed_premises']=[];item['_nodes']=[];item['_negative']=[];item['temporal_evidence']=history
            for rel in o['typed_relations']:
                h=model.hypotheses.get(rel['id'])
                entry={**rel,'truth_value':UNKNOWN.json(),'evidence_ids':[],'dependence_groups':[],'status':'absent'}
                if rel['family'] in suppressed:entry['status']='suppressed'
                elif model.variant=='C5-abstract-only' and rel['family']!='geometry':entry['status']='ablation-omitted'
                elif h and o['complete']:
                    if rel['id'] not in beliefs:
                        refs=[]
                        for channel in ('positive','negative'):
                            refs.append(node('Truth_ModusPonens',f'(Truth_ModusPonens (stv 1.0 0.99) {TV.from_json(h[channel]).metta()})',
                                 rel['target'] if channel=='positive' else 'Not '+rel['target'],[{'observation':rel,'truth_value':TV(1,.99).json()},{'hypothesis':rel['id'],'truth_value':h[channel]}],h['evidence_ids'],h['dependence_groups'],[rel['id']]))
                        neg=node('Truth_Negation',f'(Truth_Negation ({refs[1]}))',rel['target'],[{'node':refs[1]}],h['evidence_ids'],h['dependence_groups'],[rel['id']])
                        selected=node('BestConfidenceCandidate',f'(let ($tv $e) (BestConfidenceCandidate ((({refs[0]}) (positive)) (({neg}) (negative)))) $tv)',rel['target'],[{'node':refs[0]},{'node':neg}],h['evidence_ids'],h['dependence_groups'],[rel['id']])
                        beliefs[rel['id']]={'positive':refs[0],'selected':selected,'nodes':refs+[neg,selected]}
                    b=beliefs[rel['id']];item['_nodes']+=b['nodes'];entry.update(status='learned-native-conditional',proof_node=b['selected'],evidence_ids=h['evidence_ids'],dependence_groups=h['dependence_groups'],
                        supporting_evidence=h['supporting_evidence'],contradicting_evidence=h['contradicting_evidence'])
                    target={'RayObstruction':'Obstruction'}.get(rel['target'],rel['target'])
                    bridge=base.hypotheses.get(old_relation('Bridge',{'edge':target+'-to-NotLegal'})['id'])
                    if bridge and model.variant=='C5-full' and not (h['supporting_evidence'] and h['contradicting_evidence']):
                        overlap=set(h['dependence_groups'])&set(bridge['dependence_groups'])
                        entry['bridge_overlap']=sorted(overlap)
                        if not overlap or not options.dependence_aware:
                            if rel['id'] not in paths:
                                ids=h['evidence_ids']+bridge['evidence_ids'];groups=h['dependence_groups']+bridge['dependence_groups']
                                n=node('Truth_ModusPonens',f'(Truth_ModusPonens ({b["positive"]}) {TV.from_json(bridge["positive"]).metta()})','Not LegalMove',[{'node':b['positive']},{'hypothesis':bridge['id'],'truth_value':bridge['positive']}],ids,groups,[bridge['id']])
                                q=node('Truth_Negation',f'(Truth_Negation ({n}))','LegalMove',[{'node':n}],ids,groups,[bridge['id']])
                                paths[rel['id']]=[n,q]
                            item['_nodes']+=paths[rel['id']];item['_negative'].append(paths[rel['id']][-1])
                item['typed_premises'].append(entry)
    except OverflowError as exc:error=str(exc)
    old_timeout=runtime.timeout
    try:
        if error:raise NativeError(error)
        runtime.timeout=max(.001,options.timeout_seconds-(time.perf_counter()-started));values=session.premises.batch(nodes)
    except NativeError as exc:values={};error=str(exc)
    finally:runtime.timeout=old_timeout
    for move,item in zip(moves,items):
        legacy={'classification':item['classification'],'truth_value':item['legal_move_truth_value'],
                'local_truth_value':item['local_admissibility_truth_value'],'scope':'C4 conditional projection, not a complete positive legality proof'}
        item['legacy_projection']=legacy;item['composition']='native-partial; unary negative chains, no verified positive AND'
        item['decision_policy']='Supported native negative proof or unknown; no positive label without a global composition theorem.'
        item['proof_plan']={'required_families':['geometry','destination','ray','exposure']+(['temporal'] if move.effect!='ordinary' or move.promotion else []),
            'native_conjunction':'unsupported','attempt':'Match typed independently revised conditionals; preserve separate raw TVs; no host TV fusion.',
            'positive_proof_complete':False,'gaps':['No verified independent-premise conjunction.','No native proof of universal king safety from separate opponent frames.']}
        names=list(dict.fromkeys(item.pop('_nodes',[])));negatives=item.pop('_negative',[])
        if error or item['classification']=='incomplete':
            item['classification']=item['status']='incomplete';item['gaps'].append(error or 'Reference inference incomplete')
            continue
        for entry in item['typed_premises']:
            if 'proof_node' in entry:entry['truth_value']=values[entry['proof_node']].json()
        item['proof_trace'] += [{**traces[n],'truth_value':values[n].json(),
                                'premises':[{**p,**({'truth_value':values[p['node']].json()} if 'node' in p else {})} for p in traces[n]['premises']]} for n in names]
        # Alternatives are never revised together. Deterministic first supported
        # negative is a proof witness, not a confidence aggregation operation.
        witnesses=[(n,values[n]) for n in negatives if classify(values[n],base_options)=='contradicted' and classify(values[n],options)=='contradicted']
        if legacy['classification']=='contradicted' and classify(TV.from_json(legacy['truth_value']),options)=='contradicted':
            item['classification']='contradicted';item['status']='native-constraint-chain'
        elif witnesses:
            n,tv=witnesses[0];item['classification']='contradicted';item['status']='native-factored-constraint';item['legal_move_truth_value']=tv.json();item['selected_negative_witness']=n
        else:
            item['classification']='unknown';item['status']='native-partial-proof-gap';item['legal_move_truth_value']=UNKNOWN.json()
            item['gaps']=list(dict.fromkeys(item['gaps']+item['proof_plan']['gaps']))
        item['negative_alternatives']=[{'node':n,'truth_value':tv.json()} for n,tv in witnesses]
        item['premise_conflicts']=[{'id':p['id'],'supporting':p.get('supporting_evidence'),'contradicting':p.get('contradicting_evidence')} for p in item['typed_premises'] if p.get('supporting_evidence') and p.get('contradicting_evidence')]
        if move.effect in ('castle','en-passant') and history['status']=='conflicting':
            item['classification']='unknown';item['status']='temporal-conflict';item['legal_move_truth_value']=UNKNOWN.json();item['gaps']+=history['conflicts']
        item['matched_rule_ids']=sorted({r for t in item['proof_trace'] for r in t['matched_rule_ids']})
        item['evidence_ids']=sorted({e for t in item['proof_trace'] for e in t['evidence_ids']})
        item['abstention_reason']=item['gaps'] if item['classification']=='unknown' else []
        item['proof_dag_refs']=[digest(t) for t in item['proof_trace']]
    result.update(schema=5,model_version=model.version,representation=model.variant,budget=asdict(options),cache_scope=scope,
        coverage='strict-negative-and-unknown; positive completion unsupported',temporal_evidence=history,
        native_invocations=result['native_invocations']+session.premises.calls-calls,
        scheduled_invocations=result['scheduled_invocations']+len(nodes),cache_hits=result['cache_hits']+session.premises.hits-hits,
        cache_entries=len(session.base.cache)+len(session.premises.cache),proof_bytes_estimate=result['proof_bytes_estimate']+size,
        elapsed_seconds=time.perf_counter()-started,truncated=result['truncated'] or error is not None,error=error or result['error'],
        scheduler='scoped-typed-premise-cache' if optimized else 'reference',
        proof_dag={digest(t):t for i in items for t in i['proof_trace']})
    result['grounded_atoms']+=sum(len(i.get('typed_premises',[])) for i in items)
    result['unique_premise_groundings']=len(beliefs)
    return result

def counterfactual(position,move,model,options=None,runtime=None):
    from pln_chess.api import find_move
    runtime=runtime or Runtime();position=Position.from_fen(position) if isinstance(position,str) else position
    if getattr(model,'schema',None)!=5:raise ValueError('Premise counterfactuals require a Cycle 5 checkpoint')
    candidate=find_move(position,move)
    if candidate is None:raise ValueError('Move outside grammar')
    options=options or Cycle5Options();before=infer_moves(position,model,options,runtime,[candidate])
    return {'before':before,'without':{f:infer_moves(position,model,replace(options,suppress_families=(f,)),runtime,[candidate]) for f in FAMILIES},
            'scope':'Suppress complete evidence families, including overlapping local C4 categories; preserve all raw native results.'}
