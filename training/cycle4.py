"""Locked Cycle 4 curriculum. Reference rules are confined to this module."""
import random
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.cycle4.ontology import descriptors
from training.cycle3 import enrich


def enrich4(row):
    row=enrich(row);p=Position.from_fen(row['fen']);m=next(m for m in candidates(p) if m.notation==row['move'])
    o=descriptors(p,m);c=o['context']
    # Auxiliary condition labels are generated ONLY in the training boundary.
    # Production sees raw occupancy and learned conditionals, never these labels.
    labels={'BoundaryConflict':not c['destination_exists'],
            'DestinationConflict':c['destination']=='Friendly' or c['destination_kind']=='King'}
    for cell in o['ray_motifs']['cells']:
        affected=o['piece'] in ('Rook','Bishop','Queen','Pawn') or m.effect=='castle'
        labels['Obstruction:'+cell['occupancy']]=affected and cell['occupancy'] not in ('Empty','Boundary')
    return {**row,'c4_component_labels':labels}


def symmetry_key(fen):
    board=chess.Board(fen);forms=[]
    for b in (board,board.mirror()):
        for f in (lambda s:s,chess.flip_horizontal,chess.flip_vertical,chess.flip_diagonal,
                  lambda s:chess.flip_horizontal(chess.flip_vertical(s)),
                  lambda s:chess.flip_horizontal(chess.flip_diagonal(s)),
                  lambda s:chess.flip_vertical(chess.flip_diagonal(s)),
                  lambda s:chess.flip_horizontal(chess.flip_vertical(chess.flip_diagonal(s)))):
            forms.append(b.transform(f).board_fen())
    return min(forms)


