"""Replay the delivered Cycle 9 source before any Cycle 10 production change."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from pln_chess.common import ROOT, read_json, write_json, digest
from scripts.cycle9_baseline import sha

START = '257473d2462c75f84d3975bb91d85a8c1cc269dd'


def run(out, snapshot):
    out = out.resolve(); snapshot = snapshot.resolve()
    if not snapshot.exists():
        subprocess.run(['git', 'clone', '--shared', str(ROOT), str(snapshot)], check=True)
        subprocess.run(['git', 'checkout', '--detach', START], cwd=snapshot, check=True)
        (snapshot/'.runtime').mkdir()
        (snapshot/'.runtime/petta').symlink_to(ROOT/'.runtime/petta', target_is_directory=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=snapshot,text=True).strip()==START
    env = dict(os.environ, PLN_CHESS_ROOT=str(snapshot), PYTHONPATH=f'{snapshot}/src:{snapshot}', TMPDIR='/dev/shm')
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT'): env.pop(key,None)
    out.mkdir(parents=True,exist_ok=True)
    files=read_json(snapshot/'artifacts/cycle9/manifest.json')['files']
    assert all(sha(snapshot/p)==v['sha256'] for p,v in files.items())
    tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',START],cwd=snapshot,text=True).splitlines()
    protected={p:sha(snapshot/p) for p in tracked if p.startswith(('artifacts/','docs/','fixtures/','vendor/','configs/')) or p.endswith('.lock')}
    probe='import json,sys,importlib.metadata; from pln_chess.pln import Runtime; from pln_chess.cycle6.inference import production_code_hash; r=Runtime(); r.verify(); print(json.dumps(dict(runtime=r.manifest,python=sys.version,production_code_hash=production_code_hash(),dependencies={k:importlib.metadata.version(k) for k in ("pytest","chess","setuptools")})))'
    import json
    identity=json.loads(subprocess.check_output([sys.executable,'-c',probe],cwd=snapshot,env=env,text=True))
    write_json(out/'manifest.json',dict(starting_head=START,initial_working_tree=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        snapshot=str(snapshot),snapshot_status=subprocess.check_output(['git','status','--short'],cwd=snapshot,text=True),
        protected_files=protected,cycle9_manifest_verified=len(files),identity=identity,
        model=read_json(snapshot/'artifacts/cycle9/acceptance.json'),dataset_hash=read_json(snapshot/'artifacts/cycle9/datasets/dataset.json')['hash'],
        configurations={f'cycle{i}':read_json(snapshot/f'configs/cycle{i}.json') for i in (8,9)},
        dependency_locks={str(p.relative_to(snapshot)):sha(p) for p in snapshot.glob('*.lock')}))
    (out/'datasets').mkdir(exist_ok=True)
    shutil.copy2(snapshot/'artifacts/cycle9/datasets/dataset.json',out/'datasets/dataset.json')
    def command(name,args):
        log=out/f'logs/{name}.txt';log.parent.mkdir(exist_ok=True);start=time.time()
        with log.open('w') as stream:
            result=subprocess.run([sys.executable,*args],cwd=snapshot,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'commands/{name}.json',dict(argv=[sys.executable,*args],cwd=str(snapshot),source_head=START,
            started_unix=start,elapsed_seconds=time.time()-start,returncode=result.returncode,log=str(log.relative_to(out))))
        if result.returncode: raise RuntimeError(f'{name}: {log}')
        print(name,'passed',flush=True)
    # Each evaluator owns three workers; run those groups sequentially to bound memory.
    command('historical-regression',['-m','scripts.cycle9_regression','--out',str(out)])
    command('cycle9-evaluation',['-m','scripts.cycle9_evaluate','--out',str(out),'--source',str(snapshot)])
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(command,'tests',['-m','pytest','-q']),pool.submit(command,'controls',['-m','evaluation.cycle9_controls','--out',str(out)])]
        for job in jobs: job.result()
    from evaluation.cycle3 import read_gzip
    comparisons=[]
    fields=('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids','dependence_groups','proof_status','backoff','model_version','runtime_version','local_truth_value','typed_premises','promotion_selection')
    for receipt in sorted((out/'evaluation').glob('*.receipt.json')):
        r=read_json(receipt); artifact=r['artifact'];new=read_gzip(out/artifact);old=read_gzip(snapshot/'artifacts/cycle9'/artifact)
        assert [{k:x[k] for k in fields} for x in new['rows']]==[{k:x[k] for k in fields} for x in old['rows']],artifact
        assert [p['predicted'] for p in new['positions']]==[p['predicted'] for p in old['positions']]
        assert all(digest([new['native_proof_dag'][i] for i in row['proof_refs']])==row['proof_id'] for row in new['rows'])
        comparisons.append(dict(artifact=artifact,sha256=sha(out/artifact),positions=len(new['positions']),rows=len(new['rows']),exact_native_proof_parity=True,metrics=new['metrics']))
    assert len(comparisons)==48
    write_json(out/'proof-parity.json',dict(passed=True,comparisons=comparisons))
    command('performance',['-m','evaluation.cycle9_benchmark','--out',str(out),'--arm','C9-reproduced'])
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    write_json(out/'reproduction-receipt.json',dict(passed=True,starting_head=START,identity=identity,cycle9_shards=48,
        historical_suites=26,exact_native_proof_parity=True,protected_files=len(protected),
        negative_controls=read_json(out/'C8-promotion-relative-negative-regressions.json'),
        tests=(out/'logs/tests.txt').read_text(),benchmark_samples=126,
        scope='Executed native replay; finite behavior and proof equivalence. Timing is a fresh measurement, not exact wall-time reproduction.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--snapshot',required=True,type=Path)
    a=p.parse_args();run(a.out,a.snapshot)
