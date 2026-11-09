"""Preregistered complete synthetic games and controlled robustness pairs.

The reference chess implementation is used only in this offline dataset builder.
No Cycle 9 holdout is used for operational learning.
"""
import argparse
from collections import Counter
from pathlib import Path
import random
import chess
from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from training.cycle8_data import translation_key, construct, SCENARIOS

OPENINGS = {
 'italian':'e2e4 e7e5 g1f3 b8c6 f1c4 f8c5',
 'french':'e2e4 e7e6 d2d4 d7d5 b1c3 g8f6',
 'bird':'f2f4 d7d5 g1f3 g8f6 e2e3 g7g6',
 'reti':'g1f3 d7d5 c2c4 e7e6 b2b3 g8f6',
 'ruy-lopez':'e2e4 e7e5 g1f3 b8c6 f1b5 a7a6',
 'sicilian':'e2e4 c7c5 g1f3 d7d6 d2d4 c5d4',
 'pirc':'e2e4 d7d6 d2d4 g8f6 b1c3 g7g6',
 'alekhine':'e2e4 g8f6 e4e5 f6d5 d2d4 d7d6',
 'kings-indian':'d2d4 g8f6 c2c4 g7g6 b1c3 f8g7',
 'dutch':'d2d4 f7f5 c2c4 g8f6 b1c3 e7e6',
 'slav':'d2d4 d7d5 c2c4 c7c6 g1f3 g8f6',
 'nimzo':'d2d4 g8f6 c2c4 e7e6 b1c3 f8b4',
 'vienna':'e2e4 e7e5 b1c3 g8f6 f2f4 d7d5',
 'scotch':'e2e4 e7e5 g1f3 b8c6 d2d4 e5d4',
}

# Each pair has the same focus movement; the listed edit is the causal variable.
PAIRS = [
 ('multiple-blockers','7k/8/8/8/1R1p1p2/8/8/K7 w - - 0 1','b4h4','f4',None,False,False),
 ('blocker-identity','7k/8/8/8/1R1p4/8/8/K7 w - - 0 1','b4h4','d4','n',False,False),
 ('destination-allegiance','7k/8/8/8/1Q4n1/8/8/K7 w - - 0 1','b4g4','g4','N',True,False),
 ('pin-discovered-attack','4r2k/8/8/8/8/8/4R3/4K3 w - - 0 1','e2d2','e8','b',False,True),
 ('double-check','4r2k/8/8/8/1b6/8/2N5/4K3 w - - 0 1','c2b4','e8',None,False,True),
 ('king-destination-attack','3r3k/8/8/8/8/8/2K5/8 w - - 0 1','c2d3','d8',None,False,True),
 ('en-passant-discovery','7k/8/8/r4pPK/8/8/8/8 w - f6 0 2','g5f6','a5',None,False,True),
 ('castle-transit-attack','5rk1/8/8/8/8/8/8/4K2R w K - 0 1','e1g1','f8',None,False,True),
]


