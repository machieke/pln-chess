"""Frozen source episodes and dependent occupancy variants, not inference code."""
import copy
import itertools
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from research.cycle15.observations import ray
from scripts.cycle15_baseline import sha
from .records import record

SOURCE=ROOT/'artifacts/cycle10/sources/tcec-season26-divisionp/tcec-season26-divisionp.pgn'
REGISTER=ROOT/'artifacts/cycle16/corpus-registration.json'
OCCUPANCIES=tuple(''.join(p) for p in itertools.product('EOU',repeat=2))


def register(destination=REGISTER):
    import chess.pgn
    source_hash=sha(SOURCE);roots=[];seen=set();game_index=0
    with SOURCE.open() as stream:
        while len(roots)<42:
            game=chess.pgn.read_game(stream)
            if game is None:break
            game_index+=1
            if game.errors:raise ValueError('Malformed source game')
            moves=list(game.mainline_moves())
            game_hash=digest([game.headers.get('Event'),game.headers.get('Round'),[m.uci() for m in moves]])
            if game_hash in seen:continue
            seen.add(game_hash);board=game.board();chosen=None
            for ply,move in enumerate(moves,1):
                board.push(move)
                if ply<12:continue
                for a,piece in sorted(board.piece_map().items()):
                    if piece.piece_type not in (chess.ROOK,chess.BISHOP,chess.QUEEN):continue
                    for t in sorted(board.piece_map()):
                        if a==t:continue
                        shape,cells=ray([chess.square_file(a),chess.square_rank(a)],
                                        [chess.square_file(t),chess.square_rank(t)])
                        compatible=piece.piece_type==chess.QUEEN or (piece.piece_type==chess.ROOK and shape=='orthogonal') or (piece.piece_type==chess.BISHOP and shape=='diagonal')
                        if len(cells)==2 and compatible:
                            chosen=(a,t,shape,ply,board.copy());break
                    if chosen:break
                if chosen:break
            if chosen is None:continue
            a,t,shape,ply,board=chosen;index=len(roots)
            split='train' if index<12 else 'development' if index<18 else 'test'
            ident='episode_'+game_hash[:20]
            state=dict(id='state_'+digest([game_hash,ply])[:24],root=ident,actor='white' if board.turn else 'black',
                history='history_'+digest([game_hash,[m.uci() for m in moves[:ply]]])[:24],unknown=[],pieces=[
                dict(id='entity_'+digest([game_hash,square])[:20],kind=chess.piece_name(p.piece_type),
                    owner='white' if p.color else 'black',cell=[chess.square_file(square),chess.square_rank(square)])
                for square,p in sorted(board.piece_map().items())])
            roots.append(dict(id=ident,split=split,source_ancestry='tcec_game_'+game_hash,
                game_index=game_index,game_identity=game_hash,ply=ply,fen=board.fen(),
                source_headers=dict(game.headers),coarse_geometry=shape+'-two-intervening-cells',
                attacker='entity_'+digest([game_hash,a])[:20],target='entity_'+digest([game_hash,t])[:20],state=state))
    if len(roots)!=42:raise ValueError('Insufficient qualifying source episodes')
    return record(destination,dict(schema='cycle16-source-episodes-v1',source=str(SOURCE.relative_to(ROOT)),
        source_sha256=source_hash,roots=roots,selection='First compatible two-cell pair from ply 12; no reference labels',
        independence='Distinct source games, not independent openings or engine populations; variants remain dependent',
        grouping_audit=groups(roots)))


def roots():return read_json(REGISTER)['roots']


def groups(items):
    strata={split:sorted({r['coarse_geometry'] for r in items if r['split']==split}) for split in ('train','development','test')}
    seen=set(strata['train'])|set(strata['development'])
    return dict(source_episode_counts={s:sum(r['split']==s for r in items) for s in strata},
        unique_source_games=len({r['game_identity'] for r in items}),geometry_strata=strata,
        wholly_unseen_test_geometry=sorted(set(strata['test'])-seen),
        test_roots_wholly_unseen_geometry=sum(r['split']=='test' and r['coarse_geometry'] not in seen for r in items),
        arbitrary_geometry_transfer_claim=False)


def variant(root,occupancy):
    if occupancy not in OCCUPANCIES:raise ValueError('Expected two E/O/U symbols')
    state=copy.deepcopy(root['state']);lookup={p['id']:p for p in state['pieces']}
    _,cells=ray(lookup[root['attacker']]['cell'],lookup[root['target']]['cell'])
    state['pieces']=[p for p in state['pieces'] if tuple(p['cell']) not in cells]
    state['unknown']=[];state['id']='variant_'+digest([root['id'],occupancy])[:24]
    state['history']='hypothetical_'+digest([root['state']['history'],occupancy])[:24]
    for index,(cell,value) in enumerate(zip(cells,occupancy)):
        if value=='O':state['pieces'].append(dict(id=f'blocker_{index}_'+root['id'],kind='knight',owner=state['actor'],cell=list(cell)))
        if value=='U':state['unknown'].append(list(cell))
    return state


def reference(state,attacker,target):
    """Evaluation-only full completion set for relevant unknown cells."""
    import chess
    lookup={p['id']:p for p in state['pieces']};a=lookup.get(attacker);t=lookup.get(target)
    if a is None or t is None:return dict(label=None,reason='invalid query domain',completions=[])
    _,cells=ray(a['cell'],t['cell']);unknown=[tuple(c) for c in state['unknown'] if tuple(c) in cells]
    if len(unknown)>7:raise ValueError('Completion bound exceeded')
    values=[]
    for statuses in itertools.product((False,True),repeat=len(unknown)):
        board=chess.Board(None)
        for p in state['pieces']:
            board.set_piece_at(chess.square(*p['cell']),chess.Piece(getattr(chess,p['kind'].upper()),p['owner']=='white'))
        for cell,occupied in zip(unknown,statuses):
            if occupied:board.set_piece_at(chess.square(*cell),chess.Piece(chess.KNIGHT,chess.WHITE))
        values.append(chess.square(*t['cell']) in board.attacks(chess.square(*a['cell'])))
    return dict(label=values[0] if len(set(values))==1 else None,completions=values,
        reason='All relevant occupancy completions agree' if len(set(values))==1 else 'Both influence and obstruction completions exist',
        oracle='python-chess Board.attacks; evaluation only')
