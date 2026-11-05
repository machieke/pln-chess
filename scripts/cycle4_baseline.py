"""Reproduce the immutable Cycle 3 baseline without writing its artifacts."""
import hashlib,json,lzma,os,platform,subprocess,time
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.domain import Position
from pln_chess.cycle3.inference import infer_moves
from pln_chess.cycle3.native import NativeSession
from evaluation.cycle3 import evaluate,read_gzip

START='38cd26b97c3cf2ffe33eac526006c9820f8c3f82'

def pack(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    path.write_bytes(lzma.compress(raw))
    assert lzma.decompress(path.read_bytes())==raw

def main():
    out=Path(os.environ.get('C4_OUT',ROOT/'artifacts/cycle4'));out.mkdir(parents=True,exist_ok=True)
    subprocess.run(['git','cat-file','-e',START+'^{commit}'],check=True)
    runtime=Runtime(timeout=180)
    tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',START],text=True).splitlines()
    preserved={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in tracked
               if p.startswith(('artifacts/','fixtures/','vendor/','configs/')) or p.endswith('.lock')}
    receipt={'starting_head':START,'actual_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             'status':subprocess.check_output(['git','status','--short'],text=True),'runtime':runtime.manifest,
             'platform':platform.uname()._asdict(),'python':platform.python_version(),'preserved':preserved,
             'command':'TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle4_baseline','results':{}}
    write_json(out/'baseline-start.json',receipt)
    model=Model.load(ROOT/'artifacts/cycle3/C3-full-model.json',runtime)
    for prefix,data_path,splits in [('frozen','cycle2',('heldout-transfer','adversarial')),
                                   ('new','cycle3',('challenge','independent-games','validation'))]:
        dataset=read_json(ROOT/f'artifacts/{data_path}/dataset.json')
        for split in splits:
            report=evaluate(dataset,model,split,runtime)
            old=read_gzip(ROOT/f'artifacts/cycle3/C3-full-{prefix}-{split}.json.xz')
            fields=('precision','recall','f1','abstention_rate','exact_move_set_accuracy','self_check_false_legal')
            old_rows={(r['fixture'],r['move']):(r['classification'],r['truth_value'],r['proof_id']) for r in old['rows']}
            parity=all(old_rows[(r['fixture'],r['move'])]==(r['classification'],r['truth_value'],r['proof_id']) for r in report['rows'])
            assert parity and all(report['metrics'][k]==old['metrics'][k] for k in fields)
            receipt['results'][prefix+'-'+split]={'metrics':report['metrics'],'proof_tv_class_parity':parity,'dataset_hash':dataset['hash']}
            pack(out/f'baseline/{prefix}-{split}.json.xz',report)
            print('BASELINE',prefix,split,parity,{k:report['metrics'][k] for k in fields},flush=True)
    fen='r1bqkbr1/pp1pp2p/2n5/2p2p2/4P2p/2N5/PPPP1R1N/R1BQKB2 w Qq - 3 10'
    session=NativeSession(runtime);benchmark={};parity=[]
    for mode in ('reference','cold','warm'):
        result=infer_moves(fen,model,runtime=runtime,session=None if mode=='reference' else session,optimized=mode!='reference')
        benchmark[mode]={k:result[k] for k in ('elapsed_seconds','native_invocations','scheduled_invocations','cache_hits','proof_bytes_estimate','truncated')}
        parity.append(digest(result['candidates']))
    assert len(set(parity))==1
    receipt['benchmark']={'runs':benchmark,'candidate_count':len(result['candidates']),'full_candidate_parity':True,'digest':parity[0]}
    write_json(out/'baseline.json',receipt)
    print('BASELINE COMPLETE',benchmark,flush=True)

if __name__=='__main__':main()
