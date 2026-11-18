"""Outcome-blind structural census; raw antecedent qualification only.

No attack, clearance-measurement, native model or prediction calls are permitted
in this selector. A direction holdout is fixed before inference.
"""
import copy
from collections import Counter
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from .records import record, sha

SOURCE = ROOT/'artifacts/cycle10/sources/tcec-season26-divisionp/tcec-season26-divisionp.pgn'
REGISTER = ROOT/'artifacts/cycle19/corpus-registration.json'
DIRECTIONS = ('+x', '+y', '-x', '-y')


def roots():
    return read_json(REGISTER)['roots']


def root_record(game, moves, board, game_id, index, ply, a, t, direction):
    import chess
    ident = 'c19root_' + game_id[:20]
    entity = lambda square: 'entity_' + digest([game_id, square])[:20]
    state = dict(id='state_'+digest([game_id, ply])[:24], root=ident,
        actor='white' if board.turn else 'black',
        history='history_'+digest([game_id, [m.uci() for m in moves[:ply]]])[:24], unknown=[],
        pieces=[dict(id=entity(s), kind=chess.piece_name(p.piece_type),
            owner='white' if p.color else 'black', cell=[chess.square_file(s), chess.square_rank(s)])
            for s, p in sorted(board.piece_map().items())])
    return dict(id=ident, source_collection='tcec-season26-divisionp',
        source_ancestry='tcec_game_'+game_id, game_identity=game_id, game_index=index,
        ply=ply, fen=board.fen(), source_headers=dict(game.headers),
        attacker=entity(a), target=entity(t), direction=direction, state=state,
        endpoint_locations=[[chess.square_file(a), chess.square_rank(a)],
                            [chess.square_file(t), chess.square_rank(t)]],
        source_move_prefix=[m.uci() for m in moves[:ply]],
        coarse_geometry='orthogonal-two-intervening-cells')


def census(destination=REGISTER):
    import chess.pgn
    prior = {c: read_json(ROOT/f'artifacts/cycle{c}/corpus-registration.json') for c in (15,16,17)}
    excluded = {r['game_identity'] for c in (16,17) for r in prior[c]['roots']}
    assert all(r['source_ancestry'].startswith('synthetic-') for r in prior[15])
    receipt_path = ROOT/'artifacts/cycle10/sources/tcec-season26-divisionp/receipt.json'
    receipt = read_json(receipt_path)
    assert sha(SOURCE) == receipt['downloads']['data']['sha256']
    candidates = []; log = []; seen = set()
    with SOURCE.open() as stream:
        for index in range(1,241):
            game = chess.pgn.read_game(stream)
            if game is None: break
            if game.errors: raise ValueError('Malformed source game')
            moves = list(game.mainline_moves())
            gid = digest([game.headers.get('Event'),game.headers.get('Round'),[m.uci() for m in moves]])
            if gid in excluded or gid in seen:
                log.append(dict(game_index=index, game_identity=gid,
                    status='historical-game-excluded' if gid in excluded else 'duplicate-source-game'))
                continue
            seen.add(gid); board = game.board(); natural = {}; curriculum = {}
            for ply, move in enumerate(moves,1):
                board.push(move)
                if ply < 12: continue
                pieces = board.piece_map()
                for a, piece in sorted(pieces.items()):
                    if piece.piece_type != chess.ROOK: continue
                    ax, ay = chess.square_file(a), chess.square_rank(a)
                    for t in sorted(pieces):
                        tx, ty = chess.square_file(t), chess.square_rank(t)
                        dx, dy = tx-ax, ty-ay
                        if sorted((abs(dx),abs(dy))) != [0,3]: continue
                        direction = ('+x' if dx>0 else '-x') if dx else ('+y' if dy>0 else '-y')
                        sx, sy = dx//3, dy//3
                        qualified = all(board.piece_at(chess.square(ax+i*sx,ay+i*sy)) is None for i in (1,2))
                        if direction not in natural:
                            natural[direction] = root_record(game,moves,board,gid,index,ply,a,t,direction)
                        if qualified and direction != '-y' and direction not in curriculum:
                            curriculum[direction] = root_record(game,moves,board,gid,index,ply,a,t,direction)
                if len(natural)==4 and len(curriculum)==3: break
            log.append(dict(game_index=index,game_identity=gid,status='eligible' if natural else 'no-structural-pair',
                natural_directions=sorted(natural), qualified_training_directions=sorted(curriculum)))
            if natural: candidates.append(dict(gid=gid,natural=natural,curriculum=curriculum))
            if len(candidates)>=200: break
    # Selection uses only availability, direction and the registered raw training
    # antecedent. No measured conclusion or native prediction is available here.
    training = [r for r in candidates if r['curriculum']][:48]
    used = {r['gid'] for r in training}
    remaining = [r for r in candidates if r['gid'] not in used]
    development = remaining[:24]; test = remaining[24:96]
    selected = []
    for i, row in enumerate(training):
        choices=row['curriculum']; preferred=DIRECTIONS[i%3]
        r=copy.deepcopy(choices.get(preferred,next(iter(choices.values()))))
        r.update(split='A' if i<24 else 'B', population='natural-training',
            selection='Raw empty-path antecedent curriculum; -y withheld',direction_fallback=preferred not in choices)
        selected.append(r)
    for split, rows in (('development',development),('test',test)):
        for i,row in enumerate(rows):
            choices=row['natural']; preferred='-y' if split=='test' else DIRECTIONS[i%3]
            r=copy.deepcopy(choices.get(preferred,next(iter(choices.values()))))
            r.update(split=split,population='natural-'+split,
                selection='Structural eligibility only; first pair in preferred direction, source-order fallback',
                direction_fallback=preferred not in choices)
            selected.append(r)
    value=dict(schema='cycle19-corpus-v1',source=str(SOURCE.relative_to(ROOT)),source_sha256=sha(SOURCE),
        acquisition_receipt=str(receipt_path.relative_to(ROOT)),acquisition_receipt_sha256=sha(receipt_path),
        license=receipt['source']['license'],attribution=receipt['attribution'],
        candidate_game_limit=240,eligible_root_limit=200,candidate_games=len(log),eligible_games=len(candidates),
        historical_games_excluded=sorted(excluded),historical_cycle15='84 synthetic roots; no natural source games',
        census=log,roots=selected,split_counts=dict(Counter(r['split'] for r in selected)),
        diagnostic_roots=[r['id'] for r in selected if r['split']=='test'][:12],
        target_counts=dict(training=48,development=24,test=72),
        heldout_direction='-y; absent from training, preferred on test; actual fallback is disclosed',
        selection_outcomes_accessed=False,new_to_project=False,
        project_novelty='New to Cycle15-18 consequence fits; source archive and some games may have appeared in earlier legal evaluation; supplied templates and publisher shared',
        independence='One root per game; games can share openings, engines, publisher and upstream representation')
    return record(destination,value)
