"""End-to-end trained demonstrations plus an untrained-context exposure test."""
import copy
import pytest
from pln_chess.api import explain_move
from pln_chess.learning import Model
from pln_chess.common import ROOT
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.observations import observe

@pytest.fixture(scope='module')
def model(runtime):
    return Model.load(ROOT/'artifacts/model.json',runtime)

@pytest.mark.parametrize('name,expected',[
    ('rook-clear','supported'),('rook-blocked','contradicted'),('rook-enemy','supported'),('rook-friendly','contradicted'),
    ('rook-pinned','contradicted'),('bishop-clear','supported'),('bishop-blocked','contradicted'),
    ('queen-clear','supported'),('knight-jump','supported'),('pawn-white','supported'),('pawn-black','supported'),
    ('pawn-blocked','contradicted'),('pawn-capture','supported'),('pawn-empty-diagonal','contradicted'),
    ('king-safe','supported'),('king-attacked','contradicted'),('king-adjacent','contradicted'),
    ('castle-clear','supported'),('castle-no-right','contradicted'),('castle-through-attack','contradicted'),
    ('castle-queenside','supported'),('castle-queenside-outer-blocked','contradicted'),
    ('en-passant','supported'),('en-passant-no-target','contradicted'),('en-passant-opens-ray','contradicted'),
    ('promotion','supported'),('promotion-friendly','contradicted')])
def test_native_trained_contrasts(name,expected,runtime,dataset,model):
    fixture=next(p for p in dataset['positions'] if p['id']==name)
    result=explain_move(fixture['fen'],fixture['focus_move'],model,runtime=runtime)
    assert not result['truncated'],result['error']
    candidate=result['candidate']
    assert candidate['classification']==expected
    assert candidate['proof_trace'] and candidate['evidence_ids']
    assert candidate['status']=='native-partial'


def test_inferred_exposure_lowers_untrained_context(runtime,dataset,model):
    fixture=next(p for p in dataset['positions'] if p['id']=='rook-pinned')
    p=Position.from_fen(fixture['fen']);m=find_move(p,fixture['focus_move']);key=observe(p,m)['key']
    partial=copy.deepcopy(model);partial.hypotheses.pop(key)
    result=explain_move(p,m,partial,runtime=runtime)['candidate']
    assert result['context_only_truth_value']['strength']==.5
    assert result['legal_move_truth_value']['strength']<.5
    assert any(a['exposure_support']['strength']>.8 for a in result['attack_beliefs'])
    # Weak priors preserve honest abstention despite directional counterevidence.
    assert result['classification']=='unknown'
