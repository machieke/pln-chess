"""Content-identified, resumable native external evaluation; labels stay offline."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time

from pln_chess.common import ROOT, read_json, write_json, digest
from scripts.cycle9_baseline import sha


def worker(out,source,arm,split,collection,offset,checkpoint,mode):
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from pln_chess.cycle6.inference import production_code_hash
    from evaluation.cycle8 import evaluate
    data=read_json(out/'datasets/dataset.json');runtime=Runtime(timeout=180)
    model=PromotionModel.load(checkpoint,runtime)
    fixtures=[f for f in data['positions'] if f['split']==split and f['source_collection']==collection]
    if mode!='operational':fixtures=fixtures[:10]
    fixtures=fixtures[offset:offset+20];assert fixtures
    name=f'{arm}-{mode}-{split}-{collection}-{offset:04}'
    target=out/f'evaluation/{name}.json.xz';receipt=out/f'evaluation/{name}.receipt.json'
    identity=dict(dataset_hash=data['hash'],model_version=model.version,checkpoint_sha256=sha(checkpoint),
        production_code_hash=production_code_hash(),evaluator_sha256=sha(source/'evaluation/cycle8.py'),
        driver_sha256=sha(__file__),fixtures=[p['id'] for p in fixtures],mode=mode,arm=arm,
        historical_policy='fen-only; no historical events invented from FEN')
    if receipt.exists():
        old=read_json(receipt)
        if old['identity']==identity and target.exists() and sha(target)==old['sha256']:
            print('VERIFIED RESUME',name,flush=True);return
    report=evaluate({**data,'positions':fixtures},model,split,runtime,
                    Cycle8Options(mode=mode,max_native_invocations=100000,timeout_seconds=180),target)
    assert all(digest([report['native_proof_dag'][i] for i in row['proof_refs']])==row['proof_id'] for row in report['rows'])
    # New-cohort errors and budgets are measurements, never filtered or asserted away.
    write_json(receipt,dict(identity=identity,sha256=sha(target),artifact=str(target.relative_to(out)),
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        source_status=subprocess.check_output(['git','status','--short','--','src'],cwd=source,text=True),
        metrics=report['metrics'],positions=len(report['positions']),rows=len(report['rows']),
        proof_hash=digest([r['proof_id'] for r in report['rows']]),native_proofs_verified=True))
    print(name,'recall',report['metrics']['recall'],'false-legal',report['metrics']['false_positive'],flush=True)


def run(out,source,arm,checkpoint,only=None,modes=('operational',)):
    data=read_json(out/'datasets/dataset.json');jobs=[]
    if arm=='frozen':
        assert sha(checkpoint)==sha(source/'artifacts/cycle8/model/C8-promotion-relative.json')
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==read_json(ROOT/'configs/cycle10.json')['starting_head']
    else:
        assert read_json(out/'frozen-complete.json')['passed'],'External adaptation requires completed frozen evaluation'
    for mode in modes:
        for split in data['counts']:
            if only and split!=only:continue
            if mode!='operational' and split!='external-test':continue
            collections=sorted({f['source_collection'] for f in data['positions'] if f['split']==split})
            for collection in collections:
                n=sum(f['split']==split and f['source_collection']==collection for f in data['positions'])
                if mode!='operational':n=min(10,n)
                jobs.extend((split,collection,offset,mode) for offset in range(0,n,20))
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm')
    def command(job):
        split,collection,offset,mode=job;name=f'{arm}-{mode}-{split}-{collection}-{offset:04}'
        log=out/f'logs/{name}.txt';log.parent.mkdir(parents=True,exist_ok=True);start=time.time()
        argv=[sys.executable,str(Path(__file__).resolve()),'--worker','--out',str(out),'--source',str(source),'--arm',arm,
              '--checkpoint',str(checkpoint),'--split',split,'--collection',collection,'--offset',str(offset),'--mode',mode]
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/{name}.json',dict(argv=argv,cwd=str(source),started_unix=start,elapsed_seconds=time.time()-start,
            returncode=result.returncode,log=str(log.relative_to(out)),environment={k:env[k] for k in ('PLN_CHESS_ROOT','PYTHONPATH','TMPDIR')}))
        if result.returncode:raise RuntimeError(f'Evaluation failed: {log}')
        print('completed',name,flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(command,jobs):pass
    if arm=='frozen' and not only:
        receipts=[read_json(p) for p in (out/'evaluation').glob('frozen-operational-*.receipt.json')]
        assert sum(r['positions'] for r in receipts)==len(data['positions'])
        write_json(out/'frozen-complete.json',dict(passed=True,positions=len(data['positions']),dataset_hash=data['hash'],
            model_sha256=sha(checkpoint),calibration_sha256=sha(source/'artifacts/cycle9/calibration/results.json'),
            new_training_before_evaluation=False,source_head=read_json(ROOT/'configs/cycle10.json')['starting_head'],
            completed_unix=time.time(),receipts={r['artifact']:r['sha256'] for r in receipts}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--source',type=Path,default=ROOT)
    p.add_argument('--arm',default='frozen');p.add_argument('--checkpoint',type=Path);p.add_argument('--worker',action='store_true')
    p.add_argument('--split');p.add_argument('--collection');p.add_argument('--offset',type=int,default=0);p.add_argument('--mode',default='operational')
    p.add_argument('--all-modes',action='store_true');a=p.parse_args();a.out=a.out.resolve();a.source=a.source.resolve()
    a.checkpoint=(a.checkpoint or a.source/'artifacts/cycle8/model/C8-promotion-relative.json').resolve()
    worker(a.out,a.source,a.arm,a.split,a.collection,a.offset,a.checkpoint,a.mode) if a.worker else run(a.out,a.source,a.arm,a.checkpoint,a.split,('operational','strict','experimental') if a.all_modes else ('operational',))
