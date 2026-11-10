"""Concept proofs, uncertainty, native boundaries and learned-evidence removal."""
import builtins
import copy
from dataclasses import replace

import pytest

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.pln import NativeError
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle12.ontology import CONCEPTS, observe_concept
from pln_chess.cycle12.inference import infer_concepts, ConceptSession


@pytest.fixture(scope='module')
def concept_models(runtime):
    return (ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime),
            FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime))


@pytest.fixture(scope='module')
def concept_cases():
    rows=read_json(ROOT/'artifacts/cycle12/datasets/concepts.json')['records']
    return {concept:next(r['input'] for r in rows if r['input']['concept']==concept and r['split']=='train' and r['variant']=='base') for concept in CONCEPTS}


def query(case,models,runtime,session=None,options=None):
    return infer_concepts([case],*models,runtime=runtime,session=session,
        options=options or FieldOptions(timeout_seconds=180))['concepts'][0]


@pytest.mark.parametrize('concept',tuple(CONCEPTS))
def test_empty_concept_model_cannot_invent_positive_knowledge(concept,concept_cases,concept_models,runtime):
    result=query(concept_cases[concept],(ConceptModel(runtime.version),concept_models[1]),runtime)
    assert result['classification']=='unknown'
    assert result['raw_stv']==dict(strength=.5,confidence=0.)
    assert result['proof_trace']==[] and not result['conditional_proof_complete']


@pytest.mark.parametrize('concept',tuple(CONCEPTS))
def test_native_conditionals_never_masquerade_as_joint_theorems(concept,concept_cases,concept_models,runtime):
    result=query(concept_cases[concept],concept_models,runtime)
    assert result['conditional_proof_complete']
    assert result['joint_proof_complete'] is False
    assert result['proof_id']==digest(result['proof_trace'])
    assert result['proof_trace'][0]['premises'][0]['predicate']=='ObservedStructuralRolePacket'
    assert all(node['operator'] in ('Truth_ModusPonens','Truth_Negation','BestConfidenceCandidate') for node in result['proof_trace'])
    native=runtime.batch([(n['id'],n['native_expression']) for n in result['proof_trace']])
    assert all(native[n['id']].json()==n['truth_value'] for n in result['proof_trace'])


def test_selected_hypothesis_removal_retracts_conditional(concept_cases,concept_models,runtime):
    case=concept_cases['Pin'];intact=query(case,concept_models,runtime)
    model=copy.deepcopy(concept_models[0]);model.hypotheses.pop(intact['rule_id'])
    missing=query(case,(model,concept_models[1]),runtime)
    assert intact['classification']=='supported' and missing['classification']=='unknown'
    assert not missing['proof_trace'] and model.version!=concept_models[0].version


@pytest.mark.parametrize('concept',tuple(CONCEPTS))
def test_required_unknown_role_does_not_become_negative(concept,concept_cases,concept_models,runtime):
    from pln_chess.domain import parse_square
    case=copy.deepcopy(concept_cases[concept]);case['unknown_squares']=[parse_square(next(iter(case['roles'].values())))]
    row=query(case,concept_models,runtime)
    assert row['classification']=='unknown' and not row['conditional_proof_complete'] and row['gaps']


def test_zero_budget_survives_warm_cache(concept_cases,concept_models,runtime):
    session=ConceptSession(runtime);case=concept_cases['Pin']
    query(case,concept_models,runtime,session)
    result=query(case,concept_models,runtime,session,FieldOptions(max_native_invocations=0))
    assert result['classification']=='incomplete' and not result['conditional_proof_complete']


def test_zero_sensor_confidence_is_not_a_certain_packet(concept_cases,concept_models,runtime):
    row=query(concept_cases['Pin'],concept_models,runtime,options=FieldOptions(sensor_confidence=0))
    assert row['classification']=='unknown' and not row['proof_trace']


def test_cache_rebinds_model_source_and_returned_mutation(concept_cases,concept_models,runtime):
    case=concept_cases['Pin'];session=ConceptSession(runtime)
    original=query(case,concept_models,runtime,session)
    expected=copy.deepcopy(original);original['proof_trace'].clear();original['gaps'].append('mutated-client-copy')
    assert query(case,concept_models,runtime,session)==expected
    changed={**case,'source':'different-observer'}
    other=query(changed,concept_models,runtime,session)
    assert other==query(changed,concept_models,runtime)
    assert other['proof_id']!=expected['proof_id'] and other['raw_stv']==expected['raw_stv']


def test_native_failure_has_no_host_fallback(concept_cases,concept_models,runtime,monkeypatch):
    def fail(*args,**kwargs):raise NativeError('controlled unavailable native process')
    session=ConceptSession(runtime)
    monkeypatch.setattr(session.native,'batch',fail)
    row=query(concept_cases['Pin'],concept_models,runtime,session)
    assert row['classification']=='incomplete' and not row['conditional_proof_complete']


def test_native_fields_and_packet_learning_have_separate_dependencies(concept_cases,concept_models,runtime):
    intact=query(concept_cases['Fork'],concept_models,runtime)
    without=query(concept_cases['Fork'],(concept_models[0],FieldModel(runtime.version)),runtime)
    assert any(r['conditional_proof_complete'] for r in intact['field_relations'])
    assert all(r['classification']=='unknown' for r in without['field_relations'])
    assert intact['raw_stv']==without['raw_stv']
    assert not intact['joint_proof_complete'] and not without['joint_proof_complete']


def test_schema_rejects_model_identity_or_runtime_tampering(concept_models,runtime,tmp_path):
    path=tmp_path/'concept.json';concept_models[0].export(path)
    supplied=read_json(path);supplied['runtime_version']='wrong';write_json(path,supplied)
    with pytest.raises(ValueError):ConceptModel.load(path,runtime)
    supplied['version']='rehashed-is-still-not-enough';write_json(path,supplied)
    with pytest.raises(ValueError):ConceptModel.load(path,runtime)


def test_production_concept_path_does_not_import_reference_engine(concept_cases,concept_models,runtime,monkeypatch):
    original=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name=='chess' or name.startswith(('chess.','training.','evaluation.')):
            raise AssertionError('Reference dependency in production inference')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guarded)
    assert query(concept_cases['Pin'],concept_models,runtime)['proof_trace']


@pytest.mark.parametrize('correction',[
    {'concept':'Unknown'}, {'roles':{}}, {'roles':{'attacker':'z9'}},
    {'move':'not-a-move'}, {'unknown_squares':[(99,99)]}, {'source':[]},
])
def test_malformed_concept_inputs_fail_before_native_work(correction,concept_cases):
    with pytest.raises((ValueError,TypeError)):
        observe_concept({**concept_cases['Pin'],**correction})


def test_labels_and_complete_board_keys_are_not_observation_inputs(concept_cases):
    case=concept_cases['Pin'];observation=observe_concept(case)
    forbidden={**case,'label':True,'reference':{'label':True}}
    with pytest.raises(ValueError):observe_concept(forbidden)
    text=str(observation['descriptor'])
    assert case['fen'] not in text and 'source' not in observation['descriptor']
