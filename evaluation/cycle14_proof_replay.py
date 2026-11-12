"""Replay all unique native traces and verify complete compact archive expansion.

Shared mathematical calculations may be memoized; each evidence occurrence and
all ordered premises remain bound by its archive root and reconstruction hash.
"""
import argparse
from pathlib import Path
from collections import Counter

from pln_chess.common import ROOT,digest,read_json
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle14.proofs import ProofStore
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle13_performance import CountedRuntime
from evaluation.cycle3 import read_gzip
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def replay_archive(path,runtime,session):
    archive=read_gzip(path);objects=archive['objects'];trace_ids=set();native=set();covered=set()
    for identifier,(kind,value) in objects.items():
        if kind!='dict':continue
        fields=dict(value)
        if 'native_expression' in fields:native.add(identifier)
        if 'proof_trace' in fields:
            tag,target=fields['proof_trace'];assert tag=='ref';trace_ids.add(target)
    for identifier in trace_ids:
        kind,items=objects[identifier];assert kind=='list'
        for tag,target in items:assert tag=='ref';covered.add(target)
    assert native<=covered,'Every archived native node must belong to an auditable ordered trace'
    nodes=0;replayed=[]
    with ProofStore() as store:
        root=store.import_archive(archive)
        semantic=store.legacy_digest(root,omit_keys=('execution','incremental'))
        for identifier in sorted(trace_ids):
            trace=store.expand(identifier)
            if not trace:continue
            jobs=[(n['id'],n['native_expression']) for n in trace]
            values=session.batch(jobs)
            assert all(values[n['id']].json()==n['truth_value'] for n in trace)
            nodes+=len(trace);replayed.append(identifier)
    return dict(archive_sha256=sha(path),root=archive['root'],canonical_legacy_sha256=archive['canonical_legacy_sha256'],
        semantic_sha256=semantic,unique_objects=len(objects),unique_native_nodes=len(native),
        trace_objects=len(trace_ids),native_nodes_in_unique_traces=nodes,replayed_trace_ids=replayed,
        full_archive_reconstruction_verified=True,every_archived_native_node_covered=True)


def run(source,out):
    source,out=Path(source).resolve(),Path(out).resolve();runtime=CountedRuntime(timeout=900);runtime.verify()
    session=NativeSession(runtime,max_entries=50000);session.bind(digest(['c14-full-proof-replay',runtime.manifest]))
    selected=read_json(source/'features/selected-generations.json');results=[]
    for kind in ('immediate','temporal'):
        index=read_json(source/'features'/selected[kind]/'index.json')
        for record in index['records']:
            path=source/record['archive'];assert sha(path)==record['archive_sha256']
            target=out/'receipts'/f'{kind}-{record["id"]}.json'
            if target.exists():
                receipt=read_json(target);assert receipt['archive_sha256']==sha(path) and receipt['runtime']==runtime.manifest
                assert receipt['production_code_hash']==production_code_hash()
            else:
                receipt=replay_archive(path,runtime,session)
                assert receipt['semantic_sha256']==record['semantic_sha256']
                receipt.update(id=record['id'],kind=kind,passed=True,runtime=runtime.manifest,production_code_hash=production_code_hash())
                atomic_json(target,receipt)
            results.append(receipt)
            print('C14 NATIVE ARCHIVE REPLAY',kind,record['id'],flush=True)
    atomic_json(out/'verified.json',dict(passed=True,production_code_hash=production_code_hash(),runtime=runtime.manifest,
        archives=len(results),kinds=dict(Counter(r['kind'] for r in results)),unique_archive_native_nodes=sum(r['unique_native_nodes'] for r in results),
        full_archive_expansions_verified=len(results),native_trace_nodes=sum(r['native_nodes_in_unique_traces'] for r in results),
        interpreter_launches_this_invocation=runtime.process_launches,native_arithmetic_cache_hits_this_invocation=session.hits,
        pure_native_operators_executed_this_invocation=session.calls,
        receipts={str((out/'receipts'/f'{r["kind"]}-{r["id"]}.json').relative_to(out)):sha(out/'receipts'/f'{r["kind"]}-{r["id"]}.json') for r in results},
        scope='Complete registered compact native proof corpus, not a sampled proof check. This replays recorded native expressions; separate fresh feature extraction verifies observation construction on selected cases. Cached arithmetic never merges evidence occurrences.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='artifacts/cycle14');p.add_argument('--out',required=True);a=p.parse_args();run(a.source,a.out)
