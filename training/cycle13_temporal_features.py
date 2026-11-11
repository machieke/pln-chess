"""Gated native replay of the independently registered supplied branches."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha
from evaluation.cycle7_io import pack


def worker(arguments):
    out, plan, source_hash = arguments
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.pln import Runtime
    from pln_chess.learning import Model
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.concepts import ForkModel
    from pln_chess.cycle13.api import PreferenceOptions, PreferenceSession
    from pln_chess.cycle13.temporal import analyze_continuations
    from pln_chess.cycle12.temporal import semantic_replay
    runtime = Runtime(timeout=900)
    legal = Model.load(ROOT / 'artifacts/cycle12/model/C12-default.json', runtime)
    field = FieldModel.load(ROOT / 'artifacts/cycle11/model/C11-field-trained.json', runtime)
    concept = ConceptModel.load(ROOT / 'artifacts/cycle12/model/C12-concept-trained.json', runtime)
    fork = ForkModel.load(out / 'model/C13-fork-role.json', runtime)
    empty = PreferenceModel(runtime.version)
    identity = dict(source_hash=source_hash, plan_hash=digest(plan), production_code_hash=production_code_hash(),
        runtime=runtime.manifest, legal=legal.version, field=field.version, concept=concept.version, fork=fork.version,
        driver_sha256=sha(__file__))
    path = out / 'temporal/features' / (plan['id'] + '.json.xz')
    receipt_path = out / 'temporal/features' / (plan['id'] + '.receipt.json')
    if receipt_path.exists():
        receipt = read_json(receipt_path)
        assert receipt['identity'] == identity, 'Retain this feature generation before changing source'
        assert receipt['sha256'] == sha(path)
        return receipt
    result = analyze_continuations(plan['fen'], {k:[v] for k,v in plan['branches'].items()},
        legal_model=legal, field_model=field, concept_model=concept, fork_model=fork,
        preference_model=empty, options=PreferenceOptions(timeout_seconds=900), runtime=runtime,
        session=PreferenceSession(runtime), history=plan['history'], horizons=(2,3),
        source='cycle13-registered-pair/' + plan['id'], selection_provenance=plan['response_selection'])
    assert not result['execution']['truncated']
    assert result['unexamined_responses']
    assert {row['horizon'] for row in result['comparisons']} == {2,3}
    assert all(row['preference']['status'] == 'indeterminate' for row in result['comparisons'])
    pack(path, result)
    receipt = dict(passed=True, plan_id=plan['id'], identity=identity, artifact=str(path.relative_to(out)),
        sha256=sha(path), semantic_sha256=digest(semantic_replay(result)), label_independent=True,
        comparisons=[dict(id=plan['id'] + '-ply' + str(row['horizon']), horizon=row['horizon'], packet=row['packet'])
            for row in result['comparisons']], execution=result['execution'])
    write_json(receipt_path, receipt)
    print('TEMPORAL NATIVE FEATURES', plan['id'], flush=True)
    return receipt


def run(out, workers=2):
    out = Path(out).resolve()
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    data = read_json(out / 'datasets/temporal-plans.json')
    expected = data.pop('hash')
    assert digest(data) == expected
    with ProcessPoolExecutor(max_workers=workers) as pool:
        receipts = list(pool.map(worker, [(str(out), row, expected) for row in data['records']]))
    rows = [{**comparison, 'plan_id':receipt['plan_id'], 'artifact':receipt['artifact'], 'identity':receipt['identity']}
        for receipt in receipts for comparison in receipt['comparisons']]
    assert len(rows) == len(receipts) * 2
    write_json(out / 'temporal/features/index.json', dict(passed=True, plan_hash=expected,
        source_games=len(receipts), comparisons=len(rows), records=rows, receipts=receipts,
        labels_used=False, response_search_in_production=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    run(args.out, args.workers)
