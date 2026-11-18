"""Registered falsification controls for native selection, identity and transport."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from pln_chess.common import digest
from research.cycle15.native_reasoner import Sentence,Budgets,parse
from research.cycle19.records import record
from .observations import build,fixture,COMBINED
from .native import derive,resume,projection
from .state import validate,query_list
from .demonstrations import rejected,equal

def identity_controls():
    state,rays=fixture();one=build(state,rays[:1]);two=build(state,rays)
    perm=build(state,rays[::-1]+rays)
    assert two==perm and len(two.lineage['cells'])==len(set(map(tuple,two.lineage['cells'].values())))==64
    assert one.lineage['cells']==two.lineage['cells']
    assert {f.stamps for f in one.facts}<={f.stamps for f in two.facts}
    maps=list(two.lineage['legacy_cell_maps'].values());assert maps[0]['cell_0']!=maps[1]['cell_0']
    def shared(st,kind):
        w=build(st,rays)
        return [k for k,v in w.lineage['observations'].items() if v['term'].startswith('('+kind+' ') and len(v['legacy'])>1]
    shared_empty=shared(state,'Empty');assert shared_empty
    blocked=deepcopy(state);blocked['pieces'].append(dict(id='joint_blocker',cell=[2,3],kind='pawn',owner='black'))
    blockers=shared(blocked,'Occupied');assert blockers
    unknown=deepcopy(state);unknown['unknown'].append([2,3])
    withheld=build(unknown,rays);ucell=next(k for k,v in withheld.lineage['cells'].items() if v==[2,3])
    assert any(f.term.startswith('(UnknownOccupancy '+ucell) for f in withheld.facts)
    assert not any(f.term.startswith('(Empty '+ucell) for f in withheld.facts)
    reversed_roles=build(state,[(rays[0][1],rays[0][0])]);assert reversed_roles.lineage['cells']==one.lineage['cells']
    renamed=deepcopy(state);renamed['pieces'][0]['id']='cell_0'
    alias=build(renamed,[('cell_0',rays[0][1])]);assert alias.lineage['pieces']['cell_0'] not in alias.lineage['cells']
    other=deepcopy(state);other['id']='other_state'
    assert not (set(build(other,rays).lineage['cells'])&set(two.lineage['cells']))
    distinct=build(state,rays,events=['capture_a','capture_b'])
    assert len(distinct.facts)==2*len(two.facts) and len({f.term for f in distinct.facts})==len(two.facts)
    assert build(state,rays,events=['capture_a','capture_a'])==build(state,rays,events=['capture_a'])
    return dict(passed=True,legacy_cell_zero=[m['cell_0'] for m in maps],shared_empty=shared_empty,shared_occupied=blockers,
        all_64_reversible=True,stable_under_expansion=True,permutation_and_duplicate_ray=True,
        reversed_roles=True,unknown_explicit=True,renamed_entity=True,different_state=True,
        distinct_event_same_proposition_retained=True,duplicate_event_idempotent=True,lineage=two.lineage)

def run(out):
    out=Path(out);identity=identity_controls();record(out/'identity.json',identity)
    state,rays=fixture();w=build(state,rays);q='(Attack a t s)';n='(NoAttack a t s)'
    zero='(Empty z s)';missing='(State outside)'
    def fact(text,stamp,confidence=.9,strength=1):
        return Sentence(text,strength,confidence,('audit_'+stamp,),'audit-input')
    facts=[fact(q,'first'),fact(q,'second',strength=.8),fact(n,'negative'),fact(zero,'zero',0)]
    qs=[q,n,zero,q,missing];budget=Budgets(0,16,16,15)
    result=derive(facts,[],qs,w.identity,budget)
    rev=derive(facts,[],qs[::-1],w.identity,budget);single=derive(facts,[],[q],w.identity,budget)
    ans=[v['answer'] for v in result['readouts']]
    assert ans==[v['answer'] for v in rev['readouts']][::-1] and ans[0]==ans[3]==single['readouts'][0]['answer']
    assert ans[0]['stamps']==['audit_first'] and ans[2] is ans[4] is None and projection(result,q,n)['classification']=='conflicting'
    assert result['state']['queues']==rev['state']['queues']==single['state']['queues']
    for bad in ([],None,'(State s)',['(State $x)'],['(State)'],['(Invalid s)']):
        assert rejected(lambda:query_list(bad))
    # Equal-priority task order, right below the strict native limits.
    small=Budgets(3,3,4,15)
    bounded=derive(facts,[],[q,n],w.identity,small)
    part=derive(facts,[],[q,n],w.identity,replace(small,steps=1))
    final=resume(part['state'],w.identity,part['state']['snapshot'],[q,n],2)
    assert equal(final,bounded) and part['selected']+final['selected']==bounded['selected']
    assert all(len(queue)<cap for queue,cap in zip(final['state']['queues'],(3,4)))
    empty=derive(facts,[],[q],w.identity,budget,tasks=[])
    again=resume(empty['state'],w.identity,empty['state']['snapshot'],[q],32)
    zero_run=resume(part['state'],w.identity,part['state']['snapshot'],[q,n],0)
    assert not again['selected'] and equal(empty,again) and not zero_run['selected'] and equal(part,zero_run)
    # A real native derivation expands a 256-sentence input beyond the fresh bound.
    seed=fact('(State seed)','source',1)
    rules=[fact(f'(Implication (State seed) (Empty c{i} seed))',f'rule_{i}',.8) for i in range(3)]
    many=[seed]+[fact(f'(State filler{i})',f'filler_{i}',.8) for i in range(252)]
    big=derive(many,rules,['(Empty c0 seed)'],w.identity,Budgets(1,512,512,30),tasks=[seed])
    assert len(big['state']['queues'][1])>256
    restored=resume(big['state'],w.identity,big['state']['snapshot'],['(Empty c0 seed)'])
    assert equal(big,restored)
    assert rejected(lambda:derive([*many,seed],rules,[q],w.identity))
    preserved=deepcopy(part['state']);sid=preserved['snapshot']
    assert rejected(lambda:resume(preserved,w.identity,sid,[q],32,timeout=.001))
    assert validate(preserved,w.identity,sid)==part['state']
    integrity={}
    def reject_mutation(name,mutate,rehash):
        value=deepcopy(preserved);mutate(value)
        if rehash:value['snapshot']=digest({k:v for k,v in value.items() if k!='snapshot'})
        integrity[name]=rejected(lambda:validate(value,w.identity,value['snapshot'] if rehash else sid))
    reject_mutation('reordered_under_old_id',lambda x:x['queues'][1].reverse(),False)
    reject_mutation('unsupported_schema',lambda x:x.update(schema='invalid'),True)
    reject_mutation('missing_queue',lambda x:x['queues'].pop(),True)
    reject_mutation('invalid_tv',lambda x:x['queues'][1][0][1][1].__setitem__(1,'1.5'),True)
    reject_mutation('invalid_constructor',lambda x:x['queues'][1][0][1].__setitem__(0,['Unregistered','a']),True)
    reject_mutation('incomplete',lambda x:x.update(resource_status='interrupted'),True)
    reject_mutation('capacity_mismatch',lambda x:x['capacities'].update(beliefs=1),True)
    for field in ('runtime','model'):
        integrity[field]=rejected(lambda:validate(preserved,replace(w.identity,**{field:'incorrect'}),sid))
    return record(out/'verified.json',dict(passed=True,tie_winner=ans[0],retained_zero=any(s[1][0]==parse(zero) for s in result['state']['queues'][1]),
        zero_readout=ans[2],missing=ans[4],conflict=True,duplicate_and_reverse=True,empty_and_zero_step=True,
        malformed_queries_rejected=True,near_capacity=[len(q) for q in final['state']['queues']],
        interrupted_child_rejected=True,source_preserved=True,real_large_native_return=len(big['state']['queues'][1]),
        fresh_limit_refused=True,large_receipt=big['state']['native_receipt'],integrity=integrity))
