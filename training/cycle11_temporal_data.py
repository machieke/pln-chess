"""Predeclared temporal claim perturbations; no inference outcomes selected."""
import argparse
import copy
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.cycle10.temporal import replay, STANDARD_FEN


def claim(sequence, move, source='controlled-observer', group='controlled-history', kind='observed-event', confidence=.99, **extra):
    return dict(sequence=sequence, move=move, source=source, dependence_group=group,
                epistemic_type=kind, confidence=confidence, **extra)


def generate(out):
    out = Path(out)
    cases = []
    moves = ['e2e4', 'e7e5', 'g1f3', 'b8c6']
    full = replay(STANDARD_FEN, moves, source='controlled-observer', initial_trust='attested-standard-start')
    base = dict(initial_fen=STANDARD_FEN, claims=[claim(i, move) for i, move in enumerate(moves, 1)],
        source='cycle11-control', initial_trust='attested-standard-start', expected_fen=full['resulting_fen'],
        expected_events=len(moves), complete=True)

    def add(name, supplied, native, expectation, **extra):
        cases.append(dict(id=name, input=copy.deepcopy(supplied), expected_native_available=native,
            expectation=expectation, **extra))

    add('complete-observations', base, True, 'Exact ordered structural replay')
    add('reverse-delivery', {**base, 'claims': list(reversed(base['claims']))}, True, 'Same semantic replay, explicitly different delivery order')
    add('shuffled-delivery', {**base, 'claims': [base['claims'][i] for i in (2, 0, 3, 1)]}, True, 'Same semantic replay')
    add('identical-duplicate', {**base, 'claims': base['claims']+[base['claims'][1]]}, True, 'Duplicate retained in delivery audit, counted once')
    add('all-events-duplicated', {**base, 'claims': base['claims']*2}, True, 'No independent evidence increase')
    add('corroborating-source', {**base, 'claims': base['claims']+[claim(2, 'e7e5', source='second-observer', group='second-source')]},
        True, 'Consistent source claims remain distinct, without confidence aggregation')
    aliased = copy.deepcopy(base['claims'])
    aliased[1]['external_event_id'] = 'publisher-event-two'
    add('conflicting-provenance-identifier', {**base, 'claims': aliased+[claim(3, 'g1f3', external_event_id='publisher-event-two')]},
        False, 'The same source event identifier cannot silently refer to two different transitions')
    add('missing-first-event', {**base, 'claims': base['claims'][1:]}, False, 'Missing sequence 1 is explicit; no fabricated predecessor')
    add('missing-middle-event', {**base, 'claims': [base['claims'][i] for i in (0, 2, 3)]}, False, 'Stop trusted contiguous replay at the gap')
    add('missing-final-event', {**base, 'claims': base['claims'][:-1]}, False, 'Expected event count prevents silently accepting a truncated delivery')
    add('contradictory-later-claim', {**base, 'claims': base['claims']+[claim(2, 'd7d5', source='second-observer')]}, False, 'Earlier evidence and later contradiction both remain')
    add('contradictory-earlier-delivery', {**base, 'claims': [claim(2, 'd7d5', source='second-observer')]+base['claims']}, False, 'Conflict outcome is independent of arrival order')
    altered = copy.deepcopy(base['claims'])
    altered[1]['before_fen'] = full['resulting_fen']
    add('reported-before-state-conflict', {**base, 'claims': altered}, False, 'A conflicting event state claim is not ignored')
    altered = copy.deepcopy(base['claims'])
    altered[1]['after_fen'] = STANDARD_FEN
    add('reported-after-state-conflict', {**base, 'claims': altered}, False, 'Structural consequence conflicts with supplied after-state')
    add('expected-final-state-conflict', {**base, 'expected_fen': STANDARD_FEN}, False, 'Conflicting final state is explicit')
    metadata = dict(fen=STANDARD_FEN.replace('KQkq', '-'), source='conflicting-import', dependence_group='metadata-source', epistemic_type='trusted-metadata', confidence=.99)
    add('conflicting-trusted-metadata', {**base, 'metadata_claims': [metadata]}, False, 'Conflicting imported FEN rights do not erase the initial claim')
    metadata['fen'] = STANDARD_FEN
    add('matching-trusted-metadata', {**base, 'metadata_claims': [metadata]}, True, 'Matching metadata is retained without extra probability weight')
    altered = copy.deepcopy(base['claims'])
    for item in altered:
        item['epistemic_type'] = 'inferred-history'
    add('inferred-history-only', {**base, 'claims': altered}, False, 'Inferred structural history is not promoted to direct observations')
    altered = copy.deepcopy(base['claims'])
    altered[-1]['epistemic_type'] = 'unknown-history'
    add('unknown-final-event', {**base, 'claims': altered}, False, 'An unknown event cannot establish a trusted history')
    altered = copy.deepcopy(base['claims'])
    altered[-1]['confidence'] = .4
    add('lower-confidence-event', {**base, 'claims': altered}, True, 'The exported legacy trust policy cannot exceed the weakest supplied confidence', expected_confidence=.4)
    altered[-1]['confidence'] = 0.0
    add('zero-confidence-event', {**base, 'claims': altered}, False, 'Zero-confidence observation does not establish eligibility')
    # Partial PGN / SetUp histories have a known local start, unknown earlier
    # rights history, and an observed immediate predecessor for en passant.
    initial = '7k/5p2/8/6P1/8/8/8/K7 b - - 0 1'
    ep = replay(initial, ['f7f5'], source='partial-PGN')
    partial = dict(initial_fen=initial, claims=[claim(1, 'f7f5', source='partial-PGN')],
        source='partial-PGN', initial_trust='unknown', expected_fen=ep['resulting_fen'], expected_events=1, complete=False)
    add('partial-pgn-observed-predecessor', partial, True, 'Fresh local EP predecessor is observed; earlier castling history stays unknown', candidate='g5f6')
    add('fen-only-metadata', dict(initial_fen=ep['resulting_fen'], claims=[], source='FEN-import', initial_trust='unknown', complete=False),
        False, 'FEN EP metadata alone is not an observed predecessor', candidate='g5f6')
    add('trusted-fen-metadata', dict(initial_fen='6k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1', claims=[],
        source='trusted-import', initial_trust='trusted-import', complete=False), True,
        'Explicit imported rights trust is preserved; no observed EP event is invented', candidate='e1g1')
    rook_initial = '6k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1'
    rook_moves = ['h1h2', 'g8f8', 'h2h1', 'f8g8']
    rook_history = replay(rook_initial, rook_moves, source='rook-return', initial_trust='trusted-import')
    add('rook-return-retains-lost-right', dict(initial_fen=rook_initial, claims=[claim(i, move, source='rook-return') for i, move in enumerate(rook_moves, 1)],
        source='rook-return', initial_trust='trusted-import', expected_fen=rook_history['resulting_fen'], expected_events=4), True,
        'Returning the rook does not restore its lost castling right', candidate='e1g1')
    corpus = read_json(ROOT / 'artifacts/cycle10/datasets/dataset.json')
    fixture = next(f for f in corpus['positions'] if f['id'] == 'c10-position-00861')
    game = next(g for g in corpus['games'] if g['id'] == fixture['source_game'])
    actual = dict(initial_fen=game['initial_fen'], claims=[claim(i, move, source=game['source_collection'], group=game['id'])
        for i, move in enumerate(game['moves'][:fixture['ply']], 1)], source=game['source_collection']+'/'+game['id'],
        initial_trust='attested-standard-start', expected_fen=fixture['fen'], expected_events=fixture['ply'], complete=False)
    add('published-prefix', actual, True, 'Actual published prefix reproduces the original en-passant state', candidate='d5e6', source_game=game['id'])
    add('published-prefix-missing-event', {**actual, 'claims': actual['claims'][:9]+actual['claims'][10:]}, False,
        'A missing published event is surfaced even when final FEN metadata is supplied', candidate='d5e6', source_game=game['id'])
    payload = dict(schema='temporal-claim-controls-v11', cases=cases, chosen_before_inference=True,
        scope='Declared claim perturbations; complete source history remains preserved and no contradictory claim is silently replaced.')
    payload['hash'] = digest(payload)
    write_json(out / 'datasets/temporal-controls.json', payload)
    print('Temporal controls', len(cases), payload['hash'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    generate(parser.parse_args().out)
