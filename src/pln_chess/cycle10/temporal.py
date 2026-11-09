"""Versioned supplied-event transport; structural replay never proves legal play.

The transport records input trust and event identity. Existing native inference
receives the unchanged legacy history contract; this module adds no PLN formula.
"""
from dataclasses import replace
import math
from pln_chess.common import digest
from pln_chess.domain import Position

STANDARD_FEN='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
SCHEMA='temporal-transport-v10'
TRUST=('unknown','trusted-import','attested-standard-start')


def replay(initial_fen,moves,*,source,dependence_group=None,confidence=.99,
           initial_trust='unknown',complete=False,model_version=None,runtime_version=None,expected_fen=None):
    if not isinstance(source,str) or not source.strip():raise ValueError('A historical evidence source is required')
    if dependence_group is not None and (not isinstance(dependence_group,str) or not dependence_group.strip()):
        raise ValueError('Invalid history dependence group')
    if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(confidence) or not 0<=confidence<1:
        raise ValueError('History confidence must be finite and in [0,1)')
    if initial_trust not in TRUST:raise ValueError('Unknown initial history trust policy')
    if type(complete) is not bool:raise ValueError('Complete-record flag must be boolean')
    if not isinstance(moves,(list,tuple)) or len(moves)>4096 or any(not isinstance(m,str) for m in moves):
        raise ValueError('History must contain at most 4096 supplied UCI events')
    for value in (model_version,runtime_version):
        if value is not None and (not isinstance(value,str) or not value):raise ValueError('Invalid model or runtime identity')
    state=Position.from_fen(initial_fen);initial_fen=state.fen()
    if initial_trust=='attested-standard-start' and initial_fen!=STANDARD_FEN:
        raise ValueError('Standard-start attestation requires the standard initial state')
    expected_fen=Position.from_fen(expected_fen).fen() if expected_fen is not None else None
    dependence_group=dependence_group or source
    supplied=dict(initial_fen=initial_fen,moves=list(moves),source=source,dependence_group=dependence_group,
        confidence=float(confidence),initial_trust=initial_trust,complete=complete,
        model_version=model_version,runtime_version=runtime_version,expected_fen=expected_fen)
    events=[];propositions=[]
    def proposition(predicate,epistemic_type,value,event_ids=()):
        record=dict(predicate=predicate,epistemic_type=epistemic_type,value=value,source=source,
            dependence_group=dependence_group,event_ids=list(event_ids),truth_value=None,
            scope='Provenance relation only; no additional native PLN conclusion or computed probability.')
        record['id']=digest(record);propositions.append(record)
    proposition('HistoricalEvidenceSource','supplied-provenance',source)
    proposition('HistoryConfidence','supplied-trust-policy',float(confidence))
    proposition('InitialStateMetadata','unknown-history' if initial_trust=='unknown' else 'trusted-imported-metadata',
        dict(fen=initial_fen,trust=initial_trust))
    from pln_chess.api import find_move
    for sequence,notation in enumerate(moves,1):
        move=find_move(state,notation)
        if move is None:raise ValueError(f'Event {sequence} is outside the structural candidate grammar')
        successor=state.successor(move)
        if successor is None:raise ValueError(f'Event {sequence} has no in-board structural successor')
        mover=state.at(move.start)
        before={p.square:(p.kind,p.owner) for p in state.pieces};after={p.square:(p.kind,p.owner) for p in successor.pieces}
        event=dict(schema='observed-transition-v10',sequence=sequence,move=notation,before=state.fen(),after=successor.fen(),
            before_state_id=state.id,after_state_id=successor.id,source=source,dependence_group=dependence_group,
            observation_confidence=float(confidence),historical_legality='unverified',
            previous_event_id=events[-1]['id'] if events else None,
            mover=dict(entity_id=mover.id,kind=mover.kind,owner=mover.owner,from_square=list(move.start),to_square=list(move.end)),
            effects=dict(rights_before=state.rights,rights_after=successor.rights,ep_before=state.ep,ep_after=successor.ep,
                removed_or_changed=[dict(square=list(s),piece=list(v)) for s,v in sorted(before.items()) if after.get(s)!=v],
                added_or_changed=[dict(square=list(s),piece=list(v)) for s,v in sorted(after.items()) if before.get(s)!=v]))
        # JSON round trips preserve the event digest and event equality.
        for field in ('ep_before','ep_after'):
            if event['effects'][field] is not None:event['effects'][field]=list(event['effects'][field])
        event['id']=digest(event);events.append(event)
        proposition('ObservedMove','observed-event',dict(sequence=sequence,move=notation,before=state.id,after=successor.id),[event['id']])
        proposition('PreviouslyMoved','inferred-structural-relation',dict(entity_id=mover.id,kind=mover.kind,owner=mover.owner),[event['id']])
        state=successor
    if events:
        last=events[-1];mover=last['mover']
        if mover['kind']=='Pawn' and abs(mover['to_square'][1]-mover['from_square'][1])==2:
            proposition('LastMoveDoublePawnAdvance','inferred-structural-relation',
                dict(event_id=last['id'],target=last['effects']['ep_after'],owner=mover['owner']),[last['id']])
    attested=initial_trust!='unknown'
    proposition('RetainedCastlingRight','inferred-structural-relation' if attested else 'unknown-history',
        dict(reported_rights=state.rights,initial_metadata_attested=attested,
             supported_scope='Rights retained by supplied structural transitions from explicitly trusted initial metadata' if attested else 'FEN flags do not establish unmoved history'),
        [e['id'] for e in events])
    conflicts=[]
    if expected_fen is not None and state.fen()!=expected_fen:
        conflicts.append(dict(kind='reported-state-mismatch',expected_fen=expected_fen,replayed_fen=state.fen()))
    omitted=max(0,len(events)-512)
    legacy_initial=events[omitted]['before'] if omitted else initial_fen
    # Bind full supplied history, trust and model/runtime into native cache lineage,
    # including any prefix outside the legacy planner's 512-event replay window.
    legacy=dict(initial_fen=legacy_initial,moves=list(moves[omitted:]),
        source=source+'#transport-input-'+digest(supplied),confidence=float(confidence),castling_history_attested=attested)
    receipt=dict(schema=SCHEMA,input=supplied,events=events,propositions=propositions,resulting_fen=state.fen(),
        status='conflicting' if conflicts else 'structurally-consistent' if events else 'truncated',conflicts=conflicts,
        historical_legality='unverified',model_version=model_version,runtime_version=runtime_version,
        legacy_evidence=legacy,legacy_window=dict(retained_events=len(legacy['moves']),omitted_prefix_events=omitted,
            scope='Full events remain in this receipt; only the native legacy transport window is bounded.'),
        scope='Supplied observations and explicit initial trust, not verified historical legality, empirical calibration, or a complete positive legality proof.')
    receipt['id']=digest(receipt)
    return receipt


