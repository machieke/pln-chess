"""Offline extraction of native comparison evidence before preference fitting."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def worker(arguments):
    out, row, source_hash = arguments
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.pln import Runtime
    from pln_chess.learning import Model
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.concepts import ForkModel
    from pln_chess.cycle13.api import compare_moves, PreferenceOptions, PreferenceSession
    from pln_chess.cycle12.temporal import semantic_replay
    runtime = Runtime(timeout=600)
    legal = Model.load(ROOT / 'artifacts/cycle12/model/C12-default.json', runtime)
    field = FieldModel.load(ROOT / 'artifacts/cycle11/model/C11-field-trained.json', runtime)
    concept = ConceptModel.load(ROOT / 'artifacts/cycle12/model/C12-concept-trained.json', runtime)
    fork = ForkModel.load(out / 'model/C13-fork-role.json', runtime)
    empty = PreferenceModel(runtime.version)
    options = PreferenceOptions(timeout_seconds=600)
    identity = dict(source_hash=source_hash, row_hash=digest(row), production_code_hash=production_code_hash(),
        runtime=runtime.manifest, legal=legal.version, field=field.version, concept=concept.version, fork=fork.version,
        driver_sha256=sha(__file__))
    path = out / 'features' / (row['id'] + '.json.xz')
    receipt_path = out / 'features' / (row['id'] + '.receipt.json')
    if receipt_path.exists():
        receipt = read_json(receipt_path)
        assert receipt['identity'] == identity, 'Feature source changed; retain this generation and use a new output directory'
        assert receipt['sha256'] == sha(path)
        return receipt
    result = compare_moves(row['fen'], *row['moves'], legal_model=legal, field_model=field,
        concept_model=concept, fork_model=fork, preference_model=empty, options=options,
        runtime=runtime, session=PreferenceSession(runtime), history=row['history'],
        source='cycle13-registered-pair/' + row['id'])
    assert not result['execution']['truncated'], row['id']
    assert result['preference']['status'] == 'indeterminate'
    assert result['preference']['conditional_proof_complete'] is False
    pack(path, result)
    receipt = dict(passed=True, id=row['id'], identity=identity, artifact=str(path.relative_to(out)),
        sha256=sha(path), semantic_sha256=digest(semantic_replay(result)), packet=result['packet'],
        label_independent=True, extraction_model='empty-preference-checkpoint',
        execution=result['execution'])
    write_json(receipt_path, receipt)
    print('NATIVE FEATURES', row['id'], flush=True)
    return receipt


def run(out, workers=2):
    out = Path(out).resolve()
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    data = read_json(out / 'datasets/source-pairs.json')
    expected = data.pop('hash')
    assert digest(data) == expected
    tasks = [(str(out), row, expected) for row in data['records']]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(worker, tasks))
    identity = {r['identity']['production_code_hash'] for r in results}
    assert len(identity) == 1 and len(results) == len(data['records'])
    write_json(out / 'features/index.json', dict(passed=True, source_hash=expected, records=results,
        cases=len(results), production_code_hash=identity.pop(), reference_labels_used=False,
        scope='Native fields, concepts and independent legal beliefs; empty preference model during extraction.'))


def training_records(out, temporal=False):
    """Join offline supervision after extraction; labels never enter inference."""
    out = Path(out)
    source = {r['id']:r for r in read_json(out / 'datasets/source-pairs.json')['records']}
    features = read_json(out / 'features/index.json')
    labels = {r['id']:r for r in read_json(out / 'datasets/reference-labels.json')['records']}
    assert features['source_hash'] == read_json(out / 'datasets/source-pairs.json')['hash']
    records = []
    for receipt in features['records']:
        row, label = source[receipt['id']], labels[receipt['id']]
        records.append(dict(id=row['id'], fen=row['fen'], moves=row['moves'], label=label['label'],
            packet=receipt['packet'], split=row['split'], source_game=row['source_game'], source=row['source'],
            dependence_group=row['dependence_group'], transformation_lineage=row['transformation_lineage'],
            temporal_context=dict(horizon=1, history=row['history']),
            model_versions={key:receipt['identity'][key] for key in ('legal','field','concept','fork')},
            reference_evidence_id=label['evidence_id'], feature_artifact=receipt['artifact'],
            source_record=row))
    if temporal:
        temporal_features = read_json(out / 'temporal/features/index.json')
        temporal_labels = {r['id']:r for r in read_json(out / 'datasets/temporal-labels.json')['records']}
        by_id = {r['id']:r for r in records}
        for receipt in temporal_features['records']:
            label = temporal_labels[receipt['id']]
            root = by_id[label['plan_id']]
            records.append({**root, 'id':receipt['id'], 'label':label['label'], 'packet':receipt['packet'],
                'temporal_context':label['temporal_context'], 'reference_evidence_id':label['evidence_id'],
                'feature_artifact':receipt['artifact']})
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    run(args.out, args.workers)
