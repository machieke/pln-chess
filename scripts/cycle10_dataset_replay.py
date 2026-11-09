"""Regenerate registered data in the fresh checkout without network access."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def run(out,checkout,work):
    out=Path(out).resolve();checkout=Path(checkout).resolve();work=Path(work).resolve()
    if work.exists():raise ValueError('Dataset replay requires a new output directory')
    work.mkdir(parents=True);shutil.copytree(out/'sources',work/'sources')
    env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}')
    argv=[str(checkout/'.venv/bin/python'),'-m','training.cycle10_data','--out',str(work)]
    start=time.time();log=out/'bootstrap/dataset-replay.txt'
    with log.open('w') as stream:r=subprocess.run(argv,cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT)
    receipt=dict(argv=argv,cwd=str(checkout),returncode=r.returncode,elapsed_seconds=time.time()-start,
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip(),
        environment={k:env[k] for k in ('PLN_CHESS_ROOT','PYTHONPATH')})
    write_json(out/'bootstrap/dataset-replay-command.json',receipt)
    if r.returncode:raise RuntimeError(str(log))
    before=read_json(out/'datasets/dataset.json');after=read_json(work/'datasets/dataset.json');assert before==after
    assert not subprocess.check_output(['git','status','--short'],cwd=checkout,text=True)
    write_json(out/'bootstrap/dataset-replay.json',dict(passed=True,exact_replay=True,dataset_hash=after['hash'],
        dataset_sha256=sha(work/'datasets/dataset.json'),clean_checkout=True,**receipt))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--checkout',required=True);p.add_argument('--work',required=True)
    a=p.parse_args();run(a.out,a.checkout,a.work)
