"""Oracle-side dataset audit, independent of the production learner."""
import chess
from pln_chess.common import digest


def test_dataset_content_hash(dataset):
    assert dataset['hash']==digest({k:v for k,v in dataset.items() if k not in ('hash','manifest')})


def test_synthetic_starting_positions_are_valid(dataset):
    for fixture in dataset['positions']:
        board=chess.Board(fixture['fen'])
        assert board.is_valid(),(fixture['id'],board.status())


def test_named_check_scenarios_are_real(dataset):
    boards={p['id']:chess.Board(p['fen']) for p in dataset['positions']}
    assert len(boards['double-check'].checkers())==2
    assert boards['mate'].is_checkmate()
    assert boards['stalemate'].is_stalemate()
    for fixture_id,move in [('rook-pinned','c2e2'),('castle-through-attack','e1g1'),('en-passant-opens-ray','c5d6')]:
        board=boards[fixture_id]
        assert chess.Move.from_uci(move) not in board.legal_moves
