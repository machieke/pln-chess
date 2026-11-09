"""Serial, fixed-fixture before/after measurements with complete proof parity."""
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
from pln_chess.api import find_move
from evaluation.cycle7_io import pack
from evaluation.experiments import quantile


def fixtures(out):
    data=read_json(Path(out)/'datasets/dataset.json')
    return [dict(id='single',fen='r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29',move='f7e8n'),
        dict(id='sparse',fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1'),
        {**read_json(ROOT/'artifacts/cycle5/benchmarks/positions.json')[0],'id':'full-214'},
        {**max([p for p in data['positions'] if p['split']=='special-moves'],key=lambda p:p['promotion_candidates']),'id':'promotion-heavy'},
        {**max([p for p in data['positions'] if p['split']=='adversarial'],key=lambda p:p['candidate_count']),'id':'adversarial'},
        {**max([p for p in data['positions'] if p['split']=='independent-games'],key=lambda p:p['candidate_count']),'id':'independent-game'}]


def run(out,arm,repetitions=7):
    out=Path(out);rt=Runtime(timeout=180);path=ROOT/'artifacts/cycle8/model/C8-promotion-relative.json'
    start=time.perf_counter();model=PromotionModel.load(path,rt);load=time.perf_counter()-start
    options=Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180)
    records=[]
    for fixture in fixtures(out):
        p=Position.from_fen(fixture['fen']);moves=[find_move(p,fixture['move'])] if fixture.get('move') else None;samples=[]
        for rep in range(repetitions):
            session=Session(rt);hashes=[]
            for mode in ('reference','cold','warm'):
                start=time.perf_counter()
                result=infer_moves(p,model,options,rt,moves,None if mode=='reference' else session,optimized=mode!='reference')
                elapsed=time.perf_counter()-start;fingerprint=digest(result['candidates']);hashes.append(fingerprint)
                assert not result['truncated'],result['error']
                if mode=='warm':assert result['native_invocations']==0
                samples.append(dict(repetition=rep,mode=mode,wall_seconds=elapsed,candidate_digest=fingerprint,
                    candidate_count=len(result['candidates']),python_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                    **{k:result[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','cache_entries','grounded_atoms','proof_bytes_estimate','truncated','error')}))
                if rep==0 and mode=='reference':pack(out/f'performance/proofs/{arm}-{fixture["id"]}.json.xz',result)
            assert len(set(hashes))==1
        aggregate={}
        for mode in ('reference','cold','warm'):
            rows=[r for r in samples if r['mode']==mode];hits=sum(r['cache_hits'] for r in rows);miss=sum(r['native_invocations'] for r in rows)
            aggregate[mode]=dict(n=len(rows),latency_seconds={f'p{int(q*100)}':quantile([r['wall_seconds'] for r in rows],q) for q in (.5,.95,.99)},
                native_calls=[r['native_invocations'] for r in rows],grounded_atoms=[r['grounded_atoms'] for r in rows],
                cache_hit_rate=hits/(hits+miss) if hits+miss else None,truncation_rate=0,
                python_peak_rss_kib=max(r['python_peak_rss_kib'] for r in rows),child_peak_rss_kib=max(r['child_peak_rss_kib'] for r in rows))
        records.append(dict(fixture=fixture,samples=samples,aggregates=aggregate,full_candidate_proof_parity=True))
        write_json(out/f'performance/{arm}.json',dict(arm=arm,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            production_code_hash=production_code_hash(),model_version=model.version,runtime=rt.manifest,checkpoint_bytes=path.stat().st_size,
            checkpoint_load_seconds=load,records=records,
            memory_scope='Separate cumulative Python-parent and maximum terminated-child RSS high-water marks, not simultaneous total peak.',
            quantiles=f'Nearest-rank empirical quantiles from {repetitions} samples per arm. p95/p99 are sample maxima; no reliable tail guarantee.'))
        print(arm,fixture['id'],{k:v['latency_seconds'] for k,v in aggregate.items()},flush=True)
    profiler=cProfile.Profile();profiler.enable()
    infer_moves(p,model,options,rt,moves,session)
    profiler.disable();stream=io.StringIO();pstats.Stats(profiler,stream=stream).sort_stats('cumulative').print_stats(60)
    (out/f'performance/{arm}-profile.txt').write_text(stream.getvalue())
    profiler.dump_stats(str(out/f'performance/{arm}.prof'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--arm',required=True);p.add_argument('--repetitions',type=int,default=7)
    a=p.parse_args();run(a.out,a.arm,a.repetitions)