def generate(out):
    out=Path(out);cfg=read_json(ROOT/'configs/cycle9.json')
    historical=set();historical_files={}
    paths=[ROOT/'fixtures/dataset.json', *sorted((ROOT/'artifacts').glob('cycle*/dataset.json')),
           *sorted((ROOT/'artifacts').glob('cycle*/datasets/dataset.json'))]
    for path in paths:
        if 'cycle9' in str(path):continue
        data=read_json(path);historical_files[str(path.relative_to(ROOT))]=digest(data)
        for row in data.get('positions',[])+data.get('examples',[]):
            if row.get('fen'):historical.add(translation_key(row['fen']))
    positions=[];games=[];used={};excluded=Counter();pairs=[]
    def add(board,split,family,group,**extra):
        if not board.is_valid() or board.is_game_over():return None
        key=translation_key(board.fen())
        if key in historical:excluded['historical-equivalent']+=1;return None
        if key in used:excluded['duplicate-equivalent']+=1;return None
        moves=list(candidates(Position.from_fen(board.fen())))
        expected={m.uci() for m in board.legal_moves}
        assert expected <= {m.notation for m in moves}, 'Candidate generator misses reference move'
        fixture=dict(id=f'c9-{split}-{len(positions):04}',fen=board.fen(),split=split,family=family,
                     structural_family=family,dependence_group=group,translation_key=key,
                     candidate_count=len(moves),promotion_candidates=sum(bool(m.promotion) for m in moves),
                     unknown_squares=[],**extra)
        used[key]=split;positions.append(fixture);return fixture
    for split,key in [('development','development_families'),('calibration','calibration_families'),('independent-games','heldout_families')]:
        for family in cfg[key]:
            for index in range(cfg['games_per_family']):
                seed=cfg['seeds'][index%len(cfg['seeds'])]+10000*list(OPENINGS).index(family)+index//len(cfg['seeds'])
                rng=random.Random(seed);board=chess.Board();history=[];fens=[]
                opening=OPENINGS[family].split()
                while not board.is_game_over():
                    legal=sorted(board.legal_moves,key=lambda m:m.uci())
                    move=chess.Move.from_uci(opening[len(history)]) if len(history)<len(opening) else rng.choice(legal)
                    assert move in legal
                    board.push(move);history.append(move.uci())
                    if not board.is_game_over() and len(history)>=12:fens.append((len(history),board.fen()))
                    if len(history)>6000:raise RuntimeError('Resource guard: incomplete game must not count')
                gid=f'c9-game-{family}-{seed}';sampled=[];available=list(range(len(fens)))
                for q in (.10,.30,.50,.70,.90):
                    target=int(q*(len(fens)-1))
                    for n in sorted(available,key=lambda j:(abs(j-target),j)):
                        ply,fen=fens[n];fixture=add(chess.Board(fen),split,'game/'+family,gid,source_game=gid,ply=ply,
                            phase='opening' if ply<=24 else 'endgame' if len(chess.Board(fen).piece_map())<=10 else 'middlegame')
                        available.remove(n)
                        if fixture:sampled.append(fixture['id']);break
                assert len(sampled)==cfg['positions_per_game']
                outcome=board.outcome();assert outcome
                games.append(dict(id=gid,split=split,family=family,seed=seed,initial_fen=chess.STARTING_FEN,
                    moves=history,final_fen=board.fen(),termination=outcome.termination.name,result=outcome.result(),
                    complete=True,sampled_fixtures=sampled))
                print('complete game',gid,len(history),outcome.termination.name,flush=True)
    rng=random.Random(909090)
    for family,fen,focus,square,symbol,label_a,label_b in PAIRS:
        for repeat in range(8):
            for attempt in range(20000):
                a=chess.Board(fen);b=a.copy();b.set_piece_at(chess.parse_square(square),chess.Piece.from_symbol(symbol) if symbol else None)
                # Shared irrelevant context is explicitly controlled, never counted as a new family.
                for j in range(2+repeat%3):
                    occupied=set(a.piece_map())|set(b.piece_map())|{chess.parse_square(focus[:2]),chess.parse_square(focus[2:4]),chess.parse_square(square)}
                    choices=[s for s in chess.SQUARES if s not in occupied and chess.square_rank(s) in (1,2,5,6)]
                    s=rng.choice(choices);p=chess.Piece(chess.KNIGHT if j%2 else chess.PAWN,bool(j%2))
                    a.set_piece_at(s,p);b.set_piece_at(s,p)
                m=chess.Move.from_uci(focus)
                if not all(x.is_valid() and not x.is_game_over() for x in (a,b)):continue
                if (m in a.legal_moves,m in b.legal_moves)!=(label_a,label_b):continue
                ka,kb=translation_key(a.fen()),translation_key(b.fen())
                if ka==kb or any(k in historical or k in used for k in (ka,kb)):continue
                group=f'c9-pair-{family}-{repeat}'
                left=add(a,'adversarial',family,group,focus_move=focus,pair_side='a')
                right=add(b,'adversarial',family,group,focus_move=focus,pair_side='b')
                assert left and right
                pairs.append(dict(id=group,family=family,fixtures=[left['id'],right['id']],focus_move=focus,
                    edit=dict(square=square,piece=symbol),expected_labels=[label_a,label_b],
                    expectation='invariance' if label_a==label_b else 'sensitivity'))
                break
            else:raise RuntimeError('Cannot create pair '+family)
    for scenario in SCENARIOS:
        for index in range(4):
            while True:
                b,start,end=construct(scenario,rng,extras=1+index%3)
                focus=chess.square_name(start)+chess.square_name(end)+('q','r','b','n')[index]
                if index%2:b=b.mirror();focus=chess.square_name(chess.square_mirror(start))+chess.square_name(chess.square_mirror(end))+focus[-1]
                if add(b,'special-moves','promotion/'+scenario,f'c9-special-{scenario}-{index}',focus_move=focus):break
    for family,fen,focus,square,symbol,_,_ in PAIRS[-2:]:
        for index in range(8):
            while True:
                b=chess.Board(fen)
                for j in range(3):
                    s=rng.choice([s for s in chess.SQUARES if not b.piece_at(s) and chess.square_rank(s) in (1,2,5,6)])
                    b.set_piece_at(s,chess.Piece(chess.KNIGHT,bool(j%2)))
                if index%2:b.remove_piece_at(chess.parse_square(square))
                if add(b,'special-moves',family,f'c9-special-{family}-{index}',focus_move=focus):break
    result=dict(schema=9,registration_hash=digest(cfg),positions=positions,games=games,examples=[],counterfactual_pairs=pairs,
        counts=dict(Counter(p['split'] for p in positions)),game_counts=dict(Counter(g['split'] for g in games)),
        oracle=dict(version=chess.__version__,scope='Offline generation, complete game replay and labels only'),
        leakage_audit=dict(historical_datasets=historical_files,historical_equivalence_keys=len(historical),
            excluded=dict(excluded),cross_split_equivalent_positions=0,game_overlap=0,training_examples=0,
            policy='No new training; complete-board translation/color/file equivalence excluded. Atomic local relations intentionally recur. Opening families disjoint across development/calibration/test. Games within a family are clustered, not IID human games.'),
        limitations=['Seeded random legal games are synthetic, not human or engine play.',
                    'Adversarial edits are paired and share source ancestry.',
                    'Full-board equivalence exclusion does not establish independence of all local features.'])
    result['hash']=digest(result);write_json(out/'datasets/dataset.json',result)
    write_json(out/'datasets/manifest.json',dict(hash=result['hash'],counts=result['counts'],games=result['game_counts'],
        complete_games=len(games),positions=len(positions),pairs=len(pairs),registration_hash=result['registration_hash'],leakage=result['leakage_audit']))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    data=generate(parser.parse_args().out);print(data['counts'],data['hash'])
