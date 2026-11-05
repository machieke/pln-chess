"""Scoped temporal observations and explicit trust; no historical legality oracle."""
from dataclasses import asdict,dataclass
import math
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.pln import TV,UNKNOWN

MODES=('fen-only','trusted-metadata','event-backed')

def inspect(position,mode='fen-only',evidence=None):
    position=Position.from_fen(position) if isinstance(position,str) else position
    if mode not in MODES:raise ValueError('Unknown temporal mode')
    e=dict(evidence or {});confidence=e.get('confidence',.8)
    if isinstance(confidence,bool) or not isinstance(confidence,(float,int)) or not math.isfinite(confidence) or not 0<=confidence<1:
        raise ValueError('Temporal confidence must be finite and in [0,1)')
    r={'mode':mode,'fen':position.fen(),'metadata':{'rights':position.rights,'ep':position.ep},
       'source':e.get('source'),'events':[],'status':'unknown','conflicts':[],
       'ep_truth_value':UNKNOWN.json(),'castle_truth_value':UNKNOWN.json(),
       'scope':'Temporal observations do not establish historical legality or current king safety.',
       'provenance':'unverified FEN metadata','evidence':e}
    if mode!='fen-only' and not e.get('source'):raise ValueError('A source is required for temporal trust')
    if mode=='trusted-metadata':
        r.update(status='external-claim',provenance='supplied metadata, not learned history')
        r['ep_truth_value']=TV(float(position.ep is not None),confidence).json()
        r['castle_truth_value']=TV(float(position.rights!='-'),confidence).json()
    elif mode=='event-backed':
        if 'initial_fen' not in e or 'moves' not in e:raise ValueError('Event-backed history requires initial_fen and moves')
        if not isinstance(e['moves'],(list,tuple)) or len(e['moves'])>512 or any(not isinstance(m,str) for m in e['moves']):
            raise ValueError('History must contain at most 512 move events')
        from pln_chess.cycle4.history import HistoryEvidence
        try:
            _,receipt=HistoryEvidence(e['initial_fen'],tuple(e['moves']),e['source'],confidence,
                                     e.get('castling_history_attested',False)).apply(position.fen())
        except ValueError as error:
            r.update(status='conflicting',conflicts=[str(error)],provenance='inconsistent supplied event history')
        else:
            r.update(status='structurally-consistent' if e['moves'] else 'truncated',provenance='supplied move events',history_receipt=receipt)
            r['events']=[{**v,'id':digest([e['source'],i,v]),'source':e['source'],'sequence':i+1} for i,v in enumerate(receipt['transitions'])]
            if receipt['ep_predecessor_observed']:r['ep_truth_value']=TV(1.,confidence).json()
            if receipt['castling_history_attested']:
                r['castle_truth_value']=TV(float(position.rights!='-'),confidence).json()
            r['history_gap']='Structural event consistency does not verify legal play; unmoved king/rook history requires a separate attestation.'
    r['id']=digest(r)
    return r

def transform_evidence(evidence,transform):
    raise ValueError('Temporal evidence must be independently supplied after a spatial transform; no automatic history transform is certified')
