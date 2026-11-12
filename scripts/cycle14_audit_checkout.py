"""Fresh sparse research checkout without duplicating historical legal outputs."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from pln_chess.common import ROOT, write_json
from scripts.cycle9_baseline import sha


PATHS=['src','training','evaluation','scripts','configs','vendor','tests',
    'artifacts/cycle10/datasets','artifacts/cycle10/sources',
    'artifacts/cycle11/model','artifacts/cycle12/model','artifacts/cycle12/datasets',
    'artifacts/cycle13/model','artifacts/cycle13/datasets','artifacts/cycle13/sources',
    'artifacts/cycle13/concepts']


def run(out,checkout,commit,reference_source,resume=False):
    out,checkout,reference_source=map(lambda p:Path(p).resolve(),(out,checkout,reference_source))
    assert resume or not checkout.exists(),'Preserve prior checkout generations'
    out.mkdir(parents=True,exist_ok=True)
    commands=json.loads((out/'commands.json').read_text()) if resume else []
    if resume:
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()==commit
        assert not (checkout/'.runtime').exists(),'Resume here is only for a pre-runtime bootstrap failure'
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout)
    def command(name,argv,cwd=ROOT,env=None):
        began=time.time();log=out/(name+'.txt')
        if log.exists():
            attempt=1
            while log.with_suffix(f'.attempt-{attempt}.txt').exists():attempt+=1
            log.rename(log.with_suffix(f'.attempt-{attempt}.txt'))
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(name=name,argv=argv,cwd=str(cwd),returncode=result.returncode,
            started_unix=began,elapsed_seconds=time.time()-began,log_sha256=sha(log)))
        write_json(out/'commands.json',commands)
        assert result.returncode==0,str(log)
    if not resume:command('clone',['git','clone','--shared','--no-checkout',str(ROOT),str(checkout)])
    # Git 2.25 accepts --cone on init, but treats it as a path on set.
    command('sparse-init',['git','sparse-checkout','init','--cone'],checkout)
    command('sparse',['git','sparse-checkout','set',*PATHS],checkout)
    command('checkout',['git','checkout','--detach',commit],checkout)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout)
    assert (resume or not (checkout/'.venv').exists()) and not (checkout/'.runtime').exists()
    command('bootstrap',['bash','scripts/bootstrap.sh','--dependencies-only'],checkout)
    env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}',TMPDIR='/dev/shm')
    probe='import json,sys,importlib.metadata;from pln_chess.pln import Runtime;from pln_chess.cycle6.inference import production_code_hash;r=Runtime();r.verify();print(json.dumps(dict(runtime=r.manifest,production_code_hash=production_code_hash(),python=sys.version,dependencies={k:importlib.metadata.version(k) for k in ("pytest","chess","setuptools")})))'
    command('identity',[str(checkout/'.venv/bin/python'),'-c',probe],checkout,env)
    # This teacher was independently compiled in the first fresh C14 checkout.
    # Reuse and disclose its byte-bound build receipt; do not claim a second build.
    destination=checkout/'.runtime/cycle13-reference'
    shutil.copytree(reference_source,destination)
    assert sha(destination/'stockfish/src/stockfish')==sha(reference_source/'stockfish/src/stockfish')
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout)
    write_json(out/'verified.json',dict(passed=True,initial_source_head=commit,checkout=str(checkout),
        initial_clean=True,final_clean=True,fresh_venv=True,fresh_runtime=True,
        identity=json.loads((out/'identity.txt').read_text()),sparse_paths=PATHS,
        dependency_lock_sha256=sha(checkout/'requirements-dev.lock'),runtime_lock_sha256=sha(checkout/'configs/runtime-lock.json'),
        inherited_reference_source=str(reference_source),reference_binary_sha256=sha(destination/'stockfish/src/stockfish'),
        scope='Fresh local source, virtual environment and pinned native runtime. Sparse checkout omits unrelated historical legal output copies. The separately recorded fresh offline teacher build is copied byte-identically, not claimed compiled twice.'))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('out','checkout','commit','reference-source'):p.add_argument('--'+name,required=True)
    p.add_argument('--resume',action='store_true')
    a=p.parse_args();run(a.out,a.checkout,a.commit,a.reference_source,a.resume)
