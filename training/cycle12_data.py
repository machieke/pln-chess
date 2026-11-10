"""Offline, preregistered local-concept fixtures and independent references.

No production concept implementation is imported here. Reference labels are
stored separately from the input contract. Transforms/counterfactuals inherit
the entire motif family; labels and model predictions never select a split.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, replace
from itertools import combinations
from pathlib import Path

import chess

from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from pln_chess.domain import Position, Piece, parse_square, square_name
from pln_chess.spatial import ray_cells


TARGETS = {
    'Pin': 'PotentialPinAlignment',
    'Fork': 'PotentialMultipleTargetAttack',
    'DiscoveredAttack': 'NewAttackAfterSuppliedEdit',
    'DiscoveredDefense': 'NewDefenseAfterSuppliedEdit',
    'OverloadedDefender': 'CompetingDefenseObligations',
    'TrappedPiece': 'NoOrdinaryGeometricExit',
    'MultipleAttackers': 'MultipleLocalAttackSources',
    'ThreatRemoval': 'ThreatAbsentAfterSuppliedEdit',
}


def fen(pieces, turn=chess.WHITE):
    board = chess.Board(None)
    board.turn = turn
    for square, symbol in pieces.items():
        board.set_piece_at(chess.parse_square(square), chess.Piece.from_symbol(symbol))
    return board.fen(en_passant='fen')


def input_case(concept, pieces, roles, move=None):
    return dict(concept=concept, fen=fen(pieces), roles=roles, move=move,
                unknown_squares=[], source='cycle12-controlled-observation')


def reference(case):
    """Independent offline labels for named, deliberately limited targets."""
    board = chess.Board(case['fen'])
    roles = {k: chess.parse_square(v) for k, v in case['roles'].items()}
    get = lambda name: board.piece_at(roles[name])
    attacks = lambda source, target: get(source) is not None and get(target) is not None and roles[target] in board.attacks(roles[source])
    opposite = lambda a, b: get(a) is not None and get(b) is not None and get(a).color != get(b).color
    concept = case['concept']
    after = board.copy()
    legal = None
    if case['move']:
        move = chess.Move.from_uci(case['move'])
        legal = move in board.legal_moves
        after.push(move)
    details = {}
    if concept == 'Pin':
        a, m, t = (roles[k] for k in ('attacker', 'intervening', 'target'))
        removed = board.copy()
        removed.remove_piece_at(m)
        label = bool(opposite('attacker', 'intervening') and opposite('attacker', 'target')
                     and attacks('attacker', 'intervening') and not attacks('attacker', 'target')
                     and get('attacker').piece_type in (chess.ROOK, chess.BISHOP, chess.QUEEN)
                     and t in removed.attacks(a))
        details = dict(absolute_pin=bool(get('intervening') and get('target') and get('target').piece_type == chess.KING
                                         and board.is_pinned(get('intervening').color, m)),
                       target_role='king' if get('target') and get('target').piece_type == chess.KING else 'named-nonking-target',
                       legal_restriction_proved_by_conditional=False)
    elif concept == 'Fork':
        label = bool(all(attacks('attacker', t) and opposite('attacker', t) for t in ('target_a', 'target_b')))
        details = dict(target_values=None, complete_joint_native_proof=False)
    elif concept == 'MultipleAttackers':
        label = bool(all(attacks(a, 'target') and opposite(a, 'target') for a in ('attacker_a', 'attacker_b'))
                     and get('attacker_a').color == get('attacker_b').color)
    elif concept in ('DiscoveredAttack', 'DiscoveredDefense', 'ThreatRemoval'):
        a, t = roles['attacker'], roles['target']
        before_influence = bool(board.piece_at(a) and board.piece_at(t) and t in board.attacks(a))
        after_influence = bool(after.piece_at(a) and after.piece_at(t) and t in after.attacks(a))
        if concept == 'ThreatRemoval':
            label = before_influence and not after_influence
        else:
            allegiance = bool(get('attacker') and get('target') and
                              (get('attacker').color == get('target').color) == (concept == 'DiscoveredDefense'))
            label = allegiance and not before_influence and after_influence
        details = dict(before_influence=before_influence, after_influence=after_influence,
                       supplied_edit_reference_legal=legal, reference_successor_fen=after.fen(en_passant='fen'))
    elif concept == 'OverloadedDefender':
        defenses = [bool(attacks('defender', t) and not opposite('defender', t)) for t in ('ward_a', 'ward_b')]
        threats = [bool(attacks(e, t) and opposite(e, t)) for e, t in (('enemy_a', 'ward_a'), ('enemy_b', 'ward_b'))]
        label = all(defenses + threats)
        details = dict(defense_obligations=defenses, threats=threats, strategic_overload=None,
                       missing='No quantified proof that both obligations cannot be met; no material or target-value ordering.')
    elif concept == 'TrappedPiece':
        p = get('subject')
        board.turn = p.color
        moves = [m.uci() for m in board.generate_pseudo_legal_moves(from_mask=chess.BB_SQUARES[roles['subject']])
                 if not board.is_castling(m) and not board.is_en_passant(m)]
        legal_exits = [m.uci() for m in board.generate_legal_moves(from_mask=chess.BB_SQUARES[roles['subject']])]
        label = not moves
        details = dict(ordinary_geometric_exits=sorted(moves), reference_legal_exits=sorted(legal_exits),
                       strategically_trapped=None, unfavorable_exits=None,
                       missing='The conditional does not establish the quality of exits or a complete safe-mobility theorem.')
    else:
        raise ValueError(concept)
    return dict(label=bool(label), target=TARGETS[concept], details=details,
                board_valid=board.is_valid(), source='offline-python-chess-and-explicit-limited-target-contract',
                scope='Local structural supervision only; no complete strategic label or production legality gate.')


def _canonical_oriented(case):
    """Role geometry modulo D4, translation, ID and colour (pawn-safe subgroup).

    Role positions/kinds define family topology; occupancy interventions inherit
    the pre-intervention family. Distant context is deliberately absent.
    """
    p = Position.from_fen(case['fen'])
    roles = sorted(case['roles'])
    anchor = parse_square(case['roles'][roles[0]])
    owner = p.at(anchor).owner if p.at(anchor) else 'White'
    has_pawn = any(p.at(parse_square(s)) and p.at(parse_square(s)).kind == 'Pawn' for s in case['roles'].values())
    variants = []
    transforms = [lambda x, y: (x, y), lambda x, y: (-x, y)] if has_pawn else [
        lambda x, y: (x, y), lambda x, y: (-x, y), lambda x, y: (x, -y), lambda x, y: (-x, -y),
        lambda x, y: (y, x), lambda x, y: (-y, x), lambda x, y: (y, -x), lambda x, y: (-y, -x)]
    for transform in transforms:
        records = []
        for role in roles:
            square = parse_square(case['roles'][role])
            piece = p.at(square)
            dx, dy = square[0]-anchor[0], square[1]-anchor[1]
            if has_pawn and owner == 'Black': dy = -dy
            records.append([role, piece.kind if piece else 'Absent',
                            None if piece is None else piece.owner == owner, list(transform(dx, dy))])
        move = None
        if case['move']:
            a, b = parse_square(case['move'][:2]), parse_square(case['move'][2:4])
            move = [list(transform(a[0]-anchor[0], (a[1]-anchor[1])*(-1 if has_pawn and owner == 'Black' else 1))),
                    list(transform(b[0]-anchor[0], (b[1]-anchor[1])*(-1 if has_pawn and owner == 'Black' else 1))), case['move'][4:]]
        neighborhood = None
        if case['concept']=='TrappedPiece':
            # Board-edge distance and the supplied movement fan are relevant
            # local geometry, unlike distant, unqueried board contents.
            neighborhood=dict(occupied=sorted([piece.kind,piece.owner==owner,
                list(transform(piece.square[0]-anchor[0],piece.square[1]-anchor[1]))] for piece in p.pieces),
                corners=sorted(list(transform(x-anchor[0],y-anchor[1])) for x,y in ((0,0),(0,7),(7,0),(7,7))))
        variants.append(canonical([case['concept'], records, move, neighborhood]))
    return min(variants)


def canonical_motif(case):
    variants=[case]
    swaps={'Fork':(('target_a','target_b'),),
           'MultipleAttackers':(('attacker_a','attacker_b'),),
           'OverloadedDefender':(('ward_a','ward_b'),('enemy_a','enemy_b'))}
    if case['concept'] in swaps:
        roles=dict(case['roles'])
        for a,b in swaps[case['concept']]:roles[a],roles[b]=roles[b],roles[a]
        variants.append({**case,'roles':roles})
    return min(_canonical_oriented(c) for c in variants)


def generate(out):
    out = Path(out)
    groups = {}

    def family(name, split, base, variants):
        motif = canonical_motif(base)
        identifier = 'motif:'+digest(motif)
        if identifier in groups:
            assert groups[identifier]['split'] == split, (name, groups[identifier]['name'])
            return
        cases = [('base', base), *variants]
        groups[identifier] = dict(id=identifier, name=name, split=split, canonical_motif=motif,
                                 cases=cases)

    # Different ray lengths are different raw motifs. Distance pooling, if used
    # by a learner, remains an explicit representational assumption.
    lengths = [('train',1,1), ('train',1,2), ('train',2,1), ('calibration',2,2),
               ('test',1,3), ('test',3,1), ('test',2,3), ('test',3,2), ('test',1,5), ('test',2,4)]
    for symbol, step in (('R',(1,0)), ('B',(1,1)), ('Q',(1,0)), ('Q',(1,1))):
        for split, first, second in lengths:
            a = (0,0)
            m = (step[0]*first,step[1]*first)
            t = (step[0]*(first+second),step[1]*(first+second))
            for target in ('k','q'):
                names = [square_name(s) for s in (a,m,t)]
                pieces = dict(zip(names,(symbol,'n',target)))
                roles = dict(zip(('attacker','intervening','target'),names))
                base = input_case('Pin',pieces,roles)
                no_target = {k:v for k,v in pieces.items() if k != names[2]}
                own_middle = {**pieces,names[1]:'N'}
                family(f'pin-{symbol}-{step}-{first}-{second}-{target}',split,base,[
                    ('target-absent',input_case('Pin',no_target,roles)),
                    ('intervening-other-allegiance',input_case('Pin',own_middle,roles))])

    fork_shapes = [
        ('N','train',(1,2),(-1,2)), ('N','train',(1,2),(-1,-2)),
        ('N','calibration',(1,2),(2,1)), ('N','test',(1,2),(-2,1)),
        ('N','test',(1,2),(2,-1)), ('P','test',(-1,1),(1,1)),
        ('K','train',(1,0),(0,1)), ('K','calibration',(1,0),(1,1)), ('K','test',(-1,0),(1,0)),
    ]
    for kind in ('R','Q'):
        for split,a,b in [('train',1,1),('train',1,2),('calibration',2,2),('test',3,3),('test',3,2)]:
            fork_shapes.append((kind,split,(-a,0),(0,b)))
    for kind, split, da, db in fork_shapes:
        center=(3,3)
        a,b=[(center[0]+v[0],center[1]+v[1]) for v in (da,db)]
        roles=dict(attacker='d4',target_a=square_name(a),target_b=square_name(b))
        pieces={'d4':kind,roles['target_a']:'q',roles['target_b']:'r'}
        base=input_case('Fork',pieces,roles)
        one={k:v for k,v in pieces.items() if k!=roles['target_b']}
        friend={**pieces,roles['target_b']:'R'}
        family(f'fork-{kind}-{da}-{db}',split,base,[('one-target',input_case('Fork',one,roles)),
            ('friendly-second-target',input_case('Fork',friend,roles))])

    for concept, target in (('DiscoveredAttack','q'),('DiscoveredDefense','N')):
        for symbol,step in (('R',(1,0)),('B',(1,1)),('Q',(1,0)),('Q',(1,1))):
            for split,first,second in lengths:
                m=(first*step[0],first*step[1]);t=((first+second)*step[0],(first+second)*step[1])
                off=(m[0],m[1]+1) if step==(1,0) else (m[0]+1,m[1])
                roles=dict(attacker='a1',mover=square_name(m),target=square_name(t))
                pieces={'a1':symbol,roles['mover']:'R',roles['target']:target}
                move=roles['mover']+square_name(off)
                base=input_case(concept,pieces,roles,move)
                # A second observed obstruction prevents the newly opened ray.
                ray=ray_cells((0,0),t)
                extra=next((s for s in ray if s!=m),None)
                variants=[]
                if extra:
                    variants.append(('remaining-obstruction',input_case(concept,{**pieces,square_name(extra):'p'},roles,move)))
                # The move may be a structural intervention, not legal chess.
                # The reference and runtime are required to say so explicitly.
                family(f'{concept}-{symbol}-{step}-{first}-{second}',split,base,variants)

    for split,a,b in lengths:
        # Independent attackers approach a target along different relative rays.
        target=(a,0); second=(a,b)
        roles=dict(attacker_a='a1',attacker_b=square_name(second),target=square_name(target))
        pieces={'a1':'R',roles['attacker_b']:'Q',roles['target']:'n'}
        base=input_case('MultipleAttackers',pieces,roles)
        family(f'multiple-{a}-{b}',split,base,[('one-source',input_case('MultipleAttackers',
            {k:v for k,v in pieces.items() if k!=roles['attacker_b']},roles))])
        # Defense and opposing threats are separate obligations, not overload.
        roles=dict(defender='a1',ward_a=square_name((a,0)),ward_b=square_name((0,b)),
                   enemy_a=square_name((a,7)),enemy_b=square_name((7,b)))
        pieces={'a1':'Q',roles['ward_a']:'N',roles['ward_b']:'R',roles['enemy_a']:'r',roles['enemy_b']:'q'}
        base=input_case('OverloadedDefender',pieces,roles)
        family(f'obligations-{a}-{b}',split,base,[('one-obligation',input_case('OverloadedDefender',
            {k:v for k,v in pieces.items() if k!=roles['enemy_b']},roles))])

    for split,first,second in lengths:
        end=first+second
        roles=dict(attacker='a1',target=square_name((end,0)),mover=square_name((first,1)))
        pieces={'a1':'r',roles['target']:'Q',roles['mover']:'R'}
        move=roles['mover']+square_name((first,0))
        base=input_case('ThreatRemoval',pieces,roles,move)
        irrelevant=roles['mover']+square_name((first,2))
        family(f'threat-removal-{first}-{second}',split,base,[('irrelevant-edit',input_case('ThreatRemoval',pieces,roles,irrelevant))])

    # Trapping labels deliberately concern ordinary geometric exits only.
    # All exact symmetric locations belong to one canonical role family below;
    # boundary topology is explicitly part of the family for this local domain.
    for kind in ('N','B','R'):
        for split,source in [('train','a1'),('train','b2'),('calibration','c3'),('test','d4')]:
            board=chess.Board(None);s=chess.parse_square(source)
            board.set_piece_at(s,chess.Piece.from_symbol(kind))
            if kind=='N': dest=list(board.attacks(s))
            else:
                x,y=chess.square_file(s),chess.square_rank(s)
                dirs=[(dx,dy) for dx in (-1,0,1) for dy in (-1,0,1) if (dx or dy) and
                      ((dx and dy) if kind=='B' else (not dx or not dy))]
                dest=[chess.square(x+dx,y+dy) for dx,dy in dirs if 0<=x+dx<8 and 0<=y+dy<8]
            pieces={source:kind,**{chess.square_name(t):'P' for t in dest}}
            roles={'subject':source}
            # Named surrounding occupancy supplies a local family, not distant
            # context; include these slots in canonical topology only.
            base=input_case('TrappedPiece',pieces,roles)
            escape={k:v for k,v in pieces.items() if k!=chess.square_name(dest[0])}
            name=f'trapped-{kind}-{source}'
            topology=canonical_motif(base)
            identifier='motif:'+digest(['TrappedPiece',topology])
            groups[identifier]=dict(id=identifier,name=name,split=split,canonical_motif=topology,
                cases=[('base',base),('escape-cell',input_case('TrappedPiece',escape,roles))])

    records=[]
    for group in groups.values():
        for variant,case in group['cases']:
            row=dict(id=group['name']+'/'+variant,split=group['split'],structural_family=group['id'],
                     dependence_group=group['id'],transformation_lineage=[group['id']],input=case,
                     reference=reference(case),variant=variant)
            row['evidence_id']='concept-observation:'+digest(row)
            records.append(row)
    payload=dict(schema=12,inputs_created_without_model_predictions=True,
        records=records,families=[{k:v for k,v in g.items() if k!='cases'} for g in groups.values()],
        targets=TARGETS,scope='Controlled local motifs; many omit kings and are explicitly structural contexts, not valid full games.',
        special_holdout='All pawn fork motifs are held out as one family. No independent pawn-fork training equivalent is introduced to force a successful transfer.',
        reference_implementation_sha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest())
    payload['hash']=digest(payload)
    write_json(out/'datasets/concepts.json',payload)
    counts=Counter((r['split'],r['input']['concept'],str(r['reference']['label'])) for r in records)
    summary=dict(dataset_hash=payload['hash'],records=len(records),families=len(groups),
        counts={'/'.join(k):v for k,v in sorted(counts.items())},
        families_by_split=dict(Counter(g['split'] for g in groups.values())),
        no_model_predictions_used=True,canonical_family_overlap=[])
    assert summary['families_by_split']['test']>=10
    write_json(out/'datasets/concepts-registration.json',summary)
    print(summary,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    generate(parser.parse_args().out)
