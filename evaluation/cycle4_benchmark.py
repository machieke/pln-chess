"""Fresh-process, complete-proof reference/cold/warm benchmark for schemas 3/4."""
import argparse,resource
from pathlib import Path
from pln_chess.common import read_json,write_json,digest
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cycle3.native import NativeSession

def benchmark(checkpoint,positions,output):
    runtime=Runtime(timeout=180);model=Model.load(checkpoint,runtime)
    if model.schema==4:
        from pln_chess.cycle4.inference import infer_moves
    else:
        from pln_chess.cycle3.inference import infer_moves
    records=[]
    for p in positions:
        session=NativeSession(runtime);runs={};hashes=[]
        for mode in ('reference','cold','warm'):
            r=infer_moves(p['fen'],model,runtime=runtime,session=None if mode=='reference' else session,optimized=mode!='reference')
            if r['truncated']:raise RuntimeError('Incomplete benchmark '+p['id'])
            hashes.append(digest(r['candidates']))
            runs[mode]={k:r[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','cache_entries','proof_bytes_estimate')}
            runs[mode]['peak_process_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            count=len(r['candidates'])
            del r
        assert len(set(hashes))==1
        records.append({'fixture':p['id'],'fen':p['fen'],'candidates':count,'runs':runs,'full_proof_parity':True,'semantic_digest':hashes[0]})
    result={'model_version':model.version,'corpus':records,'checkpoint_bytes':Path(checkpoint).stat().st_size,
            'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'rss_scope':'Fresh inference-only process; model and one complete candidate result at a time. Peak includes interpreter and native bridge orchestration.',
            'budget_scope':'Estimated proof metadata limit; not an OS RSS cap.'}
    write_json(output,result);return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--checkpoint',required=True);parser.add_argument('--positions',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();benchmark(args.checkpoint,read_json(args.positions),args.output)
