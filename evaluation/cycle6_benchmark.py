"""Fresh-process complete-candidate parity with mode and budget scoped caching."""
import json,time
from pathlib import Path
from pln_chess.common import read_json,write_json,digest
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import infer_moves,Session,Cycle6Options
from evaluation.cycle4_benchmark import address_space_peak_kib

def benchmark(checkpoint,positions,output,mode='operational'):
    rt=Runtime(timeout=180);model=Model.load(checkpoint,rt);records=[]
    startup=time.perf_counter();rt.execute('!(println! (READY))');startup=time.perf_counter()-startup
    for p in positions:
        session=Session(rt);runs={};hashes=[]
        for cache in ('reference','cold','warm'):
            r=infer_moves(p['fen'],model,Cycle6Options(mode=mode),rt,session=None if cache=='reference' else session,optimized=cache!='reference')
            assert not r['truncated'];hashes.append(digest(r['candidates']))
            occurrences=sum(len(c['proof_trace']) for c in r['candidates']);dag=r['proof_dag']
            runs[cache]={k:r[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','cache_entries','proof_bytes_estimate','grounded_atoms')}
            runs[cache].update(peak_process_rss_kib=address_space_peak_kib(),serialized_candidate_bytes=len(json.dumps(r['candidates'],separators=(',',':')).encode()),
                logical_proof_occurrences=occurrences,exported_dag_nodes=len(dag),duplicate_proof_occurrences=occurrences-len(dag),
                lossless_dag_export_bytes=len(json.dumps({'nodes':dag,'refs':{c['candidate_id']:c.get('proof_dag_refs',[]) for c in r['candidates']}},separators=(',',':')).encode()),
                opponent_frame_occurrences=sum(len(c.get('relative_neighborhood',{}).get('opponent_frames',[])) for c in r['candidates']))
            count=len(r['candidates']);del r
        assert len(set(hashes))==1
        records.append({'fixture':p['id'],'fen':p['fen'],'candidates':count,'runs':runs,'full_proof_parity':True,'semantic_digest':hashes[0]})
    result={'mode':mode,'model_version':model.version,'runtime':rt.manifest,'corpus':records,'interpreter_startup_seconds':startup,
        'checkpoint_bytes':Path(checkpoint).stat().st_size,'peak_process_rss_kib':address_space_peak_kib(),
        'memory_scope':'Fresh-process VmHWM; complete API proofs retained. Interned export size is measured separately, not claimed as reduced live memory.'}
    if output:write_json(output,result)
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--positions',required=True);p.add_argument('--output',required=True);p.add_argument('--mode',choices=('operational','strict','experimental'),default='operational');a=p.parse_args()
    benchmark(a.checkpoint,read_json(a.positions),a.output,a.mode)
