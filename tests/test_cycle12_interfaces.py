"""Promotion gates, graph provenance and bounded experimental API isolation."""
import builtins
import copy
from types import SimpleNamespace
import pytest
from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle12.acceptance import CHECKS, accepted_model, default_checkpoint
from pln_chess.cycle12.candidates import enumerate_concepts
from pln_chess.cycle12.ontology import observe_concept
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle11.fields.model import FieldModel


def receipt(runtime,promoted=True):
    config=read_json(ROOT/'configs/cycle12.json')
    versions=[config['accepted_legal_model_version']]+([config['promotion_candidate_version']] if promoted else [])
    return dict(passed=True,all_required_checks_executed=True,checks={key:True for key in CHECKS},
        accepted_model_versions=versions,accepted_legacy_model_versions=[],runtime_version=runtime.version,
        production_code_hash=production_code_hash(),registration_hash=digest(config),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9,10,11)},
        legal_candidate_promoted=promoted,default_model_version=versions[-1],field_model_is_default=False,concept_model_is_default=False)


def test_candidate_requires_every_gate_and_explicit_promotion(runtime,tmp_path,monkeypatch):
    monkeypatch.setenv('C12_OUT',str(tmp_path));valid=receipt(runtime)
    candidate=SimpleNamespace(schema=8,version=valid['default_model_version'],runtime_version=runtime.version)
    write_json(tmp_path/'acceptance.json',valid);assert accepted_model(candidate)
    for key in CHECKS:
        changed=copy.deepcopy(valid);changed['checks'][key]=False;write_json(tmp_path/'acceptance.json',changed)
        assert not accepted_model(candidate)
    for change in (dict(production_code_hash='stale'),dict(registration_hash='changed'),dict(legal_candidate_promoted=False),
                   dict(field_model_is_default=True),dict(concept_model_is_default=True),dict(default_model_version='other')):
        write_json(tmp_path/'acceptance.json',{**valid,**change});assert not accepted_model(candidate)
    write_json(tmp_path/'acceptance.json',receipt(runtime,False));assert not accepted_model(candidate)


def test_experimental_models_are_excluded_even_if_receipt_lists_their_version(runtime,tmp_path,monkeypatch):
    monkeypatch.setenv('C12_OUT',str(tmp_path));valid=receipt(runtime)
    for model in (ConceptModel(runtime.version),FieldModel(runtime.version)):
        write_json(tmp_path/'acceptance.json',{**valid,'accepted_model_versions':[model.version],
            'default_model_version':model.version})
        assert not accepted_model(model)


def test_explicit_previous_cycle_override_cannot_fall_through(runtime,tmp_path,monkeypatch):
    from pln_chess.cycle11.acceptance import accepted_model as previous
    monkeypatch.setenv('C12_OUT',str(tmp_path));monkeypatch.setenv('C11_OUT',str(tmp_path/'missing-old-output'))
    valid=receipt(runtime);write_json(tmp_path/'acceptance.json',valid)
    model=SimpleNamespace(schema=8,version=valid['default_model_version'],runtime_version=runtime.version)
    assert accepted_model(model) and not previous(model)
    assert default_checkpoint('explicit-fallback')=='explicit-fallback'


def test_bounded_enumeration_does_not_assign_verdicts():
    position=Position.from_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    result=enumerate_concepts(position,max_candidates=3)
    assert len(result['candidates'])==3 and result['truncated']
    assert result['strategic_verdicts'] is False
    for case in result['candidates']:
        assert 'classification' not in case and 'label' not in case
        observe_concept(case)


def test_graph_keeps_separate_provenance_for_same_proposition(runtime):
    from pln_chess.cycle12.api import inspect_interactions
    from pln_chess.cycle12.graph import validate_graph
    case=dict(concept='Pin',fen='8/8/8/8/8/8/8/Rnk5 w - - 0 1',roles=dict(attacker='a1',intervening='b1',target='c1'),source='role-source')
    result=inspect_interactions(case['fen'],FieldModel(runtime.version),ConceptModel(runtime.version),
        runtime=runtime,cases=[case],source='separate-field-source')
    assert validate_graph(result['graph'])
    nodes=[n for n in result['graph']['nodes'] if n['kind']=='relative-observation']
    assert {'role-source','separate-field-source'} <= {n['observation']['source'] for n in nodes}


def test_legal_inference_does_not_import_experimental_modules(runtime,monkeypatch):
    from pln_chess.api import explain_move
    from pln_chess.cycle8.model import PromotionModel
    model=PromotionModel.load(ROOT/'artifacts/cycle10/model/C10-default.json',runtime)
    original=builtins.__import__
    def guard(name,*args,**kwargs):
        if name.startswith('pln_chess.cycle12') and name not in ('pln_chess.cycle12.acceptance',):
            raise AssertionError('Legal inference imported experimental concepts')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guard)
    assert explain_move('7k/8/8/8/R6p/8/8/6K1 w - - 0 1','a4h4',model,runtime=runtime,mode='operational')['candidate']


@pytest.mark.parametrize('limit',[-1,65,True,1.5])
def test_bad_enumeration_limits_are_rejected(limit):
    with pytest.raises(ValueError):enumerate_concepts('7k/8/8/8/R6p/8/8/6K1 w - - 0 1',max_candidates=limit)
