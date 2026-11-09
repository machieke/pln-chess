"""Bounded, source-identified C9 evaluation shards with lossless native proofs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json,digest

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def worker(out,source,split,offset,mode):
    # Source isolation is configured by the parent before importing production modules.
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from pln_chess.cycle6.inference import production_code_hash
    from evaluation.cycle8 import evaluate
    from evaluation.cycle7_io import pack
    data=read_json(out/'datasets/dataset.json');rt=Runtime(timeout=180)
    model=PromotionModel.load(source/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    fixtures=[p for p in data['positions'] if p['split']==split]
    # Secondary modes have an explicitly registered 25-position independent comparison,
    # plus all 80 dedicated special-move positions; operational scores every fixture.
    if mode!='operational' and split=='independent-games':fixtures=fixtures[:25]
    fixtures=fixtures[offset:offset+25];assert fixtures
    name=f'{mode}-{split}-{offset:04}';target=out/f'evaluation/{name}.json.xz'
    receipt_path=out/f'evaluation/{name}.receipt.json'
    identity=dict(dataset_hash=data['hash'],model_version=model.version,production_code_hash=production_code_hash(),
        evaluator_sha256=sha(source/'evaluation/cycle8.py'),driver_sha256=sha(__file__),fixtures=[p['id'] for p in fixtures],mode=mode)
    if receipt_path.exists():
        old=read_json(receipt_path)
        if old['identity']==identity and target.exists() and sha(target)==old['sha256']:
            print('VERIFIED RESUME',name,flush=True);return
    report=evaluate({**data,'positions':fixtures},model,split,rt,
                    Cycle8Options(mode=mode,max_native_invocations=100000,timeout_seconds=180),target)
    assert report['metrics']['incomplete']==0
    assert all(digest([report['native_proof_dag'][i] for i in row['proof_refs']])==row['proof_id'] for row in report['rows'])
    write_json(receipt_path,dict(identity=identity,sha256=sha(target),artifact=str(target.relative_to(out)),
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        metrics=report['metrics'],positions=len(report['positions']),rows=len(report['rows']),
        proof_hash=digest([r['proof_id'] for r in report['rows']]),native_proofs_verified=True))
    print(name,report['metrics']['recall'],report['metrics']['false_positive'],report['metrics']['false_illegal'],flush=True)


def run(out,source,only=None):
    data=read_json(out/'datasets/dataset.json');jobs=[]
    for mode in ('operational','strict','experimental'):
        for split in data['counts']:
            if only and split!=only:continue
            if mode!='operational' and split not in ('independent-games','special-moves'):continue
            n=min(25,data['counts'][split]) if mode!='operational' and split=='independent-games' else data['counts'][split]
            jobs.extend((split,offset,mode) for offset in range(0,n,25))
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm')
    def command(job):
        split,offset,mode=job;name=f'{mode}-{split}-{offset:04}';log=out/f'logs/{name}.txt'
        log.parent.mkdir(parents=True,exist_ok=True)
        argv=[sys.executable,str(Path(__file__).resolve()),'--out',str(out),'--source',str(source),
              '--worker','--split',split,'--offset',str(offset),'--mode',mode]
        started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/{name}.json',dict(argv=argv,cwd=str(source),started_unix=started,
            elapsed_seconds=time.time()-started,returncode=result.returncode,log=str(log.relative_to(out)),
            environment={k:env[k] for k in ('PLN_CHESS_ROOT','PYTHONPATH','TMPDIR')}))
        if result.returncode:raise RuntimeError(f'{name} failed: {log}')
        print('completed',name,flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(command,jobs):pass


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--source',type=Path,default=ROOT)
    p.add_argument('--worker',action='store_true');p.add_argument('--split');p.add_argument('--offset',type=int,default=0)
    p.add_argument('--mode',default='operational');a=p.parse_args();a.out=a.out.resolve();a.source=a.source.resolve()
    worker(a.out,a.source,a.split,a.offset,a.mode) if a.worker else run(a.out,a.source,a.split)
