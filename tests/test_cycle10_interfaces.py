"""External diagnostics stay bounded, source-bound and separate from inference."""
from copy import deepcopy
import hashlib
import json
from types import SimpleNamespace
import pytest
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle10.acceptance import CHECKS,accepted_model
from pln_chess.cycle10.diagnostics import report,failure_proof,temporal_control,calibrated_diagnostic
from pln_chess.cycle10.temporal import replay,verify


def receipt():
    return dict(passed=True,all_required_checks_executed=True,checks={k:True for k in CHECKS},new_learning_promoted=False,
        accepted_model_versions=['known'],accepted_legacy_model_versions=['legacy'],runtime_version='runtime',
        production_code_hash=production_code_hash(),registration_hash=digest(read_json(ROOT/'configs/cycle10.json')),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9)})


def test_acceptance_rejects_missing_checks_stale_sources_runtime_and_new_learning(tmp_path,monkeypatch):
    monkeypatch.setenv('C10_OUT',str(tmp_path));model=SimpleNamespace(version='known',runtime_version='runtime')
    assert not accepted_model(model)
    valid=receipt();write_json(tmp_path/'acceptance.json',valid);assert accepted_model(model)
    assert not accepted_model(SimpleNamespace(version='experimental',runtime_version='runtime'))
    assert accepted_model(SimpleNamespace(version='legacy',runtime_version='runtime'),legacy=True)
    for changed in ({'production_code_hash':'wrong'},{'runtime_version':'wrong'},{'new_learning_promoted':True},
                    {'registration_hash':'wrong'},{'all_required_checks_executed':False},{'legacy_registrations':{}},
                    *({'checks':{**valid['checks'],key:False}} for key in CHECKS)):
        write_json(tmp_path/'acceptance.json',{**valid,**changed});assert not accepted_model(model)


def test_explicit_older_output_override_stays_fail_closed(tmp_path,monkeypatch):
    from pln_chess.cycle9.acceptance import accepted_model as previous
    monkeypatch.setenv('C10_OUT',str(tmp_path));write_json(tmp_path/'acceptance.json',receipt())
    monkeypatch.setenv('C9_OUT',str(tmp_path/'missing'))
    assert not previous(SimpleNamespace(version='known',runtime_version='runtime'))


@pytest.mark.parametrize('section,arm',[('../sources/manifest','frozen'),('summary','../small'),('unknown','frozen')])
def test_external_report_selectors_cannot_open_arbitrary_paths(section,arm):
    with pytest.raises(ValueError):report(section,arm)


def test_missing_reports_are_explicit_and_case_indices_are_bounded(tmp_path,monkeypatch):
    monkeypatch.setenv('C10_OUT',str(tmp_path));assert report()['available'] is False
    with pytest.raises(ValueError):failure_proof(-1)
    with pytest.raises(ValueError):failure_proof(0,'../../')
    with pytest.raises(ValueError):temporal_control(True)


def test_external_calibration_never_modifies_candidate_and_rejects_adapted_identity(tmp_path,monkeypatch):
    monkeypatch.setenv('C10_OUT',str(tmp_path));mapping=[dict(probability=.2,n=10,legal=2)]*10
    data=dict(model_version='known',frozen_mapping={'complete':mapping,'in-board':mapping},
        external_mapping={'complete':mapping,'in-board':mapping},fit_split='external-calibration',fit_games=24,dataset_hash='dataset')
    path=tmp_path/'calibration/results.json';write_json(path,data)
    write_json(tmp_path/'acceptance.json',{**receipt(),'calibration_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    candidate=dict(model_version='known',runtime_version='runtime',mode='operational',classification='unknown',
        raw_stv=dict(strength=.5,confidence=.0),observations={'context':{'destination_exists':True}})
    original=deepcopy(candidate);result=calibrated_diagnostic(candidate)
    assert candidate==original and result['available'] and not result['native'] and not result['changes_classification']
    assert result['population']=='in-board'
    assert not calibrated_diagnostic({**candidate,'model_version':'adapted'})['available']
    assert not calibrated_diagnostic({**candidate,'mode':'strict'})['available']
    assert not calibrated_diagnostic({**candidate,'classification':'incomplete'})['available']
    assert not calibrated_diagnostic({**candidate,'temporal_evidence':{'mode':'event-backed'}})['available']
    write_json(path,{**data,'fit_games':999});assert not calibrated_diagnostic(candidate)['available']


def test_temporal_receipt_survives_json_and_retains_nonlegal_structural_scope():
    # Structural replay can represent a rook jumping over a pawn, without certifying it.
    import chess
    fen='7k/8/8/8/8/8/2RP4/2K5 w - - 0 1'
    assert chess.Move.from_uci('c2e2') not in chess.Board(fen).legal_moves
    history=replay(fen,['c2e2'],source='supplied-unverified-sequence')
    assert verify(json.loads(json.dumps(history)))
    assert history['historical_legality']=='unverified'
    assert all(p['truth_value'] is None for p in history['propositions'])


def test_public_history_transport_rejects_stale_model_binding_before_native_inference():
    from pln_chess.api import explain_move
    history=replay('7k/5p2/8/6P1/8/8/8/K7 b - - 0 1',['f7f5'],source='source',model_version='old')
    model=SimpleNamespace(schema=8,version='new',runtime_version='runtime')
    with pytest.raises(ValueError,match='different model'):
        explain_move(history['resulting_fen'],'g5f6',model,temporal_evidence=history,mode='operational')
