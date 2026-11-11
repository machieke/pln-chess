"""Run the fixed studies when complete, source-bound native features are ready."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


def run(out,wait=False):
    out=Path(out).resolve();code=production_code_hash()
    for module,gate in (
        ('evaluation.cycle13_preferences','features/index.json'),
        ('evaluation.cycle13_temporal','temporal/features/index.json'),
        ('evaluation.cycle13_dependence',None)):
        if gate:
            while True:
                try:
                    receipt=read_json(out/gate)
                    assert receipt['passed']
                    break
                except (FileNotFoundError,json.JSONDecodeError):
                    if not wait:raise
                    time.sleep(2)
            if 'production_code_hash' in receipt:assert receipt['production_code_hash']==code
            else:assert all(r['identity']['production_code_hash']==code for r in receipt['receipts'])
        name=module.rsplit('.',1)[1];log=out/'studies'/f'{name}.txt'
        log.parent.mkdir(parents=True,exist_ok=True)
        if log.exists():raise ValueError('Preserve previous study attempt before rerunning '+name)
        argv=[sys.executable,'-u','-m',module,'--out',str(out)];started=time.time()
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT)
        write_json(log.with_suffix('.command.json'),dict(argv=argv,returncode=result.returncode,
            started_unix=started,elapsed_seconds=time.time()-started,production_code_hash=code,
            driver_sha256=sha(ROOT/(module.replace('.','/')+'.py'))))
        if result.returncode:raise RuntimeError(str(log))
        print('FIXED STUDY COMPLETE',module,flush=True)
    write_json(out/'studies/verified.json',dict(passed=True,production_code_hash=code,
        summaries={p:sha(out/p) for p in ('preferences/summary.json','temporal/summary.json','dependence/summary.json')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--wait',action='store_true')
    args=parser.parse_args();run(args.out,args.wait)
