"""Bounded structural role enumeration, never a strategic or legal verdict."""
from dataclasses import asdict
from itertools import combinations, product

from pln_chess.common import digest
from pln_chess.domain import Position, square_name
from pln_chess.hypotheses import offsets
from pln_chess.cycle11.fields.ontology import validate_position
from .ontology import CONCEPTS, structural_successor


def enumerate_concepts(position,*,move=None,concepts=None,source='supplied-concept-context',max_candidates=32,source_ids=None):
    position=Position.from_fen(position) if isinstance(position,str) else position;validate_position(position)
    if type(max_candidates) is not int or not 0<=max_candidates<=64:raise ValueError('Concept candidate limit must be between 0 and 64')
    selected=tuple(concepts or CONCEPTS)
    if len(set(selected))!=len(selected) or any(c not in CONCEPTS for c in selected):raise ValueError('Invalid concept selection')
    if move is not None:structural_successor(position,move)
    pieces=sorted(position.pieces,key=lambda p:p.id);selected_ids=set(source_ids) if source_ids is not None else {p.id for p in pieces}
    fans={p.id:{(dx,-dy if p.kind=='Pawn' and p.owner=='Black' else dy) for dx,dy in offsets(p.kind)} for p in pieces}
    def reaches(a,b):return (b.square[0]-a.square[0],b.square[1]-a.square[1]) in fans[a.id]
    def roles(**values):return {k:square_name(v.square) for k,v in values.items()}
    mover=position.at((ord(move[0])-97,int(move[1])-1)) if move else None
    def generate(concept):
        if concept=='TrappedPiece':
            for p in pieces:
                if p.id in selected_ids:yield roles(subject=p)
        elif concept=='Fork':
            for p in pieces:
                if p.id not in selected_ids:continue
                for a,b in combinations([q for q in pieces if q.owner!=p.owner and reaches(p,q)],2):
                    yield roles(attacker=p,target_a=a,target_b=b)
        elif concept=='Pin':
            for p in pieces:
                if p.kind not in ('Bishop','Rook','Queen') or p.id not in selected_ids:continue
                targets=[q for q in pieces if q.owner!=p.owner and reaches(p,q)]
                for a,b in product(targets,repeat=2):
                    dx,dy=a.square[0]-p.square[0],a.square[1]-p.square[1]
                    ex,ey=b.square[0]-p.square[0],b.square[1]-p.square[1]
                    if dx*ey==dy*ex and dx*ex+dy*ey>0 and max(abs(dx),abs(dy))<max(abs(ex),abs(ey)):
                        yield roles(attacker=p,intervening=a,target=b)
        elif concept=='MultipleAttackers':
            for target in pieces:
                for a,b in combinations([p for p in pieces if p.owner!=target.owner and reaches(p,target)],2):
                    if a.id in selected_ids or b.id in selected_ids:yield roles(attacker_a=a,attacker_b=b,target=target)
        elif concept=='OverloadedDefender':
            for p in pieces:
                if p.id not in selected_ids:continue
                for a,b in combinations([q for q in pieces if q.id!=p.id and q.owner==p.owner and reaches(p,q)],2):
                    enemies_a=[q for q in pieces if q.owner!=p.owner and reaches(q,a)]
                    enemies_b=[q for q in pieces if q.owner!=p.owner and reaches(q,b)]
                    for ea,eb in product(enemies_a,enemies_b):yield roles(defender=p,ward_a=a,ward_b=b,enemy_a=ea,enemy_b=eb)
        elif mover is not None:
            for p in pieces:
                if p.id not in selected_ids:continue
                for target in pieces:
                    if p.id==target.id:continue
                    same=p.owner==target.owner
                    if (concept=='DiscoveredDefense')!=same:continue
                    if reaches(p,target):yield roles(attacker=p,mover=mover,target=target)
    iterators={c:iter(generate(c)) for c in selected};result=[];exhausted=set()
    # Round-robin selection gives every requested family an opportunity within the bound.
    while len(result)<=max_candidates and len(exhausted)<len(selected):
        for concept,iterator in iterators.items():
            if concept in exhausted:continue
            try:bindings=next(iterator)
            except StopIteration:exhausted.add(concept);continue
            case=dict(concept=concept,fen=position.fen(),roles=bindings,source=source,
                pieces=[asdict(p) for p in position.pieces],unknown_squares=[list(s) for s in position.unknown_squares])
            if concept in ('DiscoveredAttack','DiscoveredDefense','ThreatRemoval'):case['move']=move
            case['id']='enumerated-concept:'+digest(case);result.append(case)
            if len(result)>max_candidates:break
    return dict(candidates=result[:max_candidates],truncated=len(result)>max_candidates,requested_families=list(selected),
        structural_selection_only=True,strategic_verdicts=False,complete_candidate_population=len(exhausted)==len(selected),
        scope='Bounded relative geometry and named roles select queries. Occupancy, learned evidence, legality and strategic value are not decided by enumeration; an omitted candidate is not negative evidence.')
