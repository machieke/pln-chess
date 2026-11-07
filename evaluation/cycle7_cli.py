"""CLI benchmark, with the same mode and proof parity contracts as inference."""
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.pln import Runtime
from pln_chess.cycle7.inference import infer_moves, Cycle7Options, Session, default_mode

def benchmark(model,positions=None,output=None,mode=None):
    rt=Runtime(timeout=180);options=Cycle7Options(mode=mode or default_mode(model));rows=[]
    for p in read_json(positions or ROOT/'artifacts/cycle5/benchmarks/positions.json'):
        session=Session(rt);arms={};hashes=[]
        for arm in ('reference','cold','warm'):
            r=infer_moves(p['fen'],model,options,rt,session=None if arm=='reference' else session,optimized=arm!='reference')
            hashes.append(digest(r['candidates']))
            arms[arm]={k:r[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','proof_bytes_estimate','truncated')}
        rows.append({'fixture':p['id'],'runs':arms,'full_candidate_parity':len(set(hashes))==1})
    result={'mode':options.mode,'model_version':model.version,'runtime':rt.manifest,'fixtures':rows}
    if output:write_json(output,result)
    return result
