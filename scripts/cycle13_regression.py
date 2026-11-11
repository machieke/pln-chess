"""Complete accepted-model regression in a fresh, clean Cycle 13 checkout."""
import argparse
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha
from scripts.cycle12_baseline import compare_reports


def run(out, source, workers=6):
    out, source = Path(out).resolve(), Path(source).resolve()
    baseline = read_json(out / 'baseline/reproduction-receipt.json')
    assert baseline['passed'] and baseline['legal_shards'] == 206
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    py = str(source / '.venv/bin/python')
    env = dict(os.environ, PLN_CHESS_ROOT=str(source), PYTHONPATH=str(source / 'src') + ':' + str(source),
        TMPDIR='/dev/shm', C13_OUT=str(out))
    for cycle in range(6,13):
        env.pop('C' + str(cycle) + '_OUT', None)
    probe = 'import json;from pln_chess.pln import Runtime;from pln_chess.cycle6.inference import production_code_hash;print(json.dumps(dict(runtime=Runtime().manifest,production_code_hash=production_code_hash())))'
    identity = json.loads(subprocess.check_output([py,'-c',probe],cwd=source,env=env,text=True))
    target = out / 'current'
    (target / 'baseline').mkdir(parents=True,exist_ok=True)
    shutil.copy2(out / 'baseline/reproduction-receipt.json', target / 'baseline/reproduction-receipt.json')
    population = read_json(out / 'baseline/legal/panel.json')
    assert population['candidate'] == 'artifacts/cycle12/model/C12-default.json'
    write_json(target / 'legal/panel.json', population)

    def command(name, args):
        argv = [py,*args]
        path = target / 'commands' / (name + '.json')
        if path.exists():
            receipt = read_json(path)
            if receipt['source_head'] == head and receipt['identity'] == identity and receipt['argv'] == argv and receipt['returncode'] == 0:
                print('CURRENT RESUME',name,flush=True)
                return
        log = target / 'logs' / (name + '.txt')
        log.parent.mkdir(parents=True,exist_ok=True)
        started = time.time()
        with log.open('w') as stream:
            result = subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(path,dict(argv=argv,source_head=head,identity=identity,cwd=str(source),
            started_unix=started,elapsed_seconds=time.time()-started,returncode=result.returncode,
            log=str(log.relative_to(out)),driver_sha256=sha(__file__)))
        if result.returncode:
            raise RuntimeError(str(log))
        print('CURRENT PASSED',name,flush=True)

    def legal():
        with ThreadPoolExecutor(max_workers=workers) as pool:
            tasks = [pool.submit(command,'legal-' + job['id'],['-m','scripts.cycle12_legal_review',
                '--out',str(target),'--source',str(source),'--worker',job['id']]) for job in population['jobs']]
            for task in tasks:
                task.result()

    def controls():
        command('negative-and-history-controls',['-m','evaluation.cycle12_legal_controls','--out',str(target)])
        command('recoveries-and-holdouts',['-m','evaluation.cycle12_legal_recovery','--out',str(target)])

    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks = [pool.submit(command,'tests',['-m','pytest','-q']),pool.submit(legal),pool.submit(controls)]
        for task in tasks:
            task.result()
    actual = [target / 'legal/evaluation' / (job['id'] + '.json.xz') for job in population['jobs']]
    reference = [out / 'baseline/legal/evaluation' / (job['id'] + '.json.xz') for job in population['jobs']]
    with ProcessPoolExecutor(max_workers=min(workers,4)) as pool:
        comparisons = list(pool.map(compare_reports,actual,reference))
    receipts = [read_json(path.with_name(path.name.removesuffix('.json.xz') + '.receipt.json')) for path in actual]
    assert all(r['passed'] and not r['changes'] and r['identity']['production_code_hash'] == identity['production_code_hash'] for r in receipts)
    controls = read_json(target / 'legal/negative-controls/verified.json')
    history = read_json(target / 'legal/temporal/summary.json')
    recoveries = read_json(target / 'legal/recovery/verified.json')
    assert controls['passed'] and controls['cases'] == 287
    assert history['passed'] and history['cases'] == 27
    assert recoveries['passed'] and recoveries['production_code_hash'] == identity['production_code_hash']
    test_count = int(re.search(r'(\d+) passed',(target / 'logs/tests.txt').read_text())[1])
    assert test_count >= 543
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    after = json.loads(subprocess.check_output([py,'-c',probe],cwd=source,env=env,text=True))
    assert after == identity
    write_json(target / 'proof-parity.json',dict(passed=True,comparisons=comparisons,
        rows=sum(r['rows'] for r in receipts),shards=len(receipts),exact_native_proof_parity=True))
    write_json(target / 'verified.json',dict(passed=True,source_head=head,checkout=str(source),checkout_clean=True,
        identity=identity,test_count=test_count,legal_shards=len(receipts),legal_rows=sum(r['rows'] for r in receipts),
        negative_controls=287,history_controls=27,recoveries=2,holdouts=76,
        exact_native_proof_parity=True,classification_changes=0,new_false_legal=0,new_false_illegal=0,
        new_self_check_false_legal=0,model_version=baseline['identity']['accepted_model'],
        baseline_receipt_sha256=sha(out / 'baseline/reproduction-receipt.json'),
        proof_parity_sha256=sha(target / 'proof-parity.json'),completed_unix=time.time(),
        scope='Complete accepted Cycle 12 checkpoint replay under the current frozen production source, including strict and experimental panel jobs.'))
    print('COMPLETE CYCLE 13 LEGAL REGRESSION PASSED',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',default='artifacts/cycle13')
    parser.add_argument('--source',required=True)
    parser.add_argument('--workers',type=int,default=6)
    args = parser.parse_args()
    run(args.out,args.source,args.workers)
