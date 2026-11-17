"""Registered natural-source selection. No inference or final-label selection."""
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from research.cycle16.corpus import SOURCE, ray
from research.cycle16.records import record
from scripts.cycle15_baseline import sha

REGISTER = ROOT / 'artifacts/cycle17/corpus-registration.json'
DIRECTIONS = ('+x', '+y', '-x', '-y')


def roots():
    return read_json(REGISTER)['roots']


def register(destination=REGISTER):
    import chess.pgn
    historical = read_json(ROOT/'artifacts/cycle16/corpus-registration.json')['roots']
    seen = {r['game_identity'] for r in historical}
    selected = []
    with SOURCE.open() as stream:
        game_index = 0
        while len(selected) < 54:
            game = chess.pgn.read_game(stream)
            if game is None:
                break
            game_index += 1
            if game.errors:
                raise ValueError('Malformed source game')
            moves = list(game.mainline_moves())
            identity = digest([game.headers.get('Event'), game.headers.get('Round'), [m.uci() for m in moves]])
            if identity in seen:
                continue
            seen.add(identity)
            index = len(selected)
            split = 'A' if index < 12 else 'B' if index < 24 else 'development' if index < 30 else 'test'
            desired_phase, desired_direction = index % 3, DIRECTIONS[(index // 3) % 4]
            board = game.board()
            best = None
            for ply, move in enumerate(moves, 1):
                board.push(move)
                if ply < 12:
                    continue
                for a, piece in sorted(board.piece_map().items()):
                    if piece.piece_type != chess.ROOK:
                        continue
                    for t in sorted(board.piece_map()):
                        if a == t:
                            continue
                        ac, tc = [chess.square_file(a), chess.square_rank(a)], [chess.square_file(t), chess.square_rank(t)]
                        shape, cells = ray(ac, tc)
                        if shape != 'orthogonal' or len(cells) != 2:
                            continue
                        if split in ('A', 'B') and any(board.piece_at(chess.square(*c)) for c in cells):
                            continue
                        phase = 0 if ply < 40 else 1 if ply < 80 else 2
                        direction = ('+x' if tc[0] > ac[0] else '-x') if tc[0] != ac[0] else ('+y' if tc[1] > ac[1] else '-y')
                        rank = (phase != desired_phase, direction != desired_direction, ply, a, t)
                        if best is None or rank < best[0]:
                            best = rank, a, t, ply, phase, direction, board.copy()
            if best is None:
                continue
            rank, a, t, ply, phase, direction, board = best
            ident = 'episode_' + identity[:20]
            state = dict(id='state_'+digest([identity, ply])[:24], root=ident,
                actor='white' if board.turn else 'black',
                history='history_'+digest([identity, [m.uci() for m in moves[:ply]]])[:24], unknown=[],
                pieces=[dict(id='entity_'+digest([identity, square])[:20], kind=chess.piece_name(p.piece_type),
                    owner='white' if p.color else 'black', cell=[chess.square_file(square), chess.square_rank(square)])
                    for square, p in sorted(board.piece_map().items())])
            selected.append(dict(id=ident, split=split, source_ancestry='tcec_game_'+identity,
                game_identity=identity, game_index=game_index, ply=ply, fen=board.fen(),
                source_headers=dict(game.headers), coarse_geometry='orthogonal-two-intervening-cells',
                direction=direction, phase=phase, desired_direction=desired_direction, desired_phase=desired_phase,
                selection_fallback=bool(rank[0] or rank[1]),
                attacker='entity_'+digest([identity, a])[:20], target='entity_'+digest([identity, t])[:20], state=state))
    if len(selected) != 54:
        raise ValueError(f'Only {len(selected)} eligible roots; report and revise registration explicitly')
    return record(destination, dict(schema='cycle17-source-episodes-v1', roots=selected,
        source=str(SOURCE.relative_to(ROOT)), source_sha256=sha(SOURCE), historical_games_excluded=len(historical),
        selection='Registered deterministic phase/direction preference; natural EE training; no final attack labels',
        independence='Distinct games in one engine tournament; openings/engines/publisher remain shared'))
