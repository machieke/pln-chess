"""Fixed worked examples and metamorphic controls, without model selection."""
import argparse
from dataclasses import replace
from pathlib import Path

import chess

from pln_chess.common import digest, write_json
from pln_chess.domain import Position, Piece, parse_square, square_name
from pln_chess.api import find_move
from pln_chess.spatial import translate, reflect_files, color_flip, ray_cells
from training.cycle11_data import labels

WORKED = [
    ('rook-obstruction', '7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1', 'd4f5', 'a4', 'attack', 'A blocker moves off the rook ray.'),
    ('bishop-diagonal', '7k/8/8/8/3P4/2B5/8/6K1 w - - 0 1', 'd4d5', 'c3', 'attack', 'A pawn opens the bishop diagonal toward the opposing king.'),
    ('knight-relocation', '6k1/8/8/8/3N4/8/8/1K6 w - - 0 1', 'd4f5', 'd4', 'attack', 'A knight changes its directional targets.'),
    ('pinned-defender', '4r1k1/8/8/8/8/8/4R1P1/4K3 w - - 0 1', 'e2f2', 'e2', 'defense', 'A rook geometrically defends a pawn, but this move exposes its king.'),
    ('discovered-attack', '6k1/8/8/8/8/8/6B1/1K4R1 w - - 0 1', 'g2f3', 'g1', 'attack', 'Moving the bishop reveals the rook attack.'),
    ('king-exposure', '4r1k1/8/8/8/8/8/4B3/4K3 w - - 0 1', 'e2d3', 'e8', 'king-exposure', 'A proposed bishop move exposes the moving side king.'),
    ('multiple-defenders', '6k1/8/8/8/3P4/2B2N2/8/1K6 w - - 0 1', 'f3g5', 'c3', 'defense', 'A pawn has bishop and knight defenders; one relocates. Evidence is not automatically combined.'),
    ('unknown-observation', '7k/8/8/8/R6p/8/8/6K1 w - - 0 1', 'a4a5', 'a4', 'attack', 'An unobserved ray cell preserves uncertainty.'),
    ('promotion', '7k/1P6/8/8/8/8/8/6K1 w - - 0 1', 'b7b8n', 'b7', 'mobility', 'Underpromotion changes the mover kind and its subsequent field.'),
    ('en-passant', '7k/8/8/R4pP1/8/8/8/6K1 w - f6 0 2', 'g5f6', 'a5', 'attack', 'En passant removes a pawn away from the destination and opens the rook ray.'),
    ('rook-battery', '6k1/8/8/8/1R1R4/8/8/6K1 w - - 0 1', 'd4d5', 'b4', 'defense', 'Moving the front rook changes the rear rook protection and open ray.'),
    ('defended-minor', '6k1/8/8/8/3N4/2B5/8/1K6 w - - 0 1', 'd4f5', 'c3', 'defense', 'A knight leaves a square geometrically protected by a bishop.'),
    ('double-check-resolution', '4r1k1/8/8/8/1b6/8/8/4K3 w - - 0 1', 'e1f1', 'e8', 'king-exposure', 'The king moves from two simultaneous attack relations; absence afterward is not a global safety theorem.'),
    ('discovered-defense', '6k1/7N/8/8/4P3/3B4/8/1K6 w - - 0 1', 'e4e5', 'd3', 'defense', 'A pawn move opens the bishop protection of a knight.'),
    ('en-passant-exposure', '7k/8/8/r4pPK/8/8/8/8 w - f6 0 2', 'g5f6', 'a5', 'king-exposure', 'Removing both pawns exposes the moving side king to the rook.'),
]

BASES = [
    ('rook-ray', '8/6k1/8/8/1R4p1/8/1K6/8 w - - 0 1', 'b4', 'g4', 'attack'),
    ('bishop-ray', '8/6k1/8/5p2/8/3B4/1K6/8 w - - 0 1', 'd3', 'f5', 'attack'),
    ('queen-defense', '8/6k1/8/8/1Q3N2/8/1K6/8 w - - 0 1', 'b4', 'f4', 'defense'),
    ('pawn-direction', '8/6k1/8/8/4p3/3P4/1K6/8 w - - 0 1', 'd3', 'e4', 'attack'),
    ('knight-mobility', '8/6k1/8/8/3N4/8/1K6/8 w - - 0 1', 'd4', 'f5', 'mobility'),
    ('king-ray', '8/8/8/8/1R4k1/8/1K6/8 b - - 0 1', 'b4', 'g4', 'king-exposure'),
]

TRANSFERS = [
    ('rook-attack-six', '7k/8/8/8/8/8/R5n1/K7 w - - 0 1', 'a2', 'g2', 'attack'),
    ('bishop-attack-five', '7k/5n2/8/8/8/8/B7/1K6 w - - 0 1', 'a2', 'f7', 'attack'),
    ('queen-mobility-seven', '8/7k/8/8/8/8/3K4/Q7 w - - 0 1', 'a1', 'a8', 'mobility'),
    ('rook-defense-five', '7k/8/8/8/8/1R4B1/8/1K6 w - - 0 1', 'b3', 'g3', 'defense'),
    ('bishop-defense-six', 'k7/6N1/8/8/8/8/8/B6K w - - 0 1', 'a1', 'g7', 'defense'),
    ('rook-exposure-six', '8/8/8/8/R5k1/8/8/K7 b - - 0 1', 'a4', 'g4', 'king-exposure'),
    ('queen-exposure-five', '8/6k1/8/8/8/8/1Q6/7K b - - 0 1', 'b2', 'g7', 'king-exposure'),
    ('bishop-mobility-six', '8/8/7k/8/8/8/8/BK6 w - - 0 1', 'a1', 'g7', 'mobility'),
]


