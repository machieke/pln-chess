"""Fresh local checkout bootstrap with source and dependency receipts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,write_json
from scripts.cycle9_baseline import sha


def run(out,checkout,commit):
    out=Path(out).resolve();checkout=Path(checkout).resolve()
    if checkout.exists():raise ValueError('Bootstrap requires a new checkout path')
    out.mkdir(parents=True,exist_ok=True);commands=[]
    def command(name,args,cwd=ROOT,env=None):
        start=time.time();log=out/f'{name}.txt'
        with log.open('w') as stream:r=subprocess.run(args,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(name=name,argv=args,cwd=str(cwd),started_unix=start,elapsed_seconds=time.time()-start,returncode=r.returncode,log=log.name))
        write_json(out/'commands.json',commands)
        if r.returncode:raise RuntimeError(f'{name}: {log}')
    command('clone',['git','clone','--shared',str(ROOT),str(checkout)])
    command('checkout',['git','checkout','--detach',commit],cwd=checkout)
    initial=subprocess.check_output(['git','status','--short'],cwd=checkout,text=True)
    assert not initial and not (checkout/'.venv').exists() and not (checkout/'.runtime').exists()
    command('bootstrap',['bash','scripts/bootstrap.sh','--dependencies-only'],cwd=checkout)
    env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}',TMPDIR='/dev/shm')
    probe='import json,sys,importlib.metadata; from pln_chess.pln import Runtime; from pln_chess.cycle6.inference import production_code_hash; r=Runtime();r.verify();print(json.dumps(dict(runtime=r.manifest,production_code_hash=production_code_hash(),python=sys.version,dependencies={k:importlib.metadata.version(k) for k in ("pytest","chess","setuptools")})))'
    command('identity',[str(checkout/'.venv/bin/python'),'-c',probe],cwd=checkout,env=env)
    identity=json.loads((out/'identity.txt').read_text());final=subprocess.check_output(['git','status','--short'],cwd=checkout,text=True)
    assert not final
    write_json(out/'verified.json',dict(passed=True,initial_source_head=commit,checkout=str(checkout),initial_clean=True,
        fresh_venv=True,fresh_runtime=True,final_clean=True,identity=identity,
        dependency_lock_sha256=sha(checkout/'requirements-dev.lock'),runtime_lock_sha256=sha(checkout/'configs/runtime-lock.json'),
        scope='Fresh dependency bootstrap at registered source. Final implementation source and tests will be separately bound after checkout advancement.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--checkout',required=True);p.add_argument('--commit',required=True)
    a=p.parse_args();run(a.out,a.checkout,a.commit)
