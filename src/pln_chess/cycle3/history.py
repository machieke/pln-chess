"""Accept an explicit predecessor as a structural observation, never certify a game."""
from dataclasses import replace
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.common import digest


def observe_transition(fen,previous_fen,last_move):
    previous=Position.from_fen(previous_fen);current=Position.from_fen(fen)
    move=find_move(previous,last_move)
    if move is None:raise ValueError('Previous move is outside candidate grammar')
    successor=previous.successor(move)
    if successor is None or successor.fen()!=current.fen():raise ValueError('Contradictory predecessor/transition observation')
    receipt={'previous_fen':previous_fen,'move':last_move,'fen':fen,'provenance':'supplied-history-observation',
             'scope':'Structural transition consistency only. Does not validate historical move legality.'}
    receipt['id']=digest(receipt)
    return replace(current,history_known=True),receipt
