"""Finish all research arms after frozen evaluation, then run isolated timing."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json


def run(out,source,wait=False):
    out=Path(out).resolve();source=Path(source).resolve();deadline=time.time()+43200
    def required(path):
        while not path.exists():
            if not wait or time.time()>deadline:raise RuntimeError(f'Required completed stage: {path}')
            time.sleep(5)
        assert read_json(path)['passed']
    required(out/'initial-stage-complete.json')
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    py=str(source/'.venv/bin/python');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm',C10_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT'):env.pop(key,None)
    def command(name,args):
        start=time.time();log=out/f'logs/{name}.txt';log.parent.mkdir(exist_ok=True)
        with log.open('w') as stream:r=subprocess.run([py,*args],cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/{name}.json',dict(argv=[py,*args],cwd=str(source),source_head=head,started_unix=start,
            elapsed_seconds=time.time()-start,returncode=r.returncode,log=str(log.relative_to(out))))
        if r.returncode:raise RuntimeError(f'{name}: {log}')
        print(name,'passed',flush=True)
    command('adaptation',['-m','training.cycle10_adapt','--out',str(out)])
    def evaluation(arm):
        args=['-m','scripts.cycle10_evaluate','--out',str(out),'--source',str(source),'--arm',arm,'--split','external-test']
        if arm in ('small','large'):args+=['--checkpoint',str(out/f'adaptation/model/{arm}.json')]
        command('evaluation-'+arm,args)
    # The established-regression study may still own three workers here.
    evaluation('small')
    required(out/'current/verified.json')
    # Two groups of three workers fit the eight-core study host. Timing is later.
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks=[pool.submit(evaluation,arm) for arm in ('large','temporal')]
        for task in tasks:task.result()
    command('temporal-controls',['-m','evaluation.cycle10_temporal','--out',str(out)])
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks=[pool.submit(command,'adaptation-regressions',['-m','scripts.cycle10_adapt_regression','--out',str(out)]),
               pool.submit(command,'dependence-predictions',['-m','evaluation.cycle10_dependence','--out',str(out)])]
        for task in tasks:task.result()
    for arm in ('small','large','temporal'):
        command('analysis-'+arm,['-m','evaluation.cycle10_analysis','--out',str(out),'--arm',arm])
    command('adaptation-analysis',['-m','evaluation.cycle10_adaptation_analysis','--out',str(out)])
    # The separately running established-regression study must have no workers left.
    required(out/'current/verified.json')
    command('benchmark-C10-current',['-m','evaluation.cycle10_benchmark','--out',str(out),'--data',str(out/'datasets/dataset.json'),'--arm','C10-current'])
    command('history-performance',['-m','evaluation.cycle10_history_performance','--out',str(out)])
    command('performance-comparison',['-m','evaluation.cycle10_performance_analysis','--out',str(out)])
    command('verification',['-m','scripts.cycle10_verify','--out',str(out)])
    write_json(out/'research-complete.json',dict(passed=True,source_head=head,new_learning_promoted=False,
        scope='All frozen/adapted/history experiments, established regression gates and serial performance measurements. Application smoke, visual proof and rendered reports are separately recorded delivery steps.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True);p.add_argument('--wait',action='store_true')
    a=p.parse_args();run(a.out,a.source,a.wait)
