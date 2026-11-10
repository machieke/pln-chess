"""Offline references for supplied legal sequences and structural interactions."""
import argparse
from pathlib import Path
import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.api import find_move
from training.cycle11_data import labels


SEQUENCES = [
    ('developing-attack',chess.STARTING_FEN,
     'e2e4 e7e5 g1f3 b8c6 f1c4 f8c5','Development changes several attack and defense fields.'),
    ('discovered-attack-preparation','6k1/8/8/8/8/8/6B1/1K4R1 w - - 0 1',
     'g2f3 g8h7 g1g7 h7h6','A bishop vacates the rook ray; the supplied replies relocate the exposed king.'),
    ('defender-removal','7k/8/8/8/3rp3/2B5/8/1K2R3 w - - 0 1',
     'c3d4 h8h7 e1e4 h7g6','Capturing a rook removes its local defense of a pawn before a later capture.'),
    ('pin-formation-release','4k3/4n3/8/8/8/8/1K6/R7 w - - 0 1',
     'a1e1 e8f8 e1e7 f8g8','The rook aligns a knight with its king; a king move releases that absolute-pin geometry.'),
    ('knight-fork-creation','8/8/3r3k/8/3N4/8/8/K7 w - - 0 1',
     'd4f5 h6g6 f5d6 g6f6','A knight influences two targets; a king relocation and capture change both relations.'),
    ('pawn-fork-escape','7k/8/2q1r3/8/3P4/8/8/K7 w - - 0 1',
     'd4d5 c6c7 d5e6 h8g8','A pawn creates two local attacks; one target leaves before the other is captured.'),
    ('mobility-restriction','N6k/8/2P5/1P6/8/8/8/7K w - - 0 1',
     'b5b6 h8g8 c6c7 g8h8','Friendly pawns occupy both geometric exits of a corner knight.'),
    ('promotion-threat','7k/8/1P6/8/8/8/8/6K1 w - - 0 1',
     'b6b7 h8g8 b7b8n g8f7','A supplied underpromotion changes the piece kind and its influence pattern.'),
    ('king-exposure','4r1k1/8/8/8/8/8/4B3/4K3 w - - 0 1',
     'e1f1 e8e2 f1g1 e2e1','A king leaves a pin alignment; later rook moves create a new exposed-king relation.'),
    ('discovered-defense','6k1/7N/8/8/4P3/3B4/8/1K6 w - - 0 1',
     'e4e5 g8f7 h7f6 f7f8','A pawn opens a bishop defense before the defended knight relocates.'),
    ('en-passant-ray','7k/5p2/8/R5P1/8/8/8/6K1 b - - 0 1',
     'f7f5 g5f6 h8g8 a5a8','Observed double-pawn movement precedes en passant and a changed rook ray.'),
    ('captured-blocker-queen-ray','7k/8/5r2/8/8/8/1B6/Q1n4K w - - 0 1',
     'b2c1 h8g8 a1f6 g8h7','A bishop capture vacates a queen diagonal, followed by a later target capture.'),
]


def field_reference(board):
    rows=[]
    for source in sorted(board.piece_map()):
        for target in chess.SQUARES:
            if source==target:continue
            expected=labels(board,source,target)
            # Cycle 11's mobility reference included king-to-rook castling
            # aliases. New panels exclude every reference castling move.
            if board.piece_at(source).piece_type==chess.KING:
                probe=board.copy();probe.turn=board.piece_at(source).color
                if probe.is_castling(chess.Move(source,target)):
                    expected['mobility']=None
            rows.append(dict(source=chess.square_name(source),target=chess.square_name(target),labels=expected))
    return rows


def generate(out):
    out=Path(out);sequences=[]
    for name,initial,notations,description in SEQUENCES:
        board=chess.Board(initial)
        assert board.is_valid(),(name,board.status())
        state=Position.from_fen(initial)
        frames=[dict(step=0,fen=board.fen(en_passant='fen'),field_reference=field_reference(board))]
        events=[]
        for index,notation in enumerate(notations.split(),1):
            move=chess.Move.from_uci(notation)
            assert move in board.legal_moves,(name,index,notation,board.fen())
            proposed=find_move(state,notation)
            assert proposed is not None
            state=state.successor(proposed)
            board.push(move)
            expected=board.fen(en_passant='fen')
            assert state.fen()==expected,(name,index)
            event=dict(index=index,move=notation,observed_fen=expected,
                source='controlled-supplied-sequence/'+name,dependence_group='sequence/'+name,
                confidence=.99)
            event['id']='sequence-event:'+digest(event)
            events.append(event)
            frames.append(dict(step=index,fen=expected,field_reference=field_reference(board)))
        source=dict(id=name,description=description,initial_fen=initial,events=events,
            source='controlled-supplied-sequence/'+name,dependence_group='sequence/'+name,
            unknown_squares=[],scope='Supplied legal moves, independently checked offline. The system did not select or plan this sequence.')
        sequences.append(dict(input=source,reference=dict(frames=frames,all_moves_legal=True,
            source='offline-python-chess',strategic_quality=None)))
    # Before/after demonstrations reuse frozen, disclosed Cycle 11 source
    # examples as development controls, not independent concept holdouts.
    old=read_json(ROOT/'artifacts/cycle11/datasets/worked-controls.json')
    interactions=[]
    for case in old['worked']:
        board=chess.Board(case['fen']);before=field_reference(board)
        board.push(chess.Move.from_uci(case['move']))
        interactions.append(dict(input={k:v for k,v in case.items() if not k.startswith('reference_')},
            reference=dict(before=before,after=field_reference(board),legal=case['reference_legal'],
                           after_fen=board.fen(en_passant='fen')),
            ancestry='cycle11-worked/'+case['id'],use='Development interaction control; excluded from independent training and test metrics.'))
    payload=dict(schema=12,sequences=sequences,interactions=interactions,
        partial_history_protocol='Remove the middle event move while retaining its independently supplied snapshot; subsequent states may be observed but the missing transition remains unknown. Also test a missing event without a replacement snapshot and a conflicting supplied successor.',
        temporal_selection='Hand-supplied before implementation; no model scores or search selected these moves.',
        mobility_reference_correction='All king castling aliases are outside ordinary mobility. Original Cycle 11 labels and errors remain unchanged.')
    payload['hash']=digest(payload)
    write_json(out/'datasets/sequences.json',payload)
    write_json(out/'datasets/sequences-registration.json',dict(hash=payload['hash'],sequences=len(sequences),
        moves=sum(len(r['input']['events']) for r in sequences),states=sum(len(r['reference']['frames']) for r in sequences),
        interactions=len(interactions),all_moves_reference_legal=True))
    print('Registered supplied sequences',len(sequences),'interactions',len(interactions),payload['hash'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    generate(parser.parse_args().out)
