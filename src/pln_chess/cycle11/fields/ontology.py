"""Typed local observations. Occupancy and geometry do not decide influence."""
from dataclasses import asdict

from pln_chess.common import digest
from pln_chess.domain import inside, square_name, PIECES
from pln_chess.spatial import geometry, ray_cells

GRAMMAR = 'relative-potential-fields-v11'
TARGETS = dict(geometry='GeometricReachability', attack='AttackPotential', defense='DefensePotential',
              mobility='MobilityPotential', **{'king-exposure':'KingExposurePotential'})
FIELDS = ('attack', 'defense', 'mobility', 'king-exposure')
KINDS = set(PIECES.values())


def validate_position(position):
    pieces = position.pieces
    if len(pieces) > 64 or len({p.id for p in pieces}) != len(pieces) or len({p.square for p in pieces}) != len(pieces):
        raise ValueError('Field observations require unique in-board entities and occupied cells')
    if position.turn not in ('White','Black'):
        raise ValueError('Invalid observed side to move')
    for square in [p.square for p in pieces]+list(position.unknown_squares):
        if len(square) != 2 or any(type(n) is not int for n in square) or not inside(square):
            raise ValueError('Invalid observed cell coordinate')
    if any(p.kind not in KINDS or p.owner not in ('White','Black') or not isinstance(p.id,str) or not p.id for p in pieces):
        raise ValueError('Invalid typed piece observation')


def snapshot_id(position):
    return 'field-state:'+digest(dict(fen=position.fen(), pieces=[asdict(p) for p in sorted(position.pieces,key=lambda p:p.id)],
        unknown_squares=sorted(set(position.unknown_squares)), history_known=position.history_known, rights_known=position.rights_known))


def validate_descriptor(family, descriptor):
    if family not in TARGETS or not isinstance(descriptor,dict):
        raise ValueError('Unknown field family or descriptor')
    piece, motion = descriptor.get('piece'), descriptor.get('motion')
    if piece not in KINDS | {'Unknown'}:
        raise ValueError('Invalid relative source kind')
    expected = {'piece','motion'}
    if piece in ('Rook','Bishop','Queen'):
        valid_motion = motion in ('orthogonal','diagonal','offset')
    elif piece == 'Unknown':
        valid_motion = motion == 'unknown'
    else:
        valid_motion = isinstance(motion,list) and len(motion)==2 and all(type(n) is int and -7<=n<=7 for n in motion)
        if valid_motion:
            valid_motion = motion != [0,0] and motion[0]>=0 and (piece=='Pawn' or 0<=motion[0]<=motion[1])
    if not valid_motion:
        raise ValueError('Invalid relative motion category')
    if family != 'geometry':
        expected |= {'intermediate_occupancy','destination'}
        if descriptor.get('intermediate_occupancy') not in ('empty','occupied','unknown'):
            raise ValueError('Invalid intermediate occupancy category')
        destination = descriptor.get('destination')
        if not isinstance(destination,dict) or set(destination)!={'allegiance','kind'}:
            raise ValueError('Invalid destination category')
        if destination not in [dict(allegiance='empty',kind='empty'),dict(allegiance='unknown',kind='unknown')]+[
                dict(allegiance=allegiance,kind=kind) for allegiance in ('friendly','opponent') for kind in ('King','other')]:
            raise ValueError('Invalid destination allegiance or type')
        if family=='mobility' and piece=='Pawn' and motion==[0,2]:
            expected.add('start_boundary_distance')
            if type(descriptor.get('start_boundary_distance')) is not int or not 0<=descriptor['start_boundary_distance']<=7:
                raise ValueError('Invalid owner-relative boundary distance')
    if set(descriptor)!=expected:
        raise ValueError('Field keys may contain only the registered relative features')
    return True


def key(family, descriptor):
    validate_descriptor(family,descriptor)
    return 'c11field:'+digest([GRAMMAR,family,descriptor])[:32]


