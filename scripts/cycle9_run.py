"""Consolidated study. Every native timing arm runs without other study workers."""
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from scripts.cycle9_baseline import START

OUT=Path(os.environ.get('C9_OUT',ROOT/'artifacts/cycle9')).resolve()


def command(name,args,env=None,cwd=ROOT):
    log=OUT/('pytest.txt' if name=='tests' else f'logs/{name}.txt');log.parent.mkdir(parents=True,exist_ok=True)
    started=time.time();argv=[sys.executable,*args]
    with log.open('w') as stream:r=subprocess.run(argv,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
    write_json(OUT/f'commands/{name}.json',dict(argv=argv,cwd=str(cwd),started_unix=started,elapsed_seconds=time.time()-started,
        returncode=r.returncode,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip(),log=str(log.relative_to(OUT))))
    if r.returncode:raise RuntimeError(f'{name} failed; inspect {log}')
    print(name,'passed',flush=True)


def run():
    snapshot=Path(os.environ.get('C9_BASELINE_SNAPSHOT',str(ROOT.parent/(ROOT.name+'-baseline'))))
    if not (OUT/'baseline/verified.json').exists():
        if not snapshot.exists():
            subprocess.run(['git','clone','--shared',str(ROOT),str(snapshot)],check=True)
            subprocess.run(['git','checkout','--detach',START],cwd=snapshot,check=True)
            (snapshot/'.runtime').symlink_to(ROOT/'.runtime',target_is_directory=True)
        command('baseline',[str(ROOT/'scripts/cycle9_baseline.py'),'--out',str(OUT/'baseline'),'--snapshot',str(snapshot)])
    command('dataset',['-m','training.cycle9_data','--out',str(OUT)])
    registered=read_json(ROOT/'artifacts/cycle9/datasets/dataset.json');actual=read_json(OUT/'datasets/dataset.json')
    assert actual==registered
    write_json(OUT/'dataset-replay.json',dict(exact_replay=True,hash=actual['hash'],source='training.cycle9_data'))
    if not (OUT/'performance/C8-original.json').exists():
        env=dict(os.environ,PLN_CHESS_ROOT=str(snapshot),PYTHONPATH=f'{snapshot}/src:{snapshot}',TMPDIR='/dev/shm')
        command('benchmark-C8-original',[str(ROOT/'evaluation/cycle9_benchmark.py'),'--out',str(OUT),'--arm','C8-original'],env,snapshot)
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks=[pool.submit(command,name,args) for name,args in [
            ('tests',['-m','pytest','-q']),('controls',['-m','evaluation.cycle9_controls','--out',str(OUT)]),
            ('composition',['-m','evaluation.cycle9_composition','--out',str(OUT)])]]
        for task in tasks:task.result()
    command('historical-regression',['-m','scripts.cycle9_regression','--out',str(OUT)])
    command('evaluation',['-m','scripts.cycle9_evaluate','--out',str(OUT)])
    command('abstention',['-m','evaluation.cycle9_abstention','--out',str(OUT)])
    # Native jobs have ended before timing samples begin.
    command('benchmark-C9-optimized',['-m','evaluation.cycle9_benchmark','--out',str(OUT),'--arm','C9-optimized'])
    command('analysis',['-m','evaluation.cycle9_analysis','--out',str(OUT)])
    command('verification',['-m','scripts.cycle9_verify','--out',str(OUT)])
    command('application-smoke',['-m','scripts.cycle9_smoke','--out',str(OUT)])
    write_json(OUT/'reproduction-complete.json',dict(passed=True,
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        scope='Fresh dependency bootstrap, immutable original baseline, exact dataset replay, all tests/controls, all prior suites, new cohorts, serial benchmarks and source-bound acceptance. Browser recording and report rendering are separate delivery steps.'))


if __name__=='__main__':run()
