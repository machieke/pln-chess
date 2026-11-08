"""Dependency-ordered full study, with at most three concurrent subprocesses."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys
import time
from pln_chess.common import ROOT,write_json
from scripts.cycle8_baseline import START
from scripts.cycle8_evaluate import ARMS

OUT=Path(os.environ.get('C8_OUT',ROOT/'artifacts/cycle8')).resolve()


def command(name,args):
    log=OUT/('pytest.txt' if name=='tests' else f'logs/{name}.txt');log.parent.mkdir(parents=True,exist_ok=True)
    start=time.time()
    with log.open('w') as stream:
        result=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    receipt={'name':name,'argv':[sys.executable,*args],'cwd':str(ROOT),'started_unix':start,'elapsed_seconds':time.time()-start,
        'returncode':result.returncode,'log':str(log.relative_to(OUT)),'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    write_json(OUT/f'commands/{name}.json',receipt)
    if result.returncode:raise RuntimeError(f'{name} failed: {log}')
    print(name,'passed',flush=True);return receipt


def group(jobs):
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(command,*job) for job in jobs]
        for f in futures:f.result()


def run():
    snapshot=ROOT.parent/(ROOT.name+'-c7-snapshot')
    if not snapshot.exists():
        subprocess.run(['git','clone','--shared','--no-hardlinks',str(ROOT),str(snapshot)],check=True)
        subprocess.run(['git','checkout','--detach',START],cwd=snapshot,check=True)
        (snapshot/'.runtime').symlink_to(ROOT/'.runtime',target_is_directory=True)
    command('baseline',[str(ROOT/'scripts/cycle8_baseline.py'),'--snapshot',str(snapshot),'--out',str(OUT/'baseline')])
    command('dataset',['-m','training.cycle8_data','--out',str(OUT)])
    group([('tests',['-m','pytest','-q']),('composition',['-m','evaluation.cycle8_composition_lab','--out',str(OUT/'composition')]),
        ('training',['-m','training.cycle8','--out',str(OUT)])])
    command('forensics',['-m','scripts.cycle8_forensics','--out',str(OUT)])
    group([(arm,['-m','scripts.cycle8_evaluate','--out',str(OUT),'--arm',arm]) for arm in ARMS]+
        [('controls-'+variant,['-m','scripts.cycle8_controls','--out',str(OUT),'--variant',variant]) for variant in ('C8-frozen','C8-promotion-relative','C8-no-promotion-training')])
    # No concurrent native/evaluation work during timing measurements.
    for variant in ('C7-frozen','C8-frozen','C8-promotion-relative','C8-no-promotion-training'):
        command('benchmark-'+variant,['-m','evaluation.cycle8_benchmark','--out',str(OUT),'--variant',variant])
    command('analysis',['-m','evaluation.cycle8_analysis','--out',str(OUT)])
    command('verification',['-m','scripts.cycle8_verify','--out',str(OUT)])
    command('smoke',['-m','scripts.cycle8_smoke','--out',str(OUT)])
    write_json(OUT/'reproduction-complete.json',{'passed':True,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'scope':'Full clean bootstrap, original C7 replay, deterministic C8 training, evaluations, controls, serial benchmarks, analysis, acceptance and actual application smoke checks.'})


if __name__=='__main__':run()
