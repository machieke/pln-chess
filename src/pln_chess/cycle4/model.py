"""Schema 4 evidence replay. All uncertainty arithmetic executes in native PLN."""
from dataclasses import dataclass,field,asdict
from pathlib import Path
from pln_chess.common import digest,read_json,write_json
from pln_chess.pln import Runtime,TV
from pln_chess.learning import PRIOR
from pln_chess.evidence import Ledger
from pln_chess.domain import Position
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle4 import SCHEMA
from pln_chess.cycle4.ontology import descriptors,relation

VARIANTS={'C4-full','C4-observations','C4-no-exposure','C4-no-induction','C4-no-dependence'}

@dataclass
class FactoredModel:
    runtime_version:str
    variant:str='C4-full'
    hypotheses:dict=field(default_factory=dict)
    induction:dict=field(default_factory=dict)
    ledger_digest:str=''
    training_report:dict=field(default_factory=dict)
    schema:int=4
    grammar:str=SCHEMA

    @property
    def version(self):return digest(asdict(self))
    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return {'path':str(path),'version':self.version,'hypotheses':len(self.hypotheses)}
    @classmethod
    def load(cls,path,runtime=None):
        data=read_json(path);version=data.pop('version');model=cls(**data)
        if model.schema!=4 or model.grammar!=SCHEMA or model.variant not in VARIANTS:raise ValueError('Unsupported Cycle 4 representation')
        if version!=model.version:raise ValueError('Checkpoint integrity mismatch')
        if runtime and model.runtime_version!=runtime.version:raise ValueError('Checkpoint/runtime mismatch')
        for h in model.hypotheses.values():TV.from_json(h['positive']);TV.from_json(h['negative'])
        for h in model.induction.values():TV.from_json(h['truth_value'])
        return model
    def inspect_hypothesis(self,key):return {'id':key,**self.hypotheses.get(key,{}),'model_version':self.version}


def observe_example(position,move,label,source,dependence_group,ledger_path,runtime=None,
                    variant='C4-full',transformation_lineage=None,auxiliary_labels=None,
                    idempotency_key=None,observation_confidence=.5,movement_label=None,
                    component_labels=None,evidence_role='observation',_payload_only=False,constraint_bridge_targets=None):
    from pln_chess.api import find_move
    runtime=runtime or Runtime();position=Position.from_fen(position) if isinstance(position,str) else position
    move=find_move(position,move) if isinstance(move,str) else move
    if move is None:raise ValueError('Move outside candidate grammar')
    if type(label) is not bool or (movement_label is not None and type(movement_label) is not bool):raise ValueError('Labels must be Boolean')
    if variant not in VARIANTS:raise ValueError('Unsupported variant')
    if evidence_role not in ('observation','exposure-bridge','legality-bridge'):raise ValueError('Unknown evidence role')
    if any(type(v) is not bool for v in (auxiliary_labels or {}).values()):raise ValueError('Attack labels must be Boolean')
    if any(type(v) is not bool for v in (component_labels or {}).values()):raise ValueError('Component labels must be Boolean')
    obs=descriptors(position,move);targets=[]
    for rel in obs['relations']:
        target=rel['target'];value=None
        if target=='LocalAdmissibility':value=movement_label if movement_label is not None else True if label else None
        elif target=='GeometryObserved' and (movement_label is True or label):value=True
        elif target=='Obstruction':value=(component_labels or {}).get('Obstruction:'+rel['descriptor']['occupancy'])
        else:value=(component_labels or {}).get(target)
        if value is not None:targets.append({**rel,'label':value})
    if evidence_role=='observation':
        for a in obs['attack_relations']:
            key=a['attacker_id'] if a['phase']=='successor' else a['phase']+':'+a['attacker_id']
            if key in (auxiliary_labels or {}):targets.append({**a['relation'],'label':auxiliary_labels[key]})
    elif any((auxiliary_labels or {}).values()):
        edge='Attack-to-Exposure' if evidence_role=='exposure-bridge' else 'Exposure-to-NotLegal'
        targets.append({**relation('Bridge',{'edge':edge}), 'label':True if evidence_role=='exposure-bridge' else not label})
    # Constraint-to-illegality is trained in a separate pool, not assumed in the sensor.
    if evidence_role=='legality-bridge':
        if movement_label is False:
            targets.append({**relation('Bridge',{'edge':'LocalFailure-to-NotLegal'}),'label':not label})
        for target in ('Obstruction','DestinationConflict','BoundaryConflict'):
            if any(t['target']==target and t['label'] for t in targets):
                targets.append({**relation('Bridge',{'edge':target+'-to-NotLegal'}),'label':not label})
        # Bridge records do not also train the antecedent condition.
        targets=[t for t in targets if t['target'] not in ('Obstruction','DestinationConflict','BoundaryConflict')]
    for target in constraint_bridge_targets or []:
        if target not in ('Obstruction','DestinationConflict','BoundaryConflict'):raise ValueError('Unknown constraint bridge target')
        if any(t['target']==target and t['label'] for t in targets):
            targets.append({**relation('Bridge',{'edge':target+'-to-NotLegal'}),'label':not label})
        targets=[t for t in targets if t['target']!=target]
    payload={'position_id':position.id,'candidate_id':move.id,'label':label,'source':source,
             'relative_feature_fingerprint':digest(obs['local_context']),
             'dependence_group':dependence_group,'transformation_lineage':transformation_lineage or [],
             'targets':targets,'runtime_version':runtime.version,'model_version':SCHEMA,
             'observation_tv':TV(float(label),observation_confidence if obs['complete'] else 0).json(),
             'input':{'fen':position.fen(),'move':move.notation},'evidence_role':evidence_role,
             'population_stratum':obs['piece'],'distance':obs['pattern']['geometry']['distance']}
    return payload if _payload_only else Ledger(ledger_path).append(payload,idempotency_key)


