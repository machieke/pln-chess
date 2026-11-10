"""Separate native field snapshots and explicitly diagnostic structural deltas."""
from dataclasses import replace, asdict
from pln_chess.common import ROOT, digest
from pln_chess.domain import Position, square_name
from pln_chess.pln import Runtime
from .inference import build_field, FieldOptions, FieldSession
from .ontology import snapshot_id


def compare_candidate(position,move,field_model,*,legal_checkpoint=None,history_input=None,
                      options=None,runtime=None,families=None,source_ids=None,legal_mode='operational'):
    from pln_chess.api import find_move, explain_move
    from pln_chess.cycle8.inference import Cycle8Options
    from pln_chess.cycle8.model import PromotionModel
    position=Position.from_fen(position) if isinstance(position,str) else position
    candidate=find_move(position,move) if isinstance(move,str) else move
    if candidate is None:raise ValueError('Candidate is outside the structural grammar')
    successor=position.successor(candidate)
    if successor is None:raise ValueError('Candidate has no in-board structural successor')
    # Unknown source contents cannot become observed by applying a hypothetical
    # edit. This also covers the second entity relocated during castling.
    unknown=set(position.unknown_squares)
    old_entities={p.id:p for p in position.pieces}
    for piece in successor.pieces:
        old=old_entities.get(piece.id)
        if old and old.square in unknown:unknown.add(piece.square)
    successor=replace(successor,unknown_squares=tuple(sorted(unknown)))
    options=options or FieldOptions()
    runtime=runtime or Runtime(timeout=options.timeout_seconds)
    legal=legal_checkpoint or ROOT/'artifacts/cycle10/model/C10-default.json'
    if not isinstance(legal,PromotionModel):legal=PromotionModel.load(legal,runtime)
    history=None
    if history_input:
        if history_input.get('schema') in ('temporal-transport-v10','temporal-transport-v11'):
            history=history_input
        elif 'claims' in history_input:
            from pln_chess.cycle11.temporal import replay_claims
            history=replay_claims(**{**history_input,'model_version':legal.version,'runtime_version':runtime.version})
        else:
            from pln_chess.cycle10.temporal import replay
            history=replay(**{**history_input,'model_version':legal.version,'runtime_version':runtime.version})
    # The field budget never makes the independent legal proof look supported.
    legal_result=explain_move(position,candidate,legal,options=Cycle8Options(timeout_seconds=options.timeout_seconds,
        max_native_invocations=options.max_native_invocations),runtime=runtime,temporal_evidence=history,mode=legal_mode)
    session=FieldSession(runtime)
    context='supplied-field-comparison'
    before=build_field(position,field_model,options=options,runtime=runtime,session=session,source=context,families=families,source_ids=source_ids)
    after=build_field(successor,field_model,options=options,runtime=runtime,session=session,source=context,families=families,source_ids=source_ids)
    first={r['relation_id']:r for r in before['relations']}
    second={r['relation_id']:r for r in after['relations']}
    differences=[]
    fields=('classification','raw_stv','rule_id','relative_displacement','target_square','source_square','observation_id')
    def endpoint(record):
        if record is None:return None
        return {key:record[key] for key in ('relation_id','family','source_entity','target_entity','source_square','target_square',
            'classification','raw_stv','relative_displacement','rule_id','proof_id','evidence_ids','gaps','conditional_proof_complete')}
    for identifier in sorted(first.keys()|second.keys()):
        a,b=first.get(identifier),second.get(identifier)
        if a is not None and b is not None and all(a[f]==b[f] for f in fields):continue
        transition=('absent' if a is None else a['classification'])+'-to-'+('absent' if b is None else b['classification'])
        differences.append(dict(relation_id=identifier,family=(a or b)['family'],transition=transition,
            before=endpoint(a),after=endpoint(b),change_truth_value=None,proof_status='host-diagnostic',
            scope='Comparison of separate conditional proofs. Missing relations are not false; this change has no native truth value.'))
    new_entities={p.id:p for p in successor.pieces}
    changed_cells=sorted({p.square for p in position.pieces if new_entities.get(p.id)!=p}|
        {p.square for p in successor.pieces if old_entities.get(p.id)!=p})
    effects=dict(kind=candidate.effect,move=candidate.notation,
        removed_entities=[asdict(p) for identifier,p in old_entities.items() if identifier not in new_entities],
        moved_entities=[dict(entity=identifier,before=asdict(old_entities[identifier]),after=asdict(p))
            for identifier,p in new_entities.items() if identifier in old_entities and p!=old_entities[identifier]],
        changed_cells=[square_name(s) for s in changed_cells],rights_before=position.rights,rights_after=successor.rights,
        ep_before=position.ep,ep_after=successor.ep,scope='Host structural edit, not a native conclusion of legal play.')
    certificate=dict(before_snapshot=snapshot_id(position),after_snapshot=snapshot_id(successor),move=candidate.notation,
        candidate_classification=legal_result['candidate']['classification'],candidate_proof_id=digest(legal_result['candidate']['proof_trace']),
        legal_model_version=legal.version,field_model_version=field_model.version,runtime_version=runtime.version,
        successor_status='hypothetical-structural-successor')
    certificate['id']=digest(certificate)
    return dict(schema='relative-field-comparison-v11',candidate=legal_result['candidate'],legal_execution={k:v for k,v in legal_result.items() if k!='candidate'},
        before=before,after=after,differences=differences,structural_effects=effects,comparison_certificate=certificate,
        temporal_transport=history,strategic_score=None,move_ranking=None,native_change_propositions=False,
        scope='Independent native conditional fields around a hypothetical structural edit. No combined safety theorem or strategic evaluation.')
