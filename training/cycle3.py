"""Independent attack-sensor curriculum and compositional adversaries.

All auxiliary labels and fixture validity checks are isolated from production.
"""
import random
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.cycle3.descriptors import descriptors
from training.factory import attack_labels,reference_label

SEED=314159


def enrich(row):
    p=Position.from_fen(row['fen']);m=next(m for m in candidates(p) if m.notation==row['move'])
    o=descriptors(p,m);board=chess.Board(p.fen());labels=attack_labels(p,m)
    for phase in ('origin','transit'):
        for a in [a for a in o['attack_relations'] if a['phase']==phase]:
            if phase=='origin':state=p
            else:
                from pln_chess.domain import Move
                step=1 if m.end[0]>m.start[0] else -1
                state=p.successor(Move(m.start,(m.start[0]+step,m.start[1])))
            b=chess.Board(state.fen());king=b.king(p.turn=='White');attacker=next(x for x in state.pieces if x.id==a['attacker_id'])
            labels[phase+':'+a['attacker_id']]=king is not None and chess.square(*attacker.square) in b.attackers(p.turn!='White',king)
    try:pseudo=board.is_pseudo_legal(chess.Move.from_uci(m.notation))
    except ValueError:pseudo=False
    # These labels describe separately observable conditions, not legal AND safety.
    components={'PathUnoccupied':all(x=='Empty' for x in o['context']['intermediate']),
                'DestinationAvailable':o['context']['destination'] in ('Empty','Opponent'),
                'BoundaryObserved':o['context']['destination_exists']}
    if m.effect in ('castle','en-passant') or m.promotion:components['TemporalMoveObserved']=pseudo
    return {**row,'attack_labels':labels,'component_labels':components,'movement_label':pseudo}


