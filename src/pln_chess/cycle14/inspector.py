"""Opt-in inspector inputs and durable proof retrieval, without teacher access."""
import os
from pathlib import Path

from pln_chess.common import ROOT,read_json
from pln_chess.domain import Position,parse_square
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle13.concepts import ForkModel
from pln_chess.cycle13.model import PreferenceModel as PreviousModel
from pln_chess.cycle13.api import PreferenceOptions,PreferenceSession
from .model import PreferenceModel
from .api import compare_moves,retrieve
from .temporal import analyze_continuations
from .proofs import ProofStore


def output_root():return Path(os.environ.get('C14_OUT',ROOT/'artifacts/cycle14'))
def store_path():return Path(os.environ.get('C14_PROOF_STORE',ROOT/'.runtime/cycle14/proofs.sqlite'))


def catalog():
    out=output_root();registry=read_json(out/'model/registry.json') if (out/'model/registry.json').exists() else None
    models=['frozen-c13','empty']+(['primary-immediate','primary-temporal'] if registry else [])
    examples=[dict(id='controlled-relative-rook',fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
        moves=['a1a2','a1b1'],history=None,source='Controlled structural inspection',split='diagnostic',
        branches={'A':['a1a2','e8e7','a2a3'],'B':['a1b1','e8f7','b1b2']},
        response_selection='Explicit controlled supplied lines; no optimal-response claim.')]
    data=read_json(out/'datasets/source-pairs.json')
    plans={r['id']:r for r in read_json(out/'datasets/temporal-plans.json')['records']} if (out/'datasets/temporal-plans.json').exists() else {}
    for row in data['records']:
        if row['split'] not in ('train','historical-test','historical-calibration'):continue
        plan=plans.get(row['id'])
        examples.append(dict(id=row['id'],fen=row['fen'],moves=row['moves'],history=row['history'],
            source=row['source']['cohort'],split=row['split'],branches=plan['branches'] if plan else None,
            response_selection=plan['response_selection'] if plan else None))
    return dict(schema='compact-inspector-catalog-v14',models=models,examples=examples,
        scope='Source observations only; new final-test groups remain excluded from interactive development.')


def inspect(payload,*,temporal=False,store=None):
    allowed={'fen','move_a','move_b','branches','history','unknown_squares','preference_model','mode',
        'max_invocations','timeout','sensor_confidence','max_candidates','incremental','horizons','selection_provenance','view'}
    if not isinstance(payload,dict) or set(payload)-allowed:raise ValueError('Invalid compact request fields; reference labels and scores are not inference inputs')
    if not temporal and any(k in payload for k in ('branches','horizons','selection_provenance')):
        raise ValueError('Continuation fields require the continuation endpoint')
    unknown=payload.get('unknown_squares',[])
    if not isinstance(unknown,list) or len(unknown)>64:raise ValueError('Invalid unknown observations')
    position=Position.from_fen(payload['fen'],unknown_squares=[parse_square(s) for s in unknown])
    options=PreferenceOptions(max_native_invocations=payload.get('max_invocations',100000),
        timeout_seconds=payload.get('timeout',900),sensor_confidence=payload.get('sensor_confidence',.99),
        max_candidates=payload.get('max_candidates',16),incremental=payload.get('incremental',True),mode=payload.get('mode','operational'))
    runtime=Runtime(timeout=options.timeout_seconds);variant=payload.get('preference_model','frozen-c13');out=output_root()
    if variant=='empty':preference=PreviousModel(runtime.version)
    elif variant=='frozen-c13':preference=PreviousModel.load(ROOT/'artifacts/cycle13/model/C13-preference-relational.json',runtime)
    elif variant in ('primary-immediate','primary-temporal'):
        registry=read_json(out/'model/registry.json');name=registry['primary_immediate' if variant=='primary-immediate' else 'primary_temporal']
        preference=PreferenceModel.load(out/registry['models'][name]['path'],runtime)
        if preference.version!=registry['models'][name]['version']:raise ValueError('Experimental registry identity mismatch')
    else:raise ValueError('Unknown or unavailable experimental model')
    models=dict(legal_model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',runtime),
        field_model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime),
        concept_model=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime),
        fork_model=ForkModel.load(ROOT/'artifacts/cycle13/model/C13-fork-role.json',runtime),preference_model=preference)
    own=store is None;store=store or ProofStore(store_path())
    try:
        settings=dict(**models,runtime=runtime,options=options,session=PreferenceSession(runtime),store=store,
            history=payload.get('history'),source='cycle14-interactive-inspector',view=payload.get('view','summary'))
        result=analyze_continuations(position,payload['branches'],**settings,horizons=payload.get('horizons',(2,3)),
            selection_provenance=payload.get('selection_provenance','Explicit inspector-supplied lines')) if temporal else compare_moves(position,payload['move_a'],payload['move_b'],**settings)
        result['inspector_model']=dict(requested=variant,version=preference.version,trained=bool(preference.hypotheses))
        return result
    finally:
        if own:store.close()


def proof(handle,*,view='summary',offset=0,limit=64,store=None):
    if not isinstance(handle,str) or not handle.startswith('proof-request:') or len(handle)>128:raise ValueError('Invalid durable proof handle')
    own=store is None;store=store or ProofStore(store_path())
    try:return retrieve(store,handle,view=view,offset=offset,limit=limit)
    finally:
        if own:store.close()
