"""Structural projections only. Semantic predicates require learned evidence."""
from pln_chess.common import digest
from pln_chess.cycle4.ontology import descriptors as previous
from pln_chess.cycle5 import SCHEMA

FAMILIES=('geometry','destination','ray','boundary','exposure','temporal')

def relation(family,descriptor,target):
    return {'id':'c5:'+digest([SCHEMA,family,target,descriptor])[:24],
            'family':family,'target':target,'descriptor':descriptor,
            'origin':'host-grounded local abstraction','composition':'not native AND'}

def descriptors(position,move,pre_frames=None):
    o=previous(position,move);c=o['context'];base=o['local_context']
    geometry={k:base[k] for k in ('piece','motion','effect','promotion')}
    for k in ('start_edge_distance','end_edge_distance'):
        if k in base:geometry[k]=base[k]
    destination={'occupancy':c['destination'],'royal_contact':c['destination_kind']=='King'}
    relations=[relation('geometry',geometry,'GeometryCompatible'),
               relation('destination',destination,'DestinationConflict'),
               relation('boundary',{'exists':c['destination_exists']},'BoundaryConflict')]
    # Per-cell raw occupancy; no sensor decides whether a chess path is blocked.
    relations.extend(relation('ray',{'piece':o['piece'],'effect':move.effect,'occupancy':cell['occupancy']},'RayObstruction')
                     for cell in o['ray_motifs']['cells'])
    relations=list({r['id']:r for r in relations}.values())
    if pre_frames is None:
        from pln_chess.observations import attack_observations
        pre_frames=attack_observations(position,position.turn)
    neighborhood={'signed_displacement':c['geometry']['offset'],'owner_forward':position.turn,
                  'geometry':c['geometry'],'source_occupancy':o['piece'],'destination':destination,
                  'ray_cells':o['ray_motifs']['cells'],
                  'pre_move_opponent_frames':[a['descriptor'] for a in pre_frames],
                  'opponent_frames':[{'phase':a['phase'],'descriptor':a['relation']['descriptor']} for a in o['attack_relations']]}
    return {**o,'typed_relations':relations,'relative_neighborhood':neighborhood,
            'fine_combination':digest(base),'abstract_combination':digest([geometry,destination,base['ray_contents']]),
            'hierarchy':{'sensor':o['factored_premises'],'abstraction':relations,
                         'refinement_policy':'No automatic refinement from heldout errors. Conflict remains visible; no generated exact-context rule.'}}
