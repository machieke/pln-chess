"""Replay C7 from an immutable checkout; never import changing production code."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

START = 'c6ee658352395abe6e276cafdf1ddf59830a17a0'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def replay(arm, out):
    from pln_chess.common import ROOT, read_json, digest
    from pln_chess.pln import Runtime
    from pln_chess.cycle7.model import BackoffModel
    from pln_chess.cycle7.inference import Cycle7Options
    from scripts.cycle7_baseline import SPLITS
    from evaluation.cycle7 import evaluate
    from evaluation.cycle7_io import pack
    from evaluation.cycle3 import read_gzip
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == START
    runtime = Runtime(timeout=180)
    model_name = 'C7-learned-8' if arm == 'C7-learned-8-locked' else 'C7-frozen'
    mode = {'C7-strict': 'strict', 'C7-experimental': 'experimental'}.get(arm, 'operational')
    model = BackoffModel.load(ROOT / f'artifacts/cycle7/model/{model_name}.json', runtime)
    jobs = [(key, ROOT / f'artifacts/{source}/dataset.json', split) for key, source, split in SPLITS]
    jobs.append(('cycle7-independent-games', ROOT / 'artifacts/cycle7/datasets/dataset.json', 'independent-games'))
    if arm == 'C7-experimental':
        jobs = [job for job in jobs if job[0] in ('cycle6-independent-games', 'cycle7-independent-games')]
    summary = {}
    fields = ('fixture', 'move', 'classification', 'truth_value', 'proof_id', 'rule_ids', 'evidence_ids',
              'dependence_groups', 'proof_status', 'backoff', 'model_version', 'runtime_version')
    for key, path, split in jobs:
        data = read_json(path)
        report = evaluate(data, model, split, runtime, options=Cycle7Options(mode=mode, max_native_invocations=100000))
        old = read_gzip(ROOT / f'artifacts/cycle7/evaluation/{arm}-{key}.json.xz')
        assert [{k: r[k] for k in fields} for r in report['rows']] == [{k: r[k] for k in fields} for r in old['rows']], (arm, key)
        assert [p['predicted'] for p in report['positions']] == [p['predicted'] for p in old['positions']]
        assert not report['metrics']['incomplete']
        for row in report['rows']:
            assert digest([report['native_proof_dag'][i] for i in row['proof_refs']]) == row['proof_id']
        target = out / f'evaluation/{arm}-{key}.json.xz'
        pack(target, report)
        summary[key] = {'metrics': report['metrics'], 'positions': len(report['positions']),
                        'dataset_hash': data['hash'], 'dataset_sha256': sha(path), 'model_version': model.version,
                        'artifact': str(target.relative_to(out)), 'sha256': sha(target), 'exact_native_proof_parity': True}
        write(out / f'{arm}-summary.json', summary)
        print(arm, key, 'EXACT PARITY', report['metrics']['recall'], report['metrics']['exact_move_set_accuracy'], flush=True)
    return summary


def run(snapshot, out):
    root = Path(__file__).resolve().parents[1]
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=snapshot, text=True).strip()
    assert actual == START
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], cwd=root, text=True).splitlines()
    protected = {p: sha(root / p) for p in tracked if p.startswith(('artifacts/', 'fixtures/', 'vendor/', 'configs/', 'tests/', 'docs/')) or p.endswith('.lock')}
    env = dict(os.environ, PYTHONPATH=str(snapshot / 'src') + ':' + str(snapshot),
               PLN_CHESS_ROOT=str(snapshot), TMPDIR='/dev/shm', PYTHONDONTWRITEBYTECODE='1')
    for name in ('C7_OUT', 'C6_OUT', 'C8_OUT'):
        env.pop(name, None)
    runtime = json.loads(subprocess.check_output([sys.executable, '-c', 'import json; from pln_chess.pln import Runtime; print(json.dumps(Runtime().manifest))'], cwd=snapshot, env=env, text=True))
    write(out / 'lock.json', {'starting_head': START, 'snapshot': str(snapshot),
          'snapshot_status': subprocess.check_output(['git', 'status', '--short'], cwd=snapshot, text=True),
          'working_status_at_lock': subprocess.check_output(['git', 'status', '--short'], cwd=root, text=True),
          'runtime': runtime, 'driver_sha256': sha(__file__), 'protected_files': protected,
          'source_files': {str(p.relative_to(root)): sha(p) for p in sorted((root / 'src').rglob('*.py'))},
          'models': {p.name: sha(p) for p in (snapshot / 'artifacts/cycle7/model').glob('*.json')},
          'reported_acceptance': json.loads((snapshot / 'artifacts/cycle7/acceptance.json').read_text()),
          'isolation': 'Pinned checkout with existing pinned runtime symlink; this is baseline replay, not the later clean bootstrap.'})
    def command(arm):
        argv = [sys.executable, str(Path(__file__).resolve()), '--out', str(out), '--worker', arm]
        log = out / f'logs/{arm}.txt'; log.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=snapshot, env=env, stdout=stream, stderr=subprocess.STDOUT)
        write(out / f'commands/{arm}.json', {'argv': argv, 'cwd': str(snapshot), 'environment': {k:env[k] for k in ('PYTHONPATH','PLN_CHESS_ROOT','TMPDIR')},
              'source_head': START, 'driver_sha256': sha(__file__), 'started_unix': start,
              'elapsed_seconds': time.time()-start, 'returncode': result.returncode, 'log': str(log.relative_to(out))})
        if result.returncode:
            raise RuntimeError(f'{arm} failed: {log}')
        print(arm, 'passed', flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(command, arm) for arm in ('C7-frozen', 'C7-learned-8-locked', 'C7-strict', 'C7-experimental')]
        for future in futures:
            future.result()
    assert all(sha(root / p) == h for p, h in protected.items())
    write(out / 'verified.json', {'passed': True, 'evaluations': 38, 'starting_head': START,
          'exact_native_proof_parity': True, 'historical_files_unchanged': len(protected), 'runtime': runtime})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--worker')
    args = parser.parse_args()
    if args.worker:
        replay(args.worker, args.out)
    else:
        run(args.snapshot, args.out)
