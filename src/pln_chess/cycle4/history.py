"""Structural temporal evidence; no claim that supplied historical moves were legal."""
from dataclasses import dataclass,asdict,replace
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.api import find_move

@dataclass(frozen=True)
class HistoryEvidence:
    initial_fen:str
    moves:tuple[str,...]
    source:str
    confidence:float=.99
    castling_history_attested:bool=False

    def apply(self,expected_fen):
        if not self.source or not 0<=self.confidence<1:raise ValueError('Invalid temporal evidence source/confidence')
        if type(self.castling_history_attested) is not bool:raise ValueError('Invalid history attestation')
        state=Position.from_fen(self.initial_fen);transitions=[]
        for notation in self.moves:
            move=find_move(state,notation)
            if move is None:raise ValueError('Historical move outside structural grammar')
            successor=state.successor(move)
            if successor is None:raise ValueError('No structural successor')
            transitions.append({'before':state.fen(),'move':notation,'after':successor.fen()});state=successor
        if state.fen()!=expected_fen:raise ValueError('Contradictory historical successor')
        # EP predecessor and castling-history attestation have distinct scopes.
        last=transitions[-1] if transitions else None
        ep_established=bool(last and state.ep is not None)
        receipt={**asdict(self),'transitions':transitions,'ep_predecessor_observed':ep_established,
                 'scope':'Observed structural transitions; historical legality is unverified.',
                 'provenance':'supplied-temporal-evidence','fen':expected_fen}
        receipt['id']=digest(receipt)
        known=self.confidence>=.99 and (ep_established or self.castling_history_attested)
        return replace(state,history_known=known),receipt
