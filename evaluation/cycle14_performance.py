"""Isolated matched legacy and compact API timings, including audit export."""
import argparse
import hashlib
import lzma
import os
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
import tempfile
import time

from pln_chess.common import ROOT,canonical,digest,read_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle12.temporal import semantic_replay
from pln_chess.cycle13.api import PreferenceOptions,PreferenceSession
from pln_chess.cycle14.proofs import ProofStore
from evaluation.cycle13_performance import CountedRuntime,workloads
from evaluation.cycle14_profile import models
from evaluation.cycle14_metrics import percentile
from training.cycle14_labels import atomic_json


def worker(out,name,arm,repetition):
    from pln_chess.cycle13.api import compare_moves as old_compare
    from pln_chess.cycle13.temporal import analyze_continuations as old_temporal
    from pln_chess.cycle14.api import compare_moves as compact_compare,retrieve
    from pln_chess.cycle14.temporal import analyze_continuations as compact_temporal
    out=Path(out);started=time.perf_counter();runtime=CountedRuntime(timeout=900);runtime_load=time.perf_counter()-started
    started=time.perf_counter();loaded=models(runtime,'ply' in name);model_load=time.perf_counter()-started
    session=PreferenceSession(runtime);options=PreferenceOptions(timeout_seconds=900);workload=workloads(ROOT/'artifacts/cycle13')[name]
    compare,temporal=(old_compare,old_temporal) if arm=='legacy' else (compact_compare,compact_temporal)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='c14-benchmark-') as temporary,ProofStore(Path(temporary)/'proofs.sqlite') as store:
        for temperature in ('cold','warm'):
            before_calls,before_launches,before_native=runtime.invocations,runtime.process_launches,runtime.elapsed
            started=time.perf_counter();extra={'store':store} if arm=='compact' else {}
            if workload['kind']=='pairs':
                result=[compare(row['fen'],*row['moves'],**loaded,**extra,runtime=runtime,session=session,options=options,
                    history=row['history'],source='cycle14-matched-performance/'+row['id']) for row in workload['pairs']]
            else:
                plan=workload['plan'];h=workload['horizon'];branches={side:[line[:h]] for side,line in plan['branches'].items()}
                result=[temporal(plan['fen'],branches,**loaded,**extra,runtime=runtime,session=session,options=options,
                    history=plan['history'],horizons=(h,),source='cycle14-matched-performance/'+plan['id'],selection_provenance=plan['response_selection'])]
            inference=time.perf_counter()-started;launches=runtime.process_launches-before_launches
            started=time.perf_counter();interactive=canonical(result).encode();serialization=time.perf_counter()-started
            payload_size=len(interactive);del interactive
            started=time.perf_counter();compressed_size=0;full_bytes=0;semantic=[];archive_seconds=0
            if arm=='legacy':
                semantic=[digest(semantic_replay(r)) for r in result]
                for r in result:
                    raw=canonical(r).encode();full_bytes+=len(raw);compressed_size+=len(lzma.compress(raw,preset=1));del raw
                retrieval=None;census=None
            else:
                semantic=[store.legacy_digest(r['proof_root'],omit_keys=('execution','incremental')) for r in result]
                archived=time.perf_counter()
                for r in result:
                    archive=store.archive(r['proof_root']);raw=canonical(archive).encode();compressed_size+=len(lzma.compress(raw,preset=1))
                    full_bytes+=sum(len(block) for block in store.canonical_chunks(r['proof_root']));del archive,raw
                archive_seconds=time.perf_counter()-archived
                retrieve_start=time.perf_counter()
                for r in result:retrieve(store,r['proof_handle'],view='proof_graph',limit=64)
                retrieval=time.perf_counter()-retrieve_start;census=store.census()
            audit_time=time.perf_counter()-started
            executions=[r['execution'] for r in result]
            assert not any(e['truncated'] or e.get('error') for e in executions)
            rows.append(dict(workload=name,arm=arm,repetition=repetition,temperature=temperature,
                inference_seconds=inference,serialization_seconds=serialization,interactive_total_seconds=inference+serialization,
                canonical_interactive_bytes=payload_size,canonical_full_bytes=full_bytes,compressed_audit_bytes=compressed_size,
                full_audit_validation_and_compression_seconds=audit_time,compact_archive_export_seconds=archive_seconds,
                graph_page_retrieval_seconds=retrieval,semantic_hashes=semantic,
                native_invocations=runtime.invocations-before_calls,interpreter_process_launches=launches,
                native_execution_including_launch_seconds=runtime.elapsed-before_native,
                process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                largest_child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                runtime_load_seconds=runtime_load,model_load_seconds=model_load,store_census=census,
                request_cache_hits=sum(r.get('delivery',{}).get('request_cache_hit',False) for r in result)))
            del result
    assert rows[0]['semantic_hashes']==rows[1]['semantic_hashes']
    atomic_json(out/'performance/receipts'/f'{name}-{arm}-{repetition}.json',dict(passed=True,rows=rows,
        production_code_hash=production_code_hash(),runtime=runtime.manifest,models={k:v.version for k,v in loaded.items()},
        memory_scope='Fresh process per workload, arm and repetition; warm retains cold caches and prior peak. Child maximum is separate and never added to parent peak.',
        pure_native_cache_and_graph_reuse='Both retain native arithmetic memoization. Compact additionally reuses a source/state/history/model/options-bound durable response.'))


