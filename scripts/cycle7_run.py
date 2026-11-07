"""Dependency-ordered subprocess orchestration, bounded to three independent jobs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys
import time
from pln_chess.common import ROOT, write_json

OUT=Path(os.environ.get('C7_OUT',ROOT/'artifacts/cycle7'))

def command(name,args):
    start=time.time();log=OUT/('pytest.txt' if name=='tests' else f'logs/{name}.txt');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as stream:
        result=subprocess.run([sys.executable,*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    receipt={'name':name,'argv':[sys.executable,*args],'started_unix':start,'elapsed_seconds':time.time()-start,
        'returncode':result.returncode,'log':str(log.relative_to(OUT)),'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    write_json(OUT/f'commands/{name}.json',receipt)
    if result.returncode:raise RuntimeError(f'{name} failed; inspect {log}')
    return receipt

def group(jobs):
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(command,*job) for job in jobs]
        for f in futures:print(f.result()['name'],'passed',flush=True)

def run():
    command('baseline',['-m','scripts.cycle7_baseline','--out',str(OUT)])
    group([('tests',['-m','pytest','-q']),
        ('native',['-m','evaluation.cycle7_native',str(OUT/'native')]),('training',['-m','scripts.cycle7_deliver','--stage','training'])])
    group([(s,['-m','scripts.cycle7_deliver','--stage',s]) for s in ('matrix-frozen','matrix-strict','matrix-learned','pilot','ablations','matrix-baselines')]+
        [('research',['-m','evaluation.cycle7_research',str(OUT)])])
    # Timings are measured after the concurrent evaluation load has ended.
    for variant in ('C6','C7'):
        command('benchmark-'+variant,['-m','evaluation.cycle7_benchmark','--out',str(OUT),'--variant',variant])
    command('analysis',['-m','evaluation.cycle7_analysis',str(OUT)])
    command('verification',['-m','scripts.cycle7_verify'])
    command('smoke',['-m','scripts.cycle7_smoke'])
    command('report',['-m','evaluation.cycle7_reporting'])

if __name__=='__main__':run()
