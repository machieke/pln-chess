"""Evaluation contracts: abstention, unknown labels and correlated uncertainty."""
import pytest
from evaluation.cycle13_metrics import metrics,calibration,bootstrap


def row(label,status,strength=.8,group='one'):
    return dict(label=label,dependence_group=group,result=dict(status=status,
        channels={s:dict(raw_stv=dict(strength=strength if s=='A' else 1-strength,confidence=.5)) for s in ('A','B')},
        conditional_proof_complete=True,joint_proof_complete=False))


def test_unknown_teacher_labels_cannot_inflate_directional_accuracy():
    rows=[row('A','A-preferred'),row('B','indeterminate',group='two'),row('unknown','A-preferred',group='three')]
    actual=metrics(rows)
    assert actual['pairwise_accuracy']==1 and actual['accuracy_including_abstention']==.5
    assert actual['directional_coverage']==.5 and actual['directional_answers_without_resolved_reference']==1
    assert actual['complete_joint_strategic_proofs']==0


def test_a_direction_on_an_ambiguous_pair_is_a_false_positive():
    actual=metrics([row('A','A-preferred'),row('no-demonstrated-preference','A-preferred',group='two')])
    assert actual['precision']['A']==.5 and actual['unsupported_direction_on_ambiguous']==1
    assert actual['correctly_supported_no_preference']==0


def test_empty_and_all_abstained_panels_have_no_invented_accuracy():
    assert metrics([])['pairwise_accuracy'] is None
    assert metrics([row('A','incomplete')])['pairwise_accuracy'] is None
    assert calibration([])['brier_score'] is None


def test_calibration_uses_strength_and_excludes_unresolved_references():
    result=calibration([row('A','A-preferred',.8),row('B','B-preferred',.2,'two'),row('unknown','A-preferred',1.,'three')])
    assert result['directional_examples']==2 and result['brier_score']==pytest.approx(.04)
    assert result['expected_calibration_error']==pytest.approx(.2)
    assert not result['raw_confidence_is_probability'] and not result['calibration_changes_inference']


def test_cluster_bootstrap_keeps_correlated_examples_together():
    rows=[row('A','A-preferred',group='same'),row('B','A-preferred',group='same')]
    result=bootstrap(rows,100)
    assert result['groups']==1
    assert result['intervals']['pairwise_accuracy']['lower']==result['intervals']['pairwise_accuracy']['upper']==.5
    assert result==bootstrap(rows,100)
