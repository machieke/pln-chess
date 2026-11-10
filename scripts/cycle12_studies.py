"""Run the registered Cycle 12 studies only after full baseline reproduction."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash


def run(out,wait=False):
    out=Path(out).resolve();baseline=out/'baseline/reproduction-receipt.json'
    while not baseline.exists():
        if not wait:raise RuntimeError('Full baseline reproduction receipt is required before learning')
        time.sleep(15)
    assert read_json(baseline)['passed'] and read_json(baseline)['cycle11_research_reproduced']
    source_hash=production_code_hash();env=dict(os.environ,TMPDIR='/dev/shm',C12_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT','C11_OUT'):env.pop(key,None)
    stages=[('learning',['-m','training.cycle12_learning','--out',str(out)]),
        ('concept-tests',['-m','pytest','tests/test_cycle12_concepts.py','-q']),
        ('concept-evaluation',['-m','evaluation.cycle12_concepts','--out',str(out)]),
        ('dependence',['-m','evaluation.cycle12_dependence','--out',str(out)]),
        ('partial-semantics',['-m','evaluation.cycle12_partial_semantics','--out',str(out)]),
        ('evolution',['-m','evaluation.cycle12_evolution','--out',str(out)])]
    for name,args in stages:
        assert source_hash==production_code_hash(),'Production changed during the registered study execution'
        path=out/'studies'/f'{name}.json';log=out/'studies'/f'{name}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        argv=[sys.executable,*args]
        if path.exists() and read_json(path).get('returncode')==0 and read_json(path).get('production_code_hash')==source_hash:
            print('RESUME STUDY',name,flush=True);continue
        started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(path,dict(argv=argv,returncode=result.returncode,production_code_hash=source_hash,
            source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            started_unix=started,elapsed_seconds=time.time()-started,log=str(log.relative_to(out))))
        if result.returncode:raise RuntimeError(str(log))
        print('CYCLE12 STUDY PASSED',name,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--wait',action='store_true')
    args=parser.parse_args();run(args.out,args.wait)
