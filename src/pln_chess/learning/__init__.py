"""Revision of seeded conditional cases; abstraction is explicit host grouping."""
from __future__ import annotations
from dataclasses import dataclass, field
from pln_chess.common import read_json,write_json,digest
from pln_chess.hypotheses import GRAMMAR_VERSION
from pln_chess.pln import Runtime,TV

PRIOR=TV(0.5,0.05)

@dataclass
class Model:
    runtime_version: str
    variant: str='full'
    hypotheses: dict=field(default_factory=dict)
    ledger_digest: str=''
    training_report: dict=field(default_factory=dict)
    schema: int=1
    grammar: str=GRAMMAR_VERSION

    @property
    def version(self):
        return digest({'runtime':self.runtime_version,'grammar':self.grammar,'variant':self.variant,
                       'hypotheses':self.hypotheses,'ledger':self.ledger_digest})

    def export(self,path):
        value={'schema':self.schema,'grammar':self.grammar,'runtime_version':self.runtime_version,
               'variant':self.variant,'hypotheses':self.hypotheses,'ledger_digest':self.ledger_digest,
               'training_report':self.training_report,'version':self.version}
        write_json(path,value)
        return {'path':str(path),'version':self.version,'hypotheses':len(self.hypotheses)}

    @classmethod
    def load(cls,path,runtime=None):
        data=read_json(path)
        if data.get('schema')==8:
            from pln_chess.cycle8.model import PromotionModel
            return PromotionModel.load(path,runtime)
        if data.get('schema')==7:
            from pln_chess.cycle7.model import BackoffModel
            return BackoffModel.load(path,runtime)
        if data.get('schema')==6:
            from pln_chess.cycle6.model import ModeModel
            return ModeModel.load(path,runtime)
        if data.get('schema')==5:
            from pln_chess.cycle5.model import PremiseModel
            return PremiseModel.load(path,runtime)
        if data.get('schema')==4:
            from pln_chess.cycle4.model import FactoredModel
            return FactoredModel.load(path,runtime)
        if data.get('schema')==3:
            from pln_chess.cycle3.model import RelationalModel
            return RelationalModel.load(path,runtime)
        if data.get('schema')==2:
            from pln_chess.cycle2.model import HierarchicalModel
            return HierarchicalModel.load(path,runtime)
        version=data.pop('version'); model=cls(**data)
        if model.schema != 1 or model.grammar != GRAMMAR_VERSION: raise ValueError('Unsupported checkpoint schema/grammar')
        if model.version!=version: raise ValueError('Checkpoint integrity mismatch')
        if runtime and runtime.version!=model.runtime_version: raise ValueError('Checkpoint/runtime mismatch')
        for value in model.hypotheses.values():
            TV.from_json(value['positive']); TV.from_json(value['negative'])
        return model

    def belief(self,key):
        return self.hypotheses.get(key,{'positive':PRIOR.json(),'negative':PRIOR.json(),'evidence_ids':[],
                                        'dependence_groups':[],'descriptor':None,'target':'unlearned'})

    def inspect_hypothesis(self,key): return {'id':key,**self.belief(key),'model_version':self.version}


def train(ledger,runtime=None,variant='full',through_sequence=None,dependence_aware=True):
    """Deterministic replay, optionally through a prior sequence for rollback.

    Each dependence group contributes at most once to each conditional case.
    Correlated conflicts are retained in the ledger and explicitly excluded.
    Positive and negative channels share provenance and are NEVER revised together.
    """
    runtime=runtime or Runtime()
    records=[r for r in ledger.records() if through_sequence is None or r['sequence']<=through_sequence]
    model=Model(runtime.version,variant=variant)
    nodes=[]; states={}; accepted=[]; skipped=[]; update_rows=[]
    for record in records:
        payload=record['payload']
        if payload['runtime_version']!=runtime.version: raise ValueError('Ledger/runtime mismatch')
        if payload.get('variant','full')!=variant: raise ValueError('Ledger representation mismatch')
        if payload['observation_tv']['confidence']==0:
            skipped.append({'evidence_id':record['evidence_id'],'reason':'zero confidence'}); continue
        for target in payload['targets']:
            key=target['key']; group=payload['dependence_group']
            state=states.setdefault(key,{'refs':[PRIOR.metta(),PRIOR.metta()], 'groups':set(), 'ids':[],
                                         'descriptor':target['descriptor'],'target':target['predicate']})
            if dependence_aware and group in state['groups']:
                skipped.append({'evidence_id':record['evidence_id'],'hypothesis':key,'reason':'correlated group already contributed'})
                continue
            state['groups'].add(group); state['ids'].append(record['evidence_id'])
            before=list(state['refs'])
            for channel,label in enumerate((target['label'],not target['label'])):
                observation=TV(float(label),payload['observation_tv']['confidence'])
                name=f'u{len(nodes)}'
                # This is a native revision of the SAME conditional proposition.
                expr=f'(let ($a $t) (|- (H {state["refs"][channel]}) (H {observation.metta()})) $t)'
                nodes.append((name,expr)); state['refs'][channel]=f'({name})'
            accepted.append({'evidence_id':record['evidence_id'],'hypothesis':key})
            update_rows.append({'evidence_id':record['evidence_id'],'hypothesis':key,'before':before,'after':list(state['refs'])})
    # Split into bounded batches, replacing earlier references with raw native TVs.
    values={}
    for start in range(0,len(nodes),250):
        batch=[]
        import re
        for name,expr in nodes[start:start+250]:
            expr=re.sub(r'\((u\d+)\)',lambda m:values[m[1]].metta() if m[1] in values else m[0],expr)
            batch.append((name,expr))
        values.update(runtime.batch(batch))
    def resolve(ref):
        if ref.startswith('(u'): return values[ref[1:-1]].json()
        return PRIOR.json()
    for key,state in states.items():
        model.hypotheses[key]={'positive':resolve(state['refs'][0]),'negative':resolve(state['refs'][1]),
                               'evidence_ids':state['ids'],'dependence_groups':sorted(state['groups']),
                               'descriptor':state['descriptor'],'target':state['target']}
    for update in update_rows:
        update['before']=[resolve(r) for r in update['before']]; update['after']=[resolve(r) for r in update['after']]
    model.ledger_digest=digest([{'evidence_id':r['evidence_id'],'sequence':r['sequence']} for r in records])
    model.training_report={'records':len(records),'accepted_updates':len(accepted),'excluded_updates':skipped,
                           'native_rule':'|- / Truth_Revision','native_invocations':len(nodes),
                           'dependence_aware':dependence_aware,'updates':update_rows,
                           'generalization':'typed relative categorical abstraction; native induction verified separately, not used for rule search'}
    return model
