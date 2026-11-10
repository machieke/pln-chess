"""Freeze and replay the accepted Cycle 10 source before Cycle 11 production edits.

The driver is new research orchestration; every inference subprocess imports the
unchanged starting checkout. Original reports and checkpoints are read-only.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha

START = 'fe9e28edc03184fee02ec535399768fd9d5883fa'
PARITY_FIELDS = ('fixture', 'move', 'classification', 'truth_value', 'proof_id',
                'rule_ids', 'evidence_ids', 'dependence_groups', 'proof_status',
                'backoff', 'model_version', 'runtime_version', 'local_truth_value',
                'typed_premises', 'promotion_selection')


def compare_reports(new_path, old_path):
    from evaluation.cycle3 import read_gzip
    new, old = read_gzip(new_path), read_gzip(old_path)
    assert [{k: r.get(k) for k in PARITY_FIELDS} for r in new['rows']] == [
        {k: r.get(k) for k in PARITY_FIELDS} for r in old['rows']], str(new_path)
    assert [p['predicted'] for p in new['positions']] == [p['predicted'] for p in old['positions']]
    assert all(digest([new['native_proof_dag'][i] for i in r['proof_refs']]) == r['proof_id'] for r in new['rows'])
    return dict(artifact=str(new_path), reference=str(old_path), sha256=sha(new_path),
                reference_sha256=sha(old_path), rows=len(new['rows']), positions=len(new['positions']),
                proof_hash=digest([r['proof_id'] for r in new['rows']]),
                exact_native_proof_parity=True, metrics=new['metrics'])


def run(out, snapshot):
    out, snapshot = Path(out).resolve(), Path(snapshot).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not snapshot.exists():
        subprocess.run(['git', 'clone', '--shared', '--no-checkout', str(ROOT), str(snapshot)], check=True)
        subprocess.run(['git', 'checkout', '--detach', START], cwd=snapshot, check=True)
        (snapshot / '.runtime').mkdir()
        (snapshot / '.runtime/petta').symlink_to(ROOT / '.runtime/petta', target_is_directory=True)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=snapshot, text=True).strip() == START
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=snapshot, text=True)
    env = dict(os.environ, PLN_CHESS_ROOT=str(snapshot), PYTHONPATH=f'{snapshot}/src:{snapshot}', TMPDIR='/dev/shm')
    for key in ('C6_OUT', 'C7_OUT', 'C8_OUT', 'C9_OUT', 'C10_OUT', 'C11_OUT'):
        env.pop(key, None)
    probe = '''import json,sys,importlib.metadata
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle8.model import PromotionModel
from pln_chess.common import ROOT
r=Runtime();m=PromotionModel.load(ROOT/'artifacts/cycle10/model/C10-default.json',r)
print(json.dumps(dict(runtime=r.manifest,production_code_hash=production_code_hash(),
python=sys.version,accepted_model=m.version,dependencies={k:importlib.metadata.version(k) for k in ('pytest','chess','setuptools')})))'''
    identity = json.loads(subprocess.check_output([sys.executable, '-c', probe], cwd=snapshot, env=env, text=True))
    if not (out / 'manifest.json').exists():
        original = read_json(snapshot / 'artifacts/cycle10/manifest.json')
        for relative, entry in original['files'].items():
            assert sha(snapshot / 'artifacts/cycle10' / relative) == entry['sha256'], relative
        tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], cwd=snapshot, text=True).splitlines()
        protected = {p: sha(snapshot / p) for p in tracked if p.startswith(('artifacts/', 'docs/', 'fixtures/', 'vendor/', 'configs/')) or p.endswith('.lock')}
        write_json(out / 'manifest.json', dict(schema=11, starting_head=START, snapshot=str(snapshot),
            snapshot_clean=True, initial_working_tree=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
            identity=identity, protected_files=protected, verified_cycle10_files=len(original['files']),
            cycle10_manifest_sha256=sha(snapshot / 'artifacts/cycle10/manifest.json'),
            accepted_checkpoint_sha256=sha(snapshot / 'artifacts/cycle10/model/C10-default.json'),
            acceptance=read_json(snapshot / 'artifacts/cycle10/acceptance.json'),
            configurations={str(p.relative_to(snapshot)): read_json(p) for p in (snapshot / 'configs').glob('*.json')},
            datasets={str(p.relative_to(snapshot)): sha(p) for p in (snapshot / 'artifacts').glob('cycle*/datasets/dataset.json')},
            dependency_locks={str(p.relative_to(snapshot)): sha(p) for p in snapshot.glob('*.lock')},
            started_unix=time.time()))
    else:
        assert read_json(out / 'manifest.json')['identity'] == identity
    for group, cycle in (('historical', 9), ('external', 10)):
        (out / group / 'datasets').mkdir(parents=True, exist_ok=True)
        shutil.copy2(snapshot / f'artifacts/cycle{cycle}/datasets/dataset.json', out / group / 'datasets/dataset.json')

    def command(name, args):
        receipt = out / f'commands/{name}.json'
        argv = [sys.executable, *args]
        if receipt.exists():
            previous = read_json(receipt)
            if previous['returncode'] == 0 and previous['argv'] == argv and previous['source_head'] == START:
                print('RESUME completed command', name, flush=True)
                return
        log = out / f'logs/{name}.txt'
        log.parent.mkdir(parents=True, exist_ok=True)
        started = time.time()
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=snapshot, env=env, stdout=stream, stderr=subprocess.STDOUT)
        write_json(receipt, dict(argv=argv, cwd=str(snapshot), source_head=START, started_unix=started,
            elapsed_seconds=time.time()-started, returncode=result.returncode, log=str(log.relative_to(out)),
            source_hash=identity['production_code_hash'], environment={k: env[k] for k in ('PLN_CHESS_ROOT', 'PYTHONPATH', 'TMPDIR')}))
        if result.returncode:
            raise RuntimeError(f'{name} failed: {log}')
        print('PASSED', name, flush=True)

    # No performance measurements overlap these six-worker replay groups.
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(command, 'tests', ['-m', 'pytest', '-q']),
                   pool.submit(command, 'negative-controls', ['-m', 'evaluation.cycle9_controls', '--out', str(out / 'historical')])]
        for future in futures:
            future.result()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(command, 'historical-suites', ['-m', 'scripts.cycle9_regression', '--out', str(out / 'historical')]),
                   pool.submit(command, 'cycle9-evaluation', ['-m', 'scripts.cycle9_evaluate', '--out', str(out / 'historical'), '--source', str(snapshot)])]
        for future in futures:
            future.result()
    external_jobs = []
    for receipt in sorted((snapshot / 'artifacts/cycle10/evaluation').glob('*.receipt.json')):
        old = read_json(receipt)
        ident = old['identity']
        if ident['arm'] not in ('frozen', 'temporal'):
            continue
        stem = receipt.name.removesuffix('.receipt.json')
        # All collections/splits are recovered from the source fixture identity,
        # avoiding ambiguous hyphen parsing in the artifact name.
        data = read_json(out / 'external/datasets/dataset.json')
        fixture = next(p for p in data['positions'] if p['id'] == ident['fixtures'][0])
        selected = [p for p in data['positions'] if p['split'] == fixture['split'] and p['source_collection'] == fixture['source_collection']]
        offset = next(i for i, p in enumerate(selected) if p['id'] == fixture['id'])
        external_jobs.append((stem, ['-m', 'scripts.cycle10_evaluate', '--worker', '--out', str(out / 'external'),
            '--source', str(snapshot), '--arm', ident['arm'], '--split', fixture['split'],
            '--collection', fixture['source_collection'], '--offset', str(offset), '--mode', ident['mode'],
            '--checkpoint', str(snapshot / 'artifacts/cycle10/model/C10-default.json')]))
    assert len(external_jobs) == 132
    with ThreadPoolExecutor(max_workers=6) as pool:
        for _ in pool.map(lambda job: command(*job), external_jobs):
            pass
    comparisons = []
    for receipt in sorted((out / 'historical/evaluation').glob('*.receipt.json')):
        record = read_json(receipt)
        comparisons.append(compare_reports(out / 'historical' / record['artifact'], snapshot / 'artifacts/cycle9' / record['artifact']))
    assert len(comparisons) == 48
    for receipt in sorted((out / 'external/evaluation').glob('*.receipt.json')):
        record = read_json(receipt)
        comparisons.append(compare_reports(out / 'external' / record['artifact'], snapshot / 'artifacts/cycle10' / record['artifact']))
    assert len(comparisons) == 180
    write_json(out / 'proof-parity.json', dict(passed=True, comparisons=comparisons))
    protected = read_json(out / 'manifest.json')['protected_files']
    assert all(sha(ROOT / p) == h for p, h in protected.items())
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=snapshot, text=True)
    write_json(out / 'reproduction-receipt.json', dict(passed=True, starting_head=START, identity=identity,
        snapshot=str(snapshot), snapshot_clean=True, historical_suites=26, cycle9_shards=48,
        cycle10_frozen_and_history_shards=132, exact_native_proof_parity=True, protected_files=len(protected),
        negative_controls=read_json(out / 'historical/C8-promotion-relative-negative-regressions.json'),
        tests=(out / 'logs/tests.txt').read_text(), completed_unix=time.time(),
        scope='Executed unchanged-source native replay of accepted operational and secondary suites. Experimental adapted models are not the accepted baseline.'))
    print('BASELINE COMPLETE', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--snapshot', required=True)
    args = parser.parse_args()
    run(args.out, args.snapshot)
