"""Independent controlled special-move curricula; oracle labels stay offline."""
import argparse
from collections import Counter
from pathlib import Path
import random

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle7.model import key
from training.cycle4 import enrich4, symmetry_key


def generate(out):
    out = Path(out)
    config = read_json(ROOT / 'configs/cycle11.json')
    rows, seen = [], {'train': set(), 'holdout': set()}

    def add(board, notation, split, group, family, initial=None, moves=(), trust='unknown', lineage=()):
        assert board.is_valid(), (family, board.fen(), board.status())
        if symmetry_key(board.fen()) in seen['holdout' if split == 'train' else 'train']:
            raise ValueError('Special-move train/holdout whole-position symmetry collision')
        seen[split].add(symmetry_key(board.fen()))
        fen = board.fen(en_passant='fen')
        history_check = chess.Board(initial or fen)
        for event in moves:
            history_check.push(chess.Move.from_uci(event))
        assert history_check.fen(en_passant='fen') == fen, (family, 'history metadata/counter mismatch')
        position = Position.from_fen(fen)
        move = find_move(position, notation)
        assert move is not None
        rel = next(r for r in descriptors(position, move)['relations'] if r['target'] == 'LocalAdmissibility')
        raw = enrich4(dict(fen=fen, move=notation, label=chess.Move.from_uci(notation) in board.legal_moves,
            source='controlled-cycle11/'+family+'/'+group, dependence_group=group,
            transformation_lineage=list(lineage), confidence=config['training_observation_confidence'],
            split=split, family=family, position_fixture='c11-special:'+digest([fen, notation, group])[:24]))
        rows.append({**raw, 'source_game': group, 'source_collection': 'synthetic-cycle11-special-move-curriculum',
            'opening_family': family, 'descriptor': rel['descriptor'], 'identifier': key(rel['descriptor'], 0),
            'channel': 'local', 'source_kind': 'declared-controlled-structural-context',
            'history_input': dict(initial_fen=initial or fen, moves=list(moves), source='controlled-cycle11-history/'+group,
                dependence_group=group, initial_trust=trust, expected_fen=fen),
            'reference_pseudo_legal': board.is_pseudo_legal(chess.Move.from_uci(notation)),
            'reference_legal': chess.Move.from_uci(notation) in board.legal_moves,
            'canonical_hash': digest(symmetry_key(fen))})

    for split, n, base in (('train', 6, 0), ('holdout', 4, 10000)):
        for group_index in range(n):
            rng = random.Random(config['seed']+30000+base+group_index)
            group = f'c11-special-{split}-layout-{group_index}'
            for direction in (-1, 1):
                # Distinct nonlocal contexts, two signed EP categories, complete
                # immediately preceding double-pawn event; no final-test position.
                for attempt in range(1000):
                    pawn_file = rng.choice(range(1, 7))
                    victim_file = pawn_file+direction
                    before = chess.Board(None)
                    before.turn = chess.BLACK
                    before.fullmove_number = 20
                    before.set_piece_at(chess.square(pawn_file, 4), chess.Piece(chess.PAWN, chess.WHITE))
                    before.set_piece_at(chess.square(victim_file, 6), chess.Piece(chess.PAWN, chess.BLACK))
                    candidates = [sq for sq in chess.SQUARES if before.piece_at(sq) is None and chess.square_rank(sq) not in (4, 5, 6)]
                    rng.shuffle(candidates)
                    before.set_piece_at(candidates.pop(), chess.Piece(chess.KING, chess.WHITE))
                    before.set_piece_at(candidates.pop(), chess.Piece(chess.KING, chess.BLACK))
                    for _ in range(2):
                        before.set_piece_at(candidates.pop(), chess.Piece(chess.KNIGHT, rng.choice((chess.WHITE, chess.BLACK))))
                    advance = chess.Move(chess.square(victim_file, 6), chess.square(victim_file, 4))
                    if not before.is_valid() or advance not in before.legal_moves:
                        continue
                    board = before.copy()
                    board.push(advance)
                    capture = chess.Move(chess.square(pawn_file, 4), chess.square(victim_file, 5))
                    if not board.is_pseudo_legal(capture):
                        continue
                    if symmetry_key(board.fen()) in seen['holdout' if split == 'train' else 'train']:
                        continue
                    break
                else:
                    raise RuntimeError('Could not generate EP curriculum')
                add(board, capture.uci(), split, group, 'en-passant', before.fen(en_passant='fen'), [advance.uci()])
                flipped = board.mirror()
                flipped_before = before.mirror()
                # Mirroring changes which side advances the fullmove counter.
                # Preserve the registered final state and align only the
                # mirrored initial counter with its supplied one-event prefix.
                flipped_before.fullmove_number = flipped.fullmove_number - int(flipped_before.turn == chess.BLACK)
                mirror_move = lambda move: chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square), promotion=move.promotion)
                add(flipped, mirror_move(capture).uci(), split, group, 'en-passant-color-transform',
                    flipped_before.fen(en_passant='fen'), [mirror_move(advance).uci()], lineage=[group])
            for side in ('king', 'queen'):
                for context in ('clear', 'blocked', 'lost-right'):
                    for attempt in range(1000):
                        board = chess.Board(None)
                        board.turn = chess.WHITE
                        board.fullmove_number = 20
                        board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
                        rook = chess.H1 if side == 'king' else chess.A1
                        board.set_piece_at(rook, chess.Piece(chess.ROOK, chess.WHITE))
                        board.castling_rights = chess.BB_SQUARES[rook] if context != 'lost-right' else 0
                        if context == 'blocked':
                            blocker = chess.F1 if side == 'king' else rng.choice((chess.B1, chess.C1, chess.D1))
                            board.set_piece_at(blocker, chess.Piece(chess.KNIGHT, chess.WHITE))
                        candidates = list(range(16, 64))
                        rng.shuffle(candidates)
                        board.set_piece_at(candidates.pop(), chess.Piece(chess.KING, chess.BLACK))
                        for _ in range(2):
                            board.set_piece_at(candidates.pop(), chess.Piece(chess.KNIGHT, rng.choice((chess.WHITE, chess.BLACK))))
                        if board.is_valid() and symmetry_key(board.fen()) not in seen['holdout' if split == 'train' else 'train']:
                            break
                    else:
                        raise RuntimeError('Could not generate castling curriculum')
                    notation = 'e1g1' if side == 'king' else 'e1c1'
                    add(board, notation, split, group, 'castling-'+context, trust='trusted-import')
                    # Color reflection has the same ancestry and never creates
                    # another independent observation for a conditional.
                    flipped = board.mirror()
                    add(flipped, 'e8g8' if side == 'king' else 'e8c8', split, group, 'castling-'+context+'-color-transform',
                        trust='trusted-import', lineage=[group])
    # Independent EP king-exposure controls retain pseudo-legality but prohibit
    # the global move. They never train a false local-movement label.
    for index, extra in enumerate(('8', '1N6', '3N4', '6N1')):
        initial = f'7k/5p2/8/r5PK/8/{extra}/8/8 b - - 0 1'
        board = chess.Board(initial)
        assert board.is_valid() and chess.Move.from_uci('f7f5') in board.legal_moves
        board.push_uci('f7f5')
        add(board, 'g5f6', 'holdout', f'c11-ep-exposure-{index}', 'ep-king-exposure', initial, ['f7f5'])
    for index, capture in enumerate((False, True)):
        fen = '2r4k/1P6/8/8/8/8/8/6K1 w - - 0 1' if capture else '7k/1P6/8/8/8/8/8/6K1 w - - 0 1'
        board = chess.Board(fen)
        for promotion in 'qrbn':
            add(board, ('b7c8' if capture else 'b7b8')+promotion, 'holdout', f'c11-promotion-{index}', 'promotion-choice-'+promotion)
    payload = dict(schema='special-move-curriculum-v11', registration_hash=digest(config), examples=rows,
        counts=dict(Counter(r['split'] for r in rows)), reference_version=chess.__version__,
        leakage=dict(train_holdout_whole_position_symmetry_overlap=[], final_external_positions_used_for_training=False,
            transformed_ancestry_preserved=True, observed_old_failures_are_development_diagnostics=True),
        scope='Synthetic controlled curriculum, with explicit supplied history. Local pseudo-legality is distinct from global king safety. No accepted checkpoint is changed.')
    payload['hash'] = digest(payload)
    write_json(out / 'datasets/legal-curriculum.json', payload)
    print('Special-move curriculum', payload['hash'], payload['counts'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    generate(parser.parse_args().out)
