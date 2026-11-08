"""Registered synthetic promotion curriculum; chess oracle stays offline."""
from collections import Counter
from pathlib import Path
import argparse
import random
import chess
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from training.cycle4 import symmetry_key, enrich4


OPENINGS = {
    'queen-pawn': ['d2d4','d7d5','c2c4','e7e6'],
    'english': ['c2c4','e7e5','b1c3','g8f6'],
    'caro-kann': ['e2e4','c7c6','d2d4','d7d5'],
    'scandinavian': ['e2e4','d7d5','e4d5','d8d5'],
}
CHOICES = ('q','r','b','n')
SCENARIOS = ['forward-empty','diagonal-empty','forward-friendly','diagonal-friendly',
             'forward-opponent-king', *[f'{direction}-opponent-{kind}' for direction in ('forward','diagonal') for kind in ('knight','bishop','rook','queen')],
             'single-diagonal-pin','single-file-exposure','single-check-evasion']


def translation_key(fen):
    """Color/file reflection and translation lineage key, ignoring counters."""
    board=chess.Board(fen);forms=[]
    for b in (board,board.mirror()):
        for reflected in (b,b.transform(chess.flip_horizontal)):
            pieces=reflected.piece_map();minx=min(chess.square_file(s) for s in pieces);miny=min(chess.square_rank(s) for s in pieces)
            forms.append(tuple(sorted((p.symbol(),chess.square_file(s)-minx,chess.square_rank(s)-miny) for s,p in pieces.items())))
    return digest(min(forms))


def construct(scenario,rng,extras=0):
    """Boards are created independently; this is not held-out transformation augmentation."""
    for _ in range(20000):
        x=rng.choice((1,2,3,4,5,6));board=chess.Board(None);board.turn=chess.WHITE
        start=chess.square(x,6);diagonal=scenario.startswith('diagonal');end=chess.square(x+(-1 if x==6 else 1) if diagonal else x,7)
        board.set_piece_at(start,chess.Piece(chess.PAWN,chess.WHITE))
        if scenario=='single-diagonal-pin':
            if x==6:continue
            own=chess.square(x-1,5);attacker=chess.square(x+1,7)
            board.set_piece_at(attacker,chess.Piece(chess.BISHOP,chess.BLACK));end=chess.square(x,7)
        elif scenario=='single-file-exposure':
            if x==6:continue
            own=chess.square(x,5);end=chess.square(x+1,7)
            board.set_piece_at(chess.square(x,7),chess.Piece(chess.ROOK,chess.BLACK))
            board.set_piece_at(end,chess.Piece(chess.KNIGHT,chess.BLACK))
        elif scenario=='single-check-evasion':
            if x==1:continue
            own=chess.square(x-1,5);end=chess.square(x-1,7)
            board.set_piece_at(end,chess.Piece(chess.ROOK,chess.BLACK))
        else:
            own=chess.square(rng.randrange(8),rng.choice((0,1,2,3)))
        board.set_piece_at(own,chess.Piece(chess.KING,chess.WHITE))
        occupied=set(board.piece_map())
        if scenario.endswith('opponent-king'):
            enemy=end
        else:
            enemy=rng.choice([s for s in chess.SQUARES if s not in occupied and chess.square_rank(s) in (2,3,4,5)])
        board.set_piece_at(enemy,chess.Piece(chess.KING,chess.BLACK))
        if scenario.endswith('friendly'):
            board.set_piece_at(end,chess.Piece(chess.ROOK,chess.WHITE))
        elif '-opponent-' in scenario and not scenario.endswith('king'):
            kind={'knight':chess.KNIGHT,'bishop':chess.BISHOP,'rook':chess.ROOK,'queen':chess.QUEEN}[scenario.split('-')[-1]]
            board.set_piece_at(end,chess.Piece(kind,chess.BLACK))
        for index in range(extras):
            available=[s for s in chess.SQUARES if s not in board.piece_map() and s not in (start,end) and chess.square_rank(s) in (1,2,3,4)]
            square=rng.choice(available);kind=(chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.PAWN)[index%4]
            board.set_piece_at(square,chess.Piece(kind,index%2==0))
        if board.is_valid():
            return board,start,end
    raise RuntimeError('Cannot build registered scenario '+scenario)


