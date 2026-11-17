"""Isolated latency categories; a stored answer is never called inference."""
import argparse
from pathlib import Path
import statistics
import time
from pln_chess.common import digest,write_json
from pln_chess.cycle14.proofs import ProofStore
from research.cycle15.native_reasoner import NativeReasoner,Budgets,save_result
from research.cycle15.queries import infer_state
from research.cycle15.observations import observe
from research.cycle15.knowledge import load_rules
from .cycle15_corpus import registration,episode


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);reasoner=NativeReasoner()
    root=next(r for r in registration() if r['split']=='development' and r['family']['length']==2)
    rows=[];example=None
    for scope in (False,True):
        for i in range(10):
            e=episode({**root,'seed':root['seed']+i},renamed=bool(i%2));state=e['after']
            state['id']+='bench'+str(i)
            started=time.perf_counter();result=infer_state(state,e['query'],reasoner=reasoner,full_scope=scope)
            elapsed=time.perf_counter()-started
            assert result['classification']=='supported-positive'
            rows.append(dict(category='cold-full' if scope else 'cold-scoped',repetition=i,
                wall_seconds=elapsed,native_wall_seconds=result['receipt']['wall_seconds'],
                rss_kib=result['receipt']['peak_rss_kib'],usage=result['usage'],evidence=save_result(result,out/'raw')))
            if example is None:example=(e,result)
    e,result=example;facts,_=observe(e['after'],e['query']['attacker'],e['query']['target']);rules=load_rules()
    for i in range(10):
        start=time.perf_counter()
        repeated=reasoner.infer(facts,rules,result['query'],contrary=result['contrary_query'],budgets=Budgets(64,128,256,15))
        rows.append(dict(category='repeated-native-materialized-inputs',repetition=i,wall_seconds=time.perf_counter()-start,
            classification=repeated['classification'],native_processes=1,evidence=save_result(repeated,out/'raw')))
    with ProofStore(out/'proofs.sqlite') as store:
        ref=store.put(result);identity=dict(state=e['after'],query=e['query'],model=result['model_identity'],
            budgets=result['budgets'],runtime=result['receipt']['runtime'],program_sha256=result['receipt']['program_sha256'])
        summary={k:result[k] for k in ('classification','answer','contrary','query')}
        handle=store.publish(ref,summary,identity)
        for i in range(10):
            start=time.perf_counter();retrieved=store.lookup(identity);elapsed=time.perf_counter()-start
            assert retrieved['summary']==summary
            rows.append(dict(category='stored-answer-retrieval',repetition=i,wall_seconds=elapsed,native_processes=0))
            start=time.perf_counter();expanded=store.expand(ref);elapsed=time.perf_counter()-start
            assert expanded==result
            rows.append(dict(category='full-proof-reconstruction',repetition=i,wall_seconds=elapsed,native_processes=0))
        changed={**identity,'state':{**e['after'],'history':'changed'}}
        assert store.lookup(changed) is None
        census=store.census();archive=store.archive(ref)
        with ProofStore() as clean:
            restored=clean.import_archive(archive)
            assert clean.expand(restored)==result
        write_json(out/'proof-integrity.json',dict(exact_roundtrip=True,changed_history_cache_miss=True,
            root=ref.id,handle=handle,archive_hash=archive['manifest_sha256'],census=census,
            evidence_occurrences_preserved=True,proof_scope=result['proof_status']))
    categories=sorted({r['category'] for r in rows})
    summary={name:dict(repetitions=len(selected:=[r for r in rows if r['category']==name]),
        median_seconds=statistics.median(r['wall_seconds'] for r in selected),
        min_seconds=min(r['wall_seconds'] for r in selected),max_seconds=max(r['wall_seconds'] for r in selected)) for name in categories}
    write_json(out/'samples.json',rows);write_json(out/'summary.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
