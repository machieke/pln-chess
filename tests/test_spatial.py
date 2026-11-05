from dataclasses import replace
import pytest
from pln_chess.domain import Position,Move,parse_square,inside
from pln_chess.spatial import DIRECTIONS,geometry,ray_cells,oriented,translate,reflect_files,color_flip
from pln_chess.hypotheses import candidates
from pln_chess.observations import observe

FEN='8/6k1/8/8/8/2R5/2K5/8 w - - 0 1'

def test_fen_roundtrip_and_all_directions():
    p=Position.from_fen(FEN); assert p.fen()==FEN
    for offset,name in DIRECTIONS.items():
        end=(3+offset[0]*2,3+offset[1]*2)
        assert geometry((3,3),end)['direction']==name
        assert ray_cells((3,3),end)==((3+offset[0],3+offset[1]),)
    assert ray_cells((3,3),(4,5))==()

@pytest.mark.parametrize('fen',['8/8 w - - 0 1','9/8/8/8/8/8/8/8 w - - 0 1','8/8/8/8/8/8/8/8 x - - 0 1'])
def test_bad_fen(fen):
    with pytest.raises(ValueError): Position.from_fen(fen)

def test_candidates_keep_illegal_occupancy_and_boundaries():
    p=Position.from_fen('7k/8/8/8/8/8/RP6/K7 w - - 0 1')
    moves=list(candidates(p))
    assert any(m.notation=='a2b2' for m in moves)
    assert any(m.notation=='a2c2' for m in moves)
    assert any(not inside(m.end) for m in moves)

@pytest.mark.parametrize('symbol,count',[('R',28),('B',28),('Q',56),('N',8),('K',10),('P',4)])
def test_all_piece_grammars(symbol,count):
    p=Position.from_fen(f'8/8/8/8/3{symbol}4/8/8/8 w - - 0 1')
    assert len(list(candidates(p)))==count

def test_pawn_orientation_and_promotions():
    p=Position.from_fen('8/2p5/8/8/8/8/2P5/8 w - - 0 1')
    assert {m.end for m in candidates(p)}=={(2,2),(2,3),(1,2),(3,2)}
    q=replace(p,turn='Black')
    assert {oriented((m.end[0]-m.start[0],m.end[1]-m.start[1]),'Black') for m in candidates(q)}=={(0,1),(0,2),(-1,1),(1,1)}
    promotion=Position.from_fen('7k/2P5/8/8/8/8/8/K7 w - - 0 1')
    assert {m.promotion for m in candidates(promotion) if m.end==(2,7)}==set('qrbn')

def test_translation_and_identity_renaming():
    p=Position.from_fen(FEN); m=Move((2,2),(4,2)); q=translate(p,(1,0)); n=Move((3,2),(5,2))
    assert observe(p,m)['context']==observe(q,n)['context']
    renamed=replace(p,pieces=tuple(replace(piece,id='renamed'+piece.id) for piece in p.pieces))
    assert observe(p,m)['key']==observe(renamed,m)['key']
    assert reflect_files(reflect_files(p)).fen()==p.fen()
    assert color_flip(color_flip(p)).fen()==p.fen()
    with pytest.raises(ValueError): translate(p,(3,0))
    with pytest.raises(ValueError): translate(Position.from_fen('4k3/8/8/8/8/8/8/4K2R w K - 0 1'),(0,1))

def test_structural_special_successors():
    ep=Position.from_fen('7k/8/8/2Pp4/8/8/8/K7 w - d6 0 1')
    move=next(m for m in candidates(ep) if m.notation=='c5d6')
    after=ep.successor(move)
    assert after.at(parse_square('d5')) is None
    assert after.at(parse_square('d6')).kind=='Pawn'
    castle=Position.from_fen('4k3/8/8/8/8/8/8/4K2R w - - 0 1')
    move=next(m for m in candidates(castle) if m.notation=='e1g1')
    after=castle.successor(move)
    assert after.at(parse_square('f1')).kind=='Rook'  # still transformed with absent rights
    assert after.at(parse_square('g1')).kind=='King'
    promotion=Position.from_fen('7k/2P5/8/8/8/8/8/K7 w - - 0 1')
    move=next(m for m in candidates(promotion) if m.notation=='c7c8n')
    assert promotion.successor(move).at(parse_square('c8')).kind=='Knight'

def test_unknown_occupancy_not_false():
    p=Position.from_fen(FEN,unknown_squares=((3,2),))
    obs=observe(p,Move((2,2),(4,2)))
    assert obs['context']['intermediate']==['Unknown']
    assert obs['tv']['confidence']==0


def test_typed_native_proposition_contract():
    from pln_chess.observations.ontology import Proposition
    from pln_chess.pln import TV
    p=Proposition('DestinationExists',('state','move'),TV(1,.99))
    assert Proposition.from_json(p.json())==p
    with pytest.raises(ValueError): Proposition('IntermediateOccupancy',('state','move','one','Empty'),TV(1,.99))
    with pytest.raises(ValueError): Proposition('LegalMove',('only-one-argument',),TV(.5,.1))
