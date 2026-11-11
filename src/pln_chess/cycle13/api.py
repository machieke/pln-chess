"""Explicit pairwise experiments, isolated from operational legal inference."""
from contextlib import contextmanager
from dataclasses import dataclass, asdict, fields
import copy
import time
from pln_chess.common import digest, canonical
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime, NativeError
from pln_chess.cycle8.inference import infer_moves, Cycle8Options, Session as LegalSession
from pln_chess.cycle10.temporal import replay, native_options
from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession
from pln_chess.cycle11.fields.ontology import validate_position
from pln_chess.cycle12.ontology import structural_successor
from pln_chess.cycle12.graph import compare_fields, compare_concepts
from .concepts import ForkSession
from .inference import PreferenceNativeSession, infer_preferences
from .fields import build_state, profile
from .ontology import GRAMMAR, seal


@dataclass(frozen=True)
class PreferenceOptions(FieldOptions):
    timeout_seconds: float = 600
    incremental: bool = True
    max_candidates: int = 16
    mode: str = 'operational'

    def __post_init__(self):
        super().__post_init__()
        if type(self.incremental) is not bool or type(self.max_candidates) is not int or not 0<=self.max_candidates<=32:
            raise ValueError('Invalid preference cache or concept bound')
        if self.mode not in ('operational','strict','experimental'):
            raise ValueError('Unknown legal inference mode')

    def field_options(self):
        return FieldOptions(**{f.name:getattr(self,f.name) for f in fields(FieldOptions)})


class PreferenceSession:
    def __init__(self,runtime):
        self.runtime=runtime;self.fields=FieldSession(runtime);self.forks=ForkSession(runtime)
        self.forks.starting.fields=self.fields
        self.preferences=PreferenceNativeSession(runtime);self.legal=LegalSession(runtime)


@contextmanager
def native_deadline(runtime,deadline):
    """Limit every interpreter launch even when legacy stages set their timeout."""
    original=runtime.execute
    def execute(*args,**kwargs):
        remaining=deadline-time.perf_counter()
        if remaining<=0:
            raise NativeError('Comparison request deadline exhausted')
        previous=runtime.timeout
        try:
            runtime.timeout=min(previous,remaining)
            return original(*args,**kwargs)
        finally:
            runtime.timeout=previous
    runtime.execute=execute
    try:
        yield
    finally:
        runtime.execute=original


def prepare(position,move_a,move_b,history,source,legal_model,runtime):
    position=Position.from_fen(position) if isinstance(position,str) else position
    if not isinstance(position,Position):
        raise ValueError('Supply a position or FEN')
    validate_position(position)
    if not isinstance(source,str) or not source or len(source)>512:
        raise ValueError('Invalid comparison source')
    if not all(isinstance(m,str) for m in (move_a,move_b)) or move_a==move_b:
        raise ValueError('Supply two distinct explicit candidate moves')
    moves=[find_move(position,m) for m in (move_a,move_b)]
    if any(m is None for m in moves):
        raise ValueError('Candidate outside the structural move grammar')
    for notation in (move_a,move_b):
        structural_successor(position,notation)
    receipt=None
    if history is not None:
        allowed={'initial_fen','moves','source','dependence_group','confidence','initial_trust','complete'}
        if not isinstance(history,dict) or set(history)-allowed:
            raise ValueError('Invalid supplied history fields')
        supplied={**history,'source':history.get('source',source)}
        receipt=replay(**supplied,model_version=legal_model.version,runtime_version=runtime.version,expected_fen=position.fen())
        if receipt['conflicts']:
            raise ValueError('Supplied history conflicts with the comparison position')
    movers={position.at(move.start).id for move in moves}
    descriptors={}
    for side,move in zip(('A','B'),moves):
        piece=position.at(move.start);orientation=1 if piece.owner=='White' else -1
        descriptors[side]=dict(piece=piece.kind,relative_displacement=[move.end[0]-move.start[0],orientation*(move.end[1]-move.start[1])],
            promotion=move.promotion,effect=move.effect)
    return position,moves,movers,descriptors,receipt


def legal_beliefs(position,moves,model,options,runtime,session,receipt=None):
    settings={f.name:getattr(options,f.name) for f in fields(FieldOptions) if f.name!='sensor_confidence'}
    local=Cycle8Options(**settings,mode=options.mode)
    if receipt is not None:
        local=native_options(receipt,local)
    result=infer_moves(position,model,local,runtime,moves,session.legal)
    counters=('elapsed_seconds','peak_process_rss_kib','native_invocations','cache_entries','cache_hits','cache_scope',
        'grounded_atoms','proof_bytes_estimate','scheduled_invocations','scheduler','unique_groundings','native_elapsed_seconds')
    execution={key:result.pop(key) for key in counters if key in result}
    execution.update(truncated=result['truncated'],error=result.get('error'))
    return {**result,'execution':execution,'temporal_transport':receipt}


def packet_for(states,descriptors,horizon,source,provenance,complete=True,gaps=None):
    gaps=list(gaps or [])
    for name,state in states.items():
        if state is None:
            complete=False;gaps.append('Missing required endpoint: '+name)
        else:
            complete &= not state['execution']['truncated']
            unknown=sum(r['classification'] in ('unknown','incomplete') for r in state['field']['relations'])
            if unknown:
                gaps.append(f'{name}: {unknown} unknown or incomplete queried field relations.')
            if state['field']['unknown_squares']:
                gaps.append(name+': supplied state has unknown cells; the query domain is partial.')
            if state['field']['missing_selected_entities']:
                gaps.append(name+': a tracked mover is absent from this endpoint; its removed query domain is not negative field evidence.')
            enumeration=state['candidate_enumeration']
            if any(e and e['truncated'] for e in enumeration.values()):
                gaps.append(name+': bounded concept enumeration omits candidates; omission is not negative evidence.')
    return seal(dict(schema=GRAMMAR,profiles={name:profile(states[name]) for name in ('before','A','B')},
        horizon=horizon,complete=bool(complete),gaps=gaps,source=source,provenance=copy.deepcopy(provenance),
        candidate_descriptors=descriptors))


