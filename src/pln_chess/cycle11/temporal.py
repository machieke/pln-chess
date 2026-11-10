"""Canonical supplied claims with explicit gaps and conflicts; no legality oracle."""
import copy
import math
from dataclasses import replace
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.cycle10.temporal import replay, TRUST, STANDARD_FEN

SCHEMA='temporal-transport-v11'


def _text(value):
    if not isinstance(value,str) or not value.strip():
        raise ValueError('History provenance must contain nonempty text')


def _confidence(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<1:
        raise ValueError('History confidence must be finite and in [0,1)')


def replay_claims(initial_fen,claims,*,source,initial_trust='unknown',expected_fen=None,
                  expected_events=None,complete=False,metadata_claims=None,model_version=None,runtime_version=None):
    _text(source)
    if initial_trust not in TRUST or type(complete) is not bool:
        raise ValueError('Invalid history trust policy')
    if expected_events is not None and (type(expected_events) is not int or not 0<=expected_events<=4096):
        raise ValueError('Expected event count must be an integer in [0,4096]')
    if not isinstance(claims,(list,tuple)) or len(claims)>16384:
        raise ValueError('At most 16384 delivered history claims are supported')
    metadata_claims=[] if metadata_claims is None else metadata_claims
    if not isinstance(metadata_claims,list) or len(metadata_claims)>4096:
        raise ValueError('Invalid metadata claim collection')
    for identity in (model_version,runtime_version):
        if identity is not None:_text(identity)
    state=Position.from_fen(initial_fen)
    initial_fen=state.fen()
    if initial_trust=='attested-standard-start' and initial_fen!=STANDARD_FEN:
        raise ValueError('Standard-start attestation requires the standard initial position')
    if expected_fen is not None:expected_fen=Position.from_fen(expected_fen).fen()
    unique={}
    for claim in claims:
        if not isinstance(claim,dict) or set(claim)-{'sequence','move','source','dependence_group','epistemic_type','confidence','before_fen','after_fen','external_event_id'}:
            raise ValueError('Unsupported history claim structure')
        sequence=claim.get('sequence')
        if type(sequence) is not int or not 1<=sequence<=4096:
            raise ValueError('Claim sequence must be an integer in [1,4096]')
        for field in ('move','source','dependence_group'):_text(claim.get(field))
        _confidence(claim.get('confidence'))
        if claim.get('epistemic_type') not in ('observed-event','inferred-history','unknown-history'):
            raise ValueError('Unsupported history epistemic type')
        if 'external_event_id' in claim:_text(claim['external_event_id'])
        for field in ('before_fen','after_fen'):
            if field in claim:Position.from_fen(claim[field])
        unique[digest(claim)]=copy.deepcopy(claim)
    canonical_claims=[dict(id=identifier,**claim) for identifier,claim in sorted(unique.items(),key=lambda item:(item[1]['sequence'],item[0]))]
    metadata={}
    for claim in metadata_claims:
        if not isinstance(claim,dict) or set(claim)!={'fen','source','dependence_group','epistemic_type','confidence'}:
            raise ValueError('Unsupported metadata claim structure')
        for field in ('source','dependence_group'):_text(claim[field])
        _confidence(claim['confidence'])
        if claim['epistemic_type']!='trusted-metadata':raise ValueError('Unsupported metadata epistemic type')
        Position.from_fen(claim['fen'])
        metadata[digest(claim)]=copy.deepcopy(claim)
    supplied=dict(initial_fen=initial_fen,claims=copy.deepcopy(list(claims)),source=source,initial_trust=initial_trust,
        expected_fen=expected_fen,expected_events=expected_events,complete=complete,metadata_claims=copy.deepcopy(metadata_claims),
        model_version=model_version,runtime_version=runtime_version)
    semantic={**supplied,'claims':canonical_claims,'metadata_claims':[dict(id=k,**v) for k,v in sorted(metadata.items())]}
    semantic_id=digest(semantic)
    by_sequence={}
    external={}
    conflicts=[]
    for claim in canonical_claims:
        by_sequence.setdefault(claim['sequence'],[]).append(claim)
        if 'external_event_id' in claim:
            external.setdefault((claim['source'],claim['external_event_id']),[]).append(claim)
    for identity,records in sorted(external.items()):
        if len({(r['sequence'],r['move']) for r in records})>1:
            conflicts.append(dict(kind='source-event-identity-conflict',source=identity[0],external_event_id=identity[1],claims=[r['id'] for r in records]))
    for sequence,records in sorted(by_sequence.items()):
        if len({r['move'] for r in records})>1:
            conflicts.append(dict(kind='different-moves-at-sequence',sequence=sequence,claims=[r['id'] for r in records]))
    for identifier,claim in sorted(metadata.items()):
        if Position.from_fen(claim['fen']).fen()!=initial_fen:
            conflicts.append(dict(kind='initial-metadata-conflict',claim=identifier,expected=initial_fen,reported=claim['fen']))
    count=max(max(by_sequence,default=0),expected_events or 0)
    gaps=[dict(kind='missing-sequence',sequence=i) for i in range(1,count+1) if i not in by_sequence]
    if expected_events is not None and max(by_sequence,default=0)>expected_events:
        conflicts.append(dict(kind='expected-event-count-exceeded',expected=expected_events,observed=max(by_sequence)))
    from pln_chess.api import find_move
    events=[]
    for sequence in range(1,count+1):
        records=by_sequence.get(sequence,[])
        if not records or len({r['move'] for r in records})!=1:break
        notation=records[0]['move']
        move=find_move(state,notation)
        successor=state.successor(move) if move is not None else None
        if successor is None:
            conflicts.append(dict(kind='invalid-structural-event',sequence=sequence,move=notation))
            break
        for claim in records:
            for field,actual in (('before_fen',state.fen()),('after_fen',successor.fen())):
                if field in claim and Position.from_fen(claim[field]).fen()!=actual:
                    conflicts.append(dict(kind='reported-event-state-conflict',sequence=sequence,field=field,claim=claim['id'],reported=claim[field],replayed=actual))
        event=dict(sequence=sequence,move=notation,before_fen=state.fen(),after_fen=successor.fen(),
            claim_ids=[r['id'] for r in records],historical_legality='unverified')
        event['id']=digest(event)
        events.append(event)
        state=successor
    if expected_fen is not None and state.fen()!=expected_fen:
        conflicts.append(dict(kind='reported-final-state-mismatch',reported=expected_fen,replayed=state.fen()))
    supplied_confidences=[c['confidence'] for c in canonical_claims]
    supplied_confidences.extend(m['confidence'] for m in metadata.values())
    confidence=min(supplied_confidences,default=.99)
    observed=all(c['epistemic_type']=='observed-event' and c['confidence']>0 for c in canonical_claims)
    native_available=bool(not gaps and not conflicts and observed and confidence>0 and
        (events or initial_trust!='unknown' or metadata))
    legacy=None
    if native_available:
        trust=initial_trust if initial_trust!='unknown' or not metadata else 'trusted-import'
        legacy=replay(initial_fen,[e['move'] for e in events],source=source+'#claims-'+semantic_id,
            dependence_group='claim-components:'+digest(sorted({c['dependence_group'] for c in canonical_claims}|{m['dependence_group'] for m in metadata.values()})),
            confidence=confidence,initial_trust=trust,complete=complete,model_version=model_version,runtime_version=runtime_version,expected_fen=expected_fen)
    result=dict(schema=SCHEMA,input=supplied,canonical_claims=canonical_claims,semantic_id=semantic_id,
        events=events,gaps=gaps,conflicts=conflicts,resulting_fen=state.fen(),native_available=native_available,
        legacy_transport=legacy,model_version=model_version,runtime_version=runtime_version,
        status='conflicting' if conflicts else 'incomplete' if gaps else 'observed' if native_available else 'unattested',
        historical_legality='unverified',confidence_policy='Minimum supplied confidence is a conservative trust selection, not probability fusion.',
        scope='Claims are structurally replayed. No native conclusion of historical legality, conjunction or global positive safety is introduced.')
    result['id']=digest(result)
    return result


def verify(receipt):
    if not isinstance(receipt,dict) or receipt.get('schema')!=SCHEMA:
        raise ValueError('Unsupported temporal transport')
    if receipt.get('id')!=digest({k:v for k,v in receipt.items() if k!='id'}):
        raise ValueError('Temporal receipt integrity mismatch')
    expected=replay_claims(**receipt['input'])
    if 'parent_receipt_id' in receipt:
        parent=receipt['parent_receipt_id']
        if not isinstance(parent,str) or len(parent)!=64:raise ValueError('Invalid parent receipt identity')
        expected['parent_receipt_id']=parent
        expected['id']=digest({k:v for k,v in expected.items() if k!='id'})
    if expected!=receipt:raise ValueError('Temporal receipt semantic replay mismatch')
    return True


def append_claims(receipt,claims):
    verify(receipt)
    if not isinstance(claims,(list,tuple)):raise ValueError('Appended claims must be a sequence')
    result=replay_claims(**{**receipt['input'],'claims':receipt['input']['claims']+list(claims)})
    result['parent_receipt_id']=receipt['id']
    result['id']=digest({k:v for k,v in result.items() if k!='id'})
    return result


def native_options(receipt,options=None,*,model_version=None,runtime_version=None):
    verify(receipt)
    for field,value in (('model_version',model_version),('runtime_version',runtime_version)):
        if value is not None and receipt[field] not in (None,value):raise ValueError('Temporal receipt '+field+' mismatch')
    from pln_chess.cycle8.inference import Cycle8Options
    options=options or Cycle8Options()
    if not receipt['native_available']:return replace(options,temporal_mode='fen-only',temporal_evidence=None)
    from pln_chess.cycle10.temporal import native_options as bridge
    return bridge(receipt['legacy_transport'],options)