def observe_relation(position, piece, target, family, *, source='supplied-field-context'):
    if family not in TARGETS:
        raise ValueError('Unknown field family')
    if not isinstance(source,str) or not source.strip():
        raise ValueError('An observation provenance source is required')
    target = tuple(target)
    if piece is None or position.at(piece.square)!=piece or not inside(target) or target==piece.square:
        raise ValueError('A field query requires an observed source and a distinct in-board target')
    unknown = set(position.unknown_squares)
    shape = geometry(piece.square,target,piece.owner)
    dx,dy = shape['offset']
    source_known = piece.square not in unknown
    kind = piece.kind if source_known else 'Unknown'
    motion = (shape['family'] if kind in ('Rook','Bishop','Queen') else [abs(dx),dy] if kind=='Pawn'
              else 'unknown' if kind=='Unknown' else sorted((abs(dx),abs(dy))))
    descriptor = dict(piece=kind,motion=motion)
    dependencies, facts = [], []

    def cell(square, role, include_contents=True):
        known = square not in unknown
        occupant = position.at(square) if known and include_contents else None
        value = dict(square=list(square), role=role, observed=known if include_contents else True,
            piece=asdict(occupant) if occupant else None,
            occupancy='unknown' if include_contents and not known else 'occupied' if occupant else 'empty' if include_contents else 'coordinate-only')
        dependencies.append(value)
        facts.append(dict(predicate='SourceObservation' if role=='source' else 'IntermediateOccupancy' if role=='intermediate' else 'DestinationObservation', **value))
        return value

    cell(piece.square,'source')
    destination = position.at(target) if target not in unknown else None
    applicable, gaps = True, []
    ray = ()
    if family != 'geometry':
        endpoint = cell(target,'destination')
        if endpoint['occupancy']=='unknown':
            destination_category = dict(allegiance='unknown',kind='unknown')
        elif destination is None:
            destination_category = dict(allegiance='empty',kind='empty')
        else:
            destination_category = dict(allegiance='friendly' if destination.owner==piece.owner else 'opponent',
                kind='King' if destination.kind=='King' else 'other')
        if kind in ('Rook','Bishop','Queen') or (kind=='Pawn' and family=='mobility' and motion==[0,2]):
            ray = ray_cells(piece.square,target)
        contents = [cell(square,'intermediate') for square in ray]
        descriptor.update(destination=destination_category,
            intermediate_occupancy='unknown' if any(not value['observed'] for value in contents)
                else 'occupied' if any(value['piece'] is not None for value in contents) else 'empty')
        if family=='mobility' and kind=='Pawn' and motion==[0,2]:
            descriptor['start_boundary_distance'] = piece.square[1] if piece.owner=='White' else 7-piece.square[1]
            facts.append(dict(predicate='OwnerRelativeBoundaryDistance',value=descriptor['start_boundary_distance']))
        if family=='defense' and target not in unknown and (destination is None or destination.owner!=piece.owner):
            applicable=False
            gaps.append('Defense domain requires an observed friendly occupied endpoint; no legal recapture is inferred.')
        if family=='king-exposure' and target not in unknown and (destination is None or destination.owner==piece.owner or destination.kind!='King'):
            applicable=False
            gaps.append('King-exposure domain requires an observed opposing king; absence is not global safety.')
        special = kind=='King' and dy==0 and abs(dx)==2
        special |= kind=='Pawn' and target==position.ep and abs(dx)==1
        if family=='mobility' and special:
            applicable=False
            gaps.append('Historical special transitions are outside ordinary mobility; use the separate legal/history learner.')
            facts.append(dict(predicate='SpecialTransitionDomain',value='outside-ordinary-mobility',ep_target=list(position.ep) if position.ep else None))
    else:
        cell(target,'target-coordinate',include_contents=False)
    complete = all(value['observed'] for value in dependencies)
    if not complete:
        gaps.append('Required local observations are unknown; no joint context premise is asserted.')
    rule_id = key(family,descriptor)
    target_entity = destination.id if destination is not None and family!='geometry' else None
    relation_target = ['entity',target_entity] if family in ('defense','king-exposure') and target_entity else ['cell',list(target)]
    relation_id = 'relation:'+digest([family,piece.id,relation_target])[:32]
    payload = dict(grammar=GRAMMAR, family=family,target=TARGETS[family],descriptor=descriptor,rule_id=rule_id,
        relation_id=relation_id,source_entity=piece.id,source_square=square_name(piece.square),target_square=square_name(target),
        target_entity=target_entity,relative_displacement=shape['offset'],relative_geometry=shape,
        dependencies=dependencies,facts=facts,complete=complete,applicable=applicable,gaps=gaps,source=source,
        scope='Host-grounded relative context observation. No attack, legal-move, safety or strategic verdict is computed by this observer.')
    payload['id'] = 'observation:'+digest(payload)
    return payload
