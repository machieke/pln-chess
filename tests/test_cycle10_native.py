"""Native temporal inference and cache parity through the versioned transport."""
from dataclasses import replace
import pytest
from pln_chess.common import ROOT,digest
from pln_chess.domain import Position
from pln_chess.api import find_move,explain_move
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options,Session
from pln_chess.cycle10.temporal import replay,native_options

EP='7k/5p2/8/6P1/8/8/8/K7 b - - 0 1'


@pytest.fixture(scope='module')
def model(runtime):return PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',runtime)


def infer(fen,notation,history,model,runtime,options=None,session=None):
    position=Position.from_fen(fen);move=find_move(position,notation)
    options=options or Cycle8Options(mode='operational')
    if history is not None:options=native_options(history,options)
    return infer_moves(position,model,options,runtime,[move],session=session)


def test_observed_predecessor_resolves_only_with_its_native_temporal_evidence(model,runtime):
    history=replay(EP,['f7f5'],source='native-transport-test',model_version=model.version,runtime_version=runtime.version)
    fen=history['resulting_fen'];unknown=infer(fen,'g5f6',None,model,runtime)
    known=infer(fen,'g5f6',history,model,runtime)
    removed=infer(fen,'g5f6',history,model,runtime,Cycle8Options(mode='operational',suppress_families=('temporal',)))
    assert unknown['candidates'][0]['classification']=='unknown'
    assert known['candidates'][0]['classification']=='supported-legal'
    assert removed['candidates'][0]['classification']=='unknown'
    assert not known['candidates'][0]['positive_proof_complete']
    assert known['candidates'][0]['proof_trace'] and known['error'] is None
    public=explain_move(fen,'g5f6',model,runtime=runtime,temporal_evidence=history,mode='operational')
    assert public['candidate']==known['candidates'][0] and public['temporal_transport']['id']==history['id']


def test_conflicting_supplied_predecessor_cannot_establish_eligibility(model,runtime):
    complete=replay(EP,['f7f5'],source='observed');fen=complete['resulting_fen']
    conflict=replay(EP,[],source='contradictory',expected_fen=fen)
    result=infer(fen,'g5f6',conflict,model,runtime)
    assert result['candidates'][0]['classification']=='unknown'
    assert result['candidates'][0]['temporal_evidence']['status']=='conflicting'


def test_native_cache_matches_fresh_proofs_after_source_and_confidence_changes(model,runtime):
    base=replay(EP,['f7f5'],source='source-a');fen=base['resulting_fen'];session=Session(runtime)
    receipts=[base,base,replay(EP,['f7f5'],source='source-b'),replay(EP,['f7f5'],source='source-a',confidence=.8)]
    for index,history in enumerate(receipts):
        reused=infer(fen,'g5f6',history,model,runtime,session=session)
        fresh=infer(fen,'g5f6',history,model,runtime,session=Session(runtime))
        assert digest(reused['candidates'])==digest(fresh['candidates'])
        if index==1:assert reused['native_invocations']==0


def test_returned_rook_keeps_lost_right_with_explicit_initial_trust(model,runtime):
    initial='6k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1'
    history=replay(initial,['h1h2','g8f8','h2h1','f8g8'],source='observed-rook-return',initial_trust='trusted-import')
    result=infer(history['resulting_fen'],'e1g1',history,model,runtime)
    assert result['candidates'][0]['classification']=='supported-illegal'
    assert result['candidates'][0]['negative_proof_complete']
