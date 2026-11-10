"""Execute mandatory legality gates in a fresh, clean Cycle 12 checkout."""
import argparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha
from scripts.cycle12_baseline import compare_reports


def run(out, source):
    out, source = Path(out).resolve(), Path(source).resolve()
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    py = source / '.venv/bin/python'
    assert py.exists()
    env = dict(os.environ, PLN_CHESS_ROOT=str(source), PYTHONPATH=f'{source}/src:{source}', TMPDIR='/dev/shm', C12_OUT=str(out))
    for key in ('C6_OUT', 'C7_OUT', 'C8_OUT', 'C9_OUT', 'C10_OUT', 'C11_OUT'):
        env.pop(key, None)
    identity_code = 'import json;from pln_chess.pln import Runtime;from pln_chess.cycle6.inference import production_code_hash;print(json.dumps(dict(runtime=Runtime().manifest,production_code_hash=production_code_hash())))'
    identity = json.loads(subprocess.check_output([str(py), '-c', identity_code], cwd=source, env=env, text=True))
    target = out / 'current'
    for group, cycle in (('historical', 9), ('external', 10)):
        (target / group / 'datasets').mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / f'artifacts/cycle{cycle}/datasets/dataset.json', target / group / 'datasets/dataset.json')

    def command(name, args):
        argv = [str(py), *args]
        receipt = target / f'commands/{name}.json'
        if receipt.exists():
            old = read_json(receipt)
            if old['source_head'] == head and old['argv'] == argv and old['returncode'] == 0 and old['identity'] == identity:
                print('RESUME', name, flush=True)
                return
        started = time.time()
        log = target / f'logs/{name}.txt'
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT)
        write_json(receipt, dict(argv=argv, cwd=str(source), source_head=head, identity=identity,
            started_unix=started, elapsed_seconds=time.time()-started, returncode=result.returncode,
            log=str(log.relative_to(out))))
        if result.returncode:
            raise RuntimeError(f'{name}: {log}')
        print('PASSED', name, flush=True)

    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(command, 'tests', ['-m', 'pytest', '-q']),
                pool.submit(command, 'negative-controls', ['-m', 'evaluation.cycle9_controls', '--out', str(target / 'historical')])]
        for job in jobs:
            job.result()
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(command, 'historical-suites', ['-m', 'scripts.cycle9_regression', '--out', str(target / 'historical')]),
                pool.submit(command, 'cycle9-evaluation', ['-m', 'scripts.cycle9_evaluate', '--out', str(target / 'historical'), '--source', str(source)])]
        for job in jobs:
            job.result()
    data = read_json(target / 'external/datasets/dataset.json')
    external_jobs = []
    for path in sorted((out / 'baseline/external/evaluation').glob('*.receipt.json')):
        old = read_json(path)
        ident = old['identity']
        fixture = next(p for p in data['positions'] if p['id'] == ident['fixtures'][0])
        selected = [p for p in data['positions'] if p['split'] == fixture['split'] and p['source_collection'] == fixture['source_collection']]
        offset = next(i for i, p in enumerate(selected) if p['id'] == fixture['id'])
        external_jobs.append((path.name.removesuffix('.receipt.json'), ['-m', 'scripts.cycle10_evaluate', '--worker',
            '--out', str(target / 'external'), '--source', str(source), '--arm', ident['arm'],
            '--split', fixture['split'], '--collection', fixture['source_collection'], '--offset', str(offset),
            '--mode', ident['mode'], '--checkpoint', str(source / 'artifacts/cycle10/model/C10-default.json')]))
    assert len(external_jobs) == 132
    with ThreadPoolExecutor(max_workers=6) as pool:
        for _ in pool.map(lambda job: command(*job), external_jobs):
            pass
    comparison_jobs = []
    for group, count in (('historical', 48), ('external', 132)):
        paths = sorted((target / group / 'evaluation').glob('*.receipt.json'))
        assert len(paths) == count
        for path in paths:
            receipt = read_json(path)
            assert receipt['native_proofs_verified']
            comparison_jobs.append((target / group / receipt['artifact'], out / 'baseline' / group / receipt['artifact']))
    with ProcessPoolExecutor(max_workers=6) as pool:
        comparisons = list(pool.map(compare_reports, [job[0] for job in comparison_jobs], [job[1] for job in comparison_jobs]))
    negatives = read_json(target / 'historical/C8-promotion-relative-negative-regressions.json')
    assert negatives['cases'] == negatives['intact_negative'] == negatives['removed_unknown'] == 287
    assert not negatives['failures']
    tests = (target / 'logs/tests.txt').read_text()
    count = re.search(r'(\d+) passed', tests)
    assert count and not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True)
    bootstrap = [p for p in out.glob('*bootstrap*/verified.json') if read_json(p)['checkout'] == str(source)]
    assert len(bootstrap) == 1 and read_json(bootstrap[0])['identity']['production_code_hash'] == identity['production_code_hash']
    protected = read_json(out / 'baseline/manifest.json')['protected_files']
    assert all(sha(ROOT / path) == value for path, value in protected.items())
    write_json(target / 'proof-parity.json', dict(passed=True, comparisons=comparisons))
    write_json(target / 'verified.json', dict(passed=True, source_head=head, checkout=str(source),
        initial_clean=True, final_clean=True, identity=identity, test_count=int(count[1]),
        historical_suites=26, cycle9_shards=48, cycle10_shards=132, negative_controls=287,
        exact_native_proof_parity=True, protected_files=len(protected),
        fresh_bootstrap_receipt=str(bootstrap[0].relative_to(out)),
        dependency_lock_sha256=sha(source / 'requirements-dev.lock'), completed_unix=time.time()))
    print('CURRENT IMPLEMENTATION GATES COMPLETE', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    run(args.out, args.source)