def verify(receipt):
    if not isinstance(receipt,dict) or receipt.get('schema')!=SCHEMA:raise ValueError('Unknown temporal transport schema')
    payload={k:v for k,v in receipt.items() if k!='id'}
    if receipt.get('id')!=digest(payload):raise ValueError('Temporal transport integrity mismatch')
    supplied=receipt.get('input')
    if not isinstance(supplied,dict):raise ValueError('Missing temporal input provenance')
    expected=replay(**supplied)
    if 'parent_receipt_id' in receipt:
        parent=receipt['parent_receipt_id']
        if not isinstance(parent,str) or len(parent)!=64:raise ValueError('Invalid parent receipt identity')
        expected['parent_receipt_id']=parent;expected['id']=digest({k:v for k,v in expected.items() if k!='id'})
    if receipt!=expected:raise ValueError('Temporal event replay or provenance mismatch')
    return True


def append_events(receipt,moves):
    verify(receipt)
    if not isinstance(moves,(list,tuple)):raise ValueError('Appended moves must be a sequence')
    supplied={**receipt['input'],'moves':receipt['input']['moves']+list(moves),'expected_fen':None,'complete':False}
    result=replay(**supplied);result['parent_receipt_id']=receipt['id']
    result['id']=digest({k:v for k,v in result.items() if k!='id'})
    return result


def native_options(receipt,options=None):
    verify(receipt)
    from pln_chess.cycle8.inference import Cycle8Options
    return replace(options or Cycle8Options(),temporal_mode='event-backed',temporal_evidence=receipt['legacy_evidence'])


def replay_game(game,ply,model_version=None,runtime_version=None):
    if type(ply) is not int or not 0<=ply<=len(game['moves']):raise ValueError('Ply is outside the supplied game record')
    source=game.get('source_collection') or game.get('source')
    if not source or not game.get('id'):raise ValueError('Game source and identity are required')
    initial=Position.from_fen(game['initial_fen']).fen()
    return replay(initial,game['moves'][:ply],source=source+'/'+game['id'],dependence_group=game['id'],
        initial_trust='attested-standard-start' if initial==STANDARD_FEN else 'unknown',
        complete=bool(game.get('complete')) and ply==len(game['moves']),model_version=model_version,runtime_version=runtime_version,
        expected_fen=game.get('final_fen') if ply==len(game['moves']) else None)
