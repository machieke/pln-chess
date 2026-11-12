"""Inspect explicit branches only: no response search, minimax or move selection."""
import copy
from itertools import product
import time
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from pln_chess.cycle10.temporal import replay, append_events
from pln_chess.cycle12.ontology import structural_successor
from pln_chess.cycle12.graph import compare_fields, compare_concepts
from .api import (PreferenceOptions,PreferenceSession,compare_moves,prepare,legal_beliefs,
    packet_for,execution_summary,native_deadline)
from .fields import build_state
from .api import identity_for,present,preference_summary,legal_summary,VIEWS,infer_preferences
from .ontology import enrich
from .proofs import ProofStore


def analyze_continuations(position,branches,*,store,legal_model,field_model,concept_model,fork_model,preference_model,
                          options=None,runtime=None,session=None,history=None,horizons=(2,3),
                          source='supplied-preference-continuations',selection_provenance='Explicit caller-supplied branches',view='summary',offset=0,limit=64,_prepared=False):
    if not isinstance(store,ProofStore):raise ValueError('Supply an explicit proof store')
    if view not in VIEWS:raise ValueError('Choose summary, proof_graph or full_archive')
    started=time.perf_counter();options=options or PreferenceOptions(timeout_seconds=900)
    if not isinstance(branches,dict) or set(branches)!={'A','B'}:
        raise ValueError('Supply explicit A and B branches')
    if not isinstance(horizons,(tuple,list)) or not horizons or len(set(horizons))!=len(horizons) or any(type(h) is not int or h not in (2,3) for h in horizons):
        raise ValueError('Continuation horizons are two and/or three plies')
    if not isinstance(selection_provenance,str) or not selection_provenance or len(selection_provenance)>2048:
        raise ValueError('Explicit bounded branch selection provenance required')
    position=Position.from_fen(position) if isinstance(position,str) else position
    first={};positions={}
    for side,alternatives in branches.items():
        if not isinstance(alternatives,list) or not 1<=len(alternatives)<=3:
            raise ValueError('Supply one through three explicit response branches per candidate')
        for index,line in enumerate(alternatives):
            if not isinstance(line,list) or not 1<=len(line)<=3 or any(not isinstance(m,str) for m in line):
                raise ValueError('Every branch contains one through three explicit UCI moves')
            if side in first and first[side]!=line[0]:
                raise ValueError('All responses for one candidate must start with the same candidate')
            first[side]=line[0];current=position;states=[]
            for notation in line:
                current=structural_successor(current,notation);states.append(current)
            positions[side,index]=states
    runtime=runtime or Runtime(timeout=options.timeout_seconds);session=session or PreferenceSession(runtime)
    position,moves,movers,descriptors,receipt=prepare(position,first['A'],first['B'],history,source,legal_model,runtime)
    if session.runtime is not runtime:
        raise ValueError('Continuation session belongs to another runtime instance')
    deadline=started+options.timeout_seconds;calls=runtime.invocations;field_options=options.field_options()
    models=dict(legal_model=legal_model,field_model=field_model,concept_model=concept_model,fork_model=fork_model,preference_model=preference_model)
    identity=identity_for(position,[first['A'],first['B']],models,options,runtime,history,source,
        branches=branches,horizons=list(horizons),selection_provenance=selection_provenance)
    cached=store.lookup(identity) if not _prepared else None
    if cached:return present(store,cached,view,offset=offset,limit=limit,cache_hit=True,elapsed=time.perf_counter()-started)
    states={};refs={};legal=[];transitions=[];packets=[];role_packets=[];bindings=[]
    with native_deadline(runtime,deadline):
        immediate=compare_moves(position,first['A'],first['B'],**models,options=options,runtime=runtime,
            session=session,history=history,source=source,store=store,_prepared=True)
        states['before']=immediate['states']['before'];refs['before']=immediate['refs']['before'];legal.append(immediate['legal'])
        for side,alternatives in branches.items():
            for index,line in enumerate(alternatives):
                before=position;previous='before'
                for ply,notation in enumerate(line,1):
                    name=f'{side}:{index}:{ply}';current=positions[side,index][ply-1]
                    if ply==1:
                        states[name]=immediate['states'][side];refs[name]=immediate['refs'][side];legality=immediate['legal']['candidates'][('A','B').index(side)]
                    elif time.perf_counter()>=deadline:
                        states[name]=None;refs[name]=None;legality=None
                    else:
                        history_receipt=append_events(receipt,line[:ply-1]) if receipt else replay(position.fen(),line[:ply-1],
                            source=source+'/hypothetical',model_version=legal_model.version,runtime_version=runtime.version,initial_trust='unknown')
                        belief=legal_beliefs(before,[find_move(before,notation)],legal_model,options,runtime,session,history_receipt)
                        legal.append(belief);legality=belief['candidates'][0]
                        refs[name],states[name]=build_state(current,position.turn,movers,store=store,field_model=field_model,concept_model=concept_model,
                            fork_model=fork_model,runtime=runtime,options=field_options,session=session,source=source,
                            incremental=options.incremental,max_candidates=options.max_candidates,before=before,move=notation)
                    prior=states.get(previous);state=states[name]
                    transition=dict(candidate=side,branch=index,ply=ply,move=notation,before=previous,after=name,
                        legality=copy.deepcopy(legality),source_lineage=line[:ply],selection_provenance=selection_provenance,
                        field_changes=compare_fields(prior['field'],state['field']) if prior and state else [],
                        concept_changes=compare_concepts(prior['concepts'],state['concepts']) if prior and state else [],
                        truth_value=None,native_temporal_proof=False,
                        scope='Host reconstruction of an explicitly supplied hypothetical transition; legal belief remains independent.')
                    transition['id']='hypothetical-transition:'+digest(transition);transitions.append(transition)
                    before=current;previous=name
        for horizon in horizons:
            for a,b in product(range(len(branches['A'])),range(len(branches['B']))):
                selected=dict(before=states['before'],A=states.get(f'A:{a}:{horizon}'),B=states.get(f'B:{b}:{horizon}'))
                packet=packet_for(selected,descriptors,horizon,source,dict(root_fen=position.fen(),
                    branches=dict(A=branches['A'][a][:horizon],B=branches['B'][b][:horizon]),
                    selection_provenance=selection_provenance,history_receipt=receipt['id'] if receipt else None,
                    state_graphs={name:s['graph']['id'] if s else None for name,s in selected.items()}),
                    complete=time.perf_counter()<deadline and not any(r['execution']['truncated'] for r in legal),
                    gaps=['Responses outside the supplied branches remain unexamined.',
                          'Temporal and strategic composition are not established by endpoint conditionals.'])
                role_packet=enrich(packet,selected,{side:position.at(move.start).id for side,move in zip(('A','B'),moves)})
                role_packets.append(role_packet)
                packets.append(role_packet if preference_model.schema=='relative-preference-model-v14' else packet)
                bindings.append(dict(horizon=horizon,branches=dict(A=a,B=b),packet=packets[-1]))
        preferences=infer_preferences(packets,preference_model,runtime=runtime,options=field_options,session=session.preferences)
    execution=execution_summary(states,legal,preferences,started,runtime,calls,deadline)
    comparisons=[]
    for binding,preference in zip(bindings,preferences['comparisons']):
        if execution['truncated']:
            preference.update(status='incomplete');preference['gaps'].append('The requested bounded inspection is incomplete.')
        comparisons.append({**binding,'preference':preference})
    root=store.put(dict(schema='bounded-preference-continuations-v13',fen=position.fen(),branches=copy.deepcopy(branches),
        selection_provenance=selection_provenance,states=refs,transitions=transitions,
        immediate=immediate['root'],comparisons=comparisons,legal_inferences=legal,
        unexamined_responses='All opponent responses and continuations outside the explicit supplied lines remain unexamined.',
        exhaustive_response_coverage=False,automatic_move_selection=False,strategic_score=None,
        model_versions=immediate['summary']['model_versions'],runtime_version=runtime.version,
        execution={**execution,'incremental':options.incremental},
        scope='Bounded supplied hypothetical branches, separate endpoint evidence and horizon-specific learned conditionals; no optimality or complete temporal theorem.'))
    coverage={side:[dict(branch=index,plies=len(line),requested_horizons=list(horizons),
        missing_horizons=[h for h in horizons if len(line)<h],
        legality=[legal_summary(t['legality']) if t['legality'] else None for t in transitions
            if t['candidate']==side and t['branch']==index]) for index,line in enumerate(lines)]
        for side,lines in branches.items()}
    summary=dict(schema='compact-continuation-inspection-v14',fen=position.fen(),actor=position.turn,
        branches=branches,horizons=list(horizons),selection_provenance=selection_provenance,
        branch_coverage=coverage,exhaustive_response_coverage=False,
        unexamined_responses='Every response outside the explicitly supplied lines remains unexamined.',
        immediate=immediate['summary'],comparisons=[dict(horizon=c['horizon'],branches=c['branches'],
            packet_id=c['packet']['id'],complete=c['packet'].get('base',c['packet'])['complete'],preference=preference_summary(c['preference']))
            for c in comparisons],model_versions=immediate['summary']['model_versions'],runtime_version=runtime.version,
        execution={**execution,'stages':[]},automatic_move_selection=False,strategic_score=None,
        joint_proof_complete=False,global_robust_preference=None,
        scope='Separate conditional answers for supplied branches; no optimality or native temporal conjunction.')
    for side,rows in coverage.items():
        for row in rows:
            row['diagnostic_only']=any(v is None or v.get('classification')!='supported-legal' for v in row['legality'])
            row['legality_unknown']=any(v is None or v.get('classification') in ('unknown','incomplete') for v in row['legality'])
            row['supported_illegal']=any(v and v.get('classification')=='supported-illegal' for v in row['legality'])
    if _prepared:return dict(root=root,summary=summary,states=states,refs=refs,immediate=immediate,
        role_packets=role_packets,comparisons=comparisons,identity=identity,transitions=transitions)
    handle=store.publish(root,summary,identity)
    return present(store,store.request(handle),view,offset=offset,limit=limit,elapsed=time.perf_counter()-started)
