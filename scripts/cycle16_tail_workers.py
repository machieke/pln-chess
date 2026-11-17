"""Run a small, distant tail of the existing legal manifest using one spare CPU.

The original preservation driver remains authoritative and later reuses these
same-source successful command receipts. No inference or comparison changes.
"""
import argparse
import os
from pathlib import Path
import subprocess
import time
from pln_chess.common import read_json,write_json
from scripts.cycle15_baseline import sha


def run(out,source):
    out=Path(out).resolve();source=Path(source).resolve()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    jobs=read_json(out/'legal/panel.json')['jobs'];assert len(jobs)==206
    env={k:v for k,v in os.environ.items() if not (k.startswith('C') and k.endswith('_OUT'))}
    env.update(PLN_CHESS_ROOT=str(source),PYTHONPATH=str(source/'src')+':'+str(source),TMPDIR='/dev/shm')
    rows=[]
    for index in reversed(range(190,206)):
        job=jobs[index];name='legal-'+job['id'];target=out/'commands'/(name+'.json')
        if target.exists():continue
        first=next((i for i,j in enumerate(jobs) if not (out/'commands'/('legal-'+j['id']+'.json')).exists()),206)
        # A conservative separation avoids the main driver's four active jobs.
        # If its frontier approaches, leave the remaining tail to that driver.
        if index-first<64:break
        log=out/'logs'/(name+'.log')
        if log.exists():continue
        argv=[str(source/'.venv/bin/python'),'-m','scripts.cycle12_legal_review',
            '--out',str(out),'--source',str(source),'--worker',job['id']]
        started=time.time()
        with log.open('x') as stream:
            process=subprocess.run(['/usr/bin/time','-v',*argv],cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipt=dict(source_head=head,argv=argv,returncode=process.returncode,elapsed_seconds=time.time()-started,
            log=str(log),log_sha256=sha(log),started_unix=started)
        write_json(target,receipt);rows.append(dict(index=index,command=str(target),frontier_at_start=first))
        print('TAIL PRESERVATION',index,job['id'],process.returncode,flush=True)
        if process.returncode:raise RuntimeError(str(log))
    write_json(out/'tail-scheduling.json',dict(source_head=head,one_additional_worker=True,jobs=rows,
        policy='Only far-tail unstarted jobs; exact standard worker command and command receipt format'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True)
    a=p.parse_args();run(a.out,a.source)