def execution_summary(states,legal,preference,started,runtime,calls,deadline):
    parts=[]
    for state in states.values():
        if state:
            parts.extend([state['execution']['field'],state['execution']['concepts']])
    parts.extend(row['execution'] for row in legal)
    parts.append(preference['execution'])
    exhausted=time.perf_counter()>=deadline
    return dict(elapsed_seconds=time.perf_counter()-started,native_invocations=runtime.invocations-calls,
        logical_native_nodes=sum(p.get('logical_native_nodes',p.get('scheduled_invocations',0)) for p in parts),
        grounded_atoms=sum(p.get('grounded_atoms',0) for p in parts),cache_hits=sum(p.get('cache_hits',0)+p.get('relation_cache_hits',0) for p in parts),
        proof_bytes=sum(p.get('proof_bytes',p.get('proof_bytes_estimate',0)) for p in parts),
        truncated=exhausted or any(p.get('truncated',False) for p in parts),
        error='Comparison request deadline exhausted' if exhausted else next((p['error'] for p in parts if p.get('error')),None),
        budget_scope='Registered logical node limit applies to each legal, field/concept and preference stage, including warm caches. One request deadline limits all interpreter launches and subsequent stages.',
        stages=parts)


def compare_moves(position,move_a,move_b,*,legal_model,field_model,concept_model,fork_model,preference_model,
                  options=None,runtime=None,session=None,history=None,source='supplied-preference-comparison'):
    started=time.perf_counter();options=options or PreferenceOptions();runtime=runtime or Runtime(timeout=options.timeout_seconds)
    session=session or PreferenceSession(runtime)
    if session.runtime is not runtime:
        raise ValueError('Comparison session belongs to a different runtime instance')
    for model in (field_model,concept_model,fork_model,preference_model):
        model.validate(runtime)
    position,moves,movers,descriptors,receipt=prepare(position,move_a,move_b,history,source,legal_model,runtime)
    calls=runtime.invocations;deadline=started+options.timeout_seconds;states={};field_options=options.field_options()
    with native_deadline(runtime,deadline):
        legal=legal_beliefs(position,moves,legal_model,options,runtime,session,receipt)
        for side,notation in (('before',None),('A',move_a),('B',move_b)):
            if time.perf_counter()>=deadline:
                states[side]=None;continue
            current=position if notation is None else structural_successor(position,notation)
            states[side]=build_state(current,position.turn,movers,field_model=field_model,concept_model=concept_model,
                fork_model=fork_model,runtime=runtime,options=field_options,session=session,source=source,
                incremental=options.incremental,max_candidates=options.max_candidates,
                before=position if notation else None,move=notation)
        packet=packet_for(states,descriptors,1,source,dict(root_fen=position.fen(),moves=[move_a,move_b],
            history_receipt=receipt['id'] if receipt else None,
            state_graphs={name:s['graph']['id'] if s else None for name,s in states.items()}),
            complete=not legal['execution']['truncated'] and time.perf_counter()<deadline,
            gaps=['Legality beliefs remain separate and may be unknown or partial; preference cannot certify a move.'])
        preference=infer_preferences([packet],preference_model,runtime=runtime,options=field_options,session=session.preferences)
    execution=execution_summary(states,[legal],preference,started,runtime,calls,deadline)
    changes={side:compare_fields(states['before']['field'],states[side]['field']) if states['before'] and states[side] else [] for side in ('A','B')}
    concept_changes={side:compare_concepts(states['before']['concepts'],states[side]['concepts']) if states['before'] and states[side] else [] for side in ('A','B')}
    result=copy.deepcopy(preference['comparisons'][0])
    if execution['truncated']:
        result.update(status='incomplete');result['gaps'].append('The complete requested inspection did not finish within its budgets.')
    execution['elapsed_seconds']=time.perf_counter()-started
    return dict(schema='pairwise-move-inspection-v13',fen=position.fen(),moves=dict(A=move_a,B=move_b),
        legality={side:copy.deepcopy(row) for side,row in zip(('A','B'),legal['candidates'])},legal_inference=legal,
        states=states,changes=changes,concept_changes=concept_changes,packet=packet,preference=result,
        model_versions=dict(legal=legal_model.version,field=field_model.version,concept=concept_model.version,fork=fork_model.version,preference=preference_model.version),
        runtime_version=runtime.version,execution={**execution,'incremental':options.incremental},
        automatic_move_selection=False,scope='Experimental pairwise conditional evidence with independent legality beliefs and explicit incomplete strategic proof.')


def compare_pairs(position,pairs,**kwargs):
    if not isinstance(pairs,(list,tuple)) or not 1<=len(pairs)<=16 or any(not isinstance(p,(list,tuple)) or len(p)!=2 for p in pairs):
        raise ValueError('Supply one through sixteen explicit candidate pairs')
    # Validate the entire envelope before any native work.
    runtime=kwargs.get('runtime') or Runtime(timeout=(kwargs.get('options') or PreferenceOptions()).timeout_seconds)
    for a,b in pairs:
        prepare(position,a,b,kwargs.get('history'),kwargs.get('source','supplied-preference-comparison'),kwargs['legal_model'],runtime)
    options=dict(kwargs,runtime=runtime,session=kwargs.get('session') or PreferenceSession(runtime))
    return [compare_moves(position,a,b,**options) for a,b in pairs]
