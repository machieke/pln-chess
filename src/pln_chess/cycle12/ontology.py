"""Typed relative role observations; no concept or chess-legality detector."""
from dataclasses import asdict, replace
import json
import re

from pln_chess.common import canonical, digest
from pln_chess.domain import Position, Piece, parse_square, square_name, inside
from pln_chess.hypotheses import offsets, candidates
from pln_chess.cycle11.fields.ontology import observe_relation, validate_position, snapshot_id, key as field_key

GRAMMAR='relative-role-packets-v12'
INTERACTIONS={
    'Influences':('piece','target','state'), 'Supports':('piece','friendly-entity','state'),
    'Obstructs':('occupant','relative-ray','state'), 'Exposes':('attacker','king','state'),
    'RestrictsMobility':('mobility-proposition','destination','state'),
    'RemovesDefense':('change','before-defense','after-domain','states'),
    'OpensAttack':('change','before-attack','after-attack','states'),
    'ChangesInfluence':('change','before-proposition','after-proposition','states'),
    'PersistsAcrossMove':('before-proposition','after-proposition','move'),
    'ContradictsInfluence':('negative-evidence','proposition','state'),
}
CONCEPTS={
    'Pin':dict(roles=('attacker','intervening','target'),target='PotentialPinAlignment',
        gaps=('Universal legal movement restriction is unproved.','Relative pin targets have no assigned strategic value.')),
    'Fork':dict(roles=('attacker','target_a','target_b'),target='PotentialMultipleTargetAttack',
        gaps=('The two independently inferred influences have no native conjunction proof.','Target value and forced gain are unassessed.')),
    'DiscoveredAttack':dict(roles=('attacker','mover','target'),target='NewAttackAfterSuppliedEdit',
        gaps=('Before/after comparison is not a native temporal implication.','The supplied edit is not certified legal by this concept.')),
    'DiscoveredDefense':dict(roles=('attacker','mover','target'),target='NewDefenseAfterSuppliedEdit',
        gaps=('A defense field does not establish a legal recapture.','The before/after relation has no native change theorem.')),
    'OverloadedDefender':dict(roles=('defender','ward_a','ward_b','enemy_a','enemy_b'),target='CompetingDefenseObligations',
        gaps=('Multiple obligations do not prove overload.','No quantified proof excludes every response that could meet both obligations.')),
    'TrappedPiece':dict(roles=('subject',),target='NoOrdinaryGeometricExit',
        gaps=('Ordinary local mobility is separate from safe legal mobility.','Unknown exits are not zero exits.','Exit quality and strategic trapping are unassessed.')),
    'MultipleAttackers':dict(roles=('attacker_a','attacker_b','target'),target='MultipleLocalAttackSources',
        gaps=('Two sources need not be independent evidence.','No combined attack strength or joint theorem is inferred.')),
    'ThreatRemoval':dict(roles=('attacker','mover','target'),target='ThreatAbsentAfterSuppliedEdit',
        gaps=('Removal of one local threat does not establish safety from other threats.','The change is not a native temporal implication.')),
}


def key(concept,descriptor):
    if concept not in CONCEPTS or not isinstance(descriptor,dict) or set(descriptor)!={'roles','components','topology'}:
        raise ValueError('Invalid typed concept descriptor')
    roles=descriptor['roles']
    if not isinstance(roles,dict) or set(roles)!=set(CONCEPTS[concept]['roles']):raise ValueError('Invalid concept roles')
    for value in roles.values():
        if not isinstance(value,dict) or set(value)!={'kind','allegiance'}:
            raise ValueError('Invalid relative role observation')
        if value['kind'] not in ('King','Queen','Rook','Bishop','Knight','Pawn','Piece','Unknown','Absent'):
            raise ValueError('Unknown role kind')
        if value['allegiance'] not in ('friendly','opponent','unknown','empty'):raise ValueError('Invalid role allegiance')
    if not isinstance(descriptor['components'],list) or len(descriptor['components'])>256:
        raise ValueError('Invalid local observation profile')
    for component in descriptor['components']:
        if not isinstance(component,dict) or set(component)!={'stage','source_role','target_role','family','descriptor'}:
            raise ValueError('Invalid component descriptor')
        if component['stage'] not in ('before','after','counterfactual') or component['source_role'] not in roles:
            raise ValueError('Invalid component role/stage')
        if component['target_role'] not in (*roles,'ordinary-destination'):raise ValueError('Invalid component target role')
        if component['descriptor'] is not None:field_key(component['family'],component['descriptor'])
        elif component['family'] not in ('attack','defense','mobility','king-exposure'):raise ValueError('Invalid absent-source component')
    topology=descriptor['topology']
    if concept=='Pin':
        if not isinstance(topology,dict) or set(topology)!={'direction_relation','distance_order'}:
            raise ValueError('Invalid relative topology')
        if topology['direction_relation'] not in ('same','opposed','noncollinear') or topology['distance_order'] not in ('inner','equal','outer'):
            raise ValueError('Invalid relative ordering')
    elif topology!={}:raise ValueError('Unexpected concept topology fields')
    return 'concept-rule:'+digest([GRAMMAR,concept,descriptor])


