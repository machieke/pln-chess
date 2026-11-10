"""Deterministic claim replay without manufactured historical certainty."""
import copy

import pytest

from pln_chess.common import digest
from pln_chess.cycle10.temporal import STANDARD_FEN
from pln_chess.cycle11.temporal import replay_claims, append_claims, native_options, verify


def claim(sequence, move, **extra):
    return dict(sequence=sequence,move=move,source='unit-observer',dependence_group='unit-history',
        epistemic_type='observed-event',confidence=.99,**extra)


def supplied():
    return dict(initial_fen=STANDARD_FEN,claims=[claim(1,'e2e4'),claim(2,'e7e5'),claim(3,'g1f3')],
        source='unit-replay',initial_trust='attested-standard-start',expected_events=3,
        model_version='test-model',runtime_version='test-runtime')


def test_order_and_duplicates_preserve_semantics_not_delivery_audit():
    data=supplied()
    before=replay_claims(**data)
    other=replay_claims(**{**data,'claims':list(reversed(data['claims']))+[data['claims'][1]]})
    assert verify(before) and verify(other)
    assert before['semantic_id']==other['semantic_id'] and before['id']!=other['id']
    assert before['legacy_transport']==other['legacy_transport']
    assert len(other['input']['claims'])==4


@pytest.mark.parametrize('missing',[0,1,2])
def test_gap_or_expected_truncation_withholds_eligibility(missing):
    data=supplied()
    data['claims'].pop(missing)
    result=replay_claims(**data)
    assert not result['native_available'] and result['gaps']
    assert native_options(result).temporal_mode=='fen-only'


def test_later_conflict_keeps_old_claim_and_parent():
    original=replay_claims(**supplied())
    snapshot=copy.deepcopy(original)
    contradiction=claim(2,'d7d5')
    result=append_claims(original,[contradiction])
    assert original==snapshot and result['parent_receipt_id']==original['id']
    assert result['input']['claims'][:3]==original['input']['claims']
    assert result['input']['claims'][-1]==contradiction
    assert not result['native_available'] and result['conflicts'] and verify(result)


def test_conflict_detection_is_delivery_order_independent():
    data=supplied()
    claims=data['claims']+[claim(2,'d7d5')]
    a=replay_claims(**{**data,'claims':claims})
    b=replay_claims(**{**data,'claims':list(reversed(claims))})
    assert a['semantic_id']==b['semantic_id'] and a['conflicts']==b['conflicts']


@pytest.mark.parametrize('kind',['inferred-history','unknown-history'])
def test_structurally_replayable_inferred_claim_is_not_direct_observation(kind):
    data=supplied()
    data['claims'][1]['epistemic_type']=kind
    result=replay_claims(**data)
    assert not result['native_available'] and not result['conflicts']
    assert result['resulting_fen']==replay_claims(**supplied())['resulting_fen']


def test_source_event_identifier_cannot_alias_two_transitions():
    data=supplied()
    data['claims'][0]['external_event_id']='publisher-1'
    data['claims'][1]['external_event_id']='publisher-1'
    result=replay_claims(**data)
    assert not result['native_available'] and result['conflicts']


def test_lower_confidence_is_selected_without_duplicate_bonus():
    data=supplied()
    data['claims'][1]['confidence']=.4
    data['claims']*=2
    result=replay_claims(**data)
    assert result['native_available']
    assert result['legacy_transport']['input']['confidence']==.4


def test_zero_confidence_cannot_establish_native_eligibility():
    data=supplied()
    data['claims'][1]['confidence']=0
    assert not replay_claims(**data)['native_available']


def test_supplied_confidence_is_not_capped_by_empty_history_default():
    data=supplied()
    for record in data['claims']:record['confidence']=.999
    result=replay_claims(**data)
    assert result['native_available']
    assert result['legacy_transport']['input']['confidence']==.999


def test_fen_ep_flag_does_not_create_observed_predecessor():
    result=replay_claims('7k/8/8/5pP1/8/8/8/K7 w - f6 0 2',[],source='FEN-only')
    assert not result['native_available']


def test_partial_history_retains_observed_local_predecessor():
    result=replay_claims('7k/5p2/8/6P1/8/8/8/K7 b - - 0 1',[claim(1,'f7f5')],source='partial-PGN')
    assert result['native_available'] and result['legacy_transport']['input']['initial_trust']=='unknown'
    assert not result['legacy_transport']['legacy_evidence']['castling_history_attested']


def test_conflicting_metadata_is_not_silently_overwritten():
    data=supplied()
    data['metadata_claims']=[dict(fen=STANDARD_FEN.replace('KQkq','-'),source='other-import',
        dependence_group='other-metadata',epistemic_type='trusted-metadata',confidence=.99)]
    result=replay_claims(**data)
    assert not result['native_available'] and result['conflicts']
    assert result['input']['metadata_claims']==data['metadata_claims']


@pytest.mark.parametrize('field',['before_fen','after_fen'])
def test_reported_event_state_must_match_structural_replay(field):
    data=supplied()
    data['claims'][1][field]=STANDARD_FEN
    result=replay_claims(**data)
    assert not result['native_available'] and result['conflicts']


def test_semantic_tamper_rejected_even_with_recomputed_digest():
    receipt=replay_claims(**supplied())
    receipt['native_available']=False
    receipt['id']=digest({key:value for key,value in receipt.items() if key!='id'})
    with pytest.raises(ValueError):verify(receipt)


def test_wrong_model_or_runtime_binding_rejected():
    receipt=replay_claims(**supplied())
    with pytest.raises(ValueError):native_options(receipt,model_version='wrong')
    with pytest.raises(ValueError):native_options(receipt,runtime_version='wrong')


@pytest.mark.parametrize('change',[dict(sequence=0),dict(sequence=True),dict(sequence=4097),dict(confidence=float('nan')),
    dict(confidence=1),dict(confidence=-.1),dict(epistemic_type='verified-legal'),dict(source=''),dict(move='bad')])
def test_invalid_claims_rejected_or_recorded_as_explicit_conflict(change):
    data=supplied()
    data['claims'][0].update(change)
    if change==dict(move='bad'):
        receipt=replay_claims(**data)
        assert not receipt['native_available'] and receipt['conflicts']
    else:
        with pytest.raises(ValueError):replay_claims(**data)
