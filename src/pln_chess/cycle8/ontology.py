"""Typed owner-relative observations, never a chess-legality predicate."""
from pln_chess.common import digest
from pln_chess.domain import PIECES, inside
from pln_chess.cycle4.ontology import descriptors

GRAMMAR = 'relative-promotion-transition-v8'


def observe(position, move):
    mover = position.at(move.start)
    if mover is None or mover.kind != 'Pawn' or move.promotion is None:
        return None
    raw = descriptors(position, move)
    orientation = 1 if mover.owner == 'White' else -1
    destination = position.at(move.end)
    known = move.end not in position.unknown_squares
    occupancy = 'Unknown' if not known else 'Boundary' if not inside(move.end) else 'Empty' if destination is None else 'Friendly' if destination.owner == mover.owner else 'Opponent'
    destination_kind = 'Unknown' if not known else destination.kind if destination else 'Empty'
    start_distance = 7-move.start[1] if orientation == 1 else move.start[1]
    end_distance = 7-move.end[1] if orientation == 1 else move.end[1]
    dx, dy = move.end[0]-move.start[0], orientation*(move.end[1]-move.start[1])
    descriptor = {'mover': mover.kind, 'relative_displacement': [abs(dx),dy],
        'start_boundary_distance': start_distance, 'end_boundary_distance': end_distance,
        'destination_exists': inside(move.end), 'destination_occupancy': occupancy,
        'destination_kind': destination_kind, 'promotion_choice': move.promotion,
        'resulting_piece': PIECES[move.promotion], 'operation': move.effect}
    facts = [
        ('OwnerRelativeBoundary', {'start_distance':start_distance,'end_distance':end_distance}, 'host-grounded'),
        ('PawnRelativeDisplacement', {'file_magnitude':abs(dx),'forward_distance':dy}, 'host-grounded'),
        ('PromotionDestination', {'occupancy':occupancy,'kind':destination_kind,'known':known}, 'sensed'),
        ('ProposedPieceTransition', {'before':'Pawn','choice':move.promotion,'after':PIECES[move.promotion]}, 'host-grounded'),
        ('PostTransitionExposureFrames', {'frames':raw['attack_relations'],'complete':raw['complete']}, 'host-grounded'),
    ]
    propositions = [{'id':'c8fact:'+digest([position.id,move.id,name,roles])[:24],
        'predicate':name,'roles':roles,'origin':origin,'position_id':position.id,'candidate_id':move.id,
        'source':'board observation / structural successor; no legality assertion'} for name,roles,origin in facts]
    return {'descriptor':descriptor,'propositions':propositions,'complete':raw['complete'],
        'owner':mover.owner,'orientation':orientation,'signed_file_displacement':dx,
        'color_canonical':True,'file_reflection_canonical':True,
        'scope':'Single learned local transition; exposure is separately sensed and evaluated by existing native chains.',
        'legacy_local_relation':next(r for r in raw['relations'] if r['target']=='LocalAdmissibility')}


def project(descriptor, variant='C8-promotion-relative'):
    omitted = {'no-destination-context':{'destination_occupancy','destination_kind'},
               'no-choice-context':{'promotion_choice','resulting_piece'}}.get(variant, set())
    return {k:v for k,v in descriptor.items() if k not in omitted}


def key(descriptor, variant='C8-promotion-relative'):
    return 'c8:'+digest([GRAMMAR,project(descriptor,variant)])[:24]
