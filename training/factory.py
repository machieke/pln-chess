"""Reproducible controlled contrasts and varied reference-game positions."""
from __future__ import annotations
import random
import chess
from pln_chess.common import ROOT,digest,write_json
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.observations import observe
from pln_chess.spatial import translate

# Families are disjoint between strict splits. Controlled translation probes are
# deliberately paired with training and reported separately from held-out tests.
SPECS=[
('rook-clear','rook-east','train','7k/8/8/8/8/8/2R5/2K5 w - - 0 1','c2e2'),
('rook-blocked','rook-east','train','7k/8/8/8/8/8/2RP4/2K5 w - - 0 1','c2e2'),
('rook-enemy','rook-east','train','7k/8/8/8/8/8/2R1n3/2K5 w - - 0 1','c2e2'),
('rook-friendly','rook-east','train','7k/8/8/8/8/8/2R1N3/2K5 w - - 0 1','c2e2'),
('rook-pinned','rook-east','train','2r4k/8/8/8/8/8/2R5/2K5 w - - 0 1','c2e2'),
('bishop-clear','bishop-main','train','8/7k/8/8/8/2B5/8/K7 w - - 0 1','c3e5'),
('bishop-blocked','bishop-main','train','8/7k/8/8/3P4/2B5/8/K7 w - - 0 1','c3e5'),
('queen-clear','queen-main','train','7k/8/8/8/2Q5/8/8/K7 w - - 0 1','c4f4'),
('knight-jump','knight-main','train','7k/8/8/3P4/2N5/8/8/K7 w - - 0 1','c4d6'),
('knight-empty','knight-main','train','7k/8/8/8/2N5/8/8/K7 w - - 0 1','c4d6'),
('pawn-white','pawn-main','train','7k/8/8/8/8/8/2P5/K7 w - - 0 1','c2c4'),
('pawn-blocked','pawn-main','train','7k/8/8/8/8/2n5/2P5/K7 w - - 0 1','c2c4'),
('pawn-black','pawn-main','train','7k/2p5/8/8/8/8/8/K7 b - - 0 1','c7c5'),
('pawn-capture','pawn-main','train','7k/8/8/8/3n4/2P5/8/K7 w - - 0 1','c3d4'),
('pawn-empty-diagonal','pawn-main','train','7k/8/8/8/8/2P5/8/K7 w - - 0 1','c3d4'),
('king-safe','king-main','train','7k/8/8/8/8/8/2K5/8 w - - 0 1','c2d2'),
('king-attacked','king-main','train','3r3k/8/8/8/8/8/2K5/8 w - - 0 1','c2d2'),
('king-adjacent','king-main','train','8/8/8/8/3k4/8/2K5/8 w - - 0 1','c2d3'),
('castle-clear','castle-main','train','4k3/8/8/8/8/8/8/4K2R w K - 0 1','e1g1'),
('castle-no-right','castle-main','train','4k3/8/8/8/8/8/8/4K2R w - - 0 1','e1g1'),
('castle-through-attack','castle-main','train','4kr2/8/8/8/8/8/8/4K2R w K - 0 1','e1g1'),
('castle-queenside','castle-queenside','train','4k3/8/8/8/8/8/8/R3K3 w Q - 0 1','e1c1'),
('castle-queenside-outer-blocked','castle-queenside','train','4k3/8/8/8/8/8/8/RN2K3 w Q - 0 1','e1c1'),
('en-passant','ep-main','train','7k/8/8/2Pp4/8/8/8/K7 w - d6 0 1','c5d6'),
('en-passant-no-target','ep-main','train','7k/8/8/2Pp4/8/8/8/K7 w - - 0 1','c5d6'),
('en-passant-opens-ray','ep-main','train','7k/8/8/r1Pp3K/8/8/8/8 w - d6 0 1','c5d6'),
('promotion','promotion-main','train','8/2P4k/8/8/8/8/8/K7 w - - 0 1','c7c8q'),
('promotion-friendly','promotion-main','train','2R5/2P4k/8/8/8/8/8/K7 w - - 0 1','c7c8q'),
('rook-long','rook-long','validation','7k/8/8/8/8/8/1R6/1K6 w - - 0 1','b2g2'),
('bishop-capture','bishop-capture','validation','7k/8/8/4n3/8/2B5/8/K7 w - - 0 1','c3e5'),
('double-check','double-check','heldout-transfer','2r4k/8/8/8/8/4b3/1R6/2K5 w - - 0 1','b2d2'),
('diagonal-pin','diagonal-pin','heldout-transfer','7k/8/7b/8/8/4B3/3K4/8 w - - 0 1','e3f2'),
('discovered-check','discovered-check','heldout-transfer','7k/8/8/8/8/1n6/r1R1K3/8 w - - 0 1','c2c4'),
('check-block','check-response','heldout-transfer','3r3k/8/8/8/8/8/2R5/3K4 w - - 0 1','c2d2'),
('check-capture','check-response','heldout-transfer','7k/8/8/8/8/8/2Rr4/3K4 w - - 0 1','c2d2'),
('mate','terminal-mate','adversarial','7k/6Q1/5K2/8/8/8/8/8 b - - 0 1','h8g8'),
('stalemate','terminal-stalemate','adversarial','7k/5K2/6Q1/8/8/8/8/8 b - - 0 1','h8g8'),
('edge-knight','edge-knight','adversarial','7k/8/8/8/8/8/8/NK6 w - - 0 1','a1b3'),
('castle-occupied','castle-occupied','adversarial','4k3/8/8/8/8/8/8/4KB1R w K - 0 1','e1g1'),
]