def train(dataset,checkpoint=None,options=None,runtime=None,ledger_path=None):
    runtime=runtime or Runtime(timeout=300);options=options or {};variant=options.get('variant','C4-full')
    if variant not in VARIANTS:raise ValueError('Unsupported variant')
    if isinstance(dataset,Ledger):ledger=dataset
    else:
        if ledger_path is None:raise ValueError('ledger_path required')
        ledger=Ledger(ledger_path);rows=read_json(dataset) if isinstance(dataset,(str,Path)) else dataset
        payloads=[]
        for r in rows.get('examples',[]) if isinstance(rows,dict) else rows:
            payloads.append(observe_example(r['fen'],r['move'],r['label'],r['source'],r['dependence_group'],ledger_path,runtime,
                variant,r.get('transformation_lineage'),r.get('attack_labels'),observation_confidence=r.get('confidence',.5),
                movement_label=r.get('movement_label'),component_labels=r.get('c4_component_labels'),evidence_role=r.get('evidence_role','observation'),_payload_only=True,
                constraint_bridge_targets=r.get('constraint_bridge_targets')))
        ledger.append_many(payloads)
    records=[r for r in ledger.records() if (options.get('through_sequence') is None or r['sequence']<=options['through_sequence'])
             and r['payload']['dependence_group'] not in options.get('retract_groups',[])]
    model=FactoredModel(runtime.version,variant);states={};nodes=[];excluded=[]
    dependent=options.get('dependence_aware',variant!='C4-no-dependence')
    for record in records:
        p=record['payload']
        if p['runtime_version']!=runtime.version or p['model_version']!=SCHEMA:raise ValueError('Ledger/runtime/ontology mismatch')
        if p['observation_tv']['confidence']==0:continue
        # Explicit transformed ancestors also identify the original sampling unit.
        groups=set([p['dependence_group']]+p.get('transformation_lineage',[]))
        for rel in p['targets']:
            key=rel['id'];state=states.setdefault(key,{'relation':{k:v for k,v in rel.items() if k!='label'},'groups':set(),'ids':[],'refs':[PRIOR.metta(),PRIOR.metta()],'labels':{True:[],False:[]}})
            if dependent and groups&state['groups']:
                excluded.append([record['evidence_id'],key]);continue
            state['groups'].update(groups);state['ids'].append(record['evidence_id']);state['labels'][rel['label']].append(record['evidence_id'])
            for channel,label in enumerate((rel['label'],not rel['label'])):
                name=f'u{len(nodes)}';tv=TV(float(label),p['observation_tv']['confidence'])
                nodes.append((name,f'(Truth_Revision {state["refs"][channel]} {tv.metta()})'));state['refs'][channel]=f'({name})'
    session=NativeSession(runtime);values=session.batch(nodes)
    for key,s in states.items():
        model.hypotheses[key]={**s['relation'],'positive':values[s['refs'][0][1:-1]].json(),'negative':values[s['refs'][1][1:-1]].json(),
            'evidence_ids':s['ids'],'dependence_groups':sorted(s['groups']),'supporting_evidence':s['labels'][True],
            'contradicting_evidence':s['labels'][False],'origin':'direct-native-revision'}
    model.ledger_digest=digest([r['evidence_id'] for r in records])
    model.training_report={'records':len(records),'dependence_aware':dependent,'native_revision_nodes':len(nodes),'executed_native_calls':session.calls,
        'excluded_update_count':len(excluded),'excluded_digest':digest(excluded),'retract_groups':options.get('retract_groups',[]),
        'migration':'Replay original labels with new target semantics; no Cycle 3 header relabeling.',
        'positive_scope':'LocalAdmissibility is trained on pseudo-legality; it is not a theorem of global king safety.',
        'induction_enabled':False,'induction':'Controlled laboratory only; production default disabled.'}
    if checkpoint:model.export(checkpoint)
    return model
