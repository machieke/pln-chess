"""Cycle 2 curriculum. All reference rule adjudication is confined to training."""
import random
import chess
from pln_chess.common import ROOT,digest,write_json,read_json
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.spatial import translate,color_flip
from pln_chess.cycle2.descriptors import descriptors
from training.factory import SPECS,attack_labels,reference_label

SEED=271828

def generate(output=None):
    rng=random.Random(SEED);positions=[]
    def add(id,family,split,fen,focus=None,lineage=None,group=None):
        if not chess.Board(fen).is_valid(): raise ValueError('Invalid fixture '+id)
        positions.append({'id':id,'family':family,'split':split,'fen':fen,'focus_move':focus,
                          'dependence_group':group or id,'lineage':lineage or [],'source_game':None})
    # Preserve historical contrast semantics; all originals remain untouched.
    for id,family,split,fen,focus in SPECS:
        add('c1-'+id,'historical-'+family,'train' if split=='train' else 'adversarial',fen,focus,group='historical-'+family)
    # Four deliberately different generative context families. Primitive relation
    # overlap is intentional; entire motif family and transformation lineage are disjoint.
    for split,count,distances,family in [('train',24,[2],'short-isolated'),('validation',9,[3],'medium-single-clutter'),
                                         ('heldout-transfer',36,[4,5,6],'long-mixed-clutter'),('adversarial',12,[3,5],'dense-opponent-context')]:
        for i in range(count):
            kind=[chess.ROOK,chess.BISHOP,chess.QUEEN][i%3];mode=(i//3)%4;distance=distances[(i//12)%len(distances)]
            diagonal=kind==chess.BISHOP or kind==chess.QUEEN and i%2
            dx,dy=(1,1) if diagonal else (1,0)
            for attempt in range(1000):
                sx=rng.randrange(8-distance);sy=rng.randrange(8-distance if diagonal else 8)
                start=chess.square(sx,sy);end=chess.square(sx+distance,sy+dy*distance)
                board=chess.Board(None);board.turn=chess.WHITE;board.set_piece_at(start,chess.Piece(kind,True))
                path=[chess.square(sx+k,sy+dy*k) for k in range(1,distance)]
                if mode==1: board.set_piece_at(path[0 if split=='train' else -1],chess.Piece(chess.KNIGHT,True))
                if mode in (2,3): board.set_piece_at(end,chess.Piece(chess.KNIGHT,mode==2))
                reserved=set(path+[start,end]);free=[s for s in chess.SQUARES if s not in reserved and board.piece_at(s) is None]
                rng.shuffle(free)
                board.set_piece_at(free.pop(),chess.Piece(chess.KING,True));board.set_piece_at(free.pop(),chess.Piece(chess.KING,False))
                extras={'train':0,'validation':1,'heldout-transfer':2,'adversarial':4}[split]
                for k in range(extras): board.set_piece_at(free.pop(),chess.Piece([chess.KNIGHT,chess.BISHOP,chess.ROOK][k%3],False))
                if board.is_valid(): break
            else: raise RuntimeError('Fixture sampler failed')
            id=f'{split}-ray-{i}';add(id,f'{family}-{chess.piece_name(kind)}-{mode}',split,board.fen(),chess.Move(start,end).uci())
    # Source games never cross partitions. No transformed training games in strict tests.
    for split,number in [('train',3),('validation',1),('heldout-transfer',4),('adversarial',1)]:
        for game in range(number):
            game_seed=SEED+10000+len(positions);grng=random.Random(game_seed);board=chess.Board()
            for ply in range(18+game*8):
                moves=list(board.legal_moves)
                if not moves: break
                board.push(grng.choice(moves))
            id=f'{split}-game-{game}';add(id,id,split,board.fen(),next(iter(board.legal_moves)).uci());positions[-1]['source_game']=game_seed
    # Explicit paired tests are never mixed with independent holdout.
    source=Position.from_fen('8/6k1/8/8/8/2R5/2K5/8 w - - 0 1')
    add('locality-source','paired-locality','train',source.fen(),'c3e3',group='paired-locality')
    add('translated','paired-locality','controlled-translation',translate(source,(1,0)).fen(),'d3f3',['locality-source','translate(1,0)'],group='paired-locality')
    perturbed=chess.Board(source.fen());perturbed.set_piece_at(chess.A8,chess.Piece(chess.KNIGHT,False))
    add('irrelevant-knight','paired-locality','irrelevant-context',perturbed.fen(),'c3e3',['locality-source','add a8 knight'],group='paired-locality')
    add('color-flip','paired-locality','controlled-translation',color_flip(source).fen(),'c6e6',['locality-source','color-flip'],group='paired-locality')
    examples=[];descriptors_by_split={}
    for p in positions:
        pos=Position.from_fen(p['fen']);board=chess.Board(p['fen'])
        for move in candidates(pos):
            try: pseudo=board.is_pseudo_legal(chess.Move.from_uci(move.notation))
            except ValueError: pseudo=False
            obs=descriptors(pos,move);descriptors_by_split.setdefault(p['split'],set()).add(next(r['id'] for r in obs['relations'] if r['tier']==4))
            examples.append({'position_fixture':p['id'],'family':p['family'],'split':p['split'],'fen':p['fen'],'move':move.notation,
                             'training_eligible':p['split']!='train' or obs['piece'] not in ('Rook','Bishop','Queen') or obs['pattern']['geometry']['distance']<=2,
                             'label':reference_label(pos,move),'movement_label':pseudo,'attack_labels':attack_labels(pos,move),
                             'source':'python-chess/'+chess.__version__,'dependence_group':p['dependence_group'],'transformation_lineage':p['lineage']})
    independent=['train','validation','heldout-transfer'];overlaps=[]
    for i,a in enumerate(independent):
        for b in independent[i+1:]:
            fa={p['family'] for p in positions if p['split']==a};fb={p['family'] for p in positions if p['split']==b}
            ga={p['source_game'] for p in positions if p['split']==a and p['source_game']};gb={p['source_game'] for p in positions if p['split']==b and p['source_game']}
            overlaps.append({'a':a,'b':b,'families':sorted(fa&fb),'games':sorted(ga&gb),
                             'fens':sorted({p['fen'] for p in positions if p['split']==a}&{p['fen'] for p in positions if p['split']==b}),
                             'local_descriptor_overlap':len(descriptors_by_split[a]&descriptors_by_split[b])})
    assert all(not o['families'] and not o['games'] and not o['fens'] for o in overlaps)
    result={'schema':2,'seed':SEED,'oracle':chess.__version__,'positions':positions,'examples':examples,'overlap_audit':overlaps,
            'split_policy':'Disjoint generative context families and source games. Reusable local descriptor overlap is the target, not leakage. Paired lineage split separately.',
            'supervision':'Legal labels, auxiliary pseudo-legal movement labels and per-opponent successor attack labels; training only.'}
    result['training_policy']='Only slider distances 1-2 enter Cycle 2 learning. All distances remain in evaluation candidate sets; longer rays are unseen during learning. B0 is the explicitly frozen historical exception.'
    result['hash']=digest(result)
    if output: write_json(output,result)
    return result

if __name__=='__main__':
    data=generate(ROOT/'artifacts/cycle2/dataset.json');print({s:sum(p['split']==s for p in data['positions']) for s in sorted({p['split'] for p in data['positions']})},len(data['examples']),flush=True)
