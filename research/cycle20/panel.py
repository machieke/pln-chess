"""Registered combined-state and local-neighborhood comparison panels."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from pln_chess.common import ROOT,read_json,digest
from research.cycle15.native_reasoner import alpha_key
from research.cycle16.experiments import observations
from research.cycle19.records import record
from .compatibility import old_pair,projected,differences
from .observations import build,eligible,fixture,models,COMBINED,queries
from .native import derive
from .state import sentence


def inventory(workspace,result):
    tasks,beliefs=result['state']['queues']
    terms=[alpha_key(sentence(s)['term']) for s in beliefs]
    receipt=result['receipt']
    return dict(unique_input_facts=len({s.term for s in workspace.facts}),observation_records=len(workspace.facts),
                observation_events=len(workspace.lineage['observations']),source_captures=len(workspace.lineage['source_events']),
                observation_stamps=len({s for f in workspace.facts for s in f.stamps}),
                rule_schemas=len(workspace.rules),initial_tasks=len(workspace.facts)+len(workspace.rules),
                unique_retained_propositions=len(set(terms)),retained_sentences=len(terms),
                retained_alternatives=len(terms)-len(set(terms)),remaining_tasks=len(tasks),selected_tasks=len(result['selected']),
                process_starts=1,derivations=result['derivations'],native_readouts=len(result['readouts']),
                semantic_targets=2*len(workspace.rays),repeated_queries=len(workspace.queries)-len(set(workspace.queries)),
                cache_lookups=0,input_bytes=len(receipt['program'].encode()),output_bytes=receipt['output_bytes'],
                parse_seconds=result['parse_seconds'],wall_seconds=receipt['wall_seconds'],
                cpu_seconds=receipt['cpu_seconds'],peak_rss_kib=receipt['peak_rss_kib'])

def channel_payload(x):
    return None if x is None else (x['strength'],x['confidence'])

def compare_c(local,combined):
    return dict(local=local['classification'],combined=combined['classification'],
                classification_equal=local['classification']==combined['classification'],
                channels_tv_equal=all(channel_payload(local[k])==channel_payload(combined[k]) for k in ('answer','contrary')),
                channels_stamps_equal=all(local[k]==combined[k] for k in ('answer','contrary')),
                selected_counts=[len(local['selected']),len(combined['selected'])],
                queues=[[len(r['remaining']),len(r['retained'])] for r in (local,combined)])

def workloads():
    roots=read_json(ROOT/'artifacts/cycle19/corpus-registration.json')['roots']
    inputs=[('development',r['state'],eligible(r['state'])) for r in roots if r['split']=='development'][:8]
    for dense in (False,True):
        state,roles=fixture(dense)
        inputs.append(('constructed-density' if dense else 'constructed-crossing',state,roles))
    cases=[]
    for population,state,rays in inputs:
        mapping={str(n):min(len(rays),n) for n in (1,2,4,8)}
        for n in sorted(set(mapping.values())):
            if n:
                cases.append(dict(population=population,state=state,rays=rays[:n],available=len(rays),
                                  requested_to_available=mapping))
    return cases

def run_panel(dest,workers=3):
    dest=Path(dest);arms=models();cases=workloads()
    jobs=[(case,arm) for case in cases for arm in arms]
    planned=sum(1+4*len(case['rays']) for case,arm in jobs)
    registration=dest/'panel.json'
    if not registration.exists():record(registration,dict(cases=cases,arms=list(arms),expected_processes=planned))
    def run(job):
        case,arm=job;state=case['state'];model=arms[arm];w=build(state,case['rays'],model)
        key=digest([state['id'],w.rays,arm]);path=dest/'rows'/(key+'.json')
        if path.exists():return read_json(path)
        if len(w.facts)+len(w.rules)>256:
            return record(path,dict(population=case['population'],arm=arm,state=state['id'],size=len(w.rays),resource='fresh-capacity-refusal'))
        result=derive(w.facts,w.rules,w.queries,w.identity,COMBINED);comparisons=[];changed=[];receipts=[]
        for i,(a,t) in enumerate(w.rays):
            qs=w.queries[3*i:3*i+3]
            parts=projected(result,qs)
            separate=old_pair(w.facts,w.rules,qs,COMBINED)
            facts,local=observations(state,a,t)
            local_pair=old_pair(facts,w.rules,queries(state['id'],a,t,local['shape']),COMBINED)
            receipts.extend(digest(r['receipt']) for r in [*separate,*local_pair])
            if any(r['incomplete'] for r in [*separate,*local_pair]):raise RuntimeError('Incomplete comparison reference')
            for l,b,ref in zip(local_pair,parts,separate):
                comparisons.append(differences(b,ref));changed.append(compare_c(l,b))
        if case['population']=='constructed-crossing' and len(w.rays)==2 and arm=='D-AB':
            record(dest/'witness.json',dict(state=state,rays=w.rays,identity=asdict(w.identity),lineage=w.lineage,
                   inputs=dict(facts=[asdict(f) for f in w.facts],rules=[asdict(r) for r in w.rules]),native=result))
        return record(path,dict(population=case['population'],arm=arm,state=state['id'],size=len(w.rays),
            resource='executed',counts=inventory(w,result),status_counts=dict(Counter(r['combined'] for r in changed)),
            b_differences=comparisons,c=changed,readouts=result['readouts'],receipt=result['state']['native_receipt'],
            fresh_separate_receipts=receipts))
    with ThreadPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(run,jobs))
    executed=[r for r in rows if r['resource']=='executed'];c=[p for r in executed for p in r['c']]
    return record(dest/'summary.json',dict(workloads=len(rows),executed=len(executed),resource_refused=len(rows)-len(executed),
        planned_processes=planned,semantic_targets=len(c),b_mismatches=sum(bool(d) for r in executed for d in r['b_differences']),
        c_class_changes=sum(not p['classification_equal'] for p in c),c_tv_changes=sum(not p['channels_tv_equal'] for p in c),
        c_stamped_changes=sum(not p['channels_stamps_equal'] for p in c),c_transitions=dict(Counter(p['local']+' -> '+p['combined'] for p in c)),
        panel=[dict(state=c['state']['id'],population=c['population'],available=c['available'],mapping=c['requested_to_available'])
               for c in cases if len(c['rays'])==1]))
