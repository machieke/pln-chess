"""Schema-3 checkpoints. Native revision, conservative dependence and explicit induction."""
from dataclasses import dataclass,field,asdict
from pathlib import Path
from pln_chess.common import digest,read_json,write_json
from pln_chess.pln import Runtime,TV
from pln_chess.learning import PRIOR
from pln_chess.evidence import Ledger
from pln_chess.domain import Position
from pln_chess.cycle3.descriptors import descriptors,relation
from pln_chess.cycle2.native import NativeSession
from pln_chess.cycle3 import SCHEMA

VARIANTS={'C3-full','C3-local','C3-exposure','C3-induction','no-obstruction','no-exposure','no-arbitration','exact-context-only'}

@dataclass
class RelationalModel:
    runtime_version:str
    variant:str='C3-full'
    hypotheses:dict=field(default_factory=dict)
    induction:dict=field(default_factory=dict)
    ledger_digest:str=''
    training_report:dict=field(default_factory=dict)
    schema:int=3
    grammar:str=SCHEMA

    @property
    def version(self): return digest(asdict(self))
    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return {'path':str(path),'version':self.version,'hypotheses':len(self.hypotheses)}
    @classmethod
    def load(cls,path,runtime=None):
        data=read_json(path);version=data.pop('version');model=cls(**data)
        if model.schema!=3 or model.grammar!=SCHEMA: raise ValueError('Unsupported Cycle 3 schema/grammar; previous schemas remain supported separately')
        if version!=model.version: raise ValueError('Checkpoint integrity mismatch')
        if model.variant not in VARIANTS:raise ValueError('Unsupported Cycle 3 variant')
        if runtime and model.runtime_version!=runtime.version: raise ValueError('Checkpoint/runtime mismatch')
        for h in model.hypotheses.values(): TV.from_json(h['positive']);TV.from_json(h['negative'])
        for h in model.induction.values(): TV.from_json(h['truth_value'])
        return model
    def inspect_hypothesis(self,key): return {'id':key,**self.hypotheses.get(key,{}),'induction':self.induction.get(key),'model_version':self.version}


def observe_example(position,move,label,source,dependence_group,ledger_path,runtime=None,
                    variant='C3-full',transformation_lineage=None,auxiliary_labels=None,
                    idempotency_key=None,observation_confidence=.5,movement_label=None,_payload_only=False,component_labels=None,evidence_role='observation'):
    from pln_chess.api import find_move
    runtime=runtime or Runtime();position=Position.from_fen(position) if isinstance(position,str) else position
    move=find_move(position,move) if isinstance(move,str) else move
    if move is None: raise ValueError('Move outside candidate grammar')
    if type(label) is not bool: raise ValueError('Label must be Boolean')
    if variant not in VARIANTS:raise ValueError('Unsupported Cycle 3 variant')
    if evidence_role not in ('observation','exposure-bridge','legality-bridge'):raise ValueError('Unknown evidence role')
    if any(type(v) is not bool for v in (auxiliary_labels or {}).values()):raise ValueError('Attack label must be Boolean')
    if movement_label is not None and type(movement_label) is not bool: raise ValueError('Movement label must be Boolean')
    obs=descriptors(position,move,variant);targets=[]
    for rel in obs['relations']:
        if rel['target']=='LegalMove':
            value=label;reason='Full local conditional outcome; negative label does not update general movement family.'
        elif rel['target'] not in ('MovementPatternSupported','GeometryObserved'):
            if rel['target'] not in (component_labels or {}):continue
            value=component_labels[rel['target']];reason='Independent auxiliary condition supervision; never inferred from negative move legality.'
            if type(value) is not bool:raise ValueError('Component label must be Boolean')
        elif movement_label is True:
            value=True;reason='Positive auxiliary pseudo-legal label supports applicable movement motifs; no negative cause is assigned to a projection.'
        elif label:
            value=True;reason='Positive legal example supports applicable movement motif.'
        else: continue
        targets.append({**rel,'label':value,'attribution':reason})
    for a in obs['attack_relations'] if evidence_role=='observation' else []:
        attack_key=a['attacker_id'] if a['phase']=='successor' else a['phase']+':'+a['attacker_id']
        if attack_key in (auxiliary_labels or {}):
            value=auxiliary_labels[attack_key]
            if type(value) is not bool: raise ValueError('Attack label must be Boolean')
            targets.append({**a['relation'],'label':value,'attribution':'Auxiliary successor attack supervision; training only.'})
    if any((auxiliary_labels or {}).values()) and evidence_role in ('exposure-bridge','legality-bridge'):
        edges=[('Attack-to-Exposure',True)] if evidence_role=='exposure-bridge' else [('Exposure-to-NotLegal',not label)]
        for edge,value in edges:
            targets.append({**relation(4,{'edge':edge},'Bridge'),'label':value,
                            'attribution':'Co-observed positive auxiliary attack and reference legality; one update per dependence group.'})
    payload={'position_id':position.id,'candidate_id':move.id,'relative_feature_fingerprint':digest(obs['local_context']),
             'label':label,'source':source,'dependence_group':dependence_group,'observation_tv':TV(float(label),observation_confidence if obs['complete'] else 0).json(),
             'targets':targets,'runtime_version':runtime.version,'model_version':SCHEMA,'variant':variant,
             'transformation_lineage':transformation_lineage or [],'input':{'fen':position.fen(),'move':move.notation},
             'population_stratum':obs['piece'],'distance':obs['pattern']['geometry']['distance'],'evidence_role':evidence_role}
    return payload if _payload_only else Ledger(ledger_path).append(payload,idempotency_key)