def supplied_position(case):
    unknown=case.get('unknown_squares',[])
    if not isinstance(unknown,(list,tuple)) or len(unknown)>64:raise ValueError('Invalid unknown cells')
    unknown=[parse_square(s) if isinstance(s,str) else s for s in unknown]
    position=Position.from_fen(case['fen'],unknown_squares=unknown)
    if 'pieces' in case:
        if not isinstance(case['pieces'],list) or len(case['pieces'])>64:raise ValueError('Invalid piece identities')
        pieces=tuple(Piece(**p) for p in case['pieces'])
        expected=sorted((p.kind,p.owner,p.square) for p in position.pieces)
        if sorted((p.kind,p.owner,p.square) for p in pieces)!=expected:raise ValueError('Piece identities disagree with supplied FEN')
        position=replace(position,pieces=pieces)
    validate_position(position)
    return position


def structural_successor(position,notation):
    if not isinstance(notation,str) or not re.fullmatch(r'[a-h][1-8][a-h][1-8][qrbn]?',notation):
        raise ValueError('Invalid supplied move notation')
    move=next((m for m in candidates(position) if m.notation==notation),None)
    if move is None:raise ValueError('Supplied move is outside the structural candidate grammar')
    successor=position.successor(move)
    if successor is None:raise ValueError('No in-board structural successor')
    unknown=set(position.unknown_squares);old={p.id:p for p in position.pieces}
    for p in successor.pieces:
        if p.id in old and old[p.id].square in unknown:unknown.add(p.square)
    return replace(successor,unknown_squares=tuple(sorted(unknown)))