def reference_label(position,move):
    board=chess.Board(position.fen())
    try: candidate=chess.Move.from_uci(move.notation)
    except ValueError: return False
    return candidate in board.legal_moves


def attack_labels(position,move):
    after=position.successor(move)
    if after is None: return {}
    owner=position.at(move.start).owner
    board=chess.Board(after.fen()); king=board.king(chess.WHITE if owner=='White' else chess.BLACK)
    if king is None: return {}
    attackers=board.attackers(chess.BLACK if owner=='White' else chess.WHITE,king)
    return {a['attacker_id']:chess.square(*next(p.square for p in after.pieces if p.id==a['attacker_id'])) in attackers
            for a in observe(position,move)['attacks']}


def generate(seed=1729,output=None):
    positions=[{'id':i,'family':f,'split':s,'fen':fen,'focus_move':m,'dependence_group':f,'lineage':[]} for i,f,s,fen,m in SPECS]
    # Translate all pieces without crossing the boundary: move fixture kings first
    # via explicit probe motifs with room around every piece.
    source=Position.from_fen('8/6k1/8/8/8/2R5/2K5/8 w - - 0 1')
    positions.append({'id':'transfer-source','family':'controlled-rook','split':'train','fen':source.fen(),'focus_move':'c3e3','dependence_group':'transfer-motif','lineage':[]})
    dest=translate(source,(1,0))
    positions.append({'id':'transfer-target','family':'controlled-rook','split':'controlled-transfer','fen':dest.fen(),'focus_move':'d3f3','dependence_group':'transfer-motif','lineage':['transfer-source','translate(1,0)']})
    # Varied multi-piece states from disjoint seeded games; only this module uses the oracle.
    for game,split in enumerate(('train','validation','heldout-transfer','adversarial')):
        rng=random.Random(seed+game); board=chess.Board()
        for ply in range(18+game*3):
            moves=list(board.legal_moves)
            if not moves: break
            board.push(rng.choice(moves))
        positions.append({'id':f'game-{game}','family':f'game-{game}','split':split,'fen':board.fen(),
                          'focus_move':next(iter(board.legal_moves)).uci() if any(board.legal_moves) else None,
                          'dependence_group':f'game-{game}','lineage':[]})
    examples=[]
    for p in positions:
        if not chess.Board(p['fen']).is_valid():
            raise ValueError(f"Invalid synthetic starting position: {p['id']}")
        position=Position.from_fen(p['fen'])
        for move in candidates(position):
            examples.append({'position_fixture':p['id'],'family':p['family'],'split':p['split'],'fen':p['fen'],
                             'move':move.notation,'label':reference_label(position,move),'attack_labels':attack_labels(position,move),
                             'source':f'python-chess/{chess.__version__}','dependence_group':p['dependence_group'],
                             'transformation_lineage':p['lineage']})
    result={'schema':1,'seed':seed,'oracle':{'distribution':'chess','version':chess.__version__},
            'positions':positions,'examples':examples}
    result['hash']=digest(result)
    result['manifest']={'position_count':len(positions),'example_count':len(examples),
                        'splits':{s:sum(p['split']==s for p in positions) for s in sorted({p['split'] for p in positions})},
                        'policy':'Strict splits disjoint by structural family/game. Controlled-transfer intentionally shares a motif and is scored separately.'}
    if output: write_json(output,result)
    return result

if __name__=='__main__':
    data=generate(output=ROOT/'fixtures/dataset.json')
    print(data['manifest'])
