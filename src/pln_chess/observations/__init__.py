"""Lossy categorical sensing. No AND reduction, attack test, or legality gate."""
from __future__ import annotations
from pln_chess.domain import inside
from pln_chess.spatial import geometry, ray_cells, delta, oriented
from pln_chess.common import digest, canonical
from pln_chess.pln import TV
from .ontology import Proposition

SENSOR_TV=TV(1.0,0.99)  # Exact FEN read; evidential reliability assumption, not empirically calibrated.

def occupancy(position,square,owner):
    if not inside(square): return 'Boundary'
    if square in position.unknown_squares: return 'Unknown'
    piece=position.at(square)
    if piece is None: return 'Empty'
    return 'Friendly' if piece.owner==owner else 'Opponent'

def attack_observations(position,owner):
    """Every opponent-to-king relative frame, regardless of attack geometry.

    Occupancy sequence is raw; Knight/Pawn/King descriptors are not adjudicated.
    Missing king or unobserved cells remain incomplete observations.
    """
    if position is None: return []
    kings=[p for p in position.pieces if p.owner==owner and p.kind=='King']
    result=[]
    for king in kings:
        for opponent in position.pieces:
            if opponent.owner==owner: continue
            descriptor={'piece':opponent.kind,'geometry':geometry(opponent.square,king.square,opponent.owner),
                        'intermediate':[occupancy(position,s,opponent.owner) for s in ray_cells(opponent.square,king.square)]}
            result.append({'attacker_id':opponent.id,'king_id':king.id,'descriptor':descriptor,
                           'key':'attack:'+digest(descriptor)[:24]})
    return sorted(result,key=lambda a:canonical(a['descriptor']))

def observe(position,move,variant='full'):
    mover=position.at(move.start)
    if mover is None: raise ValueError('Candidate has no source piece')
    geo=geometry(move.start,move.end,mover.owner)
    path=[occupancy(position,s,mover.owner) for s in ray_cells(move.start,move.end)]
    successor=position.successor(move)
    threats=attack_observations(successor,mover.owner)
    # Distance to the owner's starting edge is a sensory boundary relation.
    start_distance=mover.square[1] if mover.owner=='White' else 7-mover.square[1]
    end_distance=move.end[1] if mover.owner=='White' else 7-move.end[1]
    rights=('KQ' if mover.owner=='White' else 'kq')
    transit=[]
    if move.effect=='castle':
        step=1 if move.end[0]>move.start[0] else -1
        from pln_chess.domain import Move
        for i in (0,1):
            state=position if i==0 else position.successor(Move(move.start,(move.start[0]+step,move.start[1])))
            transit.append([x['descriptor'] for x in attack_observations(state,mover.owner)])
    pattern={'piece':mover.kind,'geometry':geo,'promotion':move.promotion,'effect':move.effect}
    context={**pattern,'intermediate':path,'destination':occupancy(position,move.end,mover.owner),
             'destination_exists':inside(move.end),'destination_kind':position.at(move.end).kind if position.at(move.end) else None,
             'pawn_start_edge_distance':start_distance if mover.kind=='Pawn' else None,
             'pawn_end_edge_distance':end_distance if mover.kind=='Pawn' else None,
             'ep_offset':list(oriented(delta(move.start,position.ep),mover.owner)) if position.ep and mover.kind=='Pawn' else None,
             'castle_rights': [r in position.rights for r in rights] if move.effect=='castle' and position.rights_known else None,
             'castle_rook': occupancy(position,(7 if geo['offset'][0]>0 else 0,move.start[1]),mover.owner) if move.effect=='castle' else None,
             'castle_rook_kind': (position.at((7 if geo['offset'][0]>0 else 0,move.start[1])).kind if position.at((7 if geo['offset'][0]>0 else 0,move.start[1])) else None) if move.effect=='castle' else None,
             'castle_rook_path': [occupancy(position,s,mover.owner) for s in ray_cells(move.start,(7 if geo['offset'][0]>0 else 0,move.start[1]))] if move.effect=='castle' else [],
             'castle_king_edge_distance':start_distance if move.effect=='castle' else None,
             'castle_transit':transit,'postmove_opponents':[a['descriptor'] for a in threats],
             'own_king_count':sum(p.owner==mover.owner and p.kind=='King' for p in (successor.pieces if successor else ())),
             'rights_known':position.rights_known if move.effect=='castle' else None}
    if variant=='no-exposure': context.pop('postmove_opponents'); context.pop('castle_transit')
    elif variant=='no-occupancy':
        for k in ('intermediate','destination','destination_kind','castle_rook','castle_rook_path','castle_rook_kind'): context.pop(k)
    elif variant=='geometry-only': context=pattern
    elif variant=='weaker-prior': context={'piece':mover.kind,'offset':geo['offset']}
    elif variant not in ('full','no-dependence'): raise ValueError(f'Unknown representation {variant}')
    geometry_key='geometry:'+digest(pattern)[:24]
    context_key='context:'+digest(context)[:24]
    complete=not position.unknown_squares and (position.rights_known or move.effect!='castle')
    tv=SENSOR_TV if complete else TV(1.0,0.0)
    atoms=[{'predicate':'PieceType','args':[mover.id,mover.kind],'tv':SENSOR_TV.json()},
           {'predicate':'Owner','args':[mover.id,mover.owner],'tv':SENSOR_TV.json()},
           {'predicate':'SideToMove','args':[position.id,position.turn],'tv':SENSOR_TV.json()},
           {'predicate':'CandidateMove','args':[position.id,mover.id,move.id],'tv':SENSOR_TV.json()},
           {'predicate':'RelativeObservation','args':[position.id,move.id,context_key],'value':context,'tv':tv.json()}]
    for step,cell in enumerate(ray_cells(move.start,move.end),1):
        atoms.append({'predicate':'IntermediateOccupancy','args':[position.id,move.id,step,occupancy(position,cell,mover.owner)],
                      'tv':(TV(1,0) if cell in position.unknown_squares else SENSOR_TV).json()})
    atoms.extend([{'predicate':'DestinationOccupancy','args':[position.id,move.id,occupancy(position,move.end,mover.owner)],'tv':tv.json()},
                  {'predicate':'DestinationExists','args':[position.id,move.id],'tv':TV(float(inside(move.end)),0.99).json()}])
    atoms=[Proposition.from_json(atom).json() for atom in atoms]
    return {'position_id':position.id,'candidate_id':move.id,'move':move.notation,'piece':mover.kind,
            'pattern':pattern,'context':context,'key':context_key,'geometry_key':geometry_key,
            'attacks':threats,'atoms':atoms,'tv':tv.json(),'complete':complete,'variant':variant}
