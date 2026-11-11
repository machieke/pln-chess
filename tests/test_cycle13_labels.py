"""Scientific label-policy controls; no production reference-engine imports."""
from copy import deepcopy

import chess.engine

from training.cycle13_labels import label, order, semantic_record, score_value


POLICY = dict(preference_margin_cp=80, ambiguous_margin_cp=20)


def evaluations(scores):
    return [dict(candidates=[dict(score=dict(cp=a, mate=None), lowerbound=False, upperbound=False),
                             dict(score=dict(cp=b, mate=None), lowerbound=False, upperbound=False)])
            for a, b in scores]


def test_direction_requires_agreement_and_registered_margin():
    assert label(evaluations([(100, 0), (120, 0)]), POLICY)[0] == 'A'
    assert label(evaluations([(0, 100), (0, 120)]), POLICY)[0] == 'B'
    for scores in [[(100, 0), (0, 120)], [(100, 0), (79, 0)], [(50, 0), (50, 0)]]:
        assert label(evaluations(scores), POLICY)[0] == 'unknown'


def test_tie_missing_output_and_bounds_do_not_force_a_direction():
    assert label(evaluations([(10, 0), (0, 20)]), POLICY)[0] == 'no-demonstrated-preference'
    assert label([], POLICY)[0] == 'unknown'
    rows = evaluations([(100, 0), (120, 0)])
    rows[0]['candidates'][0]['lowerbound'] = True
    assert label(rows, POLICY)[0] == 'unknown'


def test_mate_order_respects_original_actor_and_delaying_loss():
    mate = lambda n: dict(cp=None, mate=n)
    cp = dict(cp=10000, mate=None)
    for a, b in [(mate(2), mate(4)), (mate(-4), mate(-2)), (mate(8), cp), (cp, mate(-8))]:
        assert order(a, b, 80) == 1
        assert order(b, a, 80) == -1
    assert order(mate(3), mate(3), 80) == 0


def test_timing_cannot_change_reference_evidence_identity():
    raw = dict(id='example', label='A', evaluations=evaluations([(100, 0), (120, 0)]))
    first = semantic_record(raw)
    changed = deepcopy(raw)
    changed['evaluations'][0]['elapsed_seconds'] = 999
    changed['evaluations'][1]['candidates'][0]['engine_seconds'] = 5
    assert semantic_record(changed) == first
    changed['evaluations'][1]['candidates'][0]['score']['cp'] = 121
    assert semantic_record(changed)['evidence_id'] != first['evidence_id']
    assert 'evidence_id' not in raw


def test_terminal_mate_zero_preserves_winner_in_endpoint_labels():
    won=score_value(chess.engine.MateGiven)
    lost=score_value(chess.engine.Mate(0))
    positive=score_value(chess.engine.Cp(10000))
    assert won['mate']==lost['mate']==0
    assert won['mate_outcome']=='win' and lost['mate_outcome']=='loss'
    assert order(won,positive,80)==1 and order(positive,lost,80)==1
    assert order(won,lost,80)==1 and order(lost,won,80)==-1
