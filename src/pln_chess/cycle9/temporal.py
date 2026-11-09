"""Versioned epistemic provenance; never a historical legality theorem."""
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.api import find_move

def temporal_categories(receipt):
    """Add epistemic types without altering the legacy receipt or any native TV."""
    observed=[]
    for event in receipt['events']:
        before=Position.from_fen(event['before']);notation=event['move'];move=find_move(before,notation)
        piece=before.at(move.start);kinds=['piece-transition']
        if piece.kind=='King':kinds.append('king-moved')
        if piece.kind=='Rook':kinds.append('rook-moved')
        if piece.kind=='Pawn' and abs(move.end[1]-move.start[1])==2:kinds.append('pawn-double-step')
        if move.promotion:kinds.append('promotion-transition')
        observed.append(dict(event_id=event['id'],source=event['source'],sequence=event['sequence'],kinds=kinds,
            claim='Externally supplied event with structurally consistent state transition',historical_legality='unverified'))
    trusted=[]
    if receipt['mode']=='trusted-metadata':
        trusted.append(dict(source=receipt['source'],metadata=receipt['metadata'],policy='explicit supplied source confidence',
            independently_reconstructed=False))
    if receipt.get('history_receipt',{}).get('castling_history_attested'):
        trusted.append(dict(source=receipt['source'],claim='initial castling history attestation',independently_reconstructed=False))
    inferred=[]
    if receipt.get('history_receipt',{}).get('ep_predecessor_observed'):
        inferred.append(dict(claim='en-passant predecessor structurally matches latest supplied event',
            premise_event_ids=[e['event_id'] for e in observed[-1:]],native_complete_history_proof=False))
    result=dict(schema='temporal-epistemics-v9',source_receipt_id=receipt['id'],source_schema=receipt['schema'],
        directly_observed_events=observed,trusted_state_metadata=trusted,inferred_historical_conditions=inferred,
        unverified_fen_metadata=receipt['metadata'],status=receipt['status'],conflicts=receipt['conflicts'],
        scope='Diagnostic provenance categories only; existing native evidence and classification are unchanged.')
    result['id']=digest(result);return result



def inspect(position,mode="fen-only",evidence=None):
    from pln_chess.cycle6.history import inspect as original
    receipt=original(position,mode,evidence)
    return {"legacy_receipt":receipt,"epistemic_categories":temporal_categories(receipt)}
