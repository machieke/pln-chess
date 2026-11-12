"""Opt-in compact inspection: native inference plus durable host proof storage."""
from dataclasses import asdict
import time

from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle12.ontology import structural_successor
from pln_chess.cycle12.graph import compare_fields,compare_concepts
from pln_chess.cycle13.api import (PreferenceOptions,PreferenceSession,prepare,legal_beliefs,
    packet_for,execution_summary,native_deadline)
from pln_chess.cycle13.inference import infer_preferences as infer_previous
from .fields import build_state
from .proofs import ProofStore,Ref
from .ontology import enrich
from .inference import infer_preferences as infer_roles


VIEWS=('summary','proof_graph','full_archive')


def infer_preferences(packets,model,**kwargs):
    return (infer_roles if model.schema=='relative-preference-model-v14' else infer_previous)(packets,model,**kwargs)


def identity_for(position,moves,models,options,runtime,history,source,**extra):
    position=Position.from_fen(position) if isinstance(position,str) else position
    return dict(schema='compact-inspection-request-v14',position=asdict(position),moves=moves,
        model_versions={k:m.version for k,m in models.items()},runtime=runtime.manifest,
        production_code_hash=production_code_hash(),options=asdict(options),history=history,
        source=source,**extra)


def preference_summary(result):
    return {k:result[k] for k in ('status','channels','rule_id','descriptor','observation_id',
        'proof_id','evidence_ids','dependence_groups','model_version','runtime_version',
        'training_provenance','opposing_training_labels','conditional_proof_complete',
        'joint_proof_complete','proof_status','contradiction','no_preference_supported',
        'gaps','truth_value_origin','strategic_score','actionable_move','scope')}


def legal_summary(record):
    return {k:v for k,v in record.items() if k in ('move','uci','classification','raw_stv',
        'truth_value','model_version','runtime_version','proof_id','gaps','status',
        'proof_complete','truth_value_origin','effect')}


def present(store,request,view,*,offset=0,limit=64,cache_hit=False,elapsed=0):
    if view not in VIEWS:raise ValueError('Choose summary, proof_graph or full_archive')
    result={**request['summary'],'proof_handle':request['handle'],'proof_root':request['root'],
        'proof_store_schema':'pln-proof-dag-v14','view':view,
        'delivery':dict(request_cache_hit=cache_hit,elapsed_seconds=elapsed,
            native_work_reused=cache_hit,storage_kind='host-content-addressed-audit-DAG',
            original_execution_retained=True)}
    if view=='proof_graph':result['proof_graph']=store.page(request['root'],offset=offset,limit=limit)
    if view=='full_archive':result['archive']=store.archive(request['root'])
    return result


def retrieve(store,handle,*,view='summary',offset=0,limit=64):
    """Retrieve an immutable proof request, including after process restart."""
    started=time.perf_counter()
    return present(store,store.request(handle),view,offset=offset,limit=limit,
        cache_hit=True,elapsed=time.perf_counter()-started)


