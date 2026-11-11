"""Execute production boundary, source integrity and installed CLI checks."""
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
    out=Path(out).resolve()
    while True:
        try:
            study=read_json(out/'studies/verified.json');assert study['passed'];break
        except (FileNotFoundError,json.JSONDecodeError):
            if not wait:raise
            time.sleep(2)
    code=production_code_hash();assert study['production_code_hash']==code
    for name,argv in (
        ('integrity',[sys.executable,'-m','evaluation.cycle13_integrity','--out',str(out)]),
        ('boundary',[sys.executable,'-m','evaluation.cycle13_delivery','boundary','--out',str(out)]),
        ('cli',[sys.executable,'-m','evaluation.cycle13_cli','--out',str(out)]),
        ('figures',['/usr/bin/python3','-m','evaluation.cycle13_plots','--out',str(out)])):
        log=out/'post-studies'/f'{name}.txt';receipt=log.with_suffix('.command.json')
        if log.exists():raise ValueError('Preserve previous verification attempt before rerunning '+name)
        log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm',C13_OUT=str(out)),stdout=stream,stderr=subprocess.STDOUT)
        write_json(receipt,dict(argv=argv,returncode=result.returncode,started_unix=started,
            elapsed_seconds=time.time()-started,production_code_hash=code,log_sha256=sha(log)))
        if result.returncode:raise RuntimeError(str(log))
        print('POST-STUDY VERIFICATION',name,'PASSED',flush=True)
    write_json(out/'post-studies/verified.json',dict(passed=True,production_code_hash=code,
        receipts={p.name:sha(p) for p in sorted((out/'post-studies').glob('*.command.json'))}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--wait',action='store_true')
    args=parser.parse_args();run(args.out,args.wait)
