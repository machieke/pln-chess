"""Experimental inspector contracts, separate from legal inference/defaults."""
import os
from pathlib import Path
from pln_chess.common import ROOT, read_json
from pln_chess.domain import Position, parse_square
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle11.fields.ontology import FIELDS, TARGETS
from .model import ConceptModel
from .ontology import CONCEPTS
from .inference import infer_concepts
from .candidates import enumerate_concepts
from .incremental import IncrementalFieldSession, structural_successor
from .graph import build_graph, compare_fields
from .temporal import replay_fields


def output_root():return Path(os.environ.get('C12_OUT',ROOT/'artifacts/cycle12'))


def _models(payload,runtime):
    field=payload.get('field_model','trained');concept=payload.get('concept_model','trained')
    if field not in ('trained','empty') or concept not in ('trained','empty'):raise ValueError('Unknown experimental model selector')
    return (FieldModel.load(ROOT/f'artifacts/cycle11/model/C11-field-{field}.json',runtime),
            ConceptModel.load(output_root()/f'model/C12-concept-{concept}.json',runtime))


def _options(payload):
    return FieldOptions(max_native_invocations=payload.get('max_invocations',100000),timeout_seconds=payload.get('timeout',180),
        sensor_confidence=payload.get('sensor_confidence',.99))


def inspector_catalog():
    data=read_json(output_root()/'datasets/sequences.json')
    concepts=read_json(output_root()/'datasets/concepts.json')
    return dict(examples=[r['input'] for r in data['interactions']],sequences=[r['input'] for r in data['sequences']],
        concepts=list(CONCEPTS),concept_examples=[r['input'] for name in CONCEPTS for r in
            [r for r in concepts['records'] if r['split']=='test' and r['input']['concept']==name][:8]],
        families=list(FIELDS),models=['trained','empty'],
        scope='Experimental separate fields and limited packet conditionals; no strategic score or move selection.')


def inspect_interactions(position,field_model,concept_model,*,runtime=None,options=None,candidate=None,
                         family=None,concept=None,piece=None,max_candidates=32,cases=None,source='cycle12-inspector'):
    options=options or FieldOptions();runtime=runtime or Runtime(timeout=options.timeout_seconds)
    position=Position.from_fen(position) if isinstance(position,str) else position
    families=FIELDS if family in (None,'all') else (family,)
    if any(f not in TARGETS for f in families):raise ValueError('Unknown field family')
    concepts=tuple(CONCEPTS) if concept in (None,'all') else (concept,)
    if any(c not in CONCEPTS for c in concepts):raise ValueError('Unknown concept family')
    selected=None
    if piece:
        entity=next((p for p in position.pieces if p.id==piece),None) or position.at(parse_square(piece))
        if entity is None:raise ValueError('Selected source has no supplied entity')
        selected=[entity.id]
    session=IncrementalFieldSession(runtime)
    before=session.build(position,field_model,options=options,source=source,families=families,source_ids=selected)
    after=session.build(structural_successor(position,candidate),field_model,options=options,source=source,families=families,source_ids=selected) if candidate else None
    enumeration=enumerate_concepts(position,move=candidate,concepts=concepts,source=source,
        max_candidates=max_candidates,source_ids=selected) if cases is None else dict(candidates=cases,truncated=False,
        structural_selection_only=True,scope='Explicit supplied role packets; no automatic strategic detector.')
    result=infer_concepts(enumeration['candidates'],concept_model,field_model,options=options,runtime=runtime)
    graph=build_graph(after or before,result['concepts'],before=before if after else None,move=candidate)
    return dict(schema='interaction-inspection-v12',before=before,after=after,concepts=result['concepts'],graph=graph,
        changes=compare_fields(before,after) if after else [],candidate_enumeration=enumeration,
        candidate=dict(move=candidate,status='supplied-structural-edit',legal_classification=None,planned_move=False) if candidate else None,
        model_version=concept_model.version,field_model_version=field_model.version,runtime_version=runtime.version,
        execution=dict(concepts=result['execution'],truncated=result['execution']['truncated'] or before['execution']['truncated'] or bool(after and after['execution']['truncated'])),
        strategic_score=None,scope='Native conditional proofs plus host comparisons. A supplied move is not certified legal by this experimental endpoint.')


def inspector_fields(payload):
    allowed={'fen','field_model','concept_model','family','concept','piece','candidate','unknown_squares',
        'max_invocations','timeout','sensor_confidence','max_candidates','cases'}
    if not isinstance(payload,dict) or set(payload)-allowed:raise ValueError('Invalid interaction request fields')
    unknown=payload.get('unknown_squares',[])
    if not isinstance(unknown,list) or len(unknown)>64:raise ValueError('Invalid unknown cells')
    position=Position.from_fen(payload['fen'],unknown_squares=[parse_square(s) if isinstance(s,str) else s for s in unknown])
    options=_options(payload);runtime=Runtime(timeout=options.timeout_seconds);field,concept=_models(payload,runtime)
    return inspect_interactions(position,field,concept,runtime=runtime,options=options,candidate=payload.get('candidate') or None,
        family=payload.get('family'),concept=payload.get('concept'),piece=payload.get('piece') or None,
        max_candidates=payload.get('max_candidates',32),cases=payload.get('cases'))


def inspector_evolution(payload):
    allowed={'sequence','field_model','concept_model','family','max_invocations','timeout','sensor_confidence','max_candidates'}
    if not isinstance(payload,dict) or set(payload)-allowed:raise ValueError('Invalid evolution request fields')
    options=_options(payload);runtime=Runtime(timeout=options.timeout_seconds);field,concept=_models(payload,runtime)
    family=payload.get('family','all');families=None if family=='all' else [family]
    return replay_fields(payload['sequence'],field,runtime=runtime,options=options,concept_model=concept,
        families=families,max_candidates=payload.get('max_candidates',16))
