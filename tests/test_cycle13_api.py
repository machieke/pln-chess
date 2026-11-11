"""End-to-end experimental API boundaries and bounded structural continuations."""
import builtins
import copy
from dataclasses import replace
import pytest
from pln_chess.common import ROOT,canonical
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.domain import Position
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle12.temporal import semantic_replay
from pln_chess.cycle13.model import PreferenceModel
from pln_chess.cycle13.concepts import ForkModel
from pln_chess.cycle13.api import compare_moves,compare_pairs,PreferenceOptions,PreferenceSession
from pln_chess.cycle13.temporal import analyze_continuations
from pln_chess.cycle13.inspector import inspect

FEN='4k3/8/8/3p4/8/8/8/R3K3 w - - 0 1'
MOVES=('a1a5','a1a4')


@pytest.fixture(scope='module')
def models(runtime):
    return dict(legal_model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',runtime),
        field_model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime),
        concept_model=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime),
        fork_model=ForkModel(runtime.version),preference_model=PreferenceModel(runtime.version))


def compare(models,runtime,**kwargs):
    return compare_moves(FEN,*MOVES,**models,runtime=runtime,**kwargs)


def test_full_incremental_cold_warm_exact_complete_output_parity(models,runtime):
    outputs=[]
    for incremental in (False,True):
        session=PreferenceSession(runtime)
        for _ in range(2):
            result=compare(models,runtime,session=session,options=PreferenceOptions(incremental=incremental))
            assert not result['execution']['truncated']
            outputs.append(canonical(semantic_replay(result)))
    assert len(set(outputs))==1


def test_empty_preference_keeps_independent_native_fields_and_legality(models,runtime):
    result=compare(models,runtime)
    assert result['preference']['status']=='indeterminate'
    assert not result['preference']['conditional_proof_complete']
    assert set(result['legality'])=={'A','B'} and result['legal_inference']['proof_dag']
    assert any(r['conditional_proof_complete'] for r in result['states']['A']['field']['relations'])
    assert result['automatic_move_selection'] is False


@pytest.mark.parametrize('mode',('operational','strict','experimental'))
def test_requested_legal_modes_remain_separate(models,runtime,mode):
    result=compare(models,runtime,options=PreferenceOptions(mode=mode,max_candidates=0))
    assert result['legal_inference']['budget']['mode']==mode
    assert result['preference']['status']=='indeterminate'


def test_unknown_cells_are_preserved_and_do_not_establish_safe_zero(models,runtime):
    position=Position.from_fen(FEN,unknown_squares=((0,4),))
    result=compare_moves(position,*MOVES,**models,runtime=runtime)
    assert result['packet']['gaps']
    assert result['states']['A']['field']['unknown_squares']
    assert any(r['classification']=='unknown' for r in result['states']['A']['field']['relations'])
    assert not result['preference']['joint_proof_complete']


def test_zero_budget_and_short_deadline_remain_incomplete(models,runtime):
    for options in (PreferenceOptions(max_native_invocations=0),PreferenceOptions(timeout_seconds=.001)):
        result=compare(models,runtime,options=options)
        assert result['execution']['truncated'] and result['preference']['status']=='incomplete'


def test_supplied_history_does_not_silently_attest_initial_metadata(models,runtime):
    result=compare(models,runtime,history=dict(initial_fen=FEN,moves=[],source='unknown-start'))
    receipt=result['legal_inference']['temporal_transport']
    assert receipt['input']['initial_trust']=='unknown'
    assert not receipt['legacy_evidence']['castling_history_attested']


def test_entire_pair_batch_validated_before_native_execution(models,runtime):
    calls=runtime.invocations
    with pytest.raises(ValueError):
        compare_pairs(FEN,[MOVES,('a1a5','h8h9')],**models,runtime=runtime)
    assert runtime.invocations==calls


def test_explicit_continuations_preserve_states_proofs_and_unexamined_responses(models,runtime):
    branches=dict(A=[['a1a5','e8e7','a5a7']],B=[['a1a4','e8e7','a4a7']])
    result=analyze_continuations(FEN,branches,**models,runtime=runtime)
    assert not result['execution']['truncated']
    assert len(result['states'])==7 and len(result['transitions'])==6
    assert {r['horizon'] for r in result['comparisons']}=={2,3}
    assert result['unexamined_responses'] and not result['exhaustive_response_coverage']
    assert all(not r['native_temporal_proof'] and r['truth_value'] is None for r in result['transitions'])
    assert all(r['legality'] for r in result['transitions'])


def test_missing_response_is_incomplete_and_never_impossible(models,runtime):
    result=analyze_continuations(FEN,dict(A=[['a1a5']],B=[['a1a4','e8e7']]),**models,runtime=runtime)
    assert all(r['preference']['status']=='incomplete' for r in result['comparisons'])
    assert not result['exhaustive_response_coverage']


@pytest.mark.parametrize('branches',[
    dict(A=[['a1a5','e8e7','a5a7','e7e6']],B=[['a1a4']]),
    dict(A=[['a1a5'],['a1a4']],B=[['a1a4']]),
    dict(A=[['a1a5']]*3,B=[['a1a4']]),
    dict(A=[['a1a5','h8h9']],B=[['a1a4']])])
def test_invalid_branch_envelopes_fail_before_native_work(models,runtime,branches):
    calls=runtime.invocations
    with pytest.raises(ValueError):
        analyze_continuations(FEN,branches,**models,runtime=runtime)
    assert runtime.invocations==calls


def test_production_path_cannot_import_chess_or_training_labels(models,runtime,monkeypatch):
    original=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name=='chess' or name.startswith(('chess.','training.','evaluation.')):
            raise AssertionError('Reference dependency in production comparison')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guarded)
    assert compare(models,runtime)['states']['before']['graph']


def test_inspector_rejects_label_and_score_injection():
    for extra in ({'label':'A'},{'engine_score':100},{'reference':{}}):
        with pytest.raises(ValueError):
            inspect(dict(fen=FEN,move_a=MOVES[0],move_b=MOVES[1],**extra))