def generate(output=None):
    config=read_json(ROOT/'configs/cycle4.json');seed=config['seed'];old=read_json(ROOT/'artifacts/cycle3/dataset.json')
    positions=[dict(p) for p in old['positions'] if p['split']=='train']
    examples=[enrich4(r) for r in old['examples'] if r['split']=='train'];games=[]
    bridge_pools={}
    for target in ('Obstruction','DestinationConflict','BoundaryConflict'):
        groups=sorted({r['dependence_group'] for r in examples if any(v and (k==target or k.startswith(target+':')) for k,v in r['c4_component_labels'].items())},key=digest)
        bridge_pools[target]=groups[:max(2,len(groups)//4)]
    for r in examples:r['constraint_bridge_targets']=[target for target,groups in bridge_pools.items() if r['dependence_group'] in groups]
    occupied={p['fen'] for p in positions};train_sym={symmetry_key(p['fen']) for p in positions}
    def add(name,family,split,board,game=None,focus=None,lineage=None):
        if not board.is_valid():raise ValueError('Invalid fixture '+name)
        fen=board.fen()
        if fen in occupied:raise ValueError('Duplicate fixture '+name)
        if split not in ('translation-control',) and symmetry_key(fen) in train_sym:raise ValueError('Training symmetry overlap '+name)
        occupied.add(fen);pos=Position.from_fen(fen);grammar={m.notation for m in candidates(pos)};legal={m.uci() for m in board.legal_moves}
        if not legal<=grammar:raise ValueError('Candidate grammar missed a legal move')
        positions.append({'id':name,'family':family,'split':split,'fen':fen,'source_game':game,'dependence_group':game or name,
                          'focus_move':focus,'lineage':lineage or [],'candidates':len(grammar),'legal_candidates':len(legal)})
    for split,count,offset in [('validation',config['curriculum']['validation_games'],1000),('independent-games',config['curriculum']['independent_games'],2000)]:
        for game in range(count):
            b=chess.Board();rng=random.Random(seed+offset+game);history=[];gid=f'c4-{split}-seed-{seed+offset+game}'
            # Store the complete generated game to termination or the declared 160-ply cap.
            for ply in range(1,161):
                moves=sorted(b.legal_moves,key=lambda m:m.uci())
                if not moves:break
                move=rng.choice(moves);history.append(move.uci());b.push(move)
                if ply in config['curriculum']['plies']:add(f'{gid}-ply-{ply}',gid,split,b,gid)
            games.append({'id':gid,'split':split,'seed':seed+offset+game,'moves':history,'final_fen':b.fen(),'termination':b.outcome().result() if b.outcome() else '160-ply-cap'})
    # Independently combined layouts; no frozen test row is used as training evidence.
    structural=[
        ('rook-two-blockers','6k1/8/8/8/1R1pP3/8/8/5K2 w - - 0 1','b4g4'),
        ('bishop-two-blockers','6k1/8/8/5p2/4P3/3B4/8/1K6 w - - 0 1','d3h7'),
        ('queen-blocker-capture','6k1/8/8/8/1Q1P2r1/8/8/5K2 w - - 0 1','b4g4'),
        ('knight-jump-and-pin','6k1/8/8/5b2/8/3N4/2P5/1K6 w - - 0 1','d3f4'),
        ('rook-discovery-with-capture','k7/8/8/8/7r/3P1R1K/8/8 w - - 0 1','f3f7'),
        ('pawn-diagonal-exposure','6k1/8/8/5b2/8/3P4/8/1K6 w - - 0 1','d3d4'),
        ('king-knight-contact','6k1/8/8/8/5n2/8/4K3/1R6 w - - 0 1','e2d3'),
        ('double-check-with-blocker','3r2k1/8/8/8/6b1/8/2P2R2/3K4 w - - 0 1','f2d2'),
        ('capture-checker-with-backup','6k1/8/8/8/2b5/8/3r4/3KR3 w - - 0 1','e1d1'),
        ('ep-unknown-history','7k/8/8/1pP5/8/8/8/2K5 w - b6 0 1','c5b6'),
        ('promotion-capture-and-ray','1r6/2P3k1/8/8/8/8/8/3K4 w - - 0 1','c7b8n'),
        ('castle-queen-outer-blocker','6k1/8/8/8/8/8/8/RN2K3 w Q - 0 1','e1c1'),
    ]
    for name,fen,move in structural:add('c4-'+name,'structural-'+name,'structural-combination',chess.Board(fen),focus=move)
    from pln_chess.spatial import translate
    for index,p in enumerate([p for p in positions if p['split']=='train']):
        pos=Position.from_fen(p['fen'])
        if pos.rights!='-' or pos.ep or any(x.kind=='Pawn' for x in pos.pieces):continue
        try:other=translate(pos,(1,0))
        except ValueError:continue
        board=chess.Board(other.fen())
        if other.fen() in occupied or not board.is_valid():continue
        add(f'c4-translation-{index}',p['family'],'translation-control',board,lineage=[p.get('dependence_group',p['id'])])
        if sum(p['split']=='translation-control' for p in positions)>=6:break
    split_counts={s:sum(p['split']==s for p in positions) for s in sorted({p['split'] for p in positions})}
    test=[p for p in positions if p['split'] not in ('train','translation-control')]
    assert not train_sym&{symmetry_key(p['fen']) for p in test}
    result={'schema':4,'seed':seed,'registration_hash':digest(config),'positions':positions,'examples':examples,'games':games,'constraint_bridge_pools':bridge_pools,
            'oracle':{'version':chess.__version__,'scope':'Training and evaluation only'},
            'leakage_audit':{'counts':split_counts,'train_test_fen_overlap':[], 'train_test_board_symmetry_overlap':[],
                'train_test_source_game_overlap':[],'translation_controls':'Intentionally share training lineage; excluded from independent acceptance and bootstrap.',
                'structural_lineage':'Sparse single-component training versus named multi-component evaluation combinations. Not a proof that all abstract submotifs are disjoint; reusable subpremises are intended.',
                'old_sets':'Frozen Cycle 2 and Cycle 3 tests never admitted to training.'}}
    result['hash']=digest(result)
    if output:write_json(output,result)
    return result
