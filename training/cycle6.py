"""Preregistered independent games and factorial evaluation; oracle boundary only."""
import random
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position,Move
from pln_chess.api import find_move
from pln_chess.spatial import translate,color_flip
from pln_chess.hypotheses import candidates
from pln_chess.cycle5.ontology import descriptors
from training.cycle4 import symmetry_key
from training.cycle5 import fixture
from dataclasses import replace

def generate(output=None):
    config=read_json(ROOT/'configs/cycle6.json');positions=[];games=[];tasks=[]
    bases=[]
    def add(family,board,move,second):bases.append((family,board.fen() if hasattr(board,'fen') else board,move,second))
    for occupancy in ('Opponent','Friendly'):
        add('knight-destination',fixture(chess.KNIGHT,'f6','h5',occupancy),'f6h5',occupancy=='Opponent')
    for piece,family in [(chess.ROOK,'rook-obstruction'),(chess.BISHOP,'bishop-obstruction')]:
        src,dst,block=('b2','g7','f6') if piece==chess.BISHOP else ('b4','h4','g4')
        for blocked in (False,True):add(family,fixture(piece,src,dst,'Empty',(block,'Opponent') if blocked else None),src+dst,not blocked)
    for occupancy in ('Opponent','Friendly'):add('queen-capture',fixture(chess.QUEEN,'b4','g4',occupancy),'b4g4',occupancy=='Opponent')
    for destination in ('Opponent','Empty'):add('pawn-capture',fixture(chess.PAWN,'c4','d5',destination),'c4d5',destination=='Opponent')
    for destination in ('Empty','Opponent'):add('pawn-forward',fixture(chess.PAWN,'c4','c5',destination),'c4c5',destination=='Empty')
    for unsafe in (False,True):add('king-exposure','3r3k/8/8/8/8/8/2K5/8 w - - 0 1' if unsafe else '7k/8/8/8/8/8/2K5/8 w - - 0 1','c2d3',not unsafe)
    for name,fen,safe in [('clear','6k1/8/8/8/8/8/8/4K2R w K - 0 1',True),('occupied','6k1/8/8/8/8/8/8/4KB1R w K - 0 1',False),('attacked','5rk1/8/8/8/8/8/8/4K2R w K - 0 1',False)]:add('castle-transit',fen,'e1g1',safe)
    for unsafe in (False,True):add('ep-exposure','7k/8/8/r4pPK/8/8/8/8 w - f6 0 2' if unsafe else '7k/8/8/5pPK/8/8/8/8 w - f6 0 2','g5f6',not unsafe)
    add('mandatory-C5-knight','2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1','f6h5',True)
    for index,(family,fen,notation,bvalue) in enumerate(bases):
        p=Position.from_fen(fen);m=find_move(p,notation);board=chess.Board(fen);assert board.is_valid(),(family,fen)
        assert m is not None
        label=chess.Move.from_uci(notation) in board.legal_moves
        name=f'c6-factorial-{index}-{family}'
        positions.append({'id':name,'family':family,'fen':fen,'focus_move':notation,'split':'adversarial','source_game':None})
        variants=[('original',p,m)]
        if p.rights=='-' and p.ep is None:
            variants.append(('file-reflection',replace(p,pieces=tuple(replace(x,square=(7-x.square[0],x.square[1])) for x in p.pieces)),replace(m,start=(7-m.start[0],m.start[1]),end=(7-m.end[0],m.end[1]))))
            variants.append(('owner-rank-flip',color_flip(p),replace(m,start=(m.start[0],7-m.start[1]),end=(m.end[0],7-m.end[1]))))
            for offset in ((1,0),(-1,0),(0,1),(0,-1)):
                try:q=translate(p,offset)
                except ValueError:continue
                mm=replace(m,start=(m.start[0]+offset[0],m.start[1]+offset[1]),end=(m.end[0]+offset[0],m.end[1]+offset[1]))
                if chess.Board(q.fen()).is_valid() and ((chess.Move.from_uci(mm.notation) in chess.Board(q.fen()).legal_moves)==label):variants.append(('translation',q,mm));break
        variants.append(('piece-ID-renaming',replace(p,pieces=tuple(replace(x,id='renamed-'+str(i)) for i,x in enumerate(reversed(p.pieces)))),m))
        # Find a distant friendly pawn that preserves the oracle outcome. This
        # is test generation, never a production veto or inference observation.
        for sq in chess.SQUARES:
            xy=(chess.square_file(sq),chess.square_rank(sq))
            if p.at(xy) or xy[1] in (0,7) or max(abs(xy[0]-m.start[0]),abs(xy[1]-m.start[1]))<4:continue
            if xy==m.end or max(abs(xy[0]-m.end[0]),abs(xy[1]-m.end[1]))<3:continue
            if (xy[0]-m.start[0])*(m.end[1]-m.start[1])==(xy[1]-m.start[1])*(m.end[0]-m.start[0]):continue
            qboard=board.copy();qboard.set_piece_at(sq,chess.Piece(chess.PAWN,board.turn))
            if qboard.is_valid() and (chess.Move.from_uci(notation) in qboard.legal_moves)==label:
                variants.append(('distant-unrelated-piece',Position.from_fen(qboard.fen(en_passant='fen')),m));break
        for kind,q,mm in variants:
            tasks.append({'id':name+'-'+kind,'base_id':name,'family':family,'variant':kind,'fen':q.fen(),'position':q,'move_object':mm,
                'move':mm.notation,'label':label,'primitive_labels':{'A':True,'B':bvalue},'source_group':'heldout-'+name,
                'descriptor':descriptors(q,mm),'transform_exclusions':['No uncertified castle/EP transforms'] if p.rights!='-' or p.ep else []})
    old=[read_json(ROOT/f'artifacts/{path}/dataset.json') for path in ('cycle2','cycle3','cycle4/datasets','cycle5/datasets')]
    blocked={symmetry_key(p['fen']) for data in old for p in data['positions']}
    for split,count in [('validation',4),('independent-games',config['new_game_count'])]:
        for i in range(count):
            seed=config['new_game_seed']+(1000 if split=='validation' else 2000)+i;rng=random.Random(seed);b=chess.Board();moves=[];gid=f'c6-{split}-{seed}'
            for ply in range(1,181):
                legal=sorted(b.legal_moves,key=lambda m:m.uci())
                if not legal:break
                m=rng.choice(legal);moves.append(m.uci());b.push(m)
                if ply in config['sample_plies']:
                    assert symmetry_key(b.fen()) not in blocked
                    assert {m.uci() for m in b.legal_moves}<={m.notation for m in candidates(Position.from_fen(b.fen()))}
                    positions.append({'id':gid+f'-ply-{ply}','family':gid,'fen':b.fen(),'focus_move':None,'split':split,'source_game':gid})
            games.append({'id':gid,'seed':seed,'split':split,'moves':moves,'final_fen':b.fen()})
    # Object-only fields support invariance tests; JSON stores full serializable
    # state so renamed IDs are not accidentally normalized by FEN round-trips.
    from dataclasses import asdict
    for t in tasks:t['position']=asdict(t['position']);t['move_object']=asdict(t['move_object'])
    result={'schema':6,'registration_hash':digest(config),'positions':positions,'games':games,'factorial_tasks':tasks,
        'leakage':{'new_sampled_game_symmetry_overlap':[],'curriculum_test_provenance_overlap':[],
                   'joint_curriculum_observations':0,'full_C4_C5_prior':'Retained for operational utility, never claimed to be novel independent-premise training.'}}
    result['hash']=digest(result)
    if output:write_json(output,result)
    return result

if __name__=='__main__':
    import sys
    d=generate(sys.argv[1]);print(d['hash'],len(d['positions']),len(d['factorial_tasks']))
