"""Established operational cohorts evaluated against unpromoted adaptations."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from scripts.cycle9_baseline import sha
from scripts.cycle8_evaluate import jobs


def worker(out,arm,suite):
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from pln_chess.cycle6.inference import production_code_hash
    from evaluation.cycle8 import evaluate
    from evaluation.cycle3 import read_gzip
    checkpoint=out/f'adaptation/model/{arm}.json';rt=Runtime(timeout=180);model=PromotionModel.load(checkpoint,rt)
    _,path,split=next(j for j in jobs(ROOT/'artifacts/cycle8','C8-promotion-relative') if j[0]==suite)
    target=out/f'adaptation/regression/{arm}-{suite}.json.xz';receipt=target.with_suffix('.receipt.json')
    identity=dict(model_version=model.version,checkpoint_sha256=sha(checkpoint),dataset_sha256=sha(path),
        production_code_hash=production_code_hash(),driver_sha256=sha(__file__))
    if receipt.exists():
        old=read_json(receipt)
        if old['identity']==identity and target.exists() and sha(target)==old['sha256']:return
    report=evaluate(read_json(path),model,split,rt,Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180),target)
    assert all(digest([report['native_proof_dag'][i] for i in r['proof_refs']])==r['proof_id'] for r in report['rows'])
    original=read_gzip(ROOT/f'artifacts/cycle8/evaluation/C8-promotion-relative-{suite}.json.xz')
    lookup={(r['fixture'],r['move']):r for r in original['rows']};changes=[]
    for row in report['rows']:
        before=lookup[row['fixture'],row['move']]
        if row['classification']!=before['classification'] or row['truth_value']!=before['truth_value']:
            changes.append(dict(fixture=row['fixture'],move=row['move'],label=row['label'],before=before['classification'],
                after=row['classification'],before_tv=before['truth_value'],after_tv=row['truth_value'],
                before_proof_id=before['proof_id'],after_proof_id=row['proof_id']))
    write_json(receipt,dict(identity=identity,sha256=sha(target),artifact=str(target.relative_to(out)),metrics=report['metrics'],
        before_metrics=original['metrics'],positions=len(report['positions']),rows=len(report['rows']),changes=changes,
        native_proofs_verified=True,new_learning_promoted=False))


def run(out):
    assert read_json(out/'frozen-complete.json')['passed']
    tasks=[(arm,name) for arm in ('small','large') for name,_,_ in jobs(ROOT/'artifacts/cycle8','C8-promotion-relative')]
    def command(task):
        arm,suite=task;name=f'adapt-regression-{arm}-{suite}';log=out/f'logs/{name}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        argv=[sys.executable,'-m','scripts.cycle10_adapt_regression','--out',str(out),'--arm',arm,'--suite',suite];started=time.time()
        with log.open('w') as stream:r=subprocess.run(argv,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/{name}.json',dict(argv=argv,started_unix=started,elapsed_seconds=time.time()-started,returncode=r.returncode,log=str(log.relative_to(out))))
        if r.returncode:raise RuntimeError(str(log))
        print(name,'completed',flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(command,tasks):pass
    receipts=[read_json(p) for p in (out/'adaptation/regression').glob('*.receipt.json')]
    assert len(receipts)==len(tasks)
    write_json(out/'adaptation/regression-summary.json',dict(evaluations=len(receipts),new_learning_promoted=False,
        records=[{k:r[k] for k in ('artifact','metrics','before_metrics','positions','rows')} for r in receipts],
        changed_candidates=sum(len(r['changes']) for r in receipts),
        false_legal=sum(r['metrics']['false_positive'] for r in receipts),false_illegal=sum(r['metrics']['false_illegal'] for r in receipts),
        self_check_false_positives=sum(r['metrics']['self_check_false_legal'] for r in receipts),
        incomplete=sum(r['metrics']['incomplete'] for r in receipts)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--arm');p.add_argument('--suite')
    a=p.parse_args();a.out=a.out.resolve();worker(a.out,a.arm,a.suite) if a.arm else run(a.out)
