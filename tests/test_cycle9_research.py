"""Independent cohort, calibration and epistemic-boundary checks."""
import math
import chess
import pytest
from pln_chess.common import ROOT,read_json,digest
from evaluation.cycle9_analysis import fit,probability_metrics,wilson,bin_index
from evaluation.cycle9_controls import temporal_categories
from pln_chess.cycle6.history import inspect
from pln_chess.domain import Position
from pln_chess.api import find_move
from training.cycle9_data import PAIRS,translation_key


def test_calibration_does_not_identify_confidence_with_probability():
    rows=[dict(label=True,truth_value=dict(strength=.8,confidence=.2)),
          dict(label=False,truth_value=dict(strength=.8,confidence=.99))]
    bins=fit(rows)
    assert bins[8]['probability']==.5 and bins[8]['n']==2
    assert bins[0]['probability']==.5 and bins[0]['n']==0
    result=probability_metrics(rows,lambda r:.5)
    assert result['brier']==.25 and result['log_loss']==pytest.approx(math.log(2))
    assert result['ece']==0 and bin_index(1)==9
    assert wilson(0,100)[1]>0 # no observed error is not zero uncertainty


@pytest.mark.parametrize('spec',PAIRS)
def test_counterfactual_registration_matches_the_independent_oracle(spec):
    family,fen,move,square,symbol,left,right=spec;a=chess.Board(fen);b=a.copy()
    b.set_piece_at(chess.parse_square(square),chess.Piece.from_symbol(symbol) if symbol else None)
    m=chess.Move.from_uci(move)
    assert a.is_valid() and b.is_valid(),family
    assert (m in a.legal_moves,m in b.legal_moves)==(left,right),family


def test_temporal_epistemic_categories_do_not_relabel_metadata_as_events():
    initial='7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1';p=Position.from_fen(initial)
    q=p.successor(find_move(p,'b7b5'))
    metadata=temporal_categories(inspect(q,'trusted-metadata',dict(source='supplied-FEN',confidence=.8)))
    assert metadata['trusted_state_metadata'] and not metadata['directly_observed_events']
    history=dict(initial_fen=initial,moves=['b7b5'],source='external-events',confidence=.8,castling_history_attested=False)
    events=temporal_categories(inspect(q,'event-backed',history))
    assert 'pawn-double-step' in events['directly_observed_events'][0]['kinds']
    assert events['inferred_historical_conditions'][0]['native_complete_history_proof'] is False
    assert not events['trusted_state_metadata']


def test_registered_dataset_is_complete_and_game_disjoint():
    path=ROOT/'artifacts/cycle9/datasets/dataset.json'
    if not path.exists():pytest.skip('Generate registered C9 dataset before full delivery checks')
    data=read_json(path);claimed=data.pop('hash');assert digest(data)==claimed
    assert data['counts']['independent-games']==500 and data['game_counts']['independent-games']==100
    assert data['counts']['adversarial']>=100
    by={p['id']:p for p in data['positions']};keys={}
    for p in by.values():
        assert p['translation_key'] not in keys
        keys[p['translation_key']]=p['split']
        assert translation_key(p['fen'])==p['translation_key']
    for game in data['games']:
        board=chess.Board(game['initial_fen']);samples={by[k]['ply']:by[k] for k in game['sampled_fixtures']}
        for ply,notation in enumerate(game['moves'],1):
            move=chess.Move.from_uci(notation);assert move in board.legal_moves;board.push(move)
            if ply in samples:
                assert not board.is_game_over() and board.fen()==samples[ply]['fen']
                assert samples[ply]['split']==game['split']
        assert board.is_game_over() and board.fen()==game['final_fen'] and game['complete']
        assert board.outcome().termination.name==game['termination']