def generate(out):
    out = Path(out)
    worked = []
    for name, fen, notation, selected, family, description in WORKED:
        unknown = [(3, 3)] if name == 'unknown-observation' else []
        position = Position.from_fen(fen, unknown_squares=unknown)
        move = find_move(position, notation)
        assert move is not None
        successor = position.successor(move)
        board = chess.Board(fen)
        assert board.is_valid(), (name, board.status())
        legal = chess.Move.from_uci(notation) in board.legal_moves
        # Structural comparison includes contradicted candidates deliberately.
        # Board.push applies the edit; parse_uci/push_uci would reject it first.
        board.push(chess.Move.from_uci(notation))
        assert successor.fen() == board.fen(en_passant='fen'), name
        history = None
        if name in ('en-passant', 'en-passant-exposure'):
            initial = ('7k/5p2/8/R5P1/8/8/8/6K1 b - - 0 1' if name == 'en-passant'
                       else '7k/5p2/8/r5PK/8/8/8/8 b - - 0 1')
            prior = chess.Board(initial)
            assert chess.Move.from_uci('f7f5') in prior.legal_moves
            prior.push_uci('f7f5')
            assert prior.fen(en_passant='fen') == fen
            history = dict(initial_fen=initial, moves=['f7f5'], source='controlled-worked-example/'+name,
                           dependence_group='worked/'+name, expected_fen=fen)
        worked.append(dict(id=name, fen=fen, move=notation, selected_piece_square=selected, selected_field=family,
            description=description, unknown_squares=unknown, history_input=history,
            reference_legal=legal, reference_successor_fen=successor.fen(),
            reference_scope='Offline complete-state reference; unknown observations remain unavailable to production inference.'))
    controls = []
    for name, fen, source, target, family in BASES:
        position = Position.from_fen(fen)
        origin, end = parse_square(source), parse_square(target)
        before_label = labels(chess.Board(fen), chess.parse_square(source), chess.parse_square(target))[family]
        assert before_label is True
        transformations = (
            ('translation', translate(position, (1, 0)), lambda sq: (sq[0]+1, sq[1])),
            ('file-reflection', reflect_files(position), lambda sq: (7-sq[0], sq[1])),
            ('color-orientation', color_flip(position), lambda sq: (sq[0], 7-sq[1])),
            ('piece-id-renaming', replace(position, pieces=tuple(replace(p, id='renamed-'+p.id) for p in position.pieces)), lambda sq: sq),
            ('irrelevant-distant-piece', replace(position, pieces=position.pieces+(Piece('distant-extra', 'Knight', 'Black', (0, 5)),)), lambda sq: sq),
        )
        for operation, other, transform in transformations:
            after_source, after_target = square_name(transform(origin)), square_name(transform(end))
            after_label = labels(chess.Board(other.fen()), chess.parse_square(after_source), chess.parse_square(after_target))[family]
            assert after_label == before_label, (name, operation)
            controls.append(dict(id=name+'/'+operation, operation=operation, field=family, before_fen=fen,
                before_source=source, before_target=target, after_fen=other.fen(), after_source=after_source,
                after_target=after_target, before_pieces=[dict(id=p.id, kind=p.kind, owner=p.owner, square=list(p.square)) for p in position.pieces],
                after_pieces=[dict(id=p.id, kind=p.kind, owner=p.owner, square=list(p.square)) for p in other.pieces],
                expectation='invariant-relative-conditional', reference_before=before_label, reference_after=after_label,
                dependence_group='transform-ancestor/'+name, transformation_lineage=[name]))
        ray = ray_cells(origin, end)
        if ray:
            blocked = replace(position, pieces=position.pieces+(Piece('intervening-piece', 'Knight', position.at(origin).owner, ray[0]),))
            blocked_label = labels(chess.Board(blocked.fen()), chess.parse_square(source), chess.parse_square(target))[family]
            assert blocked_label is False
            controls.append(dict(id=name+'/blocker-added', operation='blocker-added', field=family,
                before_fen=fen, before_source=source, before_target=target, after_fen=blocked.fen(),
                after_source=source, after_target=target, expectation='sensitive-relative-conditional',
                reference_before=True, reference_after=False, dependence_group='transform-ancestor/'+name, transformation_lineage=[name]))
            controls.append(dict(id=name+'/unknown-ray-cell', operation='unknown-ray-cell', field=family,
                before_fen=fen, before_source=source, before_target=target, after_fen=fen,
                after_source=source, after_target=target, unknown_squares=[list(ray[0])],
                expectation='unknown-required-observation', reference_before=True, reference_after=True,
                dependence_group='transform-ancestor/'+name, transformation_lineage=[name]))
    transfers = []
    for name, fen, source, target, family in TRANSFERS:
        board = chess.Board(fen)
        expected = labels(board, chess.parse_square(source), chess.parse_square(target))[family]
        assert expected is True
        origin, end = parse_square(source), parse_square(target)
        transfers.append(dict(id=name, fen=fen, source=source, target=target, field=family,
            relative_displacement=[end[0]-origin[0], end[1]-origin[1]],
            distance=max(abs(end[0]-origin[0]), abs(end[1]-origin[1])), reference_label=expected,
            dependence_group='dedicated-unseen-transfer/'+name,
            scope='Long-range query withheld from sliding training; inference-time audit must verify exact displacement absence and disclose the shared pooled conditional.'))
    payload = dict(schema=11, worked=worked, transformations=controls, transfers=transfers,
        selected_without_model=True, oracle_scope='Offline reference only; no production rule or strategic score.')
    payload['hash'] = digest(payload)
    write_json(out / 'datasets/worked-controls.json', payload)
    print('Worked examples', len(worked), 'transformations', len(controls), 'transfers', len(transfers), payload['hash'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    generate(parser.parse_args().out)
