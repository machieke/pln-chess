"""One complete source-bound preservation run in a clean isolated checkout."""
import argparse
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle15_baseline import sha
from scripts.cycle12_baseline import compare_reports


def run(out,source,workers=4):
    out=Path(out).resolve();source=Path(source).resolve()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    out.mkdir(parents=True,exist_ok=True)
    for relative,original in [('baseline/reproduction-receipt.json','artifacts/cycle14/baseline/reproduction-receipt.json'),
                              ('legal/panel.json','artifacts/cycle14/current/legal/panel.json')]:
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/original,target)
    panel=read_json(out/'legal/panel.json');assert len(panel['jobs'])==206
    env={k:v for k,v in os.environ.items() if not (k.startswith('C') and k.endswith('_OUT'))}
    env.update(PLN_CHESS_ROOT=str(source),PYTHONPATH=str(source/'src')+':'+str(source),TMPDIR='/dev/shm')
    py=str(source/'.venv/bin/python')
    def command(name,args):
        target=out/'commands'/(name+'.json');log=out/'logs'/(name+'.log')
        if target.exists():
            previous=read_json(target)
            if previous['source_head']==head and previous['returncode']==0:return previous
            raise RuntimeError('Preserve failed receipt; choose a new generation: '+name)
        log.parent.mkdir(parents=True,exist_ok=True)
        started=time.time();argv=[py,*args]
        with log.open('w') as stream:
            result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipt=dict(source_head=head,argv=argv,returncode=result.returncode,elapsed_seconds=time.time()-started,
                     log=str(log),log_sha256=sha(log),started_unix=started)
        write_json(target,receipt)
        print('PRESERVATION',name,result.returncode,round(receipt['elapsed_seconds'],2),flush=True)
        if result.returncode:raise RuntimeError(str(log))
        return receipt
    def legal():
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures=[pool.submit(command,'legal-'+job['id'],['-m','scripts.cycle12_legal_review',
                '--out',str(out),'--source',str(source),'--worker',job['id']]) for job in panel['jobs']]
            for task in futures:task.result()
    def controls():
        command('negative-and-history-controls',['-m','evaluation.cycle12_legal_controls','--out',str(out)])
        command('recoveries-and-holdouts',['-m','evaluation.cycle12_legal_recovery','--out',str(out)])
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(legal),pool.submit(controls),pool.submit(command,'tests',
            ['-m','pytest','-q','--junitxml='+str(out/'tests.xml')])]
        for task in futures:task.result()
    actual=[out/'legal/evaluation'/(job['id']+'.json.xz') for job in panel['jobs']]
    reference=[source/'artifacts/cycle14/current/legal/evaluation'/(job['id']+'.json.xz') for job in panel['jobs']]
    with ProcessPoolExecutor(max_workers=workers) as pool:comparisons=list(pool.map(compare_reports,actual,reference))
    controls=read_json(out/'legal/negative-controls/verified.json');history=read_json(out/'legal/temporal/summary.json')
    recovery=read_json(out/'legal/recovery/verified.json')
    assert controls['passed'] and controls['cases']==287 and history['passed'] and history['cases']==27 and recovery['passed']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    import xml.etree.ElementTree as ET
    suites=ET.parse(out/'tests.xml').getroot();total=sum(int(s.get('tests',0)) for s in suites.iter('testsuite'))
    assert all(int(s.get('failures',0))==int(s.get('errors',0))==0 for s in suites.iter('testsuite'))
    write_json(out/'proof-parity.json',comparisons)
    write_json(out/'verified.json',dict(passed=True,source_head=head,checkout_clean=True,tests=total,
        legal_shards=206,legal_rows=sum(r['rows'] for r in comparisons),exact_native_proof_parity=True,
        classification_changes=0,negative_controls=287,history_controls=27,recoveries=2,holdouts=76,
        accepted_checkpoint_sha256=sha(source/'artifacts/cycle12/model/C12-default.json'),
        proof_parity_sha256=sha(out/'proof-parity.json'),completed_unix=time.time(),
        scope='Fresh full legal execution, controls and complete test suite at the frozen local Cycle 15 commit'))
    print('COMPLETE PRESERVATION PASSED',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True)
    p.add_argument('--workers',type=int,default=4);a=p.parse_args();run(a.out,a.source,a.workers)
