"""Finish application verification and reports after all native research gates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle10_delivery import artifact_manifest


def run(out,docs,work,plot_python='python3',browser=True,wait=False,port=18780):
    out=Path(out).resolve();docs=Path(docs).resolve();work=Path(work).resolve();deadline=time.time()+43200
    while not (out/'research-complete.json').exists():
        if not wait or time.time()>deadline:raise RuntimeError('Complete the native research stage before application verification')
        time.sleep(5)
    assert read_json(out/'research-complete.json')['passed']
    assert read_json(out/'verification.json')['production_code_hash']==production_code_hash()
    assert not subprocess.check_output(['git','status','--porcelain','--','src','tests','configs'],cwd=ROOT,text=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    env=dict(os.environ,PLN_CHESS_ROOT=str(ROOT),PYTHONPATH=f'{ROOT}/src:{ROOT}',TMPDIR='/dev/shm',C10_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT'):env.pop(key,None)
    def command(name,args,python=sys.executable):
        log=out/f'delivery/logs/{name}.txt';log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
        with log.open('w') as stream:r=subprocess.run([python,*args],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'delivery/commands/{name}.json',dict(argv=[python,*args],cwd=str(ROOT),source_head=head,
            production_code_hash=production_code_hash(),started_unix=started,elapsed_seconds=time.time()-started,
            returncode=r.returncode,log=str(log.relative_to(out))))
        if r.returncode:raise RuntimeError(f'{name}: {log}')
        print(name,'passed',flush=True)
    # Acceptance enables the unchanged C8 default in the final application.
    # Check that activation as well as the earlier unaccepted-source environment.
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks=[pool.submit(command,'application-smoke',['-m','scripts.cycle10_smoke','--out',str(out)]),
               pool.submit(command,'post-acceptance-tests',['-m','pytest','-q'])]
        for task in tasks:task.result()
    if browser:command('browser',['-m','scripts.cycle10_ui_verify','--out',str(out),'--work',str(work),'--port',str(port)])
    command('figures',[str(ROOT/'evaluation/cycle10_plots.py'),'--out',str(out)],plot_python)
    command('reports',['-m','evaluation.cycle10_delivery','--out',str(out),'--docs',str(docs)])
    required=('engineering-report','package-matrix','dataset-provenance','external-generalization','generalization-failures',
        'temporal-evidence','calibration-shift','performance','strategic-readiness','architecture-decision','reproduction','executive-summary')
    assert all((docs/(name+'.md')).stat().st_size>0 for name in required)
    assert read_json(out/'smoke/verified.json')['passed']
    if browser:assert read_json(out/'ui/verification.json')['passed']
    tests=(out/'delivery/logs/post-acceptance-tests.txt').read_text();match=re.search(r'(\d+) passed',tests)
    assert match and not re.search(r'\d+ failed|ERRORS|FAILURES',tests)
    write_json(out/'delivery/automated.json',dict(passed=True,source_head=head,production_code_hash=production_code_hash(),
        application_smoke=True,post_acceptance_test_count=int(match[1]),browser_executed=browser,
        required_reports=list(required),figures=['external-generalization','failure-taxonomy','calibration-shift','sample-efficiency','performance'],
        scope='Executed application, tests, optional recorded browser checks, figures and reports. Final screenshot inspection, manifest refresh and local Git delivery are separate review steps. No push or deployment.'))
    artifact_manifest(out,docs)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--docs',default=str(ROOT/'docs/cycle10'))
    p.add_argument('--browser-work',required=True);p.add_argument('--plot-python',default='python3')
    p.add_argument('--skip-browser',action='store_true');p.add_argument('--wait',action='store_true');p.add_argument('--port',type=int,default=18780)
    a=p.parse_args();run(a.out,a.docs,a.browser_work,a.plot_python,not a.skip_browser,a.wait,a.port)
