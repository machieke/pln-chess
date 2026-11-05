"""Public application contracts; training labels are provided by callers."""
from __future__ import annotations
from pathlib import Path
import re
from pln_chess.common import digest,canonical,read_json
from pln_chess.domain import Position,Move
from pln_chess.hypotheses import candidates
from pln_chess.observations import observe
from pln_chess.evidence import Ledger
from pln_chess.learning import Model,train as replay
from pln_chess.inference import infer_moves,Options
from pln_chess.pln import Runtime,TV
from pln_chess.spatial import translate,add,color_flip


def find_move(position,notation):
    return next((m for m in candidates(position) if m.notation==notation),None)


def explain_move(position,move,checkpoint=None,options=None,runtime=None):
    position=Position.from_fen(position) if isinstance(position,str) else position
    candidate=find_move(position,move) if isinstance(move,str) else move
    if candidate is None: raise ValueError('Move is outside the seeded candidate grammar')
    result=infer_moves(position,checkpoint,options,runtime,[candidate])
    return {k:v for k,v in result.items() if k!='candidates'} | {'candidate':result['candidates'][0]}


def observe_example(position,move,label,source,dependence_group,ledger_path,
                    runtime=None,variant='full',transformation_lineage=None,
                    auxiliary_labels=None,idempotency_key=None,observation_confidence=0.5):
    if variant in ('hierarchical','no-obstruction','no-exact'):
        from pln_chess.cycle2.model import observe_example as hierarchical_observe
        return hierarchical_observe(position,move,label,source,dependence_group,ledger_path,runtime,variant,
                                    transformation_lineage,auxiliary_labels,idempotency_key,observation_confidence)
    runtime=runtime or Runtime(); position=Position.from_fen(position) if isinstance(position,str) else position
    move=find_move(position,move) if isinstance(move,str) else move
    if move is None: raise ValueError('Move outside candidate grammar')
    if type(label) is not bool: raise ValueError('Label must be Boolean')
    obs=observe(position,move,variant)
    targets=[{'key':obs['key'],'descriptor':obs['context'],'predicate':'LegalMove','label':label}]
    # An illegal observation is never assigned to general movement geometry.
    if label:
        targets.append({'key':obs['geometry_key'],'descriptor':obs['pattern'],'predicate':'MovementPatternSupported','label':True})
    labels=auxiliary_labels or {}
    for attack in obs['attacks']:
        if attack['attacker_id'] in labels:
            if type(labels[attack['attacker_id']]) is not bool: raise ValueError('Attack label must be Boolean')
            targets.append({'key':attack['key'],'descriptor':attack['descriptor'],'predicate':'Attack','label':labels[attack['attacker_id']]})
    payload={'position_id':position.id,'candidate_id':move.id,'relative_feature_fingerprint':obs['key'],
             'label':label,'source':source,'dependence_group':dependence_group,
             'observation_tv':TV(float(label),observation_confidence if obs['complete'] else 0).json(),
             'targets':targets,'runtime_version':runtime.version,'model_version':'seed-v1','variant':variant,
             'transformation_lineage':transformation_lineage or [],'input':{'fen':position.fen(),'move':move.notation}}
    return Ledger(ledger_path).append(payload,idempotency_key)

observe_training_example=observe_example


def train(dataset,checkpoint=None,options=None,runtime=None,ledger_path=None):
    runtime=runtime or Runtime(); options=options or {}
    if options.get('representation')=='hierarchical-relative-v2' or options.get('variant') in ('hierarchical','no-obstruction','no-exact'):
        from pln_chess.cycle2.model import train as hierarchical_train
        return hierarchical_train(dataset,checkpoint,options,runtime,ledger_path)
    if isinstance(dataset,Ledger): ledger=dataset
    else:
        rows=read_json(dataset) if isinstance(dataset,(str,Path)) else dataset
        if isinstance(rows,dict): rows=rows['examples']
        if ledger_path is None: raise ValueError('A ledger_path is required for dataset ingestion')
        ledger=Ledger(ledger_path)
        for row in rows:
            observe_example(row['fen'],row['move'],row['label'],row['source'],row['dependence_group'],ledger.path,
                            runtime,options.get('variant','full'),row.get('transformation_lineage'),row.get('attack_labels'),
                            observation_confidence=row.get('confidence',0.5))
    model=replay(ledger,runtime,options.get('variant','full'),options.get('through_sequence'),
                 options.get('dependence_aware',True))
    if checkpoint: model.export(checkpoint)
    return model


def export_model(model,path): return model.export(path)
def import_model(path): return Model.load(path,Runtime())
def export_rule_beliefs(model): return {'model_version':model.version,'hypotheses':model.hypotheses}
def inspect_hypothesis(model,id): return model.inspect_hypothesis(id)


def compare_transforms(position,transform=(1,0),checkpoint=None,move=None,runtime=None):
    runtime=runtime or Runtime(); position=Position.from_fen(position) if isinstance(position,str) else position
    if transform=='color-flip':
        other=color_flip(position)
        transform_square=lambda square:(square[0],7-square[1])
    else:
        other=translate(position,transform)
        transform_square=lambda square:add(square,transform)
    original=list(candidates(position)) if move is None else [find_move(position,move)]
    if None in original: raise ValueError('Unknown move')
    transformed=[Move(transform_square(m.start),transform_square(m.end),m.promotion,m.effect) for m in original]
    a=infer_moves(position,checkpoint,runtime=runtime,selected_moves=original)
    b=infer_moves(other,checkpoint,runtime=runtime,selected_moves=transformed)
    checks=[]
    for x,y in zip(a['candidates'],b['candidates']):
        valid=x['observations']['context']==y['observations']['context']
        def proof(c):
            s=canonical(c['proof_trace'])
            s=s.replace(c['observations']['position_id'],'STATE').replace(c['candidate_id'],'MOVE')
            return s
        checks.append({'move':x['move'],'translated_move':y['move'],'context_preserved':valid,
                       'original_tv':x['legal_move_truth_value'],'translated_tv':y['legal_move_truth_value'],
                       'truth_equal':x['legal_move_truth_value']==y['legal_move_truth_value'],
                       'rules_equal':x.get('matched_rule_ids')==y.get('matched_rule_ids'),
                       'proof_isomorphic':proof(x)==proof(y),
                       'status':'incomplete' if a['truncated'] or b['truncated'] else 'tested' if valid else 'excluded-context-changed'})
    return {'passed':not(a['truncated'] or b['truncated']) and any(c['context_preserved'] for c in checks) and all(c['truth_equal'] and c['rules_equal'] and c['proof_isomorphic'] for c in checks if c['context_preserved']),
            'transform':transform if isinstance(transform,str) else list(transform),'checks':checks,'tested':sum(c['context_preserved'] for c in checks),
            'runtime_version':runtime.version,'model_version':a['model_version']}
