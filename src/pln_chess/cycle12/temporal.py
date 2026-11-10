"""Replay supplied structural events with explicit epistemic discontinuities."""
import copy
from dataclasses import replace
import math
import time

from pln_chess.common import digest
from pln_chess.domain import Position, parse_square
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from .incremental import IncrementalFieldSession, structural_successor
from .graph import build_graph, compare_fields, compare_concepts


def semantic_replay(value):
    """Remove execution counters, retaining every claim, proof and source binding."""
    if isinstance(value,dict):
        return {k:semantic_replay(v) for k,v in value.items() if k not in ('execution','incremental')}
    if isinstance(value,(tuple,list)):return [semantic_replay(v) for v in value]
    return value


def replay_fields(sequence,field_model,*,runtime=None,options=None,concept_model=None,
                  families=None,source_ids=None,max_candidates=32):
    started=time.perf_counter();options=options or FieldOptions();runtime=runtime or Runtime(timeout=options.timeout_seconds)
    if not isinstance(sequence,dict):raise ValueError('A supplied sequence must be an object')
    allowed={'id','description','initial_fen','events','source','dependence_group','unknown_squares','scope'}
    if set(sequence)-allowed:raise ValueError('Unknown sequence fields; references are not inference inputs')
    events=sequence.get('events')
    if not isinstance(events,list) or len(events)>64:raise ValueError('Supply at most 64 ordered events')
    source=sequence.get('source','supplied-sequence')
    if not isinstance(source,str) or not source or len(source)>512:raise ValueError('Invalid sequence source')
    unknown=sequence.get('unknown_squares',[])
    if not isinstance(unknown,list):raise ValueError('Invalid initial unknown cells')
    position=Position.from_fen(sequence['initial_fen'],unknown_squares=[parse_square(s) if isinstance(s,str) else tuple(s) for s in unknown])
    # Validate the entire event envelope before starting native work.
    for index,event in enumerate(events,1):
        if not isinstance(event,dict) or set(event)-{'id','index','move','observed_fen','source','dependence_group','confidence','unknown_squares'}:
            raise ValueError('Invalid supplied event fields')
        if type(event.get('index')) is not int or event['index']!=index:raise ValueError('Events must have consecutive indices starting at one')
        move=event.get('move')
        if move is not None and (not isinstance(move,str) or len(move) not in (4,5) or
            any(move[i] not in 'abcdefgh' for i in (0,2)) or any(move[i] not in '12345678' for i in (1,3)) or
            (len(move)==5 and move[4] not in 'qrbn')):raise ValueError('Malformed supplied UCI move')
        confidence=event.get('confidence',options.sensor_confidence)
        if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(confidence) or not 0<=confidence<1:
            raise ValueError('Event confidence must be finite and in [0,1)')
        if event.get('observed_fen') is not None:Position.from_fen(event['observed_fen'])
        if 'unknown_squares' in event:
            if not isinstance(event['unknown_squares'],list):raise ValueError('Invalid event unknown cells')
            for square in event['unknown_squares']:parse_square(square)
    session=IncrementalFieldSession(runtime);segment=0;confidence=options.sensor_confidence
    lineage=[];states=[];transitions=[];conflicts=[];complete=True

    def state(step,current,event=None,transition_start=None):
        if current is None:return dict(step=step,field=None,graph=None,concepts=[],candidate_enumeration=None,
            segment=segment,source_lineage=copy.deepcopy(lineage),status='unknown-state',gaps=['No observed state is available after a history gap.'])
        local_options=replace(options,sensor_confidence=confidence)
        field=session.build(current,field_model,options=local_options,source=source+'/segment/'+str(segment),families=families,source_ids=source_ids)
        concepts=[];enumeration=None;concept_execution=None
        if concept_model is not None:
            from .candidates import enumerate_concepts
            from .inference import infer_concepts
            enumeration=enumerate_concepts(current,max_candidates=max_candidates,source=source+'/segment/'+str(segment))
            if transition_start is not None:
                dynamic=enumerate_concepts(transition_start,move=event['move'],
                    concepts=['DiscoveredAttack','DiscoveredDefense','ThreatRemoval'],max_candidates=min(max_candidates,64-len(enumeration['candidates'])),
                    source=source+'/segment/'+str(segment))
                enumeration['supplied_transition_candidates']=dynamic
            else:dynamic={'candidates':[]}
            result=infer_concepts(enumeration['candidates']+dynamic['candidates'],concept_model,field_model,options=local_options,runtime=runtime)
            concepts=result['concepts'];concept_execution=result['execution']
        return dict(step=step,field=field,graph=build_graph(field,concepts),concepts=concepts,candidate_enumeration=enumeration,
            segment=segment,source_lineage=copy.deepcopy(lineage),status='observed-structural-state',gaps=[],
            observation_confidence=confidence,confidence_policy='Minimum supplied observation confidence within this continuous segment; no independent-evidence fusion.',
            execution=dict(concepts=concept_execution))

    states.append(state(0,position))
    for index,event in enumerate(events,1):
        before=position;move=event.get('move');observed=event.get('observed_fen');changes=[];event_gaps=[]
        event_id=event.get('id','supplied-event:'+digest(event))
        lineage.append(dict(event_id=event_id,index=index,move=move,source=event.get('source',source),
            dependence_group=event.get('dependence_group',sequence.get('dependence_group',source)),confidence=event.get('confidence',options.sensor_confidence)))
        candidate=structural_successor(before,move) if before is not None and move is not None else None
        conflict=candidate is not None and observed is not None and candidate.fen()!=Position.from_fen(observed).fen()
        if conflict:
            complete=False;position=None;status='conflicting-successor'
            conflicts.append(dict(index=index,event_id=event_id,structural_fen=candidate.fen(),observed_fen=observed))
            event_gaps.append('The supplied successor conflicts with the structural edit; neither is silently selected.')
        elif candidate is not None:
            position=candidate;status='observed-structural-transition'
            confidence=min(confidence,event.get('confidence',options.sensor_confidence))
            if 'unknown_squares' in event:
                position=replace(position,unknown_squares=tuple(sorted(set(position.unknown_squares)|{parse_square(s) for s in event['unknown_squares']})))
        else:
            complete=False;segment+=1;session=IncrementalFieldSession(runtime)
            confidence=min(options.sensor_confidence,event.get('confidence',options.sensor_confidence))
            if observed is not None:
                position=Position.from_fen(observed,unknown_squares=[parse_square(s) for s in event.get('unknown_squares',[])])
                # IDs in an independently reobserved state cannot assert identity across the gap.
                position=replace(position,pieces=tuple(replace(p,id='segment'+str(segment)+':'+p.id) for p in position.pieces))
                status='missing-event-observed-state' if move is None else 'unlinked-event-observed-state'
                event_gaps.append('The snapshot starts a new identity segment; the missing transition is not inferred.')
            else:
                position=None;status='missing-event-unknown-state' if move is None else 'unlinked-event-unknown-state'
                event_gaps.append('There is no supported starting state for this transition.')
        current=state(index,position,event,before if status=='observed-structural-transition' else None);states.append(current)
        if status=='observed-structural-transition':changes=compare_fields(states[-2]['field'],current['field'])
        transition=dict(index=index,event_id=event_id,move=move,status=status,source=event.get('source',source),
            dependence_group=event.get('dependence_group',sequence.get('dependence_group',source)),
            before_snapshot=states[-2]['field']['snapshot_id'] if states[-2]['field'] else None,
            after_snapshot=current['field']['snapshot_id'] if current['field'] else None,changes=changes,gaps=event_gaps,
            concept_changes=compare_concepts(states[-2]['concepts'],current['concepts']) if status=='observed-structural-transition' else [],
            native_temporal_proof=False,truth_value=None,origin='host-comparison',planned_move=False,
            scope='Supplied structural transition with separate endpoint proofs; no native temporal theorem or legal-move assertion.')
        transition['id']='supplied-transition:'+digest(transition);transitions.append(transition)
    return dict(schema='supplied-field-evolution-v12',sequence_id=sequence.get('id','sequence:'+digest(sequence)),
        states=states,transitions=transitions,conflicts=conflicts,complete_history=complete,planned_moves=False,
        model_version=field_model.version,concept_model_version=concept_model.version if concept_model else None,
        runtime_version=runtime.version,source=source,strategic_score=None,
        execution=dict(elapsed_seconds=time.perf_counter()-started,
            truncated=any(s['field'] and s['field']['execution']['truncated'] for s in states)),
        scope='Actual supplied events only. Gaps, counterfactuals, endpoint inference and host comparisons remain distinct.')
