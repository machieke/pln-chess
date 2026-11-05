"""Native constraint chains and transparent conditional-positive presentation.

LocalAdmissibility and NotLegal are different propositions. A local movement
projection is never submitted as a global safety theorem to confidence choice.
"""
from dataclasses import asdict,dataclass
from pathlib import Path
import json,time,resource
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime,TV,UNKNOWN,NativeError
from pln_chess.inference import classify
from pln_chess.cycle3.inference import Cycle3Options
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle4.ontology import descriptors,relation
from pln_chess.cycle4.model import FactoredModel

@dataclass(frozen=True)
class Cycle4Options(Cycle3Options):
    pass


def infer_moves(position,checkpoint,options=None,runtime=None,selected_moves=None,session=None,optimized=True):
    started=time.perf_counter();options=options or Cycle4Options()
    position=Position.from_fen(position) if isinstance(position,str) else position
    runtime=runtime or Runtime(timeout=options.timeout_seconds)
    model=FactoredModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    if runtime.version!=model.runtime_version:raise ValueError('Model/runtime mismatch')
    session=session or NativeSession(runtime,optimized,getattr(options,'max_cache_entries',50000))
    scope=digest([runtime.manifest,model.version,model.grammar,model.ledger_digest,position.id,asdict(options)])
    session.bind(scope);before_calls=session.calls;before_hits=session.hits
    nodes=[];traces=[];items=[];proof_bytes=0;truncated=False;unexplored=0
    def node(op,expr,target,premises,ids,groups,rules):
        nonlocal proof_bytes
        proof_bytes+=len(expr)+len(json.dumps(premises))+len(json.dumps(ids))+256
        if proof_bytes>getattr(options,'max_proof_bytes',64*1024*1024):raise OverflowError('Proof metadata budget exhausted')
        if len(nodes)>=options.max_native_invocations:raise OverflowError('Native proof budget exhausted')
        if time.perf_counter()-started>=options.timeout_seconds:raise OverflowError('Inference wall time budget exhausted')
        name=f'n{len(nodes)}';nodes.append((name,expr))
        traces.append({'id':name,'operator':op,'native_expression':expr,'conclusion':target,'premises':premises,
                       'evidence_ids':sorted(set(ids)),'dependence_groups':sorted(set(groups)),
                       'matched_rule_ids':rules,'provenance':'native-derived'})
        return name
    def conditional(rel):
        h=model.hypotheses[rel['id']];ids=h['evidence_ids'];groups=h['dependence_groups'];sensor=TV(1,.99)
        p=node('Truth_ModusPonens',f'(Truth_ModusPonens {sensor.metta()} {TV.from_json(h["positive"]).metta()})',rel['target'],
               [{'sensor':rel,'truth_value':sensor.json()},{'conditional':rel['id'],'truth_value':h['positive']}],ids,groups,[rel['id']])
        n=node('Truth_ModusPonens',f'(Truth_ModusPonens {sensor.metta()} {TV.from_json(h["negative"]).metta()})','Not '+rel['target'],
               [{'sensor':rel,'truth_value':sensor.json()},{'conditional':rel['id'],'truth_value':h['negative']}],ids,groups,[rel['id']])
        q=node('Truth_Negation',f'(Truth_Negation ({n}))',rel['target'],[{'node':n}],ids,groups,[rel['id']])
        s=node('BestConfidenceCandidate',f'(let ($tv $e) (BestConfidenceCandidate ((({p}) (positive)) (({q}) (negative)))) $tv)',rel['target'],[{'node':p},{'node':q}],ids,groups,[rel['id']])
        return {'id':rel['id'],'target':rel['target'],'selected':s,'positive':p,'negative':n,'evidence_ids':ids,'dependence_groups':groups}
    def chain(a,edges):
        result=dict(a);prior=a['positive'];ids=list(a['evidence_ids']);groups=set(a['dependence_groups'])
        for edge,target in edges:
            key=relation('Bridge',{'edge':edge})['id'];h=model.hypotheses.get(key)
            if h is None:result['chain_gap']='Unlearned bridge '+edge;break
            overlap=groups&set(h['dependence_groups'])
            if overlap and model.training_report.get('dependence_aware',True):
                result['chain_gap']='Correlated premise pools';result['overlap']=sorted(overlap);break
            ids+=h['evidence_ids'];groups.update(h['dependence_groups'])
            prior=node('Truth_ModusPonens',f'(Truth_ModusPonens ({prior}) {TV.from_json(h["positive"]).metta()})',target,
                       [{'node':prior},{'conditional':key,'truth_value':h['positive']}],ids,groups,[key])
            result['exposure' if target=='WouldExposeOwnKing' else 'negative_legality']=prior
        if 'negative_legality' in result:
            result['counter']=node('Truth_Negation',f'(Truth_Negation ({prior}))','LegalMove',[{'node':prior}],ids,groups,[a['id']+':negation'])
        result['chain_evidence_ids']=sorted(set(ids));result['chain_groups']=sorted(groups)
        return result
    for move in selected_moves if selected_moves is not None else candidates(position):
        obs=descriptors(position,move);start=len(nodes)
        item={'move':move.notation,'candidate_id':move.id,'piece':obs['piece'],'relative_pattern':obs['pattern'],
              'observations':obs,'factored_premises':obs['factored_premises'],'condition_beliefs':{},'attack_beliefs':[],
              'proof_trace':[],'matched_hypotheses':[],'matched_rule_ids':[],'evidence_ids':[],
              'movement_truth_value':UNKNOWN.json(),'local_admissibility_truth_value':UNKNOWN.json(),
              'legal_move_truth_value':UNKNOWN.json(),'classification':'unknown','status':'unknown','gaps':[],
              'decision_policy':'Native negative constraint proof; otherwise conditional local projection. No inference of safety from absent attacks.',
              'composition':'native-unary-chains; positive projection non-compositional'}
        if not obs['complete']:
            item['gaps']=obs.get('missing',[])+['Incomplete observation.'];items.append(item);continue
        try:
            matches=[conditional(r) for r in obs['relations'] if r['id'] in model.hypotheses]
            local=next((r for r in matches if r['target']=='LocalAdmissibility'),None)
            attacks=[];constraints=[]
            if model.variant!='C4-observations':
                for a in matches:
                    if a['target'] in ('Obstruction','DestinationConflict','BoundaryConflict'):
                        constraints.append(chain(a,[(a['target']+'-to-NotLegal','Not LegalMove')]))
                if local:
                    constraints.append(chain({**local,'target':'LocalFailure','positive':local['negative']},[('LocalFailure-to-NotLegal','Not LegalMove')]))
                if model.variant!='C4-no-exposure':
                    for a in obs['attack_relations']:
                        if a['relation']['id'] in model.hypotheses:
                            attacks.append({**chain(conditional(a['relation']),[('Attack-to-Exposure','WouldExposeOwnKing'),('Exposure-to-NotLegal','Not LegalMove')]),
                                            'attacker_id':a['attacker_id'],'king_id':a['king_id'],'phase':a['phase']})
            item['_refs']={'matches':matches,'local':local,'attacks':attacks,'constraints':constraints,'start':start,'end':len(nodes)}
        except OverflowError as exc:
            del nodes[start:];del traces[start:];item['classification']=item['status']='incomplete';item['gaps'].append(str(exc));truncated=True;unexplored+=1
        items.append(item)
    old_timeout=runtime.timeout;runtime.timeout=max(.001,options.timeout_seconds-(time.perf_counter()-started));error=None
    try:values=session.batch(nodes)
    except NativeError as exc:values={};error=str(exc);truncated=True
    finally:runtime.timeout=old_timeout
    # A second native pass chooses only among conclusions with the same polarity.
    # Conflicting raw conditionals stay in the proof; local support is a different proposition.
    choice_nodes=[];choices={}
    for i,item in enumerate(items):
        refs=item.get('_refs')
        if refs is None or error:continue
        negatives=[a for a in refs['attacks']+refs['constraints'] if 'counter' in a and classify(values[a['counter']],options)=='contradicted']
        if negatives:
            name=f'choose{i}';expr=' '.join(f'({values[a["counter"]].metta()} (proof{j}))' for j,a in enumerate(negatives))
            choice_nodes.append((name,f'(let ($tv $e) (BestConfidenceCandidate ({expr})) $tv)'));choices[i]=(name,negatives)
    try:
        if len(nodes)+len(choice_nodes)>options.max_native_invocations:raise NativeError('Native selection budget exhausted')
        runtime.timeout=max(.001,options.timeout_seconds-(time.perf_counter()-started))
        chosen=session.batch(choice_nodes)
    except NativeError as exc:chosen={};error=str(exc);truncated=True
    finally:runtime.timeout=old_timeout
    for i,item in enumerate(items):
        refs=item.pop('_refs',None)
        if refs is None:continue
        if error:item['classification']=item['status']='incomplete';item['gaps'].append(error);continue
        item['proof_trace']=[{**t,'truth_value':values[t['id']].json(),'premises':[{**p,**({'truth_value':values[p['node']].json()} if 'node' in p else {})} for p in t['premises']]} for t in traces[refs['start']:refs['end']]]
        for a in refs['matches']:
            h=model.hypotheses[a['id']];tv=values[a['selected']].json()
            item['matched_hypotheses'].append({**a,'truth_value':tv,'belief':h})
            item['condition_beliefs'][a['id']]={'target':a['target'],'truth_value':tv,'proof_node':a['selected'],'evidence_ids':a['evidence_ids']}
            if a['target']=='GeometryObserved':item['movement_truth_value']=tv
        for a in refs['attacks']:
            item['attack_beliefs'].append({**a,'truth_value':values[a['selected']].json(),
                'exposure_truth_value':values[a['exposure']].json() if 'exposure' in a else UNKNOWN.json(),
                'negative_legality_truth_value':values[a['negative_legality']].json() if 'negative_legality' in a else UNKNOWN.json()})
        local=refs['local'];local_tv=values[local['selected']] if local else UNKNOWN
        item['local_admissibility_truth_value']=local_tv.json();item['chosen_hypothesis_id']=local['id'] if local else None
        threats=[a for a in refs['attacks'] if classify(values[a['selected']],options)=='supported']
        disputed=[a['id'] for a in refs['attacks']+([local] if local else [])
                  if model.hypotheses[a['id']].get('supporting_evidence') and model.hypotheses[a['id']].get('contradicting_evidence')
                  and options.contradicted_strength<values[a['selected']].strength<options.supported_strength]
        item['conflicting_evidence']=disputed
        item['constraint_paths']=refs['constraints'];item['exposure_conflicts']=[a['id'] for a in threats]
        if i in choices:
            name,negative=choices[i];final=chosen[name];item['classification']='contradicted';item['status']='native-constraint-chain'
            trace={'id':name,'operator':'BestConfidenceCandidate','native_expression':dict(choice_nodes)[name],'conclusion':'LegalMove',
                   'premises':[{'node':a['counter'],'truth_value':values[a['counter']].json()} for a in negative],
                   'truth_value':final.json(),'evidence_ids':sorted({e for a in negative for e in a['chain_evidence_ids']}),
                   'dependence_groups':sorted({g for a in negative for g in a['chain_groups']}),'matched_rule_ids':[], 'provenance':'native-derived'}
            item['proof_trace'].append(trace)
        else:
            final=local_tv;item['classification']=classify(final,options);item['status']='native-partial-local-projection' if local else 'unknown'
            if disputed:
                item['classification']='unknown';item['gaps'].append('Independent observations dispute an applicable conditional; raw revision and both evidence sets retained.')
            elif threats:
                item['classification']='unknown';item['gaps'].append('Learned attack support, but no sufficiently confident independent illegality chain.')
            elif model.variant!='C4-observations' and item['classification']=='contradicted':
                item['classification']='unknown';item['gaps'].append('Local failure lacks a complete native illegality bridge.')
            if item['classification']=='supported':item['gaps'].append('Conditional local support; global safety is unproved. No observed threat is not evidence of safety.')
        if item['observations']['pattern']['effect'] in ('castle','en-passant'):
            if getattr(options,'history_consistency','unknown')=='contradictory':
                item['classification']='unknown';item['gaps'].append('Contradictory temporal evidence.')
            elif item['classification']=='supported' and not position.history_known:
                item['classification']='unknown';item['gaps'].append('Historical preconditions are not established by FEN flags.')
        item['legal_move_truth_value']=final.json()
        if local is None:item['gaps'].append('No matching pooled local hypothesis.')
        item['matched_rule_ids']=sorted({r for t in item['proof_trace'] for r in t['matched_rule_ids']})
        item['evidence_ids']=sorted({e for t in item['proof_trace'] for e in t['evidence_ids']})
        item['abstention_reason']=item['gaps'] if item['classification']=='unknown' else []
    return {'schema':4,'position_id':position.id,'fen':position.fen(),'runtime_version':runtime.version,'model_version':model.version,
            'representation':model.variant,'budget':asdict(options),'truncated':truncated,'error':error,
            'native_invocations':session.calls-before_calls,'scheduled_invocations':len(nodes)+len(choice_nodes),'cache_hits':session.hits-before_hits,
            'grounded_atoms':sum(len(i['factored_premises'])+len(i['proof_trace']) for i in items),
            'unique_groundings':len({digest([a['relation']['id'],a['phase'],a['attacker_id']]) for i in items for a in i['observations']['attack_relations']}),
            'elapsed_seconds':time.perf_counter()-started,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'candidates':items,'coverage':'native-unary-constraints; native-partial-positive','cache_scope':scope,
            'cache_entries':len(session.cache),'proof_bytes_estimate':proof_bytes,'unexplored_branches':unexplored,
            'scheduler':'pure-native-expression-cache' if optimized else 'reference'}