def train(dataset,checkpoint=None,options=None,runtime=None,ledger_path=None):
    runtime=runtime or Runtime(timeout=300);options=options or {};variant=options.get('variant','C3-full')
    if isinstance(dataset,Ledger): ledger=dataset
    else:
        if ledger_path is None: raise ValueError('ledger_path required')
        ledger=Ledger(ledger_path);rows=read_json(dataset) if isinstance(dataset,(str,Path)) else dataset
        payloads=[]
        for row in rows.get('examples',[]) if isinstance(rows,dict) else rows:
            payloads.append(observe_example(row['fen'],row['move'],row['label'],row['source'],row['dependence_group'],ledger.path,runtime,
                            variant,row.get('transformation_lineage'),row.get('attack_labels'),
                            observation_confidence=row.get('confidence',.5),movement_label=row.get('movement_label'),_payload_only=True,component_labels=row.get('component_labels'),evidence_role=row.get('evidence_role','observation')))
        ledger.append_many(payloads)
    records=[r for r in ledger.records() if options.get('through_sequence') is None or r['sequence']<=options['through_sequence']]
    model=RelationalModel(runtime.version,variant);states={};nodes=[];excluded=[]
    for record in records:
        p=record['payload']
        if p['runtime_version']!=runtime.version or p['model_version']!=SCHEMA or p['variant']!=variant: raise ValueError('Ledger/runtime/representation mismatch')
        if p['observation_tv']['confidence']==0: continue
        for rel in p['targets']:
            key=rel['id'];state=states.setdefault(key,{'relation':{k:v for k,v in rel.items() if k not in ('label','attribution')},'groups':set(),'ids':[],'refs':[PRIOR.metta(),PRIOR.metta()]})
            if options.get('dependence_aware',True) and p['dependence_group'] in state['groups']:
                excluded.append({'id':record['evidence_id'],'hypothesis':key,'reason':'dependence group already contributes'});continue
            state['groups'].add(p['dependence_group']);state['ids'].append(record['evidence_id'])
            for channel,label in enumerate((rel['label'],not rel['label'])):
                name=f'u{len(nodes)}';tv=TV(float(label),p['observation_tv']['confidence'])
                nodes.append((name,f'(Truth_Revision {state["refs"][channel]} {tv.metta()})'));state['refs'][channel]=f'({name})'
    session=NativeSession(runtime);values=session.batch(nodes)
    for key,state in states.items():
        model.hypotheses[key]={**state['relation'],'positive':values[state['refs'][0][1:-1]].json(),
                              'negative':values[state['refs'][1][1:-1]].json(),'evidence_ids':state['ids'],
                              'dependence_groups':sorted(state['groups']),'origin':'direct-native-revision'}
    model.ledger_digest=digest([r['evidence_id'] for r in records])
    model.training_report={'records':len(records),'native_revision_nodes':len(nodes),'executed_native_calls':session.calls,
                           'excluded_updates':excluded[:50],'excluded_update_count':len(excluded),'excluded_updates_digest':digest(excluded),
                           'exclusion_audit':'First 50 exclusions shown; full deterministic set recoverable by replay, sealed by digest.',
                           'dependence_aware':options.get('dependence_aware',True),
                           'credit_assignment':'Correlated projections are alternative conditionals; never fused or revised together.',
                           'induction_enabled':options.get('induction',False),'migration':'Replay schema-3 evidence from original labeled inputs; never relabel schema-2 hashes.'}
    if options.get('induction',False): integrate_induction(model,records,session)
    if checkpoint: model.export(checkpoint)
    return model


