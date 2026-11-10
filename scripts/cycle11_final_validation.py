"""Finish source-bound validation after native study workers become quiescent."""
import argparse
import os
from pathlib import Path
import subprocess
import time
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


def run(out,source,work,wait=False):
    out,source,work=(Path(p).resolve() for p in (out,source,work))
    required=[out/'current/verified.json',out/'clean-research/verified.json',out/'legal/summary.json',out/'legal/regression/summary.json']
    deadline=time.monotonic()+21600
    while not all(p.exists() for p in required):
        if not wait or time.monotonic()>deadline:raise RuntimeError('Final prerequisite receipts are missing')
        time.sleep(5)
    for path in required[:2]:assert read_json(path)['passed']
    assert read_json(out/'architecture/boundary.json')['production_code_hash']==production_code_hash()
    while subprocess.run(['pgrep','-x','swipl'],stdout=subprocess.DEVNULL).returncode==0:
        if not wait or time.monotonic()>deadline:raise RuntimeError('Native workers remain active before final validation')
        time.sleep(2)
    py=str(source/'.venv/bin/python')
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm',C11_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT'):env.pop(key,None)
    # Use the delivered research-report criteria even when the independently
    # bootstrapped production checkout predates a report-only correction.
    research_driver=Path(__file__).resolve().parents[1]/'evaluation/cycle11_delivery.py'
    commands=[]
    stages=[('acceptance',[py,'-m','evaluation.cycle11_delivery','acceptance','--out',str(out)]),
        ('accepted-default-tests',[py,'-m','pytest','-q']),
        ('performance',[py,'-m','evaluation.cycle11_performance','--out',str(out)]),
        ('browser',[py,'-m','scripts.cycle11_ui_verify','--out',str(out),'--work',str(work)]),
        ('research-acceptance',[py,str(research_driver),'research','--out',str(out)]),
        ('plots',['python3',str(source/'evaluation/cycle11_plots.py'),'--out',str(out)])]
    for name,argv in stages:
        log=out/'final-validation'/f'{name}.txt'
        log.parent.mkdir(exist_ok=True)
        started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(stage=name,argv=argv,cwd=str(source),production_code_hash=production_code_hash(),
            started_unix=started,elapsed_seconds=time.time()-started,returncode=result.returncode,log=str(log.relative_to(out)),
            research_criteria_sha256=sha(research_driver) if name=='research-acceptance' else None))
        write_json(out/'final-validation/commands.json',commands)
        if result.returncode:raise RuntimeError(str(log))
        print('FINAL VALIDATION',name,flush=True)
    write_json(out/'final-validation/verified.json',dict(passed=True,production_code_hash=production_code_hash(),
        all_stages_executed=True,stages=[name for name,_ in stages],source_checkout=str(source),
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        orchestration_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        clean_source=not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True),
        interpretation='Implementation checks passed. Research outcomes, including unmet proposed targets, are reported separately.'))
    print('FINAL VALIDATION COMPLETE',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--source',required=True)
    parser.add_argument('--browser-work',required=True)
    parser.add_argument('--wait',action='store_true')
    args=parser.parse_args()
    run(args.out,args.source,args.browser_work,args.wait)
