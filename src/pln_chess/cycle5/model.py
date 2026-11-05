"""Versioned premise ledger plus an immutable embedded Cycle 4 reference model."""
from dataclasses import dataclass,field,asdict
from pathlib import Path
from pln_chess.common import digest,read_json,write_json
from pln_chess.pln import Runtime,TV
from pln_chess.learning import PRIOR
from pln_chess.evidence import Ledger
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle4.model import FactoredModel
from pln_chess.cycle5 import SCHEMA
from pln_chess.cycle5.ontology import relation

VARIANTS=('C5-full','C5-abstract-only','C5-no-new-negatives')

@dataclass
class PremiseModel:
    runtime_version:str
    base:dict
    hypotheses:dict=field(default_factory=dict)
    ledger_digest:str=''
    training_report:dict=field(default_factory=dict)
    variant:str='C5-full'
    schema:int=5
    grammar:str=SCHEMA

    @property
    def version(self):return digest(asdict(self))
    def base_model(self):return FactoredModel(**self.base)
    def export(self,path):
        write_json(path,{**asdict(self),'version':self.version})
        return {'path':str(path),'version':self.version,'hypotheses':len(self.hypotheses)}
    @classmethod
    def load(cls,path,runtime=None):
        data=read_json(path);version=data.pop('version');m=cls(**data)
        if m.schema!=5 or m.grammar!=SCHEMA or m.variant not in VARIANTS:raise ValueError('Unsupported Cycle 5 representation')
        if m.version!=version:raise ValueError('Checkpoint integrity mismatch')
        if runtime and runtime.version!=m.runtime_version:raise ValueError('Checkpoint/runtime mismatch')
        b=m.base_model()
        if b.schema!=4 or b.runtime_version!=m.runtime_version or b.version!=m.training_report['base_version']:raise ValueError('Invalid embedded reference model')
        for key,h in m.hypotheses.items():
            if key!=relation(h['family'],h['descriptor'],h['target'])['id']:raise ValueError('Noncanonical premise identity')
            for channel in ('positive','negative'):TV.from_json(h[channel])
        return m
    def inspect_hypothesis(self,key):return {'id':key,**self.hypotheses.get(key,{}),'model_version':self.version}

def train(examples,base,runtime=None,ledger_path=None,through_sequence=None,retract_groups=(),variant='C5-full'):
    runtime=runtime or Runtime(timeout=300)
    if variant not in VARIANTS:raise ValueError('Unknown representation')
    ledger=examples if isinstance(examples,Ledger) else Ledger(ledger_path)
    if not isinstance(examples,Ledger):ledger.append_many(examples)
    records=[r for r in ledger.records() if (through_sequence is None or r['sequence']<=through_sequence)
             and not set([r['payload']['dependence_group']]+r['payload']['transformation_lineage'])&set(retract_groups)]
    states={};nodes=[];excluded=[]
    for record in records:
        p=record['payload']
        if p['model_version']!=SCHEMA or p['runtime_version']!=runtime.version:raise ValueError('Evidence/runtime/schema mismatch')
        tv=TV.from_json(p['observation_tv'])
        if tv.confidence==0:continue
        groups=set([p['dependence_group']]+p['transformation_lineage'])
        for rel in p['targets']:
            if type(rel['label']) is not bool:raise ValueError('Premise labels must be Boolean')
            key=relation(rel['family'],rel['descriptor'],rel['target'])['id']
            if key!=rel['id']:raise ValueError('Invalid relation identity')
            s=states.setdefault(key,{'relation':{k:v for k,v in rel.items() if k!='label'},'groups':set(),'ids':[],
                                    'positive':[],'negative':[],'refs':[PRIOR.metta(),PRIOR.metta()]})
            if groups&s['groups']:excluded.append([record['evidence_id'],key]);continue
            s['groups'].update(groups);s['ids'].append(record['evidence_id']);s['positive' if rel['label'] else 'negative'].append(record['evidence_id'])
            for n,label in enumerate((rel['label'],not rel['label'])):
                name=f'v5u{len(nodes)}';nodes.append((name,f'(Truth_Revision {s["refs"][n]} {TV(float(label),tv.confidence).metta()})'));s['refs'][n]=f'({name})'
    session=NativeSession(runtime);values=session.batch(nodes)
    hypotheses={key:{**s['relation'],'positive':values[s['refs'][0][1:-1]].json(),'negative':values[s['refs'][1][1:-1]].json(),
                      'evidence_ids':s['ids'],'dependence_groups':sorted(s['groups']),
                      'supporting_evidence':s['positive'],'contradicting_evidence':s['negative'],'origin':'learned-native-revision'} for key,s in states.items()}
    return PremiseModel(runtime.version,asdict(base),hypotheses,digest([r['evidence_id'] for r in records]),
                        {'base_version':base.version,'records':len(records),'excluded_updates':excluded,'revision_nodes':len(nodes),
                         'executed_calls':session.calls,'dependence_aware':True,'induction_enabled':False,
                         'positive_policy':'No global positive theorem; unsupported multi-premise composition abstains.',
                         'retract_groups':sorted(retract_groups),'through_sequence':through_sequence},variant)
