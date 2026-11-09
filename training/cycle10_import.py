"""Explicit offline PGN-to-event conversion; never imported by inference."""
from pathlib import Path
import hashlib
import chess
import chess.pgn
from pln_chess.common import digest


def import_pgn(path,source,limit=1000):
    if not isinstance(source,str) or not source.strip():raise ValueError('A provenance source is required')
    if type(limit) is not int or not 1<=limit<=1000:raise ValueError('Import limit must be 1..1000 games')
    path=Path(path);games=[]
    with path.open(encoding='utf-8-sig') as stream:
        while len(games)<limit:
            game=chess.pgn.read_game(stream)
            if game is None:break
            if game.errors:raise ValueError('Malformed PGN; no event history fabricated')
            if game.headers.get('Variant','Standard') not in ('Standard','Chess'):raise ValueError('Only standard-chess PGN import is supported')
            board=game.board();initial=board.fen(en_passant='fen');moves=[]
            if not board.is_valid():raise ValueError('Invalid PGN starting state')
            for move in game.mainline_moves():
                if move not in board.legal_moves:raise ValueError('Illegal move in imported PGN')
                moves.append(move.uci());board.push(move)
            identity=digest([source,initial,moves,dict(game.headers)])
            games.append(dict(id='imported-game-'+identity[:24],source_collection=source,source=source,
                initial_fen=initial,moves=moves,final_fen=board.fen(en_passant='fen'),headers=dict(game.headers),
                original_game_identifier=game.headers.get('Site'),complete=game.headers.get('Result','*')!='*',
                legal_replay_verified=True,provenance='User-supplied PGN converted in the explicit offline preparation boundary.'))
    if not games:raise ValueError('No games in PGN')
    return dict(schema='prepared-PGN-events-v10',games=games,oracle_scope='Reference library used only for this offline import/validation step; production replay consumes event records without importing it.',
        source=source,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),complete_games=sum(g['complete'] for g in games))
