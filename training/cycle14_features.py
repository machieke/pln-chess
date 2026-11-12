"""Native evidence extraction into standalone compact proof archives."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from pln_chess.common import ROOT,digest,read_json
from scripts.cycle9_baseline import sha
from evaluation.cycle7_io import pack
from training.cycle14_labels import atomic_json


def source_closure():
    paths=sorted((ROOT/'src').rglob('*.py'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def worker(task):
    out,row,source_hash,generation,kind,closure=task;out=Path(out)
    assert source_closure()==closure,'Extract in a frozen source checkout; do not mix source generations'
    from pln_chess.pln import Runtime
    from evaluation.cycle14_profile import models
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.api import PreferenceOptions,PreferenceSession
    from pln_chess.cycle14.api import compare_moves
    from pln_chess.cycle14.temporal import analyze_continuations
    from pln_chess.cycle14.proofs import ProofStore
    runtime=Runtime(timeout=900);loaded=models(runtime);loaded['preference_model']=PreferenceModel(runtime.version)
    options=PreferenceOptions(timeout_seconds=900)
    identity=dict(source_hash=source_hash,row_hash=digest(row),source_closure_sha256=digest(closure),
        runtime=runtime.manifest,model_versions={k:m.version for k,m in loaded.items()},driver_sha256=sha(__file__),kind=kind)
    base=out/'features'/generation;path=base/'receipts'/(row['id']+'.json');archive_path=base/'archives'/(row['id']+'.json.xz')
    if path.exists():
        receipt=read_json(path)
        assert receipt['identity']==identity,'Feature generation changed; preserve previous output'
        assert receipt['archive_sha256']==sha(archive_path)
        return receipt
    with ProofStore() as store:
        arguments=dict(**loaded,runtime=runtime,options=options,session=PreferenceSession(runtime),
            history=row['history'],source='cycle14-registered-pair/'+row['id'],store=store,_prepared=True)
        if kind=='immediate':
            result=compare_moves(row['fen'],*row['moves'],**arguments)
            observations=[dict(id=row['id'],horizon=1,packet=result['role_packet'])]
        else:
            result=analyze_continuations(row['fen'],{s:[line] for s,line in row['branches'].items()},
                **arguments,horizons=(2,3),selection_provenance=row['response_selection'])
            observations=[dict(id=row['id']+f'-ply{h}',horizon=h,packet=p) for h,p in zip((2,3),result['role_packets'])]
        assert result['summary']['execution']['error'] is None, result['summary']['execution']
        semantic=store.legacy_digest(result['root'],omit_keys=('execution','incremental'))
        archive=store.archive(result['root']);pack(archive_path,archive)
        receipt=dict(passed=True,id=row['id'],identity=identity,observations=observations,
            archive=str(archive_path.relative_to(out)),archive_sha256=sha(archive_path),
            proof_root=result['root'].id,semantic_sha256=semantic,store_census=store.census(),
            execution=result['summary']['execution'],label_independent=True,reference_labels_used=False,
            complete=all(o['packet']['base']['complete'] for o in observations),
            extraction_model='frozen-fields-and-concepts; empty C13 preference checkpoint',
            legacy_response_materialized=False)
    atomic_json(path,receipt)
    print('C14 COMPACT FEATURES',kind,row['id'],receipt['complete'],flush=True)
    return receipt


def run(out,generation,workers=4,kind='immediate'):
    out=Path(out).resolve();data=read_json(out/'datasets'/('source-pairs.json' if kind=='immediate' else 'temporal-plans.json'))
    source_hash=data['hash'];closure=source_closure()
    atomic_json(out/'features'/generation/'source-closure.json',closure)
    tasks=[(str(out),row,source_hash,generation,kind,closure) for row in data['records']]
    with ProcessPoolExecutor(max_workers=workers) as pool:receipts=list(pool.map(worker,tasks))
    payload=dict(passed=True,schema='c14-native-compact-features-v1',source_hash=source_hash,
        source_closure_sha256=digest(closure),records=receipts,cases=len(receipts),
        comparisons=sum(len(r['observations']) for r in receipts),reference_labels_used=False,
        archive_contract='Standalone content-addressed objects; exact legacy proof reconstruction on explicit demand.')
    atomic_json(out/'features'/generation/'index.json',payload)


def training_records(out,*,temporal=False,labels='revised'):
    out=Path(out);sources={r['id']:r for r in read_json(out/'datasets/source-pairs.json')['records']}
    latest={r['id']:r for r in read_json(out/'labels/immediate-g1/index.json')['records']}
    old={r['id']:r for r in read_json(ROOT/'artifacts/cycle13/datasets/reference-labels.json')['records']}
    indexes=[read_json(out/'features/immediate-g1/index.json')]
    plans={}
    if temporal:
        indexes.append(read_json(out/'features/temporal-g1/index.json'))
        latest.update({r['id']:r for r in read_json(out/'labels/temporal-g1/index.json')['records']})
        old.update({r['id']:r for r in read_json(ROOT/'artifacts/cycle13/datasets/temporal-labels.json')['records']})
        plans={r['id']:r for r in read_json(out/'datasets/temporal-plans.json')['records']}
    result=[]
    for index in indexes:
        for receipt in index['records']:
            root=sources[receipt['id']]
            for observation in receipt['observations']:
                identifier=observation['id'];label=old.get(identifier) if labels=='old' else latest.get(identifier)
                if label is None:continue
                horizon=observation['horizon'];context=dict(horizon=horizon,history=root['history'])
                if horizon>1:context['branches']={s:line[:horizon] for s,line in plans[root['id']]['branches'].items()}
                result.append(dict(id=identifier,fen=root['fen'],moves=root['moves'],label=label['label'],packet=observation['packet'],
                    split=root['split'],source_game=root['source_game'],source=root['source'],dependence_group=root['dependence_group'],
                    transformation_lineage=root['transformation_lineage'],temporal_context=context,
                    model_versions=receipt['identity']['model_versions'],reference_evidence_id=label['evidence_id'],
                    label_generation='historical-c13' if labels=='old' else label['generation'],
                    feature_artifact=receipt['archive'],source_record=root))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    parser.add_argument('--generation',default='immediate-g1');parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--kind',choices=('immediate','temporal'),default='immediate');args=parser.parse_args()
    run(args.out,args.generation,args.workers,args.kind)
