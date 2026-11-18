"""Serial alternating-order measurements on the registered two-ray D-AB input."""
from collections import Counter,defaultdict
from dataclasses import replace
from pathlib import Path
import platform
import resource
from statistics import median
import time
from pln_chess.common import digest
from research.cycle15.native_reasoner import alpha_key
from research.cycle16.experiments import observations
from research.cycle19.records import record
from .compatibility import old_pair,projected
from .observations import build,fixture,models,queries,COMBINED,Workspace
from .state import Identity,export,restore
from .demonstrations import call,corrected
from .native import resume
from .lifecycle import Generations
from .resident import Session

def clock():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return time.perf_counter(),a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime

def run(dest,meter):
    dest=Path(dest);state,roles=fixture();model=models()['D-AB'];w=build(state,roles,model)
    local=[]
    for a,t in w.rays:
        facts,scope=observations(state,a,t)
        local.append(Workspace(Identity.create(state['id'],digest(scope),model['version'],'cycle19-local'),
            facts,w.rules,[(a,t)],queries(state['id'],a,t,scope['shape']),{}))
    corrected_state=corrected(state,'occupied')
    start=call(w);sid=start['state']['snapshot'];saved=dest/'original-state.json'
    export(saved,start['state'],w.identity)
    owner=Generations();ticket,_=owner.rebuild('timing',w);owner.read(ticket,w.queries)
    modes=['legacy-separate','local-batch','combined-separate','combined-batch','chunked','restored-read','resident-load-read-continue','host-cache','corrected-rebuild']
    samples=[]

    for rep in range(7):
        for name in modes[::1 if rep%2==0 else -1]:
            receipts=[];states=[];readouts=starts=derivations=0;parsing=0;classes=[];receipt_ids=[]
            def batch(r,requested,final=True):
                nonlocal starts,derivations,parsing,readouts
                starts+=1;derivations+=r['derivations'];readouts+=len(r['readouts']);parsing+=r['parse_seconds']
                receipts.append(r['receipt']);receipt_ids.append(r['state']['native_receipt'])
                states.append((len(r['selected']),r['state']['queues']))
                if final:
                    for j in range(0,len(requested),3):
                        classes.extend(p['classification'] for p in projected(r,requested[j:j+3]))
            def separate(space):
                nonlocal starts,derivations,readouts
                for j in range(0,len(space.queries),3):
                    for old in old_pair(space.facts,space.rules,space.queries[j:j+3],COMBINED):
                        if old['incomplete']:raise ValueError('Incomplete benchmark reference')
                        starts+=1;derivations+=1;readouts+=1+bool(old['contrary_query'])
                        receipts.append(old['receipt']);receipt_ids.append(digest(old['receipt']))
                        states.append((len(old['selected']),[old['remaining'],old['retained']]))
                        classes.append(old['classification'])
            if name=='corrected-rebuild':
                cold=Generations()
                cold.publish(cold.begin(['corrected']),{'corrected':(w,start)})
            before=clock()
            if name=='legacy-separate':
                for ws in local:separate(ws)
            elif name=='local-batch':
                for ws in local:batch(call(ws),ws.queries)
            elif name=='combined-separate':separate(w)
            elif name=='combined-batch':batch(call(w),w.queries)
            elif name=='chunked':
                part=call(w,16);batch(part,w.queries,False)
                batch(resume(part['state'],w.identity,part['state']['snapshot'],w.queries,48),w.queries)
            elif name=='restored-read':
                persisted=restore(saved,w.identity,sid)
                batch(resume(persisted,w.identity,sid,w.queries),w.queries)
            elif name=='resident-load-read-continue':
                with Session(meter,'benchmark-resident') as live:
                    init=live.load(w,w.queries[:1],replace(COMBINED,steps=16));batch(init,w.queries[:1],False)
                    late=live.read(w.identity,init['state']['snapshot'],['(State '+state['id']+')']);assert late[0]['answer']
                    readouts+=1;receipts.append(live.frames[-1]);receipt_ids.append(digest(live.frames[-1]))
                    batch(live.advance(w.identity,init['state']['snapshot'],w.queries,48),w.queries)
                    starts=1
            elif name=='host-cache':
                rows,hit=owner.read(ticket,w.queries);assert hit and len(rows)==6
            else:
                replacement=build(corrected_state,roles,model)
                _,rebuilt=cold.rebuild('corrected',replacement)
                batch(rebuilt,replacement.queries)
            after=clock()
            def term(row):
                from research.cycle15.native_reasoner import render
                return alpha_key(row['term'] if isinstance(row,dict) else render(row[1][0]))
            input_spaces=local if name in ('legacy-separate','local-batch') else [replacement] if name=='corrected-rebuild' else [w]
            memory=[r['peak_rss_kib'] for r in receipts if r.get('peak_rss_kib') is not None]
            sample=dict(repetition=rep,mode=name,wall_seconds=after[0]-before[0],cpu_seconds=after[1]-before[1],
                parse_seconds=parsing if name not in ('legacy-separate','combined-separate','host-cache') else None,
                child_peak_rss_kib=max(memory) if memory else None,process_highwater_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                native_receipts=receipt_ids,native_starts=starts,derivations=derivations,native_readouts=readouts,
                semantic_targets=4,duplicate_requested_queries=0,cache_lookups=int(name=='host-cache'),
                input_bytes=sum(r.get('input_bytes',len(r['program'].encode())) for r in receipts),
                output_bytes=sum(r['output_bytes'] for r in receipts),selected=sum(n for n,_ in states),
                unique_input_facts=len({f.term for ws in input_spaces for f in ws.facts}),
                observation_stamps=len({st for ws in input_spaces for f in ws.facts for st in f.stamps}),
                observation_records=sum(len(ws.facts) for ws in input_spaces),rule_schemas=len(w.rules),
                returned_queues=[dict(remaining=len(q[0]),retained=len(q[1]),unique_propositions=len({term(v) for v in q[1]})) for _,q in states],
                classification_counts=dict(Counter(classes)) if classes else dict(Counter(p['classification'] for i in (0,3) for p in projected(start,w.queries[i:i+3]))),
                incomplete=0,late_read_seconds=live.frames[1]['wall_seconds'] if name=='resident-load-read-continue' else None)
            samples.append(sample);record(dest/'samples'/f'{rep}-{name}.json',sample)
    summary={}
    for name in modes:
        rows=[r for r in samples if r['mode']==name];stats={}
        for field in ('wall_seconds','cpu_seconds','parse_seconds','child_peak_rss_kib','native_starts','derivations','native_readouts','selected','input_bytes','output_bytes','late_read_seconds'):
            values=[r[field] for r in rows if r[field] is not None]
            if values:stats[field]=dict(median=median(values),minimum=min(values),maximum=max(values))
        summary[name]=stats
    return record(dest/'summary.json',dict(paired_repetitions=7,sample_count=len(samples),hardware=platform.uname()._asdict(),
        fixture=state['id'],model=model['version'],modes=summary,ordering='alternating forward and reverse',
        timing_scope='Single serial host. Wall and user/system CPU include construction, native work and result projection. Cache prewarmed. Resident mode includes startup and shutdown. Per-child memory where GNU time is available.'))
