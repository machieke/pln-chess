"""Synthetic root registration and evaluation-only chess references."""
import copy
import itertools
import random

from pln_chess.common import digest
from research.cycle15.observations import ray, successor


def root_family(direction, length, blocker, kind):
    return dict(direction=list(direction), length=length, blocker=blocker, kind=kind)


def registration():
    directions=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    families=[]
    for direction in directions:
        for length in range(2,8):
            for blocker in range(1,length):
                for kind in ('queen','rook' if 0 in direction else 'bishop'):
                    families.append(root_family(direction,length,blocker,kind))
    rng=random.Random(15)
    short=[f for f in families if f['length']==2];long=[f for f in families if f['length']>2]
    rng.shuffle(short);rng.shuffle(long)
    cohorts={'train':short[:8]+long[:16],'development':short[8:12]+long[16:24],
             'test':short[12:]+long[24:68]}
    result=[]
    for split,items in cohorts.items():
        for index,family in enumerate(items):
            result.append(dict(id='root_'+digest(family)[:20],split=split,family=family,
                               source_ancestry='synthetic-geometry-'+digest(family)[:20],seed=index))
    assert len(result)==84 and len({r['id'] for r in result})==84
    return result


def episode(root, *, translated=False, renamed=False):
    f=root['family'];dx,dy=f['direction'];length=f['length']
    xs=range(8-length) if dx>0 else range(length,8) if dx<0 else range(8)
    ys=range(8-length) if dy>0 else range(length,8) if dy<0 else range(8)
    starts=list(itertools.product(xs,ys))
    start=starts[(root['seed']+int(translated))%len(starts)]
    end=(start[0]+dx*length,start[1]+dy*length)
    block=(start[0]+dx*f['blocker'],start[1]+dy*f['blocker'])
    all_ray={start,end,*ray(start,end)[1]}
    free=[(x,y) for y in range(8) for x in range(8) if (x,y) not in all_ray]
    prefix=('new_' if renamed else 'p_')+root['id'][-6:]+'_'
    a,t,b,n=[prefix+k for k in ('attacker','target','blocker','unrelated')]
    state=dict(id='state_'+digest([root['id'],start,renamed])[:20],root=root['id'],actor='white',
        history='history_'+root['id'][-12:],unknown=[],pieces=[
            dict(id=a,kind=f['kind'],owner='black',cell=list(start)),
            dict(id=t,kind='king',owner='white',cell=list(end)),
            dict(id=b,kind='knight',owner='white',cell=list(block)),
            dict(id=n,kind='pawn',owner='black',cell=list(free[-1]))])
    candidate=dict(id='move_'+root['id'][-12:],piece=b,destination=list(free[0]))
    return dict(root=root,state=state,candidate=candidate,
                query=dict(attacker=a,target=t,predicate='Attack'),after=successor(state,candidate))


def variants(base):
    """Dependent diagnostics, never additional statistical roots."""
    result={'sole-blocker-leaves':(base['state'],base['after'])}
    state=base['state'];after=base['after'];a=base['query']['attacker'];t=base['query']['target']
    lookup={p['id']:p for p in state['pieces']};start=lookup[a]['cell'];end=lookup[t]['cell']
    _,cells=ray(start,end);blocker=base['candidate']['piece']
    other=[c for c in cells if list(c)!=lookup[blocker]['cell']]
    if other:
        along=successor(state,{**base['candidate'],'destination':list(other[0])})
        result['moves-along-ray']=(state,along)
        second=copy.deepcopy(state);second['id']+='second'
        second['pieces'].append(dict(id='secondblocker',kind='pawn',owner='white',cell=list(other[-1])))
        result['second-blocker-remains']=(second,successor(second,base['candidate']))
    unknown=copy.deepcopy(after);unknown['id']+='unknown';unknown['unknown']=[list(cells[0])]
    result['unknown-cell']=(state,unknown)
    unrelated=next(p for p in state['pieces'] if p['id'] not in (a,t,blocker))
    occupied={tuple(p['cell']) for p in state['pieces']};offray=next([x,y] for x,y in itertools.product(range(8),repeat=2)
        if (x,y) not in occupied and (x,y) not in cells)
    result['unrelated-move']=(state,successor(state,dict(id='unrelatedmove',piece=unrelated['id'],destination=offray)))
    for name,removed in (('attacker-removed',a),('target-removed',t)):
        current=copy.deepcopy(after);current['id']+=name;current['pieces']=[p for p in current['pieces'] if p['id']!=removed]
        result[name]=(state,current)
    replaced=copy.deepcopy(after);replaced['id']+='replacement'
    next(p for p in replaced['pieces'] if p['id']==t)['id']='replacementtarget'
    result['target-replaced']=(state,replaced)
    ordinary=copy.deepcopy(after);ordinary['id']+='ordinary'
    next(p for p in ordinary['pieces'] if p['id']==t)['kind']='knight'
    result['ordinary-target']=(state,ordinary)
    friendly=copy.deepcopy(after);friendly['id']+='friendly'
    next(p for p in friendly['pieces'] if p['id']==a)['owner']='white'
    result['friendly-source']=(state,friendly)
    return result


def reference(state, query):
    """This module is never imported by production inference."""
    import chess
    lookup={p['id']:p for p in state['pieces']};a=lookup.get(query['attacker']);t=lookup.get(query['target'])
    if a is None or t is None:return dict(label=None,reason='query-entity-absent')
    _,cells=ray(a['cell'],t['cell'])
    if {tuple(c) for c in state['unknown']} & {tuple(a['cell']),tuple(t['cell']),*cells}:
        return dict(label=None,reason='relevant-occupancy-unknown')
    board=chess.Board(None)
    for p in state['pieces']:
        board.set_piece_at(chess.square(*p['cell']),chess.Piece(getattr(chess,p['kind'].upper()),p['owner']=='white'))
    label=chess.square(*t['cell']) in board.attacks(chess.square(*a['cell']))
    if query['predicate']=='KingExposed':
        label=label and t['kind']=='king' and t['owner']==state['actor'] and a['owner']!=state['actor']
    return dict(label=label,reason='python-chess occupancy-constrained influence; not legal capture')
