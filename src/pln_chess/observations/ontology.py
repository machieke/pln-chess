"""Typed relational proposition contracts at the host/native boundary."""
from dataclasses import dataclass
from typing import Any
from pln_chess.pln import TV

SIGNATURES={
    'PieceType':(str,str), 'Owner':(str,str), 'SideToMove':(str,str),
    'CandidateMove':(str,str,str), 'RelativeObservation':(str,str,str),
    'IntermediateOccupancy':(str,str,int,str), 'DestinationOccupancy':(str,str,str),
    'DestinationExists':(str,str), 'MovementPatternSupported':(str,),
    'LegalMove':(str,str), 'WouldExposeOwnKing':(str,str), 'Attack':(str,str,str),
}

@dataclass(frozen=True)
class Proposition:
    predicate: str
    args: tuple
    tv: TV
    value: Any=None

    def __post_init__(self):
        signature=SIGNATURES.get(self.predicate)
        if signature is None or len(signature)!=len(self.args):
            raise ValueError(f'Unknown predicate/arity: {self.predicate}')
        if any(type(value) is not kind for value,kind in zip(self.args,signature)):
            raise ValueError(f'Invalid argument types for {self.predicate}')
        if not isinstance(self.tv,TV): raise TypeError('Every proposition requires a native TV')

    @classmethod
    def from_json(cls,data):
        return cls(data['predicate'],tuple(data['args']),TV.from_json(data['tv']),data.get('value'))

    def json(self):
        result={'predicate':self.predicate,'args':list(self.args),'tv':self.tv.json()}
        if self.value is not None: result['value']=self.value
        return result
