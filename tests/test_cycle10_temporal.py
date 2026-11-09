"""Event identity, epistemic boundaries, partial history and native-option transport."""
import builtins
import copy
import pytest
from pln_chess.domain import Position
from pln_chess.common import ROOT,read_json
from pln_chess.cycle8.inference import Cycle8Options
from pln_chess.cycle10.temporal import replay,append_events,native_options,replay_game,verify,STANDARD_FEN

EP='7k/5p2/8/6P1/8/8/8/K7 b - - 0 1'
CASTLE='6k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1'


def test_imported_fen_flags_never_create_observed_events_or_initial_trust():
    receipt=replay('7k/8/8/5pP1/8/8/8/K7 w - f6 0 2',[],source='FEN-only')
    assert receipt['schema']=='temporal-transport-v10' and not receipt['events']
    assert not receipt['legacy_evidence']['castling_history_attested']
    assert not any(p['epistemic_type']=='observed-event' for p in receipt['propositions'])
    assert not any(p['predicate']=='LastMoveDoublePawnAdvance' for p in receipt['propositions'])
    assert receipt['historical_legality']=='unverified'


def test_supplied_double_step_has_stable_event_lineage_without_castling_attestation():
    receipt=replay(EP,['f7f5'],source='supplied-game',dependence_group='one-game',model_version='m1',runtime_version='r')
    assert receipt['events'][0]['sequence']==1 and receipt['events'][0]['source']=='supplied-game'
    assert receipt['events'][0]['dependence_group']=='one-game'
    assert any(p['predicate']=='LastMoveDoublePawnAdvance' for p in receipt['propositions'])
    assert not receipt['legacy_evidence']['castling_history_attested']
    other=replay(EP,['f7f5'],source='supplied-game',dependence_group='one-game',model_version='m2',runtime_version='r')
    assert other['id']!=receipt['id'] and other['events']==receipt['events']
    assert verify(receipt)


def test_append_preserves_prefix_ids_and_does_not_restore_moved_rook_rights():
    first=replay(CASTLE,['h1h2','g8f8'],source='supplied',initial_trust='trusted-import')
    second=append_events(first,['h2h1','f8g8'])
    assert second['events'][:2]==first['events'] and second['parent_receipt_id']==first['id']
    assert Position.from_fen(second['resulting_fen']).rights=='Q'
    assert second['legacy_evidence']['castling_history_attested']
    assert any(p['predicate']=='PreviouslyMoved' for p in second['propositions'])


def test_conflicting_expected_state_is_reported_without_fabricated_transition():
    receipt=replay(EP,[],source='contradictory-record',expected_fen='7k/8/8/5pP1/8/8/8/K7 w - f6 0 2')
    assert receipt['status']=='conflicting' and receipt['conflicts']
    assert receipt['resulting_fen']==EP and not receipt['events']
    assert receipt['legacy_evidence']['initial_fen']==EP and receipt['legacy_evidence']['moves']==[]


@pytest.mark.parametrize('kwargs',[{'confidence':float('nan')},{'confidence':True},{'confidence':1.0},
                                  {'initial_trust':'guessed'},{'source':''}])
def test_invalid_trust_and_confidence_are_rejected(kwargs):
    with pytest.raises(ValueError):replay(EP,[],**{'source':'source',**kwargs})


def test_standard_start_attestation_is_explicit_and_scoped():
    unknown=replay(STANDARD_FEN,[],source='unverified-FEN')
    known=replay(STANDARD_FEN,[],source='published-start',initial_trust='attested-standard-start')
    assert not unknown['legacy_evidence']['castling_history_attested']
    assert known['legacy_evidence']['castling_history_attested']
    with pytest.raises(ValueError):replay(EP,[],source='bad-attestation',initial_trust='attested-standard-start')


def test_transport_tampering_is_rejected_and_native_settings_are_preserved():
    receipt=replay(EP,['f7f5'],source='supplied');tampered=copy.deepcopy(receipt)
    tampered['events'][0]['source']='changed'
    with pytest.raises(ValueError):verify(tampered)
    options=native_options(receipt,Cycle8Options(mode='strict',max_native_invocations=123,suppress_families=('temporal',)))
    assert options.mode=='strict' and options.max_native_invocations==123 and options.suppress_families==('temporal',)
    assert options.temporal_mode=='event-backed' and options.temporal_evidence==receipt['legacy_evidence']


def test_long_history_keeps_all_events_and_uses_explicit_legacy_window():
    moves=['b1a3','b8a6','a3b1','a6b8']*130
    receipt=replay(STANDARD_FEN,moves,source='structural-sequence',initial_trust='attested-standard-start')
    assert len(receipt['events'])==520 and len(receipt['legacy_evidence']['moves'])==512
    assert receipt['legacy_window']['omitted_prefix_events']==8
    assert receipt['legacy_evidence']['initial_fen']==receipt['events'][8]['before']
    assert receipt['historical_legality']=='unverified' # Repetition termination is not adjudicated by the structural replayer.


def test_production_replay_does_not_import_reference_chess(monkeypatch):
    original=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('Oracle import during replay')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guarded)
    assert replay(EP,['f7f5'],source='supplied')['events']


def test_external_pgn_prefix_replay_matches_registered_raw_fen():
    path=ROOT/'artifacts/cycle10/datasets/dataset.json'
    if not path.exists():pytest.skip('Registered corpus required')
    data=read_json(path);games={g['id']:g for g in data['games']}
    for source in sorted({g['source_collection'] for g in games.values()}):
        fixture=next(f for f in data['positions'] if f.get('source_collection')==source)
        receipt=replay_game(games[fixture['source_game']],fixture['ply'],'model','runtime')
        assert receipt['resulting_fen']==fixture['fen']
        assert len(receipt['events'])==fixture['ply'] and receipt['model_version']=='model'
