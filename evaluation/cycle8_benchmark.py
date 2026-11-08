"""Serial latency samples with full native-proof cache parity."""
from pathlib import Path
import argparse
import json
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle4_benchmark import address_space_peak_kib
from evaluation.experiments import quantile
from evaluation.cycle7_io import pack


def run(out,variant,repetitions=None,checkpoint=None,fixtures=None):
    out=Path(out);config=read_json(ROOT/'configs/cycle8.json');rt=Runtime(timeout=180)
    path=Path(checkpoint) if checkpoint else ROOT/'artifacts/cycle7/model/C7-frozen.json' if variant=='C7-frozen' else out/f'model/{variant}.json'
    model=Model.load(path,rt)
    if model.schema==8:
        from pln_chess.cycle8.inference import infer_moves,Session,Cycle8Options as Options
    else:
        from pln_chess.cycle7.inference import infer_moves,Session,Cycle7Options as Options
    options=Options(mode='operational',max_native_invocations=100000,timeout_seconds=180)
    repetitions=repetitions or config['benchmark_repetitions']
    if fixtures is None:
        old=read_json(ROOT/'artifacts/cycle5/benchmarks/positions.json')[0]
        data=read_json(out/'datasets/dataset.json')
        promotion=max([p for p in data['positions'] if p['split']=='combination-holdout'],key=lambda p:p['promotion_candidates'])
        independent=max([p for p in data['positions'] if p['split']=='independent-games'],key=lambda p:p['candidate_count'])
        fixtures=[{'id':'single-promotion','fen':'r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29','move':'f7e8n','scope':'single-candidate'},
            {**old,'scope':'full-214'}, {**promotion,'scope':'promotion-heavy'}, {**independent,'scope':'independent-game'}]
    records=[]
    for index,fixture in enumerate(fixtures):
        fixture={**fixture,'scope':fixture.get('scope',f'custom-{index}')}
        pos=Position.from_fen(fixture['fen']);moves=[find_move(pos,fixture['move'])] if fixture.get('move') else None
        samples=[]
        for repetition in range(repetitions):
            session=Session(rt);hashes=[]
            for arm in ('reference','cold','warm'):
                start=time.perf_counter()
                result=infer_moves(pos,model,options,rt,moves,None if arm=='reference' else session,optimized=arm!='reference')
                wall=time.perf_counter()-start;fingerprint=digest(result['candidates']);hashes.append(fingerprint)
                sample={'repetition':repetition,'arm':arm,'wall_seconds':wall,'candidate_digest':fingerprint,
                    'candidate_count':len(result['candidates']),'peak_rss_kib':address_space_peak_kib(),
                    **{k:result[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','cache_entries','grounded_atoms','proof_bytes_estimate','truncated','error')},
                    'native_cache_misses':result['native_invocations'],'proof_nodes':len(result['proof_dag']),
                    'proof_graph_bytes':len(json.dumps(result['proof_dag'],separators=(',',':')).encode())}
                samples.append(sample)
                if repetition==0 and arm=='reference':
                    pack(out/f'benchmarks/proofs/{variant}-{fixture["scope"]}.json.xz',result)
                assert not result['truncated'],(variant,fixture['id'],arm,result['error'])
                if arm=='warm':assert result['native_invocations']==0,(variant,fixture['id'],result['native_invocations'])
            assert len(set(hashes))==1,(variant,fixture['id'],hashes)
        aggregates={}
        for arm in ('reference','cold','warm'):
            selected=[r for r in samples if r['arm']==arm]
            aggregates[arm]={'n':len(selected),'latency_seconds':{f'p{int(q*100)}':quantile([r['elapsed_seconds'] for r in selected],q) for q in (.5,.95,.99)},
                'native_invocations':[r['native_invocations'] for r in selected],
                'grounded_atoms':[r['grounded_atoms'] for r in selected],
                'cache_hits':[r['cache_hits'] for r in selected],'cache_misses':[r['native_cache_misses'] for r in selected],
                'peak_rss_kib':max(r['peak_rss_kib'] for r in selected),
                'truncation_rate':sum(r['truncated'] for r in selected)/len(selected),
                'timeout_rate':sum(bool(r['error']) and ('timeout' in r['error'].lower() or 'wall' in r['error'].lower()) for r in selected)/len(selected)}
        records.append({'fixture':fixture,'samples':samples,'aggregates':aggregates,'full_candidate_and_native_proof_parity':True})
        print(variant,fixture['scope'],{k:v['latency_seconds'] for k,v in aggregates.items()},flush=True)
        write_json(out/f'benchmarks/{variant}.json',{'model_version':model.version,'checkpoint_bytes':path.stat().st_size,
            'production_code_hash':production_code_hash(),'runtime':rt.manifest,'records':records,
            'quantiles':'Nearest-rank empirical quantiles; five samples per arm. p95/p99 are maxima, not reliable population tail estimates.',
            'memory':'Process high-water RSS, cumulative across fixtures and repetitions; not per-call allocation.',
            'scope':'Serial measurements after evaluation jobs end; reference/cold/warm equality is within each semantic model.'})
    return records


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--variant',required=True);parser.add_argument('--repetitions',type=int)
    args=parser.parse_args();run(args.out,args.variant,args.repetitions)
