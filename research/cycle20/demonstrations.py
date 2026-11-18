"""Compact native witnesses and laboratory controls over registered raw inputs."""
from copy import deepcopy
from dataclasses import asdict,replace
from pathlib import Path
from pln_chess.common import ROOT,read_json,digest
from pln_chess.pln import NativeError
from research.cycle15.native_reasoner import Budgets,Sentence
from research.cycle19.records import record
from .observations import build,fixture,models,COMBINED
from .native import derive,resume,ExecutionFailure,projection
from .state import export,restore
from .resident import Session
from .lifecycle import Generations

def equal(a,b):
    return a['state']['queues']==b['state']['queues'] and [x['answer'] for x in a['readouts']]==[x['answer'] for x in b['readouts']]

def rejected(fn):
    try:fn()
    except (ValueError,KeyError,ExecutionFailure,NativeError):return True
    raise AssertionError('Unavailable generation was accepted')

def call(w,steps=64,qs=None,budget=COMBINED):
    return derive(w.facts,w.rules,w.queries if qs is None else qs,w.identity,replace(budget,steps=steps))

def compact(mode,out,meter=None):
    out=Path(out);s,roles=fixture();w=build(s,roles,models()['D-AB'])
    if mode in ('batch','combined'):
        if mode=='batch':w=build(s,roles[:1],models()['D-AB'])
        result=call(w)
        assert result['derivations']==1
        return record(out/'verified.json',dict(passed=True,mode=mode,rays=w.rays,lineage=w.lineage,result=result))
    if mode=='continuation':return continuation(out)
    if mode=='residency':return residency(out,meter)
    if mode in ('correction','history'):return changes(out,only_history=mode=='history')
    raise ValueError(mode)

def continuation(out):
    results=[]
    for dense,schedule in ((False,[16,16,32]),(True,[32,64])):
        s,roles=fixture(dense);w=build(s,roles,models()['D-AB'])
        whole=call(w,sum(schedule));part=call(w,schedule[0]);trace=list(part['selected'])
        first=part;refs=[part['state']['snapshot']]
        for i,steps in enumerate(schedule[1:]):
            sid=part['state']['snapshot'];path=out/f'{dense}-{i}.json'
            export(path,part['state'],w.identity);saved=restore(path,w.identity,sid)
            read=resume(saved,w.identity,sid,w.queries)
            assert equal(part,read) and read['derivations']==0
            part=resume(saved,w.identity,sid,w.queries,steps)
            trace.extend(part['selected']);refs.append(part['state']['snapshot'])
        assert equal(whole,part) and trace==whole['selected']
        results.append(dict(dense=dense,schedule=schedule,steps=len(trace),remaining=len(part['state']['queues'][0]),
            retained=len(part['state']['queues'][1]),selected_equal=True,raw_queues_equal=True,readouts_equal=True,
            partial_has_variables='$' in str(first['state']['queues']),parent_chain=refs,
            uninterrupted=whole['state']['native_receipt'],last_chunk=part['state']['native_receipt']))
    return record(out/'verified.json',dict(passed=True,comparisons=results))

def residency(out,meter):
    s,roles=fixture();w=build(s,roles,models()['D-AB'])
    full=call(w,64);q=['(State '+s['id']+')']
    with Session(meter) as live:
        pid=live.proc.pid
        initial=live.load(w,w.queries[:1],replace(COMBINED,steps=16));sid=initial['state']['snapshot']
        later=live.read(w.identity,sid,q)
        reference=resume(initial['state'],w.identity,sid,q)
        assert later[0]['answer']==reference['readouts'][0]['answer'] and later[0]['answer']
        final=live.advance(w.identity,sid,w.queries,48)
        assert equal(final,full) and initial['selected']+final['selected']==full['selected']
        assert rejected(lambda:live.read(w.identity,sid,q))
        assert live.proc.pid==pid
        frames=deepcopy(live.frames)
    assert live.proc is None and rejected(lambda:live.read(w.identity,final['state']['snapshot'],q))
    return record(out/'verified.json',dict(passed=True,pid=pid,load_snapshot=sid,later=later,
        frames=frames,request_bytes=[r['input_bytes'] for r in frames],late_derivations=0,
        fresh_parity=True,stale_rejected=True,shutdown_verified=True,continued_steps=len(final['selected'])))