def observe_concept(case):
    allowed={'id','concept','fen','roles','move','unknown_squares','source','pieces','suppress_observations'}
    if not isinstance(case,dict) or set(case)-allowed:raise ValueError('Unsupported concept input; labels are not observations')
    concept=case.get('concept')
    if concept not in CONCEPTS:raise ValueError('Unknown concept family')
    spec=CONCEPTS[concept];roles=case.get('roles')
    if not isinstance(roles,dict) or set(roles)!=set(spec['roles']):raise ValueError('Supply exactly the named concept roles')
    source=case.get('source','supplied-concept-context')
    if not isinstance(source,str) or not source.strip() or len(source)>512:raise ValueError('Invalid observation source')
    if 'id' in case and (not isinstance(case['id'],str) or len(case['id'])>512):raise ValueError('Invalid case identity')
    position=supplied_position(case);squares={name:parse_square(square) for name,square in roles.items()}
    if concept in ('Pin','Fork','MultipleAttackers') and len(set(squares.values()))!=len(squares):
        raise ValueError('These concept roles require distinct locations')
    if concept=='OverloadedDefender' and len({squares[n] for n in ('defender','ward_a','ward_b')})!=3:
        raise ValueError('Defense obligations require distinct defender and ward roles')
    suppress=case.get('suppress_observations',[])
    if not isinstance(suppress,(list,tuple)) or any(r not in roles for r in suppress):raise ValueError('Invalid suppressed role observation')
    unknown=set(position.unknown_squares)|{squares[r] for r in suppress}
    position=replace(position,unknown_squares=tuple(sorted(unknown)))
    states={'before':position};move=case.get('move')
    if move is not None:states['after']=structural_successor(position,move)
    if concept in ('DiscoveredAttack','DiscoveredDefense','ThreatRemoval') and move is None:
        raise ValueError('This concept requires a supplied structural move')
    if concept=='Pin':
        middle=position.at(squares['intervening'])
        states['counterfactual']=replace(position,pieces=tuple(p for p in position.pieces if middle is None or p.id!=middle.id))
    primary=spec['roles'][0];anchor=position.at(squares[primary])
    owner=anchor.owner if anchor and squares[primary] not in unknown else None
    role_facts={};role_descriptors={};complete=True;gaps=[]
    for role,square in squares.items():
        known=square not in unknown;piece=position.at(square) if known else None
        complete &= known
        role_facts[role]=dict(square=list(square),observed=known,piece=asdict(piece) if piece else None,
            occupancy='unknown' if not known else 'occupied' if piece else 'empty')
        kind='Unknown' if not known else 'Absent' if piece is None else piece.kind if role==primary or piece.kind=='King' else 'Piece'
        allegiance='unknown' if not known or (piece is not None and owner is None) else 'empty' if piece is None else 'friendly' if piece.owner==owner else 'opponent'
        role_descriptors[role]=dict(kind=kind,allegiance=allegiance)
        if not known:gaps.append('Required role observation is unknown: '+role)
    bindings={}
    for stage,state in states.items():
        entities={p.id:p for p in state.pieces};bindings[stage]={}
        for role,square in squares.items():
            original=position.at(square)
            current=entities.get(original.id) if original else None
            bindings[stage][role]=current.square if current else square
    components=[]

    def component(stage,source_role,target_role,family,expected_polarity,target_square=None):
        state=states[stage];start=bindings[stage][source_role]
        # Captured or hypothetically removed sources must not be replaced by
        # another occupant that happens to occupy their old square.
        old=position.at(squares[source_role]);piece=next((p for p in state.pieces if old and p.id==old.id),None)
        target=target_square if target_square is not None else bindings[stage][target_role]
        observation=observe_relation(state,piece,target,family,source=source) if piece and piece.square!=target else None
        components.append(dict(stage=stage,source_role=source_role,target_role=target_role,family=family,
            expected_polarity=expected_polarity,source_square=square_name(piece.square if piece else start),
            target_square=square_name(target),observation=observation,
            absent_source=piece is None,scope='Independent local field query; expected polarity is a hypothesis role, not an inferred truth value.'))

    if concept=='Pin':
        component('before','attacker','intervening','attack','positive')
        component('before','attacker','target','attack','negative')
        component('counterfactual','attacker','target','attack','positive')
        target=position.at(squares['target'])
        if target and target.kind=='King':component('counterfactual','attacker','target','king-exposure','positive')
    elif concept=='Fork':
        for target in ('target_a','target_b'):component('before','attacker',target,'attack','positive')
    elif concept=='MultipleAttackers':
        for attacker in ('attacker_a','attacker_b'):component('before',attacker,'target','attack','positive')
    elif concept=='OverloadedDefender':
        for ward,enemy in (('ward_a','enemy_a'),('ward_b','enemy_b')):
            component('before','defender',ward,'defense','positive');component('before',enemy,ward,'attack','positive')
    elif concept=='TrappedPiece':
        piece=position.at(squares['subject'])
        if piece:
            for dx,dy in offsets(piece.kind):
                if piece.kind=='King' and abs(dx)==2 and dy==0:continue
                if piece.kind=='Pawn' and piece.owner=='Black':dy=-dy
                target=(piece.square[0]+dx,piece.square[1]+dy)
                if inside(target) and not (piece.kind=='Pawn' and dx and target==position.ep):
                    component('before','subject','ordinary-destination','mobility','negative',target)
    else:
        family='defense' if concept=='DiscoveredDefense' else 'attack'
        for stage in ('before','after'):
            positive=(stage=='before')==(concept=='ThreatRemoval')
            component(stage,'attacker','target',family,'positive' if positive else 'negative')
    profiles=[];dependencies=[]
    for item in components:
        observation=item['observation']
        profiles.append(dict(stage=item['stage'],source_role=item['source_role'],target_role=item['target_role'],
            family=item['family'],descriptor=observation['descriptor'] if observation else None))
        if observation:
            complete &= observation['complete']
            if not observation['complete']:gaps.extend(observation['gaps'])
            dependencies.extend(dict(stage=item['stage'],**d) for d in observation['dependencies'])
    # A set of local profiles is an explicit supplied abstraction. It is not a
    # native conjunction and does not treat repeated fan cells as fresh evidence.
    profiles=[json.loads(s) for s in sorted({canonical(p) for p in profiles})]
    topology={}
    if concept=='Pin':
        a,m,t=(squares[r] for r in ('attacker','intervening','target'))
        u,v=(m[0]-a[0],m[1]-a[1]),(t[0]-a[0],t[1]-a[1])
        cross=u[0]*v[1]-u[1]*v[0];dot=u[0]*v[0]+u[1]*v[1]
        inner,outer=max(abs(n) for n in u),max(abs(n) for n in v)
        topology=dict(direction_relation='noncollinear' if cross else 'same' if dot>0 else 'opposed',
                      distance_order='inner' if inner<outer else 'equal' if inner==outer else 'outer')
    descriptor=dict(roles=role_descriptors,components=profiles,topology=topology)
    local=dict(grammar=GRAMMAR,concept=concept,target=spec['target'],descriptor=descriptor,rule_id=key(concept,descriptor),
        roles=role_facts,components=components,dependencies=dependencies,complete=bool(complete),
        gaps=list(dict.fromkeys(gaps)),source=source,
        observation_scope='Host-observed structural role packet. No field TVs are combined and no strategic verdict is computed.',
        pooling='Typed roles and unique local field-context profiles; sliding distances and multiplicities are supplied abstractions.')
    identifier='role-observation:'+digest(local)
    # Complete-state bindings stay outside the reusable local observation ID.
    return {**local,'id':identifier,'snapshots':{stage:dict(fen=p.fen(),pieces=[asdict(piece) for piece in p.pieces],
        unknown_squares=[list(s) for s in p.unknown_squares],snapshot_id=snapshot_id(p),
        status='hypothetical-intervening-piece-removal' if stage=='counterfactual' else 'supplied-state' if stage=='before' else 'supplied-structural-successor') for stage,p in states.items()}}


def component_queries(observation):
    states={stage:replace(Position.from_fen(state['fen'],unknown_squares=state['unknown_squares']),
        pieces=tuple(Piece(**p) for p in state['pieces'])) for stage,state in observation['snapshots'].items()}
    return [dict(id=observation['id']+':component:'+str(index),position=states[item['stage']],
        source_square=item['source_square'],target_square=item['target_square'],families=[item['family']],source=observation['source'])
        for index,item in enumerate(observation['components']) if item['observation'] is not None]
