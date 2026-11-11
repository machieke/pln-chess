"""Validated per-request inspector adapters; teacher scores never enter inference."""
import os
from pathlib import Path
from pln_chess.common import ROOT,read_json
from pln_chess.domain import Position,parse_square
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from .model import PreferenceModel
from .concepts import ForkModel
from .api import PreferenceOptions,PreferenceSession,compare_moves
from .temporal import analyze_continuations


def output_root():
    return Path(os.environ.get('C13_OUT',ROOT/'artifacts/cycle13'))


def catalog():
    out=output_root();source=read_json(out/'datasets/source-pairs.json')
    temporal=out/'datasets/temporal-plans.json'
    plans={r['id']:r for r in read_json(temporal)['records']} if temporal.exists() else {}
    examples=[]
    for row in source['records']:
        plan=plans.get(row['id'])
        examples.append(dict(id=row['id'],fen=row['fen'],moves=row['moves'],history=row['history'],
            source=row['source']['cohort'],split=row['split'],
            branches=plan['branches'] if plan else None,response_selection=plan['response_selection'] if plan else None))
    return dict(examples=examples,models=['relational','full','temporal','empty'],
        trained_models={name:(out/f'model/C13-preference-{name}.json').exists() for name in ('relational','full','temporal')},
        scope='Registered source positions and explicit supplied continuations. Catalog entries contain no preference labels or engine scores.')


def inspect(payload,*,temporal=False):
    allowed={'fen','move_a','move_b','branches','history','unknown_squares','preference_model','mode',
        'max_invocations','timeout','sensor_confidence','max_candidates','incremental','horizons','selection_provenance'}
    if not isinstance(payload,dict) or set(payload)-allowed:
        raise ValueError('Invalid preference request fields; external labels and scores are not inference inputs')
    if not temporal and any(k in payload for k in ('branches','horizons','selection_provenance')):
        raise ValueError('Continuation fields require the bounded continuation endpoint')
    unknown=payload.get('unknown_squares',[])
    if not isinstance(unknown,list) or len(unknown)>64:
        raise ValueError('Invalid unknown-square observations')
    position=Position.from_fen(payload['fen'],unknown_squares=[parse_square(s) for s in unknown])
    options=PreferenceOptions(max_native_invocations=payload.get('max_invocations',100000),
        timeout_seconds=payload.get('timeout',900 if temporal else 600),sensor_confidence=payload.get('sensor_confidence',.99),
        max_candidates=payload.get('max_candidates',16),incremental=payload.get('incremental',True),mode=payload.get('mode','operational'))
    variant=payload.get('preference_model','temporal' if temporal else 'relational')
    if variant not in ('relational','full','temporal','empty'):
        raise ValueError('Unknown experimental preference model')
    runtime=Runtime(timeout=options.timeout_seconds);out=output_root()
    checkpoint=out/f'model/C13-preference-{variant}.json'
    preference=PreferenceModel.load(checkpoint,runtime) if variant!='empty' and checkpoint.exists() else PreferenceModel(runtime.version)
    fork_path=out/'model/C13-fork-role.json'
    models=dict(legal_model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',runtime),
        field_model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime),
        concept_model=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime),
        fork_model=ForkModel.load(fork_path,runtime) if fork_path.exists() else ForkModel(runtime.version),preference_model=preference)
    settings=dict(**models,options=options,runtime=runtime,session=PreferenceSession(runtime),
        history=payload.get('history'),source='cycle13-interactive-inspector')
    if temporal:
        result=analyze_continuations(position,payload['branches'],**settings,horizons=payload.get('horizons',(2,3)),
            selection_provenance=payload.get('selection_provenance','Explicit inspector input'))
    else:
        result=compare_moves(position,payload['move_a'],payload['move_b'],**settings)
    result['inspector_model']=dict(requested=variant,trained=bool(preference.hypotheses),version=preference.version,
        status='Learned experimental conditionals' if preference.hypotheses else 'No learned preference evidence loaded')
    return result