def corrected(s,kind):
    s=deepcopy(s)
    if kind=='occupied':s['pieces'].append(dict(id='correction_piece',cell=[3,3],kind='knight',owner='black'))
    elif kind=='unknown':s['unknown'].append([3,3])
    elif kind=='identity':next(p for p in s['pieces'] if p['id']=='rowtarget')['id']='corrected_target'
    return s

def changes(out,only_history=False):
    s,rays=fixture();model=models()['D-AB'];w=build(s,rays,model);owner=Generations()
    original,first=owner.rebuild('main',w)
    rows,hit=owner.read(original,w.queries)
    assert not hit and owner.read(original,w.queries)==(rows,True)
    cold_new,hit=owner.read(original,['(State '+s['id']+')'])
    assert not hit and cold_new[0]['answer'] and original==owner.ticket('main')
    changes=[]
    for kind in (['occupied'] if only_history else ['occupied','unknown','identity','added-ray']):
        if changes:
            # Compare each alternative correction to the same observed base.
            owner.rebuild('main',w)
        st=corrected(s,kind);rs=[(a,'corrected_target' if kind=='identity' and t=='rowtarget' else t) for a,t in rays]
        if kind=='added-ray':rs.append(('coltarget','colrook'))
        old=owner.ticket('main');pending=owner.begin(['main'])
        assert rejected(lambda:owner.read(old,w.queries)) and rejected(lambda:owner.publish(pending,{}))
        replacement=build(st,rs,model)
        if kind=='added-ray':
            assert {f.stamps for f in w.facts} < {f.stamps for f in replacement.facts}
        new=call(replacement)
        fresh=call(build(deepcopy(st),deepcopy(rs),deepcopy(model)))
        assert equal(new,fresh) and new['selected']==fresh['selected']
        ticket=owner.publish(pending,{'main':(replacement,new)})['main']
        assert rejected(lambda:owner.check(old))
        changes.append(dict(kind=kind,old=asdict(old),replacement=asdict(ticket),fresh_parity=True,
            identity=asdict(replacement.identity),readouts=new['readouts'],receipt=new['state']['native_receipt']))
    historic=owner.historic(original.snapshot,w.queries)
    assert equal(first,historic)
    return record(out/'verified.json',dict(passed=True,original=first['state'],corrected=changes,
        historical_readouts=historic['readouts'],historical_exact=True,cache_hit=True,stale_rejected=True,
        pending_read_rejected=True,partial_publication_rejected=True,new_term_same_generation=cold_new))

def refit(out):
    from research.cycle19.study import prepare
    from research.cycle19.learning import fit
    roots=read_json(ROOT/'artifacts/cycle19/corpus-registration.json')['roots']
    training=[r for r in roots if r['population']=='natural-training']
    journal,_,annotations=prepare(training,False);excluded=training[0]['source_ancestry']
    old_model=models()['D-AB'];new=fit(journal,annotations,out/'refit','D-AB',exclude=(excluded,))['model']
    assert new==read_json(ROOT/'artifacts/cycle19/lifecycle/refits/leave-one/model.json')
    manager=Generations();state,rays=fixture();names={}
    for key,subset,model in [('first',rays[:1],old_model),('second',rays,old_model),('unrelated',rays,None)]:
        w=build(state,subset,model);names[key]=manager.rebuild(key,w)[0]
        manager.read(names[key],w.queries)
    pending=manager.invalidate_model(old_model['version'])
    assert set(pending)=={'first','second'} and manager.ticket('unrelated')==names['unrelated']
    staged={};results={}
    for key,subset in [('first',rays[:1]),('second',rays)]:
        assert rejected(lambda:manager.check(names[key]))
        w=build(state,subset,new);result=call(w);fresh=call(build(deepcopy(state),subset,new))
        assert equal(result,fresh) and result['selected']==fresh['selected']
        staged[key]=(w,result);results[key]=result['readouts']
    tickets=manager.publish(pending,staged)
    return record(out/'verified.json',dict(passed=True,excluded=excluded,old_model=old_model['version'],
        refit_model=new['version'],exact_cycle19_refit=True,old_tickets={k:asdict(v) for k,v in names.items()},
        new_tickets={k:asdict(v) for k,v in tickets.items()},new_readouts=results,unrelated_valid=True))