def generate(output=None):
    old=read_json(ROOT/'artifacts/cycle2/dataset.json');rng=random.Random(SEED)
    positions=[dict(p) for p in old['positions'] if p['split']=='train'];examples=[]
    # Freeze C2's short-ray training mask; no held-out rows are admitted.
    examples=[enrich(r) for r in old['examples'] if r['split']=='train' and r['training_eligible']]
    occupied_fens={p['fen'] for p in old['positions']}
    def add(name,family,split,board,focus=None,group=None,evidence_role='observation'):
        if not board.is_valid():raise ValueError('Invalid fixture '+name+' '+board.fen())
        if board.fen() in occupied_fens:raise ValueError('Duplicate fixture '+name)
        occupied_fens.add(board.fen())
        fixture={'id':name,'family':family,'split':split,'fen':board.fen(),'focus_move':focus,
                 'dependence_group':group or name,'lineage':[],'source_game':None}
        positions.append(fixture);p=Position.from_fen(board.fen())
        for m in candidates(p):
            examples.append(enrich({'position_fixture':name,'family':family,'split':split,'fen':p.fen(),'move':m.notation,
                            'label':reference_label(p,m),'source':f'python-chess/{chess.__version__}',
                            'dependence_group':fixture['dependence_group'],'transformation_lineage':[],
                            'training_eligible':split=='train','evidence_role':evidence_role}))
    # Isolated contact observations: no pinned piece, double check or rich opponent
    # constellation. Actual attacks are labeled by the oracle, not this sampler.
    for kind in (chess.PAWN,chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN,chess.KING):
        for index in range(8):
            for attempt in range(10000):
                b=chess.Board(None);b.turn=True
                squares=rng.sample(list(chess.SQUARES),3)
                b.set_piece_at(squares[0],chess.Piece(chess.KING,True))
                b.set_piece_at(squares[1],chess.Piece(kind,False))
                if kind!=chess.KING:b.set_piece_at(squares[2],chess.Piece(chess.KING,False))
                if not b.is_valid() or b.fen() in occupied_fens:continue
                # Demand at least one contact attack in a successor, without using
                # any frozen-test geometry or labels to choose that contact.
                p=Position.from_fen(b.fen())
                target=p.at((chess.square_file(squares[1]),chess.square_rank(squares[1]))).id
                if any(attack_labels(p,m).get(target,False) for m in candidates(p)):break
            else:raise RuntimeError('Contact sampler failed')
            role='observation' if index<4 else 'exposure-bridge' if index<6 else 'legality-bridge'
            add(f'contact-{chess.piece_name(kind)}-{index}',f'isolated-contact-{chess.piece_name(kind)}','train',b,evidence_role=role)
    adversaries=[]
    for kind,symbol in [('Rook','R'),('Bishop','B'),('Queen','Q'),('Knight','N'),('Pawn','P')]:
        orth=chess.Board('k3r3/8/8/8/5n2/4'+symbol+'3/8/4K3 w - - 0 1')
        diagonal=chess.Board('k7/8/7b/8/8/4'+symbol+'3/8/2K5 w - - 0 1')
        adversaries.extend([(f'orthogonal-pin-{kind}',orth),(f'diagonal-pin-{kind}',diagonal)])
    special=[
      ('double-check','k3r3/8/8/8/1b6/8/3R4/4K3 w - - 0 1'),
      ('check-block','k3r3/8/8/8/8/8/2R5/4K3 w - - 0 1'),
      ('checking-piece-capture','k7/8/8/8/8/8/2R1r3/4K3 w - - 0 1'),
      ('king-capture-protected','k3r3/8/8/8/8/8/4n3/4K3 w - - 0 1'),
      ('king-escape','k3r3/8/8/8/8/8/8/4K3 w - - 0 1'),
      ('castle-transit','k4r2/8/8/8/8/8/8/4K2R w K - 0 1'),
      ('castle-origin','k3r3/8/8/8/8/8/8/4K2R w K - 0 1'),
      ('castle-final','k5r1/8/8/8/8/8/8/4K2R w K - 0 1'),
      ('castle-queen-outer','7k/8/8/8/8/8/8/RB2K3 w Q - 0 1'),
      ('ep-opening-ray','6k1/8/8/r2Pp2K/8/8/8/8 w - e6 0 1'),
      ('ep-clear','6k1/8/8/3Pp3/8/8/8/K7 w - e6 0 1'),
      ('promote-empty','8/3P2k1/8/8/8/8/8/1K6 w - - 0 1'),
      ('promote-capture','4r3/3P2k1/8/8/8/8/8/1K6 w - - 0 1'),
    ]
    adversaries.extend((n,chess.Board(f)) for n,f in special)
    for name,board in adversaries:
        add('challenge-'+name,'combined-'+name,'challenge',board,group='challenge-'+name)
        # Same evaluation family; these are explicitly paired probes, not counted
        # as independent training evidence or independent structural families.
        flipped=board.mirror()
        add('flip-'+name,'combined-'+name,'paired-color-flip',flipped,group='challenge-'+name)
        if not board.castling_rights and board.ep_square is None:
            reflected=board.transform(chess.flip_horizontal)
            add('reflect-'+name,'combined-'+name,'paired-reflection',reflected,group='challenge-'+name)
    for split,count in [('validation',4),('independent-games',8)]:
        for game in range(count):
            b=chess.Board();grng=random.Random(SEED+1000+game+(0 if split=='validation' else 100))
            for _ in range(30+game*3):
                moves=list(b.legal_moves)
                if not moves:break
                b.push(grng.choice(moves))
            add(f'{split}-{game}',f'{split}-game-{game}',split,b)
            positions[-1]['source_game']=f'{split}:{game}'
    train_fens={p['fen'] for p in positions if p['split']=='train'}
    test_fens={p['fen'] for p in positions if p['split']!='train'}
    train_families={p['family'] for p in positions if p['split']=='train'}
    test_families={p['family'] for p in positions if p['split']!='train'}
    assert not train_fens&test_fens and not train_families&test_families
    result={'schema':3,'seed':SEED,'positions':positions,'examples':examples,
            'oracle':{'version':chess.__version__,'scope':'Training/evaluation only'},
            'overlap_audit':{'train_test_fen_overlap':sorted(train_fens&test_fens),'family_overlap':sorted(train_families&test_families),
                             'paired_splits':'Color/reflection share test families and dependence groups; not independent samples.',
                             'support':{split:sum(p['split']==split for p in positions) for split in sorted({p['split'] for p in positions})}}}
    result['hash']=digest(result)
    if output:write_json(output,result)
    return result
