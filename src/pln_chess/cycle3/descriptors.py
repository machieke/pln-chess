"""Relative sensing only: none of these functions decides attack or legality."""
from pln_chess.common import digest
from pln_chess.cycle2.descriptors import descriptors as previous,occupancy_motifs,motion
from pln_chess.observations import attack_observations
from pln_chess.domain import Move,inside
from pln_chess.cycle3 import SCHEMA


def relation(tier,descriptor,target='LegalMove'):
    return {'id':'c3:'+digest([SCHEMA,target,tier,descriptor])[:24],'tier':tier,'descriptor':descriptor,
            'target':target,'provenance':'host-derived','derivation':'Relative sensor projection; not a probabilistic conjunction.'}


def descriptors(position,move,variant='C3-full'):
    base_variant='no-obstruction' if variant=='no-obstruction' else 'no-exact'
    raw=previous(position,move,base_variant);c=raw['context'];piece=raw['piece']
    relations=[relation(r['tier'],r['descriptor'],r['target']) for r in raw['relations']]
    if variant=='exact-context-only':relations=[relation(6,c)]
    path={'ray_contents':raw['ray_motifs']['content_classes']}
    components=[relation(2,{'piece':piece,'motion':motion(piece,c['geometry'])},'GeometryObserved'),
                relation(2,path,'PathUnoccupied'),
                relation(3,{'destination':c['destination']},'DestinationAvailable'),
                relation(2,{'destination_exists':c['destination_exists']},'BoundaryObserved')]
    if variant=='no-obstruction':components=[r for r in components if r['target']!='PathUnoccupied']
    temporal={k:c[k] for k in ('pawn_start_edge_distance','pawn_end_edge_distance','ep_offset','castle_rights',
               'castle_rook','castle_rook_kind','castle_rook_path','castle_king_edge_distance','rights_known') if c[k] is not None}
    if move.effect in ('castle','en-passant') or move.promotion:
        components.append(relation(3,{'piece':piece,'effect':move.effect,'promotion':move.promotion,**temporal},'TemporalMoveObserved'))
    attacks=[]
    frames=[('successor',a) for a in raw['attacks']]
    if move.effect=='castle':
        direction=1 if move.end[0]>move.start[0] else -1
        for phase,state in [('origin',position),('transit',position.successor(Move(move.start,(move.start[0]+direction,move.start[1]))))]:
            frames.extend((phase,a) for a in attack_observations(state,position.turn))
    if variant not in ('C3-local','no-exposure','exact-context-only'):
        for phase,a in frames:
            d=a['descriptor'];shape={'piece':d['piece'],'motion':motion(d['piece'],d['geometry']),
                                    'ray_contents':occupancy_motifs(d['intermediate'])['content_classes']}
            attacks.append({**a,'phase':phase,'relation':relation(4,shape,'Attack')})
    missing=[]
    if move.effect=='en-passant' and not position.history_known:missing.append('Previous double push is not established by a FEN target alone.')
    if any(p.owner not in ('White','Black') for p in position.pieces):missing.append('Uncertain ownership.')
    if len({p.square for p in position.pieces})!=len(position.pieces):missing.append('Contradictory occupancy observations.')
    successor=position.successor(move)
    if inside(move.end) and (successor is None or sum(p.kind=='King' and p.owner==position.turn for p in successor.pieces)!=1):
        missing.append('Incomplete successor king observation.')
    raw.update(schema=SCHEMA,variant=variant,relations=relations+components,attack_relations=attacks,
               complete=raw['complete'] and not missing,missing=missing,temporal_observations=temporal,
               history={'known':position.history_known,'ep_target_asserted':position.ep is not None,
                        'castling_rights_known':position.rights_known},
               composition='Independent native conditionals; no AND inference. Transit attack frames are sensed separately.')
    return raw