def compare_moves(position,move_a,move_b,*,store,legal_model,field_model,concept_model,
                  fork_model,preference_model,options=None,runtime=None,session=None,
                  history=None,source='supplied-preference-comparison',view='summary',
                  offset=0,limit=64,_prepared=False):
    if not isinstance(store,ProofStore):raise ValueError('Supply an explicit proof store')
    if view not in VIEWS:raise ValueError('Choose summary, proof_graph or full_archive')
    started=time.perf_counter();options=options or PreferenceOptions()
    runtime=runtime or Runtime(timeout=options.timeout_seconds);session=session or PreferenceSession(runtime)
    if session.runtime is not runtime:raise ValueError('Comparison session belongs to another runtime')
    models=dict(legal=legal_model,field=field_model,concept=concept_model,fork=fork_model,preference=preference_model)
    for model in (field_model,concept_model,fork_model,preference_model):model.validate(runtime)
    position,moves,movers,descriptors,receipt=prepare(position,move_a,move_b,history,source,legal_model,runtime)
    identity=identity_for(position,[move_a,move_b],models,options,runtime,history,source)
    cached=store.lookup(identity) if not _prepared else None
    if cached:return present(store,cached,view,offset=offset,limit=limit,cache_hit=True,elapsed=time.perf_counter()-started)
    calls=runtime.invocations;deadline=started+options.timeout_seconds;states={};refs={}
    field_options=options.field_options()
    with native_deadline(runtime,deadline):
        legal=legal_beliefs(position,moves,legal_model,options,runtime,session,receipt)
        for side,notation in (('before',None),('A',move_a),('B',move_b)):
            if time.perf_counter()>=deadline:
                states[side]=None;refs[side]=None;continue
            current=position if notation is None else structural_successor(position,notation)
            refs[side],states[side]=build_state(current,position.turn,movers,store=store,
                field_model=field_model,concept_model=concept_model,fork_model=fork_model,
                runtime=runtime,options=field_options,session=session,source=source,
                incremental=options.incremental,max_candidates=options.max_candidates,
                before=position if notation else None,move=notation)
        packet=packet_for(states,descriptors,1,source,dict(root_fen=position.fen(),moves=[move_a,move_b],
            history_receipt=receipt['id'] if receipt else None,
            state_graphs={name:s['graph']['id'] if s else None for name,s in states.items()}),
            complete=not legal['execution']['truncated'] and time.perf_counter()<deadline,
            gaps=['Legality beliefs remain separate and may be unknown or partial; preference cannot certify a move.'])
        role_packet=enrich(packet,states,{side:position.at(move.start).id for side,move in zip(('A','B'),moves)})
        inference_packet=role_packet if preference_model.schema=='relative-preference-model-v14' else packet
        preference=infer_preferences([inference_packet],preference_model,runtime=runtime,options=field_options,session=session.preferences)
    execution=execution_summary(states,[legal],preference,started,runtime,calls,deadline)
    changes={side:compare_fields(states['before']['field'],states[side]['field']) if states['before'] and states[side] else [] for side in ('A','B')}
    concept_changes={side:compare_concepts(states['before']['concepts'],states[side]['concepts']) if states['before'] and states[side] else [] for side in ('A','B')}
    result=preference['comparisons'][0]
    if execution['truncated']:
        result.update(status='incomplete');result['gaps'].append('The complete requested inspection did not finish within its budgets.')
    execution['elapsed_seconds']=time.perf_counter()-started
    versions={k:m.version for k,m in models.items()}
    # No full duplicated response is built here. State references expand only
    # when the caller explicitly streams or reconstructs the legacy archive.
    root=store.put(dict(schema='pairwise-move-inspection-v13',fen=position.fen(),moves=dict(A=move_a,B=move_b),
        legality={side:store.put(row) for side,row in zip(('A','B'),legal['candidates'])},
        legal_inference=store.put(legal),states=refs,changes=changes,concept_changes=concept_changes,
        packet=inference_packet,preference=result,model_versions=versions,runtime_version=runtime.version,
        execution={**execution,'incremental':options.incremental},automatic_move_selection=False,
        scope='Experimental pairwise conditional evidence with independent legality beliefs and explicit incomplete strategic proof.'))
    summary=dict(schema='compact-pairwise-inspection-v14',fen=position.fen(),moves=dict(A=move_a,B=move_b),
        actor=position.turn,horizon=1,legality={side:legal_summary(row) for side,row in zip(('A','B'),legal['candidates'])},
        preference=preference_summary(result),packet_id=inference_packet['id'],complete=packet['complete'],
        model_versions=versions,runtime_version=runtime.version,execution={**execution,'stages':[]},
        automatic_move_selection=False,joint_proof_complete=False,
        scope='Experimental conditional evidence; legal beliefs and uncertainty remain separate.')
    if _prepared:return dict(root=root,summary=summary,states=states,refs=refs,legal=legal,
        packet=packet,role_packet=role_packet,identity=identity,preference=result,changes=changes,concept_changes=concept_changes)
    handle=store.publish(root,summary,identity)
    return present(store,store.request(handle),view,offset=offset,limit=limit,elapsed=time.perf_counter()-started)


def compare_pairs(position,pairs,**kwargs):
    if not isinstance(pairs,(list,tuple)) or not 1<=len(pairs)<=16 or any(not isinstance(p,(list,tuple)) or len(p)!=2 for p in pairs):
        raise ValueError('Supply one through sixteen explicit candidate pairs')
    runtime=kwargs.get('runtime') or Runtime(timeout=(kwargs.get('options') or PreferenceOptions()).timeout_seconds)
    for a,b in pairs:prepare(position,a,b,kwargs.get('history'),kwargs.get('source','supplied-preference-comparison'),kwargs['legal_model'],runtime)
    options=dict(kwargs,runtime=runtime,session=kwargs.get('session') or PreferenceSession(runtime))
    return [compare_moves(position,a,b,**options) for a,b in pairs]
