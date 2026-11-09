"""Complete the immutable baseline, serial reference timing and frozen test."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def run(out,snapshot,wait=False):
    out=Path(out).resolve();snapshot=Path(snapshot).resolve();deadline=time.time()+7200
    baseline=out/'baseline/reproduction-receipt.json'
    while not baseline.exists():
        if not wait or time.time()>deadline:raise RuntimeError('Completed baseline reproduction is required')
        time.sleep(5)
    assert read_json(baseline)['passed']
    def command(name,args,cwd=ROOT,env=None):
        start=time.time();log=out/f'logs/{name}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        argv=[sys.executable,*args]
        with log.open('w') as stream:r=subprocess.run(argv,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/{name}.json',dict(argv=argv,cwd=str(cwd),started_unix=start,elapsed_seconds=time.time()-start,
            returncode=r.returncode,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip(),
            source_status=subprocess.check_output(['git','status','--short','--','src'],cwd=cwd,text=True),log=str(log.relative_to(out))))
        if r.returncode:raise RuntimeError(f'{name}: {log}')
        print(name,'passed',flush=True)
    command('baseline-metrics',['-m','evaluation.cycle10_baseline_metrics','--out',str(out)])
    env=dict(os.environ,PLN_CHESS_ROOT=str(snapshot),PYTHONPATH=f'{snapshot}/src:{snapshot}',TMPDIR='/dev/shm')
    benchmark=out/'performance/C9-external.json';completed=out/'commands/benchmark-C9-external.json'
    if benchmark.exists() and completed.exists() and read_json(completed)['returncode']==0:
        b=read_json(benchmark)
        assert len(b['records'])==6 and all(len(r['samples'])==27 and r['full_candidate_proof_parity'] for r in b['records'])
        assert b['source_head']==read_json(out/'baseline/reproduction-receipt.json')['starting_head']
        assert b['production_code_hash']==read_json(out/'baseline/manifest.json')['identity']['production_code_hash']
        assert b['dataset_hash']==read_json(out/'datasets/dataset.json')['hash']
        assert b['driver_sha256']==sha(ROOT/'evaluation/cycle10_benchmark.py')
        write_json(out/'commands/benchmark-C9-external-reuse.json',dict(passed=True,executed_again=False,
            artifact='performance/C9-external.json',sha256=sha(benchmark),original_command_sha256=sha(completed),
            scope='Reuse the completed source/data/driver-identified serial timing arm after a later checkout-layout precondition failed.'))
    else:
        command('benchmark-C9-external',[str(ROOT/'evaluation/cycle10_benchmark.py'),'--out',str(out),
            '--data',str(out/'datasets/dataset.json'),'--arm','C9-external'],cwd=snapshot,env=env)
    command('frozen-evaluation',['-m','scripts.cycle10_evaluate','--out',str(out),'--source',str(snapshot),'--all-modes'])
    command('frozen-analysis',['-m','evaluation.cycle10_analysis','--out',str(out),'--calibration'])
    write_json(out/'initial-stage-complete.json',dict(passed=True,baseline=True,frozen_native_and_C9_calibration=True,
        experimental_model_training=False,external_calibration_fitted_after_frozen_evaluation=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--snapshot',required=True);p.add_argument('--wait',action='store_true')
    a=p.parse_args();run(a.out,a.snapshot,a.wait)
