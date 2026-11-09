"""Fresh-checkout end-to-end Cycle 10 reproduction with isolated output."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha


def run(out,checkout,snapshot,work,plot_python='python3',browser=True):
    out=Path(out).resolve();checkout=Path(checkout).resolve();snapshot=Path(snapshot).resolve();work=Path(work).resolve()
    for path in (out,checkout,snapshot,work):
        if path.exists():raise ValueError(f'Use a new reproduction directory: {path}')
    if not shutil.which('zstd'):raise ValueError('The offline PGN reader requires the zstd command-line tool')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True):
        raise ValueError('Commit the delivered package before starting a fresh-checkout reproduction')
    out.mkdir(parents=True);bootstrap(out/'bootstrap',checkout,head)
    shutil.copytree(ROOT/'artifacts/cycle10/sources',out/'sources')
    py=str(checkout/'.venv/bin/python')
    env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}',TMPDIR='/dev/shm',C10_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT'):env.pop(key,None)
    def command(name,args,python=py):
        start=time.time();log=out/f'reproduction-logs/{name}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w') as stream:r=subprocess.run([python,*args],cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'reproduction-commands/{name}.json',dict(argv=[python,*args],cwd=str(checkout),source_head=head,
            started_unix=start,elapsed_seconds=time.time()-start,returncode=r.returncode,log=str(log.relative_to(out))))
        if r.returncode:raise RuntimeError(f'{name}: {log}')
        print(name,'passed',flush=True)
    command('dataset',['-m','training.cycle10_data','--out',str(out)])
    actual=read_json(out/'datasets/dataset.json');assert actual==read_json(checkout/'artifacts/cycle10/datasets/dataset.json')
    write_json(out/'bootstrap/dataset-replay.json',dict(passed=True,exact_replay=True,clean_checkout=True,
        source_head=head,dataset_hash=actual['hash'],dataset_sha256=sha(out/'datasets/dataset.json'),
        source='Bundled immutable, licensed acquisition bytes and original receipts; no network re-acquisition needed.'))
    command('overlap',['-m','training.cycle10_overlap','--out',str(out)])
    command('architecture',['-c','import sys; from evaluation.cycle10_reporting import architecture; architecture(sys.argv[1])',str(out)])
    command('baseline',['-m','scripts.cycle10_baseline','--out',str(out/'baseline'),'--snapshot',str(snapshot)])
    command('initial-frozen-study',['-m','scripts.cycle10_initial','--out',str(out),'--snapshot',str(snapshot)])
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(command,'current-regression',['-m','scripts.cycle10_regression','--out',str(out),'--source',str(checkout)]),
              pool.submit(command,'research-experiments',['-m','scripts.cycle10_experiments','--out',str(out),'--source',str(checkout),'--wait'])]
        for job in jobs:job.result()
    command('application-smoke',['-m','scripts.cycle10_smoke','--out',str(out)])
    if browser:command('browser',['-m','scripts.cycle10_ui_verify','--out',str(out),'--work',str(work)])
    command('figures',[str(checkout/'evaluation/cycle10_plots.py'),'--out',str(out)],plot_python)
    command('reports',['-m','evaluation.cycle10_delivery','--out',str(out),'--docs',str(out/'reports')])
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    write_json(out/'reproduction-complete.json',dict(passed=True,source_head=head,clean_checkout=True,
        exact_dataset_replay=True,mandatory_implementation_gates=True,browser_executed=browser,
        source_acquisition='Reused exact delivered licensed source bytes and original acquisition receipts.',
        scope='Complete fresh native replay. Timings, timestamps and figure metadata can differ; source/data/model/proof identities and acceptance outcomes are checked. No Git push or deployment.'))
    from evaluation.cycle10_delivery import artifact_manifest
    artifact_manifest(out,out/'reports')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--checkout',required=True)
    p.add_argument('--baseline',required=True);p.add_argument('--browser-work',required=True)
    p.add_argument('--plot-python',default='python3');p.add_argument('--skip-browser',action='store_true')
    a=p.parse_args();run(a.out,a.checkout,a.baseline,a.browser_work,a.plot_python,not a.skip_browser)
