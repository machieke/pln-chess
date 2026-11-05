"""Structural local edits and actual before/after native proofs."""
from dataclasses import replace
from pln_chess.domain import Position,Piece,parse_square,inside
from pln_chess.api import explain_move,find_move
from pln_chess.spatial import color_flip


def compare(position,move,checkpoint,operation,square=None,target=None,piece='Pawn',owner=None,right='K',runtime=None):
    pos=Position.from_fen(position) if isinstance(position,str) else position
    candidate=find_move(pos,move)
    if candidate is None:raise ValueError('Unknown candidate')
    square=parse_square(square) if isinstance(square,str) else square
    target=parse_square(target) if isinstance(target,str) else target
    if any(s is not None and not inside(s) for s in (square,target)):raise ValueError('Counterfactual square is outside the board')
    changed=candidate
    if operation=='color-flip':
        after=color_flip(pos)
        changed=replace(candidate,start=(candidate.start[0],7-candidate.start[1]),end=(candidate.end[0],7-candidate.end[1]))
    elif operation=='remove-right':
        if right not in ('K','Q','k','q'):raise ValueError('Unknown castling right')
        after=replace(pos,rights=pos.rights.replace(right,'') or '-')
    elif operation=='remove-piece':
        if square is None or pos.at(square) is None:raise ValueError('No piece at square')
        after=replace(pos,pieces=tuple(p for p in pos.pieces if p.square!=square))
    elif operation=='add-blocker':
        if square is None or pos.at(square):raise ValueError('Choose an empty square')
        if piece not in ('Pawn','Knight','Bishop','Rook','Queen'):raise ValueError('Unsupported blocker type')
        owner=owner or pos.turn
        if owner not in ('White','Black'):raise ValueError('Unknown owner')
        after=replace(pos,pieces=pos.pieces+(Piece('counterfactual-piece',piece,owner,square),))
    elif operation=='move-piece':
        if square is None or target is None or pos.at(square) is None or pos.at(target):raise ValueError('Choose an occupied source and empty target')
        after=replace(pos,pieces=tuple(replace(p,square=target) if p.square==square else p for p in pos.pieces))
    else:raise ValueError('Unknown counterfactual operation')
    a=explain_move(pos,candidate,checkpoint,runtime=runtime);b=explain_move(after,changed,checkpoint,runtime=runtime)
    x=a['candidate'];y=b['candidate']
    return {'operation':operation,'before':a,'after':b,'changed_fen':after.fen(),
            'classification_changed':x['classification']!=y['classification'],
            'rules_added':sorted(set(y['matched_rule_ids'])-set(x['matched_rule_ids'])),
            'rules_removed':sorted(set(x['matched_rule_ids'])-set(y['matched_rule_ids'])),
            'condition_beliefs':{'before':x.get('condition_beliefs',{}),'after':y.get('condition_beliefs',{})},
            'scope':'Structural perturbation, not an assertion that the edited position is a reachable game state.'}
