import pytest
from evaluation.cycle14_metrics import counts,clustered_intervals,fit_calibration,calibration_metrics


def row(identifier,label,status='indeterminate',strength=.5,split='test',group=None):
    return dict(id=identifier,label=label,split=split,dependence_group=group or identifier,
        prediction=dict(status=status,contradiction=False,no_preference_supported=False,
            channels={'A':{'raw_stv':{'strength':strength,'confidence':.3}}}))


def test_unknown_reference_is_not_an_incorrect_answer_and_denominators_are_explicit():
    rows=[row('a','A','A-preferred'),row('b','B','A-preferred'),row('c','A'),
        row('d','unknown','B-preferred'),row('e','no-demonstrated-preference')]
    measured=counts(rows)
    assert [measured[k] for k in ('N_all','N_directional','N_answered','N_correct','N_wrong')]==[5,3,2,1,1]
    assert measured['answered_accuracy']==.5 and measured['directional_coverage']==2/3
    assert measured['model_answer_rate_all']==3/5
    assert counts([])['answered_accuracy'] is None
    intervals=clustered_intervals(rows,repetitions=50)
    assert intervals['groups']==5 and intervals==clustered_intervals(rows,repetitions=50)


def test_calibration_is_reserved_separate_and_does_not_normalize_native_channels():
    calibration=[row('a','A',strength=1,split='calibration'),row('b','B',strength=0,split='calibration'),
        row('c','unknown',strength=1,split='calibration')]
    mapping=fit_calibration(calibration)
    assert mapping['bins'][-1]['probability']==2/3 and mapping['bins'][0]['probability']==1/3
    assert mapping['bins'][2]['empty'] and mapping['bins'][2]['probability']==.5
    with pytest.raises(ValueError):fit_calibration([row('test','A')])
    evaluation=[row('d','A','A-preferred',1),row('e','B','B-preferred',0)]
    result=calibration_metrics(evaluation,mapping,repetitions=20)
    assert result['scores']['raw_A_strength']['brier']==0
    assert result['scores']['calibrated']['brier']==pytest.approx(1/9)
    assert result['scores']['raw_A_strength']['log_loss']>0
    assert evaluation[0]['prediction']['channels']['A']['raw_stv']['strength']==1
    assert not result['raw_channels_renormalized']
