"""Reproduce all 27 robust-history controls under the frozen promotion candidate."""
import argparse
import copy
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves, Cycle8Options
from pln_chess.pln import Runtime
from evaluation.cycle7_io import pack


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle11.temporal import replay_claims, append_claims, native_options, verify
    runtime = Runtime(timeout=180)
    model = PromotionModel.load(ROOT / 'artifacts/cycle11/model/C11-special-local.json', runtime)
    controls = read_json(ROOT / 'artifacts/cycle11/datasets/temporal-controls.json')
    rows = []
    for case in controls['cases']:
        supplied = {**case['input'], 'model_version': model.version, 'runtime_version': runtime.version}
        receipt = replay_claims(**supplied)
        assert verify(receipt) and replay_claims(**supplied) == receipt
        assert receipt['native_available'] == case['expected_native_available'], case['id']
        options = native_options(receipt, Cycle8Options(timeout_seconds=180, max_native_invocations=100000),
            model_version=model.version, runtime_version=runtime.version)
        assert options.temporal_mode == ('event-backed' if receipt['native_available'] else 'fen-only')
        if 'expected_confidence' in case:
            assert receipt['legacy_transport']['input']['confidence'] == case['expected_confidence']
        # The reported state remains usable when history has a gap. Its FEN
        # metadata alone is never promoted to an observed predecessor.
        fen = supplied.get('expected_fen') or receipt['resulting_fen']
        position = Position.from_fen(fen)
        notation = case.get('candidate', 'e1g1')
        move = find_move(position, notation)
        native = None
        if move is not None:
            result = infer_moves(position, model, options, runtime, [move])
            native = dict(candidate=result['candidates'][0],
                native_proof_id=digest(result['candidates'][0]['proof_trace']),
                execution={k: result[k] for k in ('native_invocations', 'scheduled_invocations', 'elapsed_seconds', 'truncated', 'error')})
        rows.append(dict(case=case, receipt=receipt, native=native, passed=True))
        print('Temporal control', case['id'], receipt['status'], flush=True)
    indexed = {r['case']['id']: r for r in rows}
    base = indexed['complete-observations']['receipt']
    invariant = ('reverse-delivery', 'shuffled-delivery', 'identical-duplicate', 'all-events-duplicated')
    for name in invariant:
        other = indexed[name]['receipt']
        assert other['semantic_id'] == base['semantic_id']
        assert other['legacy_transport'] == base['legacy_transport']
        assert other['id'] != base['id'], 'Delivery audit is retained even when semantic evidence is identical'
        assert indexed[name]['native']['candidate']['raw_stv'] == indexed['complete-observations']['native']['candidate']['raw_stv']
        assert indexed[name]['native']['native_proof_id'] == indexed['complete-observations']['native']['native_proof_id']
    appended = append_claims(base, [dict(sequence=2, move='d7d5', source='later-observer',
        dependence_group='later-observer', epistemic_type='observed-event', confidence=.99)])
    assert verify(appended) and not appended['native_available']
    assert appended['input']['claims'][:len(base['input']['claims'])] == base['input']['claims']
    assert appended['parent_receipt_id'] == base['id']
    rejected = []
    corrupted = copy.deepcopy(base)
    corrupted['native_available'] = False
    corrupted['id'] = digest({k:v for k,v in corrupted.items() if k != 'id'})
    for name, action in (
        ('semantic-tamper-with-recomputed-digest', lambda: verify(corrupted)),
        ('different-model', lambda: native_options(base, model_version='different-model', runtime_version=runtime.version)),
        ('different-runtime', lambda: native_options(base, model_version=model.version, runtime_version='different-runtime')),
    ):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    from scripts.cycle8_controls import negatives
    negative_results = negatives(model, runtime, out / 'legal/negative-controls')
    assert negative_results['cases'] == negative_results['intact_negative'] == negative_results['removed_unknown'] == 287
    assert not negative_results['failures']
    write_json(out / 'legal/negative-controls/verified.json', dict(passed=True, **negative_results))
    pack(out / 'legal/temporal/controls.json.xz', dict(cases=rows, append_conflict=appended, original=base))
    write_json(out / 'legal/temporal/summary.json', dict(passed=True, cases=len(rows),
        native_available=sum(r['receipt']['native_available'] for r in rows),
        withheld=sum(not r['receipt']['native_available'] for r in rows),
        conflicts={r['case']['id']: r['receipt']['conflicts'] for r in rows if r['receipt']['conflicts']},
        order_and_duplicate_native_proof_parity=list(invariant),
        append_preserves_earlier_claims=True, integrity_rejections=rejected,
        dataset_hash=controls['hash'], model_version=model.version, runtime_version=runtime.version,
        confidence_policy='Minimum explicitly supplied observation confidence; a conservative trust selection, not a probability combination.',
        limits='Structural history is not proof of historical legal play. Conflicting and incomplete histories are withheld from native eligibility; FEN-only inference remains available.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
