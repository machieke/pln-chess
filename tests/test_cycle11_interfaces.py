"""Independent field API and source-bound unchanged-model acceptance."""
import copy
from types import SimpleNamespace

import pytest

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle11.acceptance import CHECKS, accepted_model
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.api import inspect_fields, replay_history_claims, explain_move


def receipt(runtime):
    config=read_json(ROOT/'configs/cycle11.json')
    return dict(passed=True,all_required_checks_executed=True,checks={key:True for key in CHECKS},
        accepted_model_versions=[config['accepted_model_version']],accepted_legacy_model_versions=[],
        runtime_version=runtime.version,production_code_hash=production_code_hash(),
        registration_hash=digest(config),legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9,10)},
        new_learning_promoted=False,field_model_is_default=False)


def test_acceptance_requires_every_gate_and_unchanged_legal_identity(runtime,tmp_path,monkeypatch):
    monkeypatch.setenv('C11_OUT',str(tmp_path))
    valid=receipt(runtime)
    model=SimpleNamespace(version=valid['accepted_model_versions'][0],runtime_version=runtime.version)
    write_json(tmp_path/'acceptance.json',valid)
    assert accepted_model(model)
    for key in CHECKS:
        changed=copy.deepcopy(valid)
        changed['checks'][key]=False
        write_json(tmp_path/'acceptance.json',changed)
        assert not accepted_model(model)
    for change in (dict(production_code_hash='stale'),dict(runtime_version='wrong'),dict(new_learning_promoted=True),
        dict(field_model_is_default=True),dict(registration_hash='different'),dict(legacy_registrations={})):
        write_json(tmp_path/'acceptance.json',{**valid,**change})
        assert not accepted_model(model)
    write_json(tmp_path/'acceptance.json',{**valid,'accepted_model_versions':[model.version,'experimental']})
    assert not accepted_model(SimpleNamespace(version='experimental',runtime_version=runtime.version))


def test_explicit_previous_cycle_output_override_cannot_fall_through(runtime,tmp_path,monkeypatch):
    from pln_chess.cycle10.acceptance import accepted_model as previous
    monkeypatch.setenv('C11_OUT',str(tmp_path/'current'))
    monkeypatch.setenv('C10_OUT',str(tmp_path/'explicit-old-empty'))
    valid=receipt(runtime)
    write_json(tmp_path/'current/acceptance.json',valid)
    model=SimpleNamespace(version=valid['accepted_model_versions'][0],runtime_version=runtime.version)
    assert accepted_model(model) and not previous(model)


def test_public_empty_field_is_explicitly_experimental(runtime):
    model=FieldModel(runtime.version)
    result=inspect_fields('7k/8/8/8/R6p/8/8/6K1 w - - 0 1',model,
        family='attack',piece='a4',runtime=runtime,options=FieldOptions(timeout_seconds=180))
    assert result['relations'] and all(row['classification']=='unknown' for row in result['relations'])
    assert result['model_version']==model.version
    assert 'directional_index' in result and 'projection' in result


def test_candidate_status_and_native_fields_remain_separate(runtime):
    result=inspect_fields('4r1k1/8/8/8/8/8/4R1P1/4K3 w - - 0 1',FieldModel(runtime.version),
        family='defense',piece='e2',candidate='e2f2',runtime=runtime,options=FieldOptions(timeout_seconds=180))
    assert result['candidate']['classification']=='supported-illegal'
    assert result['before']['relations'] and result['after']['relations']
    assert all(row['classification']=='unknown' for side in ('before','after') for row in result[side]['relations'])
    assert all(change['change_truth_value'] is None for change in result['differences'])


def test_unknown_source_does_not_become_observed_after_hypothetical_move(runtime):
    position=Position.from_fen('7k/8/8/8/R6p/8/8/6K1 w - - 0 1',unknown_squares=[(0,3)])
    result=inspect_fields(position,FieldModel(runtime.version),family='attack',piece='a4',candidate='a4a5',
        runtime=runtime,options=FieldOptions(timeout_seconds=180))
    assert [0,4] in result['after']['unknown_squares']
    assert all(row['classification']=='unknown' for row in result['after']['relations'])


def test_v11_receipt_uses_existing_public_legal_contract(runtime):
    from pln_chess.cycle8.model import PromotionModel
    model=PromotionModel.load(ROOT/'artifacts/cycle10/model/C10-default.json',runtime)
    history=replay_history_claims('7k/5p2/8/6P1/8/8/8/K7 b - - 0 1',[
        dict(sequence=1,move='f7f5',source='public-test',dependence_group='public-test',epistemic_type='observed-event',confidence=.99)],
        source='public-test',model_version=model.version,runtime_version=runtime.version)
    result=explain_move(history['resulting_fen'],'g5f6',model,runtime=runtime,temporal_evidence=history,mode='operational')
    assert result['temporal_transport']==history and result['candidate']['classification']=='unknown'
    assert result['candidate']['temporal_evidence']['ep_truth_value']==dict(strength=1.,confidence=.99)


def test_field_inspector_rejects_arbitrary_model_selector_before_loading():
    from pln_chess.cycle11.api import inspector_fields
    with pytest.raises(ValueError):
        inspector_fields(dict(fen='7k/8/8/8/R6p/8/8/6K1 w - - 0 1',model='../../elsewhere'))


def test_legal_inference_does_not_depend_on_field_modules(runtime,monkeypatch):
    import builtins
    from pln_chess.cycle8.model import PromotionModel
    model=PromotionModel.load(ROOT/'artifacts/cycle10/model/C10-default.json',runtime)
    original=builtins.__import__
    def block(name,*args,**kwargs):
        if name.startswith('pln_chess.cycle11.fields'):
            raise AssertionError('Legal inference depends on experimental fields')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',block)
    result=explain_move('7k/8/8/8/8/8/2R5/2K5 w - - 0 1','c2e2',model,runtime=runtime,mode='operational')
    assert result['candidate']['classification']=='supported-legal'
