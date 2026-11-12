"""Replay immutable completed feature archives while their index is assembling.

Run with the fresh checkout's interpreter and PYTHONPATH. This orchestration
file is an explicit input; all inference and proof verification imports come
from that clean checkout. The ordinary full-corpus driver later verifies and
joins exactly these receipts against the completed immutable indexes.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import fcntl
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from pln_chess.common import ROOT, digest, read_json
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle13_performance import CountedRuntime
from evaluation.cycle14_proof_replay import replay_archive
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(source, out, shard=0, shards=1, stop_when=None, early_receipt=None,subshard=0,subshards=1):
    assert 0 <= shard < shards <= 4
    assert 0 <= subshard < subshards <= 4
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
        proof_driver_sha256=sha(ROOT / 'evaluation/cycle14_proof_replay.py'),
        shard=shard, shards=shards,subshard=subshard,subshards=subshards)
    identity_name = f'stream-identity-{identity["wrapper_sha256"][:12]}-shard{shard}.json'
    if subshards>1:identity_name=identity_name.replace('.json',f'-part{subshard}-of-{subshards}.json')
    if stop_when:
        assert early_receipt and Path(early_receipt).name == early_receipt
        identity['stop_when'] = str(Path(stop_when).resolve())
        identity_name = identity_name.replace('.json','-early.json')
    atomic_json(out / identity_name, identity)
    session = NativeSession(runtime, max_entries=50000)
    session.bind(digest(['c14-full-proof-replay', runtime.manifest]))
    selected = read_json(source / 'features/selected-generations.json')
    started = time.time()
    processed = set()
    def belongs(kind,identifier):
        number=int(digest([kind,identifier]),16)
        return number%shards==shard and (number//shards)%subshards==subshard
    def release_slot(complete=False):
        if stop_when and (complete or Path(stop_when).exists()):
            atomic_json(out / early_receipt, dict(passed=True,identity=identity,
                archives_validated_or_replayed=len(processed),elapsed_seconds=time.time()-started,
                interpreter_launches=runtime.process_launches,stopped_between_archives=True,
                complete_shard=complete,
                scope='Release the early verification worker for current legal controls. Completed immutable archive receipts are retained for the later full shard; this is not a corpus-completion receipt.'))
            return True
        return False
    while True:
        if release_slot():return
        progress = False
        for kind in ('immediate', 'temporal'):
            directory = source / 'features' / selected[kind]
            for path in sorted((directory / 'receipts').glob('*.json')):
                if release_slot():return
                token = (kind, path.name)
                if token in processed:
                    continue
                record = read_json(path)
                if not belongs(kind,record['id']):
                    continue
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
            expected = sum(belongs(kind,r['id'])
                for kind in ('immediate', 'temporal')
                for r in read_json(source / 'features' / selected[kind] / 'index.json')['records'])
            if len(processed) == expected:
                if release_slot(complete=True):return
                break
        if time.time()-started > 24*3600:
            raise TimeoutError('Streaming proof replay exceeded its registered stage budget')
        if not progress:
            time.sleep(5)
    suffix=f'-part{subshard}-of-{subshards}' if subshards>1 else ''
    atomic_json(out / f'stream-complete-shard{shard}-of-{shards}{suffix}.json', dict(passed=True, identity=identity,
        archives=len(processed), elapsed_seconds=time.time()-started,
        interpreter_launches=runtime.process_launches,
        scope='Early complete archive replay; completed-index aggregation is a separate mandatory step.'))


def partitioned(source,out,shard,shards,workers,policy):
    source,out=Path(source).resolve(),Path(out).resolve();started=time.time()
    selected=read_json(source/'features/selected-generations.json')
    while not all((source/'features'/selected[kind]/'index.json').exists() for kind in ('immediate','temporal')):
        if time.time()-started>24*3600:raise TimeoutError('Feature closure exceeded proof-partition scheduling budget')
        time.sleep(5)
    completed=out/f'stream-complete-shard{shard}-of-{shards}.json'
    if completed.exists():
        receipt=read_json(completed);runtime=CountedRuntime(timeout=900)
        assert receipt['passed'] and receipt['workers']==workers
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        code=production_code_hash();assert code==read_json(source/'source-freeze.json')['production_code_hash']
        for part in receipt['parts']:
            assert sha(out/part['path'])==part['sha256']
            identity=read_json(out/part['path'])['identity']
            assert identity['source_head']==head and identity['runtime']==runtime.manifest
            assert identity['proof_driver_sha256']==sha(ROOT/'evaluation/cycle14_proof_replay.py')
        count=0
        for kind in ('immediate','temporal'):
            for record in read_json(source/'features'/selected[kind]/'index.json')['records']:
                if int(digest([kind,record['id']]),16)%shards!=shard:continue
                replay=read_json(out/'receipts'/f'{kind}-{record["id"]}.json')
                assert replay['passed'] and replay['runtime']==runtime.manifest and replay['production_code_hash']==code
                assert replay['archive_sha256']==record['archive_sha256']==sha(source/record['archive'])
                assert replay['semantic_sha256']==record['semantic_sha256']
                count+=1
        assert count==receipt['archives']==sum(p['result']['archives'] for p in receipt['parts'])
        print('C14 COMPLETE PROOF PARTITION REVALIDATED',shard,count,flush=True)
        return
    def part(index):
        log=out/'partition-logs'/f'shard{shard}-part{index}-of-{workers}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w') as stream:
            subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--source',str(source),'--out',str(out),
                '--shard',str(shard),'--shards',str(shards),'--subshard',str(index),'--subshards',str(workers)],
                cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
        receipt=out/f'stream-complete-shard{shard}-of-{shards}-part{index}-of-{workers}.json'
        return dict(path=receipt.name,sha256=sha(receipt),result=read_json(receipt))
    with ThreadPoolExecutor(max_workers=workers) as pool:parts=list(pool.map(part,range(workers)))
    expected=sum(int(digest([kind,r['id']]),16)%shards==shard for kind in ('immediate','temporal')
        for r in read_json(source/'features'/selected[kind]/'index.json')['records'])
    assert all(p['result']['passed'] for p in parts) and sum(p['result']['archives'] for p in parts)==expected
    atomic_json(out/f'stream-complete-shard{shard}-of-{shards}.json',dict(passed=True,archives=expected,
        parts=parts,workers=workers,policy=policy,wrapper_sha256=sha(__file__),
        feature_workers_completed_before_launch=True,
        scope='Disjoint quotient/modulo subdivisions of one existing proof shard. Every archive retains the same full native verifier. No overlap with the other two main shards; final complete-index joining remains mandatory.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=1)
    parser.add_argument('--stop-when')
    parser.add_argument('--early-receipt')
    parser.add_argument('--subshard',type=int)
    parser.add_argument('--subshards',type=int,default=1)
    args = parser.parse_args()
    policy_path=Path(args.source)/'verification/proof-stream-policy-v2.json'
    if not policy_path.exists():policy_path=Path(args.source)/'verification/proof-stream-policy.json'
    policy=read_json(policy_path) if policy_path.exists() else {}
    workers=policy.get('workers_by_shard',{}).get(str(args.shard),1)
    if args.subshard is None and workers>1:
        assert not args.stop_when and 1<workers<=4
        lock=ROOT/'.runtime/c14-proof-stream-locks'/digest([str(Path(args.out).resolve()),args.shard,args.shards])
        lock.parent.mkdir(parents=True,exist_ok=True)
        with lock.open('a') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            partitioned(args.source,args.out,args.shard,args.shards,workers,policy)
    else:run(args.source,args.out,args.shard,args.shards,args.stop_when,args.early_receipt,args.subshard or 0,args.subshards)
