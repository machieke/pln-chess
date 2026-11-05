"""Relative geometry, never chess legality."""
from dataclasses import replace
from pln_chess.domain import inside

DIRECTIONS={(0,1):'N',(1,1):'NE',(1,0):'E',(1,-1):'SE',(0,-1):'S',(-1,-1):'SW',(-1,0):'W',(-1,1):'NW'}

def delta(start,end): return end[0]-start[0],end[1]-start[1]
def add(a,b): return a[0]+b[0],a[1]+b[1]
def oriented(offset,owner): return offset[0],offset[1]*(1 if owner=='White' else -1)

def ray_cells(start,end):
    dx,dy=delta(start,end)
    if not (dx==0 or dy==0 or abs(dx)==abs(dy)) or (dx,dy)==(0,0): return ()
    length=max(abs(dx),abs(dy)); sx=(dx>0)-(dx<0); sy=(dy>0)-(dy<0)
    return tuple((start[0]+sx*i,start[1]+sy*i) for i in range(1,length))

def geometry(start,end,owner='White'):
    dx,dy=oriented(delta(start,end),owner)
    step=((dx>0)-(dx<0),(dy>0)-(dy<0))
    family=('orthogonal' if dx==0 or dy==0 else 'diagonal' if abs(dx)==abs(dy) else 'offset')
    return {'offset':[dx,dy], 'family':family,'direction':DIRECTIONS.get(step,'Zero'), 'distance':max(abs(dx),abs(dy))}

def translate(position,offset):
    if position.rights not in ('','-') or position.ep is not None:
        raise ValueError('Translations with castling/en-passant state are not assumed symmetries')
    pieces=tuple(replace(p,square=add(p.square,offset)) for p in position.pieces)
    unknown=tuple(add(s,offset) for s in position.unknown_squares)
    if any(not inside(p.square) for p in pieces) or any(not inside(s) for s in unknown):
        raise ValueError('Translation crosses board boundary')
    return replace(position,pieces=pieces,unknown_squares=unknown)

def reflect_files(position):
    if position.rights not in ('','-'):
        raise ValueError('File reflection changes standard castling semantics')
    f=lambda s:(7-s[0],s[1])
    return replace(position,pieces=tuple(replace(p,square=f(p.square)) for p in position.pieces),
                   ep=f(position.ep) if position.ep else None,unknown_squares=tuple(f(s) for s in position.unknown_squares))

def color_flip(position):
    if position.rights not in ('','-'):
        raise ValueError('Rotate/color transform requires explicit castling mapping')
    f=lambda s:(s[0],7-s[1])
    return replace(position,pieces=tuple(replace(p,square=f(p.square),owner='Black' if p.owner=='White' else 'White') for p in position.pieces),
                   turn='Black' if position.turn=='White' else 'White',ep=f(position.ep) if position.ep else None,
                   unknown_squares=tuple(f(s) for s in position.unknown_squares))