def distribution(values):
    values=[v for v in values if v is not None];rand=random.Random(141414)
    medians=[statistics.median(rand.choices(values,k=len(values))) for _ in range(1000)] if values else []
    return dict(N=len(values),median=statistics.median(values) if values else None,
        minimum=min(values) if values else None,maximum=max(values) if values else None,
        p90=percentile(values,.9),p95=percentile(values,.95),sample_p99=percentile(values,.99),
        median_bootstrap_95=[percentile(medians,.025),percentile(medians,.975)])


def run(out,repetitions=20):
    out=Path(out).resolve();assert repetitions>=20
    code=production_code_hash();assert code==read_json(out/'source-freeze.json')['production_code_hash']
    # Caller must have stopped completed owned research jobs. Record the exact
    # process census; do not infer contention-free execution from timings.
    processes=subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True)
    active=[line for line in processes.splitlines() if any(token in line for token in (
        '-m training.cycle14_features','-m training.cycle14_labels','-m scripts.cycle14_baseline run',
        '-m scripts.cycle13_clean_research compare','-m evaluation.cycle14_responses','-m scripts.cycle14_regression',
        '-m scripts.cycle14_reproduce')) and not line.strip().startswith(str(os.getpid())+' ')]
    assert not active, 'Stop owned study jobs before headline benchmarking: '+str(active)
    atomic_json(out/'performance/workloads.json',dict(workloads=workloads(ROOT/'artifacts/cycle13'),repetitions=repetitions,
        matched_to_profile_before=True,production_code_hash=code,owned_study_processes=active,
        process_census=processes,scope='No concurrent study jobs under this cycle; unrelated host activity is not controlled.'))
    all_rows=[]
    for name in workloads(ROOT/'artifacts/cycle13'):
        for repetition in range(repetitions):
            order=('legacy','compact') if repetition%2==0 else ('compact','legacy')
            for arm in order:
                target=out/'performance/receipts'/f'{name}-{arm}-{repetition}.json'
                assert not target.exists(),'Preserve prior benchmark timings; use a new generation'
                log=out/'performance/logs'/f'{name}-{arm}-{repetition}.txt';log.parent.mkdir(parents=True,exist_ok=True)
                with log.open('w') as stream:subprocess.run([sys.executable,'-m','evaluation.cycle14_performance','--out',str(out),
                    '--worker',name,'--arm',arm,'--repetition',str(repetition)],cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT,check=True)
                receipt=read_json(target);assert receipt['production_code_hash']==code
                all_rows.extend(receipt['rows']);print('C14 BENCHMARK',name,arm,repetition,flush=True)
    summaries=[];parity={};comparisons=[]
    metrics=('interactive_total_seconds','inference_seconds','serialization_seconds','canonical_interactive_bytes',
        'canonical_full_bytes','compressed_audit_bytes','full_audit_validation_and_compression_seconds',
        'graph_page_retrieval_seconds','native_invocations','interpreter_process_launches','process_peak_rss_kib','largest_child_peak_rss_kib')
    for name in workloads(ROOT/'artifacts/cycle13'):
        rows=[r for r in all_rows if r['workload']==name];identities={tuple(r['semantic_hashes']) for r in rows}
        assert len(identities)==1
        parity[name]=dict(exact=True,requests=len(rows),semantic_hashes=next(iter(identities)))
        for arm in ('legacy','compact'):
            for temp in ('cold','warm'):
                selected=[r for r in rows if r['arm']==arm and r['temperature']==temp]
                summaries.append(dict(workload=name,arm=arm,temperature=temp,metrics={key:distribution([r[key] for r in selected]) for key in metrics}))
        for temp in ('cold','warm'):
            old={r['repetition']:r for r in rows if r['arm']=='legacy' and r['temperature']==temp}
            new={r['repetition']:r for r in rows if r['arm']=='compact' and r['temperature']==temp}
            ratios=[old[i]['interactive_total_seconds']/new[i]['interactive_total_seconds'] for i in old]
            reductions=[1-new[i]['canonical_interactive_bytes']/old[i]['canonical_interactive_bytes'] for i in old]
            comparisons.append(dict(workload=name,temperature=temp,paired_speed_ratio=distribution(ratios),paired_payload_reduction=distribution(reductions)))
    atomic_json(out/'performance/summary.json',dict(passed=True,production_code_hash=code,rows=all_rows,summaries=summaries,
        parity=parity,comparisons=comparisons,repetitions=repetitions,isolated_worker_processes=4*2*repetitions,
        interactive_latencies_include_serialization=True,native_inference_speedup_claim=False,
        scope='Equivalent frozen inputs and complete native/evidence parity. Compact warm reuse avoids repeated native requests; summary payload gains are interface gains. Complete audit cost is separately measured. Sample p99 from twenty observations is not a service guarantee.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/cycle14');p.add_argument('--worker');p.add_argument('--arm',choices=('legacy','compact'));p.add_argument('--repetition',type=int);p.add_argument('--repetitions',type=int,default=20);a=p.parse_args()
    worker(a.out,a.worker,a.arm,a.repetition) if a.worker else run(a.out,a.repetitions)
