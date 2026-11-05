"""Versioned external event observations; structural replay is never legal-play proof."""
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.cycle5.history import inspect as previous
ALIASES={'unknown':'fen-only','trusted-fen':'trusted-metadata','observed-events':'event-backed'}
def canonical_mode(mode):return ALIASES.get(mode,mode)
def inspect(position,mode='unknown',evidence=None):
    r=previous(position,canonical_mode(mode),evidence);events=[]
    for event in r['events']:
        before=Position.from_fen(event['before']);after=Position.from_fen(event['after'])
        a={p.square:(p.kind,p.owner) for p in before.pieces};b={p.square:(p.kind,p.owner) for p in after.pieces}
        record={**event,'schema':'events-v6.1','before_state_id':before.id,'after_state_id':after.id,
            'effects':{'rights_before':before.rights,'rights_after':after.rights,'ep_before':before.ep,'ep_after':after.ep,
                       'removed_or_changed':[{'square':list(s),'piece':list(v)} for s,v in sorted(a.items()) if b.get(s)!=v],
                       'added_or_changed':[{'square':list(s),'piece':list(v)} for s,v in sorted(b.items()) if a.get(s)!=v]},
            'historical_legality':'unverified','kind':'externally-supplied-structural-transition'}
        record['id']=digest(record);events.append(record)
    return {**r,'events':events,'schema':'history-v6.1','trust_mode':next((k for k,v in ALIASES.items() if v==r['mode']),r['mode']),
            'source_receipt_id':r['id'],'id':digest(['history-v6.1',r,events])}
