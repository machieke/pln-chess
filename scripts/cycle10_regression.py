"""Run established gates in a clean checkout of the final implementation source."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha

FIELDS=('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids','dependence_groups',
        'proof_status','backoff','model_version','runtime_version','local_truth_value','typed_premises','promotion_selection')


def compare(out):
    from evaluation.cycle3 import read_gzip
    out=Path(out);comparisons=[]
    for path in sorted((out/'current/evaluation').glob('*.receipt.json')):
        new=read_json(path);old=read_json(out/'baseline/evaluation'/path.name)
        assert new['native_proofs_verified'] and old['native_proofs_verified']
        assert new['proof_hash']==old['proof_hash'] and new['positions']==old['positions'] and new['rows']==old['rows']
        assert sha(out/'current'/new['artifact'])==new['sha256'] and sha(out/'baseline'/old['artifact'])==old['sha256']
        a=read_gzip(out/'current'/new['artifact']);b=read_gzip(out/'baseline'/old['artifact'])
        assert [{k:r[k] for k in FIELDS} for r in a['rows']]==[{k:r[k] for k in FIELDS} for r in b['rows']]
        assert [p['predicted'] for p in a['positions']]==[p['predicted'] for p in b['positions']]
        comparisons.append(dict(artifact=new['artifact'],rows=new['rows'],exact_native_proof_parity=True,
            production_code_hash=new['identity']['production_code_hash'],sha256=new['sha256']))
    assert len(comparisons)==48
    write_json(out/'current/cycle9-parity.json',dict(passed=True,shards=48,comparisons=comparisons,
        proof_validation='Each worker reconstructs and hashes every native proof; comparison binds artifact bytes, ordered proof hashes, classifications, truth values, hypotheses and evidence lineage.'))


def run(out,source):
    out=Path(out).resolve();source=Path(source).resolve();target=out/'current'
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True),'Use a clean implementation checkout'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    py=source/'.venv/bin/python';assert py.exists()
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm',C10_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT'):env.pop(key,None)
    (target/'datasets').mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/'artifacts/cycle9/datasets/dataset.json',target/'datasets/dataset.json')
    def command(name,args):
        start=time.time();log=target/f'logs/{name}.txt';log.parent.mkdir(exist_ok=True)
        with log.open('w') as stream:r=subprocess.run([str(py),*args],cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(target/f'commands/{name}.json',dict(argv=[str(py),*args],cwd=str(source),source_head=head,
            started_unix=start,elapsed_seconds=time.time()-start,returncode=r.returncode,log=str(log.relative_to(out))))
        if r.returncode:raise RuntimeError(f'{name}: {log}')
        print(name,'passed',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks=[pool.submit(command,'tests',['-m','pytest','-q']),
               pool.submit(command,'controls',['-m','evaluation.cycle9_controls','--out',str(target)])]
        for task in tasks:task.result()
    command('historical-regression',['-m','scripts.cycle9_regression','--out',str(target)])
    command('cycle9-evaluation',['-m','scripts.cycle9_evaluate','--out',str(target),'--source',str(source)])
    compare(out)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    tests=(target/'logs/tests.txt').read_text();match=re.search(r'(\d+) passed',tests);assert match
    identity_code='import json;from pln_chess.pln import Runtime;from pln_chess.cycle6.inference import production_code_hash;print(json.dumps(dict(runtime=Runtime().manifest,production_code_hash=production_code_hash())))'
    import json
    identity=json.loads(subprocess.check_output([str(py),'-c',identity_code],cwd=source,env=env,text=True))
    write_json(target/'verified.json',dict(passed=True,source_head=head,initial_clean=True,final_clean=True,
        checkout=str(source),test_count=int(match[1]),historical_suites=26,cycle9_shards=48,**identity,
        dependency_lock_sha256=sha(source/'requirements-dev.lock'),
        fresh_dependency_bootstrap_receipt='bootstrap/verified.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True)
    a=p.parse_args();run(a.out,a.source)
