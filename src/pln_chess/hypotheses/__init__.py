"""Finite inductive bias: geometric families plus typed relative observations."""
from pln_chess.domain import Move
from pln_chess.spatial import DIRECTIONS, add

GRAMMAR_VERSION='relative-categorical-v1'

def offsets(kind):
    if kind in ('Rook','Bishop','Queen'):
        for dx,dy in DIRECTIONS:
            if kind=='Rook' and dx and dy: continue
            if kind=='Bishop' and (not dx or not dy): continue
            for length in range(1,8): yield dx*length,dy*length
    elif kind=='Knight':
        for a,b in ((1,2),(2,1)):
            for sx in (-1,1):
                for sy in (-1,1): yield sx*a,sy*b
    elif kind=='King':
        yield from DIRECTIONS
        yield -2,0
        yield 2,0
    elif kind=='Pawn':
        yield 0,1
        yield 0,2
        yield -1,1
        yield 1,1

def candidates(position):
    for piece in position.pieces:
        if piece.owner != position.turn: continue
        for dx,dy in offsets(piece.kind):
            if piece.kind=='Pawn' and piece.owner=='Black': dy=-dy
            end=add(piece.square,(dx,dy)); effect='ordinary'
            if piece.kind=='King' and abs(dx)==2: effect='castle'
            if piece.kind=='Pawn' and dx and end==position.ep: effect='en-passant'
            promotions=('q','r','b','n') if piece.kind=='Pawn' and end[1] in (0,7) else (None,)
            for promotion in promotions:
                yield Move(piece.square,end,promotion,effect)

# Native conditional beliefs are learned on these finite-schema observations.
# No legality, blocked-path, or attacked-square result is computed here.
