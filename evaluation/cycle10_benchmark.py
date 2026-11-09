"""Serial external workloads, identical native payloads and bounded timing claims."""
import argparse
import cProfile
import io
from pathlib import Path
import pstats
import resource
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options,Session
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.domain import Position
from evaluation.cycle7_io import pack
from evaluation.experiments import quantile
from scripts.cycle9_baseline import sha


def fixtures(data):
    final=[p for p in data['positions'] if p['split']=='external-test']
    records=[{**read_json(ROOT/'artifacts/cycle5/benchmarks/positions.json')[0],'id':'full-214'}]
    for source in sorted({p['source_collection'] for p in final}):
        records.append({**max([p for p in final if p['source_collection']==source],key=lambda p:p['candidate_count']),'id':'dense-'+source})
    records.append({**min(final,key=lambda p:(p['material_count'],p['id'])),'id':'external-endgame'})
    records.append({**max(final,key=lambda p:(p['tactical_density'],p['id'])),'id':'external-tactical'})
    return records


def run(out,data_path,arm,repetitions=9):
    out=Path(out);data=read_json(data_path);runtime=Runtime(timeout=180);checkpoint=ROOT/'artifacts/cycle8/model/C8-promotion-relative.json'
    start=time.perf_counter();model=PromotionModel.load(checkpoint,runtime);loading=time.perf_counter()-start
    options=Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180);records=[]
    for fixture in fixtures(data):
        position=Position.from_fen(fixture['fen']);samples=[]
        for rep in range(repetitions):
            session=Session(runtime);payloads=[]
            for mode in ('reference','cold','warm'):
                start=time.perf_counter();result=infer_moves(position,model,options,runtime,session=None if mode=='reference' else session,optimized=mode!='reference')
                elapsed=time.perf_counter()-start;identifier=digest(result['candidates']);payloads.append(identifier)
                assert not result['truncated'] and result['error'] is None
                if mode=='warm':assert result['native_invocations']==0
                samples.append(dict(repetition=rep,mode=mode,wall_seconds=elapsed,candidate_digest=identifier,
                    candidate_count=len(result['candidates']),python_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                    **{k:result[k] for k in ('native_invocations','scheduled_invocations','grounded_atoms','cache_hits','cache_entries','proof_bytes_estimate','truncated','error')}))
                if rep==0 and mode=='reference':pack(out/f'performance/proofs/{arm}-{fixture["id"]}.json.xz',result)
            assert len(set(payloads))==1
        aggregates={}
        for mode in ('reference','cold','warm'):
            selected=[s for s in samples if s['mode']==mode];hits=sum(s['cache_hits'] for s in selected);miss=sum(s['native_invocations'] for s in selected)
            aggregates[mode]=dict(n=len(selected),latency_seconds={f'p{int(q*100)}':quantile([s['wall_seconds'] for s in selected],q) for q in (.5,.95,.99)},
                native_calls=[s['native_invocations'] for s in selected],grounded_atoms=[s['grounded_atoms'] for s in selected],
                cache_hit_rate=hits/(hits+miss) if hits+miss else None,timeout_rate=0,truncation_rate=0,
                python_peak_rss_kib=max(s['python_peak_rss_kib'] for s in selected),child_peak_rss_kib=max(s['child_peak_rss_kib'] for s in selected))
        records.append(dict(fixture=fixture,samples=samples,aggregates=aggregates,full_candidate_proof_parity=True))
        write_json(out/f'performance/{arm}.json',dict(arm=arm,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            source_status=subprocess.check_output(['git','status','--short','--','src'],cwd=ROOT,text=True),production_code_hash=production_code_hash(),
            driver_sha256=sha(__file__),dataset_hash=data['hash'],model_version=model.version,runtime=runtime.manifest,
            checkpoint_bytes=checkpoint.stat().st_size,checkpoint_load_seconds=loading,records=records,
            memory_scope='Cumulative parent and separate maximum terminated-child RSS, not simultaneous combined peak.',
            quantiles='Nine descriptive repetitions per mode; p95 and p99 are sample maxima, not validated population-tail estimates.'))
        print(arm,fixture['id'],{k:v['latency_seconds'] for k,v in aggregates.items()},flush=True)
    profiler=cProfile.Profile();profiler.enable();infer_moves(position,model,options,runtime,session=session);profiler.disable()
    stream=io.StringIO();pstats.Stats(profiler,stream=stream).sort_stats('cumulative').print_stats(60)
    (out/f'performance/{arm}-profile.txt').write_text(stream.getvalue())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--data',required=True);p.add_argument('--arm',required=True);p.add_argument('--repetitions',type=int,default=9)
    a=p.parse_args();run(a.out,a.data,a.arm,a.repetitions)
