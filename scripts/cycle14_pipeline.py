"""Resumable dependency-ordered scientific studies, with immutable receipts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out).resolve();waited=time.monotonic()
    required=['baseline/research/verified.json','features/immediate-g2/index.json','features/temporal-g1/index.json','labels/temporal-g1/index.json']
    while not all((out/p).exists() for p in required):
        if time.monotonic()-waited>24*3600:raise TimeoutError('Registered scientific input stage exceeded 24 hours; preserve unfinished cases')
        time.sleep(5)
    stages=[('register-reversals','evaluation.cycle14_studies',['register_reversals']),
        ('representation','evaluation.cycle14_studies',['representation']),
        ('fit','evaluation.cycle14_preferences',['fit']),('calibration-freeze','evaluation.cycle14_preferences',['freeze']),
        ('test','evaluation.cycle14_preferences',['test']),('factorial','evaluation.cycle14_studies',['factorial']),
        ('dependence','evaluation.cycle14_studies',['dependence']),('reversals','evaluation.cycle14_studies',['reversals']),
        ('native-locality','evaluation.cycle14_locality',[]),('bounded-responses','evaluation.cycle14_responses',['run'])]
    for name,module,args in stages:
        path=out/'pipeline/commands'/f'{name}.json';log=out/'pipeline/logs'/f'{name}.txt'
        identity=dict(module=module,args=args,driver_sha256=sha(ROOT/(module.replace('.','/')+'.py')),
            feature_indexes={p:sha(out/p) for p in required})
        if path.exists():
            old=read_json(path);assert old['identity']==identity,'Do not change an executed stage generation'
            if old['returncode']==0:continue
            attempt=1
            while log.with_suffix(f'.attempt-{attempt}.txt').exists():attempt+=1
            if log.exists():log.rename(log.with_suffix(f'.attempt-{attempt}.txt'))
            path.rename(path.with_suffix(f'.attempt-{attempt}.json'))
        if name=='bounded-responses':assert (out/'labels/responses-g1/index.json').exists()
        argv=[sys.executable,'-u','-m',module,*args,'--out',str(out)]
        started=time.time();log.parent.mkdir(parents=True,exist_ok=True);path.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w') as stream:result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT,timeout=24*3600)
        path.write_text(json.dumps(dict(identity=identity,argv=argv,returncode=result.returncode,
            started_unix=started,elapsed_seconds=time.time()-started,log_sha256=sha(log)),sort_keys=True,indent=2)+'\n')
        if result.returncode:raise RuntimeError(str(log))
        print('C14 SCIENTIFIC STAGE COMPLETE',name,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/cycle14');run(p.parse_args().out)
