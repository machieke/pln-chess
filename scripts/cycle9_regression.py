"""All established C8 acceptance suites under the consolidated implementation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from scripts.cycle9_baseline import sha,ARMS
from scripts.cycle8_evaluate import jobs


def worker(out,arm,name):
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from pln_chess.cycle6.inference import production_code_hash
    from evaluation.cycle8 import evaluate
    from evaluation.cycle3 import read_gzip
    rt=Runtime(timeout=180);model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    mode={'C8-strict':'strict','C8-experimental':'experimental'}.get(arm,'operational')
    _,path,split=next(j for j in jobs(ROOT/'artifacts/cycle8',arm) if j[0]==name)
    target=out/f'regression/{arm}-{name}.json.xz';receipt=out/f'regression/{arm}-{name}.receipt.json'
    identity=dict(source_hash=production_code_hash(),driver_sha256=sha(__file__),dataset_sha256=sha(path),model_version=model.version)
    if receipt.exists():
        previous=read_json(receipt)
        if previous['identity']==identity and target.exists() and sha(target)==previous['sha256']:
            print('VERIFIED RESUME',arm,name,flush=True);return
    report=evaluate(read_json(path),model,split,rt,Cycle8Options(mode=mode,max_native_invocations=100000,timeout_seconds=180),target)
    old=read_gzip(ROOT/f'artifacts/cycle8/evaluation/{arm}-{name}.json.xz')
    fields=('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids','dependence_groups',
            'proof_status','backoff','model_version','runtime_version','local_truth_value','typed_premises','promotion_selection')
    assert [{k:r[k] for k in fields} for r in report['rows']]==[{k:r[k] for k in fields} for r in old['rows']],(arm,name)
    assert [p['predicted'] for p in report['positions']]==[p['predicted'] for p in old['positions']]
    assert not report['metrics']['incomplete']
    if mode=='operational':
        assert all(not report['metrics'][k] for k in ('false_positive','false_illegal','self_check_false_legal'))
    assert all(digest([report['native_proof_dag'][i] for i in r['proof_refs']])==r['proof_id'] for r in report['rows'])
    write_json(receipt,dict(identity=identity,sha256=sha(target),artifact=str(target.relative_to(out)),
        metrics=report['metrics'],positions=len(report['positions']),rows=len(report['rows']),exact_native_proof_parity=True))


def run(out):
    tasks=[(arm,name) for arm in ARMS for name,_,_ in jobs(ROOT/'artifacts/cycle8',arm)]
    def command(task):
        arm,name=task;argv=[sys.executable,'-m','scripts.cycle9_regression','--out',str(out),'--arm',arm,'--suite',name]
        log=out/f'logs/regression-{arm}-{name}.txt';log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/regression-{arm}-{name}.json',dict(argv=argv,returncode=result.returncode,
            elapsed_seconds=time.time()-started,started_unix=started,cwd=str(ROOT),log=str(log.relative_to(out))))
        if result.returncode:raise RuntimeError(f'Regression failed: {log}')
        print('EXACT PARITY',arm,name,flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(command,tasks):pass
    write_json(out/'regression/verified.json',dict(passed=True,evaluations=len(tasks),all_native_proof_parity=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--arm');p.add_argument('--suite')
    a=p.parse_args();a.out=a.out.resolve();worker(a.out,a.arm,a.suite) if a.arm else run(a.out)