def integrate_induction(model,records,session):
    """Experimental conditional induction in a declared empirical sampling frame.

    One representative per dependence group and mover kind. A is a coarse local
    relation, B its first observed distance subgroup, C the legal-outcome class.
    Counts are sensor/label statistics, confidence conversion and induction native.
    Extrapolation assumes residual exchangeability, not independent chess laws.
    """
    representatives={}
    for r in records:
        p=r['payload']
        if p['observation_tv']['confidence']>0:
            representatives.setdefault((p['population_stratum'],p['dependence_group']),r)
    populations={}
    for (piece,group),r in representatives.items(): populations.setdefault(piece,[]).append(r)
    jobs=[];specs={};guards=[]
    for key,h in model.hypotheses.items():
        if h['tier']!=4 or h['target']!='LegalMove': continue
        population=populations.get(h['descriptor']['piece'],[]);n=len(population)
        a=[r for r in population if any(t['id']==key for t in r['payload']['targets'])]
        if len(a)<2 or n<4: guards.append({'hypothesis':key,'reason':'insufficient independent representatives'});continue
        distance=a[0]['payload']['distance'];b=[r for r in a if r['payload']['distance']==distance]
        nc=sum(r['payload']['label'] for r in population);nbc=sum(r['payload']['label'] for r in b)
        if not b or len(b)==n: guards.append({'hypothesis':key,'reason':'degenerate marginal denominator'});continue
        counts={'N':n,'A':len(a),'B':len(b),'C':nc,'BA':len(b),'BC':nbc}
        s=[len(a)/n,len(b)/n,nc/n,1.,nbc/len(b)]
        confidence_name=f'ic{len(specs)}';name=f'i{len(specs)}'
        jobs.append((confidence_name,f'(stv 1.0 (Truth_w2c {float(len(b))}))'))
        # Extract confidence with native let; no host uncertainty formula.
        tvs=' '.join(f'(stv {v!r} $c)' for v in s)
        expr=f'(let (stv $s $c) ({confidence_name}) (Truth_Induction {tvs}))'
        jobs.append((name,expr))
        specs[key]={'node':name,'expression':expr,'premises':s,'counts':counts,'distance_subgroup':distance,
                    'sampling_frame':'First observation per (piece, dependence group), deterministic ledger order.',
                    'assumption':'Residual exchangeability outside the observed distance subgroup; experimental.',
                    'evidence_ids':[r['evidence_id'] for r in population],
                    'dependence_groups':[r['payload']['dependence_group'] for r in population]}
    values=session.batch(jobs)
    for key,spec in specs.items(): model.induction[key]={**spec,'truth_value':values[spec['node']].json(),'origin':'native-Truth_Induction','experimental':True}
    model.training_report['induction']={'integrated':len(specs),'guards':guards,'native_nodes':len(jobs),'production_default':False}
