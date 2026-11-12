"""Replay immutable completed feature archives while their index is assembling.

Run with the fresh checkout's interpreter and PYTHONPATH. This orchestration
file is an explicit input; all inference and proof verification imports come
from that clean checkout. The ordinary full-corpus driver later verifies and
joins exactly these receipts against the completed immutable indexes.
"""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import time

from pln_chess.common import ROOT, digest, read_json
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle13_performance import CountedRuntime
from evaluation.cycle14_proof_replay import replay_archive
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(source, out):
    source, out = Path(source).resolve(), Path(out).resolve()
    runtime = CountedRuntime(timeout=900)
    runtime.verify()
    code = production_code_hash()
    assert code == read_json(source / 'source-freeze.json')['production_code_hash']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True)
    identity = dict(checkout=str(ROOT), source_head=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        production_code_hash=code, runtime=runtime.manifest,
        wrapper_path=str(Path(__file__).resolve()), wrapper_sha256=sha(__file__),
        proof_driver_sha256=sha(ROOT / 'evaluation/cycle14_proof_replay.py'))
    identity_name = 'stream-identity-' + identity['wrapper_sha256'][:12] + '.json'
    atomic_json(out / identity_name, identity)
    session = NativeSession(runtime, max_entries=50000)
    session.bind(digest(['c14-full-proof-replay', runtime.manifest]))
    selected = read_json(source / 'features/selected-generations.json')
    started = time.time()
    processed = set()
    while True:
        progress = False
        for kind in ('immediate', 'temporal'):
            directory = source / 'features' / selected[kind]
            for path in sorted((directory / 'receipts').glob('*.json')):
                token = (kind, path.name)
                if token in processed:
                    continue
                record = read_json(path)
                archive = source / record['archive']
                assert sha(archive) == record['archive_sha256']
                target = out / 'receipts' / f'{kind}-{record["id"]}.json'
                if target.exists():
                    receipt = read_json(target)
                    assert receipt['archive_sha256'] == record['archive_sha256']
                    assert receipt['production_code_hash'] == code and receipt['runtime'] == runtime.manifest
                else:
                    calls = runtime.process_launches
                    began = time.monotonic()
                    receipt = replay_archive(archive, runtime, session)
                    assert receipt['semantic_sha256'] == record['semantic_sha256']
                    receipt.update(id=record['id'], kind=kind, passed=True,
                        runtime=runtime.manifest, production_code_hash=code)
                    atomic_json(target, receipt)
                    atomic_json(out / 'stream-resources' / target.name, dict(
                        id=record['id'], kind=kind, elapsed_seconds=time.monotonic()-began,
                        interpreter_launches=runtime.process_launches-calls,
                        cumulative_self_cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+
                            resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                        cumulative_child_cpu_seconds=resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+
                            resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime))
                    print('C14 CLEAN STREAM REPLAY', kind, record['id'], flush=True)
                processed.add(token)
                progress = True
        if all((source / 'features' / selected[kind] / 'index.json').exists() for kind in ('immediate', 'temporal')):
            expected = sum(len(read_json(source / 'features' / generation / 'index.json')['records'])
                for generation in (selected['immediate'], selected['temporal']))
            if len(processed) == expected:
                break
        if time.time()-started > 24*3600:
            raise TimeoutError('Streaming proof replay exceeded its registered stage budget')
        if not progress:
            time.sleep(5)
    atomic_json(out / 'stream-complete.json', dict(passed=True, identity=identity,
        archives=len(processed), elapsed_seconds=time.time()-started,
        interpreter_launches=runtime.process_launches,
        scope='Early complete archive replay; completed-index aggregation is a separate mandatory step.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    run(args.source, args.out)
