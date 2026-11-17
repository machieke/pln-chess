"""Dependent interventions and composition counterexamples, outside scoring."""
import argparse
import copy
from dataclasses import replace
from pathlib import Path

from pln_chess.common import digest,read_json,write_json
from research.cycle15.native_reasoner import Budgets,NativeReasoner,Sentence
from research.cycle15.queries import infer_state
from research.cycle15.observations import observe
from research.cycle15.knowledge import load_rules
from training.cycle15_consequences import evidence,fit
from .cycle15_corpus import registration,episode,variants,reference
from .cycle15_consequences import compact


def run(out,checkpoint):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);reasoner=NativeReasoner();model=read_json(checkpoint)
    roots=registration();short=episode(next(r for r in roots if r['split']=='development' and r['family']['length']==2))
    long=episode(next(r for r in roots if r['split']=='development' and r['family']['length']>=4))
    rows=[]
    def record(name,result,state=None,query=None,**extra):
        row=dict(name=name,result=compact(result,out),**extra)
        if state is not None:row['reference']=reference(state,query)
        rows.append(row);print(name,row['result']['classification'],flush=True)
        return row
    for e in (short,long):
        for name,(before,after) in variants(e).items():
            record(f"scenario-{e['root']['family']['length']}-{name}",
                infer_state(after,e['query'],model,reasoner=reasoner),after,e['query'])
    for name,kwargs in [('renamed',dict(renamed=True)),('translated',dict(translated=True))]:
        changed=episode(short['root'],**kwargs)
        record(name,infer_state(changed['after'],changed['query'],model,reasoner=reasoner),changed['after'],changed['query'])
    baseline=infer_state(short['after'],short['query'],model,reasoner=reasoner)
    record('learned-baseline',baseline,short['after'],short['query'])
    record('remove-sole-attack-rule',infer_state(short['after'],short['query'],model,reasoner=reasoner,
        remove_rules=('rook-attack','bishop-attack','queen-orthogonal','queen-diagonal')))
    record('remove-one-clearance-path-with-surviving-alternative',infer_state(short['after'],short['query'],model,
        reasoner=reasoner,remove_rules=('clear-one',)))
    facts,scope=observe(short['after'],short['query']['attacker'],short['query']['target'])
    empty=[f.term for f in facts if f.term.startswith('(Empty ')]
    record('remove-essential-emptiness',infer_state(short['after'],short['query'],model,reasoner=reasoner,omit_terms=empty))
    # Production domain rules are unchanged: this registered model intervention
    # changes learned parameters only, preserving their evidential identities.
    for name,tv in [('untrained-prior',dict(strength=.5,confidence=0.)),('changed-rule-strength',dict(strength=.1,confidence=.9))]:
        changed=copy.deepcopy(model)
        for rule in changed['rules']:
            if rule!='obstruction':changed['rules'][rule]['truth_value']=tv
        changed['version']=digest({k:v for k,v in changed.items() if k!='version'})
        record(name,infer_state(short['after'],short['query'],changed,reasoner=reasoner))
    # Role-correct imported-attack chains and explicit state/ownership failures.
    exposure={**short['query'],'predicate':'KingExposed'}
    for name,state in [('actor-king',short['after']),('ordinary-target',variants(short)['ordinary-target'][1]),
                       ('friendly-source',variants(short)['friendly-source'][1])]:
        record('stage-a-'+name,infer_state(state,exposure,reasoner=reasoner,imported_attack=True,
            budgets=Budgets(128,256,512,30)),state,exposure)
    record('stage-b-exposure',infer_state(short['after'],exposure,model,reasoner=reasoner,
        budgets=Budgets(128,256,512,30)),short['after'],exposure)
    all_rules=load_rules(model);a=short['query']['attacker'];t=short['query']['target'];s=short['after']['id']
    query=f'(Attack {a} {t} {s})';contrary=f'(NoAttack {a} {t} {s})'
    swapped=[replace(f,term=f.term.replace(t,'other_target')) if f.term.startswith('(RayPath ') else f for f in facts]
    record('shared-target-swap',reasoner.infer(swapped,all_rules,query,contrary=contrary,budgets=Budgets(64,128,256,15)))
    oldfacts,_=observe(short['state'],a,t)
    record('stale-before-plus-after',reasoner.infer(facts+oldfacts,all_rules,query,contrary=contrary,budgets=Budgets(128,256,512,30)))
    # Competing observations are only injected through the low-level audit API.
    # The public state API rejects inconsistent occupancy.
    one_empty=next(f for f in facts if f.term.startswith('(Empty '))
    conflicting=Sentence(one_empty.term.replace('(Empty ','(Occupied '),1.,.99,('contrary_sensor',),'audit-input')
    record('competing-occupancy-audit',reasoner.infer(facts+[conflicting],all_rules,query,contrary=contrary,budgets=Budgets(128,256,512,30)))
    noise=Sentence(f'(Unrelated noise {s})',1.,.99,('irrelevant',),'audit-input')
    record('irrelevant-fact',reasoner.infer(facts+[noise],all_rules,query,contrary=contrary,budgets=Budgets(64,128,256,15)))
    for steps in (8,24,64,128):
        record('chess-steps-'+str(steps),infer_state(short['after'],short['query'],model,reasoner=reasoner,
            budgets=Budgets(steps,128 if steps<128 else 256,256 if steps<128 else 512,30)))
    record('reversed-input-order',reasoner.infer(list(reversed(facts)),list(reversed(all_rules)),query,contrary=contrary,budgets=Budgets(64,128,256,15)))
    record('long-path-generous',infer_state(long['after'],long['query'],model,reasoner=reasoner,budgets=Budgets(128,256,512,30)))
    # Equal global counts, differing membership in the queried path.
    pairs=[]
    for name,state in [('on-ray',short['state']),('off-ray',short['after'])]:
        result=infer_state(state,short['query'],model,reasoner=reasoner)
        pairs.append(dict(name=name,total_pieces=len(state['pieces']),occupied_cells=len(state['pieces']),
                          empty_cells=64-len(state['pieces']),reference=reference(state,short['query']),result=compact(result,out)))
    assert pairs[0]['reference']['label']!=pairs[1]['reference']['label']
    write_json(out/'information-loss.json',dict(panel=pairs,scope='Equal global occupancy counts, different connected query-ray membership; not representative accuracy'))
    trainrows=evidence([r for r in roots if r['split']=='train'])
    replay,ledger=fit(trainrows+trainrows,out/'replay',reasoner=reasoner)
    assert replay['rules']==model['rules']
    # Select the first registered training root for the held-out kind, by structure
    # only. Removing it changes the same rule queried on the development case.
    kind=short['root']['family']['kind'];direction=short['root']['family']['direction']
    name=kind+'-attack' if kind!='queen' else 'queen-'+('orthogonal' if 0 in direction else 'diagonal')
    ancestry=model['rules'][name]['ancestry'][0]
    refit,_=fit(trainrows,out/'leave-one-ancestry-out',exclude_ancestry=(ancestry,),reasoner=reasoner)
    refitted=infer_state(short['after'],short['query'],refit,reasoner=reasoner)
    record('leave-one-ancestry-out',refitted,excluded_ancestry=ancestry,
        before_rule=model['rules'][name]['truth_value'],after_rule=refit['rules'][name]['truth_value'])
    write_json(out/'learning-interventions.json',dict(replay_parameters_identical=True,
        duplicate_admissions_rejected=sum(r['action']=='duplicate-ancestry-rejected' for r in ledger),
        removed_ancestry=ancestry,heldout_rule=name,before_prediction=baseline['answer'],after_prediction=refitted['answer'],
        source='development interventions; final test untouched'))
    write_json(out/'interventions.json',rows)
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--checkpoint',required=True)
    a=p.parse_args();run(a.out,a.checkpoint)
