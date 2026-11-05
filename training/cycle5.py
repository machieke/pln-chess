"""Predeclared combination holdouts and supervised premise observations.

All oracle and auxiliary-label construction lives outside production inference.
The factorial transfer model excludes the C4 prior; full-model overlap is audited
separately rather than pretending an old trained context was unseen.
"""
import random
import chess
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.domain import Position,Move,parse_square
from pln_chess.api import find_move
from pln_chess.hypotheses import candidates
from pln_chess.cycle5 import SCHEMA
from pln_chess.cycle5.ontology import descriptors
from training.cycle4 import symmetry_key

def payload(row,rt,families=None):
    p=Position.from_fen(row['fen']);m=find_move(p,row['move']);o=descriptors(p,m)
    targets=[];labels=row.get('c4_component_labels',{})
    for rel in o['typed_relations']:
        if families is not None and rel['family'] not in families:continue
        target=rel['target'];label=None
        if target=='GeometryCompatible' and row.get('geometry_label',row.get('movement_label',False)):label=True
        if target=='DestinationConflict':label=labels.get('DestinationConflict')
        if target=='BoundaryConflict':label=labels.get('BoundaryConflict')
        if target=='RayObstruction':label=labels.get('Obstruction:'+rel['descriptor']['occupancy'])
        if label is not None:targets.append({**rel,'label':label})
    return {'position_id':p.id,'candidate_id':m.id,'relative_feature_fingerprint':o['abstract_combination'],
            'label':row['label'],'source':row['source'],'dependence_group':row['dependence_group'],
            'transformation_lineage':row.get('transformation_lineage',[]),'targets':targets,
            'observation_tv':{'strength':float(row['label']),'confidence':row.get('confidence',.5)},
            'runtime_version':rt.version,'model_version':SCHEMA,'input':{'fen':p.fen(),'move':m.notation},
            'fine_combination':o['fine_combination'],'abstract_combination':o['abstract_combination'],
            'structural_family':row.get('structural_family',row['source'])}

def fixture(piece,src,dst,destination='Empty',blocker=None,extra=0):
    """Evaluation fixture builder, with validity checked by the reference engine."""
    b=chess.Board(None);s=chess.parse_square(src);t=chess.parse_square(dst)
    b.set_piece_at(s,chess.Piece(piece,chess.WHITE))
    if destination!='Empty':b.set_piece_at(t,chess.Piece(chess.PAWN,destination=='Friendly'))
    if blocker:b.set_piece_at(chess.parse_square(blocker[0]),chess.Piece(chess.PAWN,blocker[1]=='Friendly'))
    if extra and chess.parse_square('a2') not in (s,t):b.set_piece_at(chess.parse_square('a2'),chess.Piece(chess.PAWN,chess.WHITE))
    for wk in ([s] if piece==chess.KING else map(chess.parse_square,['a1','b1','a2','h1','b2'])):
        if piece!=chess.KING and b.piece_at(wk):continue
        for bk in map(chess.parse_square,['h8','g8','h7','g7','a8','b8']):
            if b.piece_at(bk) or bk in (wk,t):continue
            q=b.copy();q.set_piece_at(wk,chess.Piece(chess.KING,chess.WHITE));q.set_piece_at(bk,chess.Piece(chess.KING,chess.BLACK));q.turn=chess.WHITE
            if q.is_valid():return q
    raise ValueError('Unable to construct valid factorial board')

def audit_leakage(train,test,prior):
    def keys(rows,key):return {r[key] for r in rows}
    report={}
    for key in ('fine_combination','abstract_combination','dependence_group','structural_family'):
        report[key+'_overlap']=sorted(keys(train,key)&keys(test,key))
    report['ancestry_overlap']=sorted({a for r in train for a in [r['dependence_group']]+r.get('transformation_lineage',[])}&
                                      {a for r in test for a in [r['dependence_group']]+r.get('transformation_lineage',[])})
    report['board_symmetry_overlap']=sorted({symmetry_key(r['fen']) for r in train}&{symmetry_key(r['fen']) for r in test})
    report['factorial_passed']=not any(report.values())
    report['full_C4_prior_test_overlap']={key:sorted(keys(prior,key)&keys(test,key)) for key in ('fine_combination','abstract_combination')}
    report['interpretation']='Factorial-only premise model is the independent transfer arm. Frozen C4 prior may already know test contexts; its overlap is explicitly listed and is not evidence of new transfer.'
    return report

