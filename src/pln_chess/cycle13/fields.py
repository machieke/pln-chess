"""Reconstructed sparse query domains and separate endpoint observations."""
from dataclasses import asdict
from pln_chess.common import digest
from pln_chess.domain import square_name
from pln_chess.cycle11.fields.inference import infer_queries
from pln_chess.cycle11.fields.ontology import validate_position, snapshot_id
from pln_chess.cycle12.candidates import enumerate_concepts
from pln_chess.cycle12.ontology import CONCEPTS
from pln_chess.cycle12.graph import build_graph
from .concepts import infer_concepts
from .ontology import FIELDS


def build_state(position,actor,mover_ids,*,field_model,concept_model,fork_model,runtime,options,session,
                source,incremental=True,max_candidates=16,before=None,move=None):
    validate_position(position)
    if not incremental:
        session.fields.relations.clear()
    queries=[]
    for piece in sorted(position.pieces,key=lambda p:p.id):
        targets={}
        def add(target,family):
            if target!=piece.square:
                targets.setdefault(target,[]).append(family)
        if piece.owner==actor:
            for other in position.pieces:
                add(other.square,'defense' if other.owner==actor else 'attack')
            if piece.id in mover_ids:
                for y in range(8):
                    for x in range(8):
                        add((x,y),'mobility')
        else:
            for king in position.pieces:
                if king.owner==actor and king.kind=='King':
                    add(king.square,'king-exposure')
        for target,families in sorted(targets.items()):
            queries.append(dict(id='comparison-field-query:'+digest([piece.id,target,sorted(families)]),
                position=position,source_square=square_name(piece.square),target_square=square_name(target),
                families=sorted(set(families)),source=source))
    result=infer_queries(queries,field_model,options,runtime,session.fields)
    field=dict(schema='relative-comparison-field-v13',fen=position.fen(),position_id=position.id,
        snapshot_id=snapshot_id(position),pieces=[asdict(p) for p in position.pieces],
        unknown_squares=[list(s) for s in sorted(position.unknown_squares)],relations=result['relations'],
        model_version=field_model.version,runtime_version=runtime.version,
        selected_source_entities=sorted(mover_ids),missing_selected_entities=sorted(set(mover_ids)-{p.id for p in position.pieces}),
        execution={k:v for k,v in result.items() if k not in ('relations','model_version','runtime_version','schema')},
        query_scope=dict(actor=actor,attacks='Observed occupied opponent targets from all actor entities',
            defenses='Observed occupied friendly wards from all actor entities',exposure='Opponent influence on observed actor kings',
            mobility='Ordinary potential destinations of the two supplied candidate mover identities only',
            omission='Unknown cells, omitted targets and captured identities are not negative relationships.'))
    static_limit=max_candidates if before is None else (max_candidates+1)//2
    static=enumerate_concepts(position,max_candidates=static_limit,source=source)
    dynamic=enumerate_concepts(before,move=move,concepts=['DiscoveredAttack','DiscoveredDefense','ThreatRemoval'],
        max_candidates=max_candidates-static_limit,source=source) if before is not None else None
    cases=static['candidates']+(dynamic['candidates'] if dynamic else [])
    concepts=infer_concepts(cases,concept_model,field_model,fork_model=fork_model,
        options=options,runtime=runtime,session=session.forks)
    relevant=[]
    for concept in concepts['concepts']:
        role=CONCEPTS[concept['concept']]['roles'][0]
        piece=concept['observation']['roles'][role]['piece']
        if piece and piece['owner']==actor:
            relevant.append(concept['case_id'])
    return dict(field=field,concepts=concepts['concepts'],actor_concept_candidates=relevant,
        graph=build_graph(field,concepts['concepts']),candidate_enumeration=dict(static=static,dynamic=dynamic),
        execution=dict(field=field['execution'],concepts=concepts['execution'],
            truncated=field['execution']['truncated'] or concepts['execution']['truncated']),
        scope='Separate native endpoint proofs and bounded structural concept candidates; no legal or strategic composition.')


def profile(state):
    def counts(rows):
        return {**{status:sum(r['classification']==status for r in rows)
            for status in ('supported','contradicted','unknown','incomplete')},'queried':len(rows)}
    if state is None:
        return dict(fields={name:counts([]) for name in FIELDS},concepts={name:counts([]) for name in CONCEPTS},
            concept_scope='bounded-role-candidates')
    selected=set(state['actor_concept_candidates'])
    return dict(fields={name:counts([r for r in state['field']['relations'] if r['family']==name]) for name in FIELDS},
        concepts={name:counts([r for r in state['concepts'] if r['concept']==name and r['case_id'] in selected]) for name in CONCEPTS},
        concept_scope='bounded-role-candidates')