def generate(out):
    out=Path(out);config=read_json(ROOT/'configs/cycle8.json');rng=random.Random(config['seed'])
    prior_paths=['fixtures/dataset.json','artifacts/cycle2/dataset.json','artifacts/cycle3/dataset.json',
        'artifacts/cycle4/datasets/dataset.json','artifacts/cycle5/datasets/dataset.json','artifacts/cycle6/datasets/dataset.json','artifacts/cycle7/datasets/dataset.json']
    historical=[p for path in prior_paths for p in read_json(ROOT/path)['positions']]
    historical_sym={symmetry_key(p['fen']) for p in historical}
    seen={};transformed={};positions=[];examples=[];games=[];excluded=Counter()
    def add(board,split,family,group,focus=None,unknown=(),lineage=(),source_game=None):
        fen=board.fen();sym=symmetry_key(fen);trans=translation_key(fen)
        if sym in historical_sym:excluded['historical-symmetry']+=1;return False
        if sym in seen and (seen[sym][0]!=split or seen[sym][1]!=group):excluded['duplicate-symmetry']+=1;return False
        if trans in transformed and transformed[trans][0]!=split:excluded['cross-split-translation']+=1;return False
        seen[sym]=(split,group);transformed[trans]=(split,group)
        p=Position.from_fen(fen);moves=list(candidates(p));legal={m.uci() for m in board.legal_moves}
        assert legal<={m.notation for m in moves}
        name=f'c8-{split}-{len(positions):04}'
        fixture={'id':name,'fen':fen,'split':split,'family':family,'structural_family':family,
            'source_game':source_game,'dependence_group':group,'transformation_lineage':list(lineage),
            'focus_move':focus,'unknown_squares':[list(s) for s in unknown],
            'candidate_count':len(moves),'promotion_candidates':sum(bool(m.promotion) for m in moves),
            'symmetry_key':sym,'translation_key':trans}
        positions.append(fixture)
        if split=='train':
            for move in moves:
                if not move.promotion:continue
                row=enrich4({'fen':fen,'move':move.notation,'label':move.notation in legal,'source':'C8-synthetic-supervision/'+group,
                    'dependence_group':group,'transformation_lineage':list(lineage),'confidence':config['observation_confidence'],
                    'split':'train','family':family,'position_fixture':name,'unknown_squares':[list(s) for s in unknown]})
                # Unknown inputs cannot supply training confidence, even though an offline oracle sees the full board.
                if unknown:row['confidence']=0.0
                examples.append(row)
        return fixture
    split_specs=[('train',0,config['training_group_repetitions']),('validation',2,1),('combination-holdout',3,1),('adversarial',4,1)]
    for split,extras,repetitions in split_specs:
        for scenario in SCENARIOS:
            for rep in range(repetitions):
                group=f'c8-{split}-{scenario}-{rep}'
                family=('isolated' if extras==0 else f'{extras}-interacting-distractors')+'/'+scenario
                while True:
                    board,start,end=construct(scenario,rng,extras)
                    focus=chess.square_name(start)+chess.square_name(end)+'n'
                    first=add(board,split,family,group,focus)
                    if first:break
                mirror=board.mirror();mirrormove=chess.square_name(chess.square_mirror(start))+chess.square_name(chess.square_mirror(end))+'n'
                # Color mirror is explicitly one source group, not a second independent observation.
                assert add(mirror,split,family,group,mirrormove,lineage=(group,))
    # Incomplete observations are separately identified and do not masquerade as complete FEN inputs.
    for split,extras in (('train',0),('adversarial',4)):
        for rep in range(4):
            while True:
                board,start,end=construct('forward-empty',rng,extras)
                group=f'c8-{split}-incomplete-{rep}'
                fixture=add(board,split,f'{extras}-distractors/incomplete-observation',group,
                    chess.square_name(start)+chess.square_name(end)+'q',unknown=((chess.square_file(end),chess.square_rank(end)),))
                if fixture:break
    for split,families in config['game_families'].items():
        for family in families:
            for index in range(config['games_per_family']):
                seed=config['seed']+1000*(list(OPENINGS).index(family)+1)+index
                game_rng=random.Random(seed);board=chess.Board();history=[];gid=f'c8-game-{family}-{seed}'
                for ply in range(1,config['game_ply_cap']+1):
                    legal=sorted(board.legal_moves,key=lambda m:m.uci())
                    if not legal:break
                    move=chess.Move.from_uci(OPENINGS[family][ply-1]) if ply<=4 else game_rng.choice(legal)
                    assert move in legal;history.append(move.uci());board.push(move)
                    if ply in config['sample_plies']:
                        assert add(board,split,'game/'+family,gid,source_game=gid)
                games.append({'id':gid,'split':split,'family':family,'seed':seed,'initial_fen':chess.STARTING_FEN,
                    'moves':history,'final_fen':board.fen(),'termination':board.outcome().result() if board.outcome() else '160-ply cap'})
    train=[p for p in positions if p['split']=='train'];test=[p for p in positions if p['split']!='train']
    families={s:sorted({p['structural_family'] for p in positions if p['split']==s}) for s in sorted({p['split'] for p in positions})}
    assert not set(families['train']) & {p['structural_family'] for p in test}
    assert not {p['symmetry_key'] for p in train}&{p['symmetry_key'] for p in test}
    assert not {p['translation_key'] for p in train}&{p['translation_key'] for p in test}
    result={'schema':8,'registration_hash':digest(config),'positions':positions,'examples':examples,'games':games,
        'oracle':{'version':chess.__version__,'scope':'Offline training and evaluation only'},
        'leakage_audit':{'structural_families':families,'train_test_family_overlap':[], 'train_test_symmetry_overlap':[],
            'train_test_translation_overlap':[],'train_test_game_overlap':[], 'excluded_generation_candidates':dict(excluded),
            'family_definition':'Complete interaction configuration: isolated or single-ray training; two/three/four additional interacting pieces in validation/combination/adversarial sets. Atomic local promotion predicates deliberately recur.',
            'color_controls':'Color mirrors share their source group and transformation ancestry within one split. They are not independent samples.',
            'sampling':'Constructed supervision and seeded synthetic games are not human games or a claim of IID population sampling.'},
        'counts':dict(Counter(p['split'] for p in positions))}
    result['hash']=digest(result);write_json(out/'datasets/dataset.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    data=generate(parser.parse_args().out);print(data['counts'],len(data['examples']),data['hash'])
