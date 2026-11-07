"""Full candidate/proof parity for frozen C6 and C7, with cold and warm caches."""
import argparse
import cProfile
import io
import json
import pstats
import time
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import infer_moves, Cycle7Options, Session
from pln_chess.cycle6.inference import infer_moves as old_infer, Cycle6Options, Session as OldSession
from evaluation.cycle4_benchmark import address_space_peak_kib

def run(out,variant,label=None):
    out=Path(out);rt=Runtime(timeout=180)
    path=ROOT/'artifacts/cycle6/model/C6-full.json' if variant=='C6' else out/'model/C7-frozen.json'
    model=Model.load(path,rt) if variant=='C6' else BackoffModel.load(path,rt)
    fn=old_infer if variant=='C6' else infer_moves;options=Cycle6Options(mode='operational') if variant=='C6' else Cycle7Options(mode='operational')
    old=read_json(ROOT/'artifacts/cycle5/benchmarks/positions.json')
    data=read_json(out/'datasets/dataset.json');large=sorted([p for p in data['positions'] if p['split']=='independent-games'],key=lambda p:p['candidate_count'],reverse=True)[:2]
    fixtures=[old[0]]+large;records=[]
    for fixture in fixtures:
        session=OldSession(rt) if variant=='C6' else Session(rt);runs={};hashes=[]
        for arm in ('reference','cold','warm'):
            started=time.perf_counter()
            r=fn(fixture['fen'],model,options,rt,session=None if arm=='reference' else session,optimized=arm!='reference')
            assert not r['truncated'];hashes.append(digest(r['candidates']))
            runs[arm]={k:r[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','cache_entries','grounded_atoms','proof_bytes_estimate')}
            runs[arm].update(wall_seconds=time.perf_counter()-started,peak_rss_kib=address_space_peak_kib(),
                serialized_candidate_bytes=len(json.dumps(r['candidates'],separators=(',',':')).encode()),
                proof_nodes=len(r['proof_dag']),proof_occurrences=sum(len(c['proof_trace']) for c in r['candidates']),
                proof_graph_bytes=len(json.dumps(r['proof_dag'],separators=(',',':')).encode()))
            count=len(r['candidates']);del r
        assert len(set(hashes))==1
        records.append({'fixture':fixture['id'],'fen':fixture['fen'],'candidate_count':count,'runs':runs,'full_candidate_parity':True,'digest':hashes[0]})
    profiler=cProfile.Profile();profiler.enable()
    fn(fixtures[0]['fen'],model,options,rt)
    profiler.disable();stream=io.StringIO();pstats.Stats(profiler,stream=stream).strip_dirs().sort_stats('cumulative').print_stats(40)
    from pln_chess.cycle6.inference import production_code_hash
    write_json(out/f'benchmarks/{label or variant}.json',{'runtime':rt.manifest,'model_version':model.version,'production_code_hash':production_code_hash(),'checkpoint_bytes':path.stat().st_size,'records':records,'profile':stream.getvalue()})
    return records

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--variant',choices=('C6','C7'),required=True);p.add_argument('--label');a=p.parse_args();run(a.out,a.variant,a.label)