def generate(runtime,output=None):
    config=read_json(ROOT/'configs/cycle5.json');old=read_json(ROOT/'artifacts/cycle4/datasets/dataset.json')
    train=[];tests=[];positions=[]
    def record(name,family,board,move,split,supervised=None):
        p=Position.from_fen(board.fen());m=find_move(p,move)
        if m is None:raise ValueError('Fixture outside grammar '+name)
        o=descriptors(p,m);label=chess.Move.from_uci(move) in board.legal_moves
        from training.cycle4 import enrich4
        raw=enrich4({'fen':board.fen(),'move':move,'label':label,'source':name,'dependence_group':family,'split':split,'confidence':.5})
        row={**raw,'geometry_label':True,'structural_family':family,'fine_combination':o['fine_combination'],
             'abstract_combination':o['abstract_combination'],'supervised_families':supervised or []}
        (train if split=='factorial-train' else tests).append(row)
        if split!='factorial-train':
            positions.append({'id':name,'family':family,'fen':board.fen(),'split':'combination-holdout','focus_move':move,
                              'source_game':None,'dependence_group':name,'lineage':[]})
    geometry=[(chess.KNIGHT,'d4','e6','Empty'),(chess.ROOK,'c3','c4','Empty'),(chess.BISHOP,'d3','e4','Empty'),
              (chess.QUEEN,'c3','c4','Empty'),(chess.QUEEN,'d3','e4','Empty'),(chess.PAWN,'d4','e5','Empty'),
              (chess.PAWN,'d4','d5','Friendly'),(chess.KING,'d3','e4','Empty')]
    # Repetitions share a synthetic-family dependence group. They test source
    # deduplication and must never inflate native confidence as independent data.
    for i,(kind,src,dst,dest) in enumerate(geometry):
        for replicate in range(4):record(f'c5-geometry-{i}-source-{replicate}','train-geometry-'+str(i),fixture(kind,src,dst,dest,extra=replicate%2),src+dst,'factorial-train',['geometry'])
    for dest in ('Empty','Friendly','Opponent'):
        for replicate in range(4):record(f'c5-destination-{dest}-{replicate}','train-destination-'+dest,fixture(chess.KING,'d3','f3',dest,extra=replicate%2),'d3f3','factorial-train',['destination','boundary'])
    for kind in (chess.ROOK,chess.BISHOP,chess.QUEEN):
        dst='f6' if kind==chess.BISHOP else 'f4';cell='e5' if kind==chess.BISHOP else 'e4'
        for occupancy in ('Friendly','Opponent'):
            for replicate in range(4):record(f'c5-ray-{kind}-{occupancy}-{replicate}',f'train-ray-{kind}-{occupancy}',fixture(kind,'d4',dst,blocker=(cell,occupancy),extra=replicate%2),'d4'+dst,'factorial-train',['ray'])
    for kind in (chess.KNIGHT,chess.ROOK,chess.BISHOP,chess.QUEEN,chess.PAWN,chess.KING):
        src,dst={chess.KNIGHT:('f6','h5'),chess.ROOK:('b4','g4'),chess.BISHOP:('c3','g7'),chess.QUEEN:('b4','g4'),chess.PAWN:('c4','d5'),chess.KING:('c3','d4')}[kind]
        record(f'c5-capture-{kind}',f'test-capture-{kind}',fixture(kind,src,dst,'Opponent'),src+dst,'test')
    for kind in (chess.ROOK,chess.BISHOP,chess.QUEEN):
        src,dst,cell=('c3','g7','e5') if kind==chess.BISHOP else ('b4','g4','e4')
        for occ in ('Friendly','Opponent'):
            record(f'c5-blocked-capture-{kind}-{occ}',f'test-blocked-capture-{kind}-{occ}',fixture(kind,src,dst,'Opponent',(cell,occ)),src+dst,'test')
    record('c5-pawn-forward','test-pawn-forward',fixture(chess.PAWN,'c4','c5'),'c4c5','test')
    record('c5-knight-friendly','test-knight-friendly',fixture(chess.KNIGHT,'f6','h5','Friendly'),'f6h5','test')
    # Exposure and temporal families are separate external holdouts, not folded
    # into the clean factorial non-overlap claim.
    for name,fen,move in [
        ('pinned','7k/8/8/8/4r3/8/2R5/2K5 w - - 0 1','c2e2'),
        ('discovered','7k/8/8/8/8/8/r2R3K/8 w - - 0 1','d2d3'),
        ('unsafe-king','7k/8/8/8/4r3/8/2K5/8 w - - 0 1','c2d3'),
        ('ep','7k/8/8/1pP5/8/8/8/2K5 w - b6 0 1','c5b6'),
        ('castle','6k1/8/8/8/8/8/8/4K2R w K - 0 1','e1g1'),
        ('check-resolution','3r2k1/8/8/8/8/8/2R5/3K4 w - - 0 1','c2d2')]:
        b=chess.Board(fen);assert b.is_valid(),name
        positions.append({'id':'c5-'+name,'family':'structural-'+name,'fen':fen,'split':'structural-holdout','focus_move':move,'source_game':None})
    prior=[]
    for row in old['examples']:
        o=descriptors(Position.from_fen(row['fen']),find_move(Position.from_fen(row['fen']),row['move']))
        prior.append({**row,'fine_combination':o['fine_combination'],'abstract_combination':o['abstract_combination']})
    leak=audit_leakage(train,tests,prior);assert leak['factorial_passed'],leak
    games=[];blocked_sym={symmetry_key(p['fen']) for cycle,path in [('cycle2','dataset.json'),('cycle3','dataset.json'),('cycle4','datasets/dataset.json')] for p in read_json(ROOT/f'artifacts/{cycle}/{path}')['positions']}
    blocked_sym|={symmetry_key(r['fen']) for r in train}
    for split,count in [(s,config['games'][s]) for s in ('validation','independent-games')]:
        for index in range(count):
            seed=config['seed']+(1000 if split=='validation' else 2000)+index;rng=random.Random(seed);b=chess.Board();moves=[];gid=f'c5-{split}-{seed}'
            for ply in range(1,config['games']['max_plies']+1):
                legal=sorted(b.legal_moves,key=lambda m:m.uci())
                if not legal:break
                m=rng.choice(legal);moves.append(m.uci());b.push(m)
                if ply in config['games']['plies']:
                    assert symmetry_key(b.fen()) not in blocked_sym
                    grammar={m.notation for m in candidates(Position.from_fen(b.fen()))}
                    assert {m.uci() for m in b.legal_moves}<=grammar
                    positions.append({'id':gid+f'-ply-{ply}','family':gid,'fen':b.fen(),'split':split,'source_game':gid,'dependence_group':gid,'focus_move':None})
            games.append({'id':gid,'seed':seed,'split':split,'moves':moves,'final_fen':b.fen()})
    factorial=[payload(r,runtime,r['supervised_families']) for r in train]
    # C4 bridge-training groups are not reused to learn their antecedents.
    examples=[]
    for row in old['examples']:
        allowed=['geometry','destination','ray','boundary']
        withheld=row.get('constraint_bridge_targets',[])
        if row.get('evidence_role')=='legality-bridge':withheld=['DestinationConflict','Obstruction','BoundaryConflict']
        allowed=[f for f in allowed if {'destination':'DestinationConflict','ray':'Obstruction','boundary':'BoundaryConflict'}.get(f) not in withheld]
        examples.append(payload(row,runtime,allowed))
    result={'schema':5,'seed':config['seed'],'registration_hash':digest(config),'positions':positions,'games':games,
            'factorial_train':train,'factorial_test':tests,'factorial_evidence':factorial,'examples':examples+factorial,
            'leakage_audit':leak,'game_leakage_audit':{'sampled_board_symmetry_overlap_with_C2_C4_and_training':[],
                'policy':'Distinct full-game seeds and provenance; only sampled test positions are symmetry-audited. Opening prefixes can coincide and never become training evidence.'},
            'supervision_caution':'Repeated synthetic observations share their family dependence group and contribute at most once per hypothesis. Sample efficiency counts distinct contexts separately from repeated observations.',
            'oracle_scope':'Fixture generation, auxiliary supervision and evaluation only.'}
    result['hash']=digest(result)
    if output:write_json(output,result)
    return result
