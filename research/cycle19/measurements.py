"""Offline audit only. Never imported by the native request path."""
import copy
from pathlib import Path
from pln_chess.common import digest
from research.cycle15.observations import validate_state
from .records import sha


def bindings(state,attacker,target,expected_state=None):
    validate_state(state)
    pieces={p['id']:p for p in state['pieces']};a=pieces.get(attacker);t=pieces.get(target)
    if expected_state is not None and state['id']!=expected_state:return None,'state-mismatch'
    if not a or not t or attacker==target or a['kind']!='rook':return None,'role-mismatch'
    dx=t['cell'][0]-a['cell'][0];dy=t['cell'][1]-a['cell'][1]
    if sorted((abs(dx),abs(dy)))!=[0,3]:return None,'outside-two-cell-domain'
    cells=[[a['cell'][0]+i*dx//3,a['cell'][1]+i*dy//3] for i in (1,2)]
    return dict(attacker=attacker,target=target,state=state['id'],cells=cells),None


def clearance(state,bound):
    """Explicit path audit independent of the influence implementation."""
    occupied={tuple(p['cell']) for p in state['pieces']};unknown={tuple(c) for c in state['unknown']}
    statuses=['O' if tuple(c) in occupied else 'U' if tuple(c) in unknown else 'E' for c in bound['cells']]
    value=False if 'O' in statuses else None if 'U' in statuses else True
    return dict(value=value,occupancy=statuses,method='explicit-coordinate-path-occupancy-v1')


def influence(state,bound):
    """Independently reconstruct board and ask rook influence, including friends."""
    import chess
    if state['unknown']:return dict(value=None,method='python-chess.Board.attacks',reason='reference-state-not-fully-specified')
    board=chess.Board(None);pieces={p['id']:p for p in state['pieces']}
    for piece in pieces.values():
        board.set_piece_at(chess.square(*piece['cell']),chess.Piece(getattr(chess,piece['kind'].upper()),piece['owner']=='white'))
    a=chess.square(*pieces[bound['attacker']]['cell']);t=chess.square(*pieces[bound['target']]['cell'])
    return dict(value=t in board.attacks(a),method='python-chess.Board.attacks',implementation_version=chess.__version__)


def environment(root,*,reference=None,observed=None,variant='natural'):
    return dict(root=root['id'],source_collection=root['source_collection'],game=root['game_identity'],
        ancestry=root['source_ancestry'],split=root['split'],variant=variant,
        reference=copy.deepcopy(reference or root['state']),observed=copy.deepcopy(observed or root['state']),
        attacker=root['attacker'],target=root['target'])


def measure(journal,event,*,expected_state=None):
    node=journal.require(event)
    if node['kind']!='environment':raise ValueError('Expected environmental parent')
    env=node['payload'];state=env['reference'];observed=env['observed']
    bound,reason=bindings(state,env['attacker'],env['target'],expected_state)
    observed_bound,observed_reason=bindings(observed,env['attacker'],env['target'])
    if state['id']!=observed['id']:observed_reason='state-mismatch';observed_bound=None
    clear=clearance(state,bound) if bound else dict(value=None,method='explicit-coordinate-path-occupancy-v1',reason=reason)
    attack=influence(state,bound) if bound else dict(value=None,method='python-chess.Board.attacks',reason=reason)
    raw=clearance(observed,observed_bound)['value'] if observed_bound else None
    agreement='unresolved' if clear['value'] is None or attack['value'] is None else 'agree' if clear['value']==attack['value'] else 'disagree'
    measurements={};annotations={}
    for target,rule,result,antecedent in (
        ('Clear','clear-two',clear,raw),('Attack','rook-attack',attack,clear['value'] if observed_bound else None)):
        payload=dict(target=target,result=result,bindings=bound,input_sha256=digest(state),
            implementation_sha256=sha(Path(__file__)),parent_event=event,agreement=agreement,
            source_collection=env['source_collection'],game=env['game'],root=env['root'],ancestry=env['ancestry'],
            fully_specified_reference=not state['unknown'],observed_input_sha256=digest(observed))
        measurement=journal.add('measurement',payload,[event]);measurements[target]=measurement
        # Terminal fit also requires its available raw context to be known;
        # an unknown environmental correction must never become an empty fact.
        eligible=antecedent is True and raw is True and result['value'] is not None and agreement=='agree'
        annotation=dict(rule=rule,target=target,label=result['value'],antecedent=antecedent,
            admitted=eligible,reason='qualified' if eligible else 'unknown-antecedent' if antecedent is None or raw is None else 'false-antecedent-or-unresolved-measurement',
            ancestry=env['ancestry'],root=env['root'],game=env['game'],split=env['split'],
            component=measurement,environment=event,trust=.5)
        parents=[measurement]
        if target=='Attack':parents.append(measurements['Clear'])
        annotations[target]=journal.add('annotation',annotation,parents)
    return dict(environment=event,measurements=measurements,annotations=annotations,
        Clear=clear,Attack=attack,agreement=agreement,raw_antecedent=raw,
        unresolved=bool(reason or observed_reason),bindings=bound)


def matrix(root,pattern):
    """U hides original truth; E/O change truth. Preserve separate state layers."""
    if len(pattern)!=2 or set(pattern)-set('EOU'):raise ValueError('Expected two E/O/U symbols')
    reference=copy.deepcopy(root['state']);bound,reason=bindings(reference,root['attacker'],root['target'])
    if reason:raise ValueError(reason)
    for i,(cell,value) in enumerate(zip(bound['cells'],pattern)):
        if value=='U':continue
        reference['pieces']=[p for p in reference['pieces'] if p['cell']!=cell]
        if value=='O':reference['pieces'].append(dict(id='intervention_'+str(i)+'_'+root['id'],kind='knight',owner=reference['actor'],cell=cell))
    reference['id']='variant_'+digest([root['id'],pattern])[:24]
    reference['history']='hypothetical_'+digest([root['state']['history'],pattern])[:24]
    observed=copy.deepcopy(reference)
    for cell,value in zip(bound['cells'],pattern):
        if value=='U':
            observed['pieces']=[p for p in observed['pieces'] if p['cell']!=cell];observed['unknown'].append(cell)
    return environment(root,reference=reference,observed=observed,variant=pattern)


def transformed(root,kind):
    env=environment(root,variant=kind)
    for layer in ('reference','observed'):
        state=env[layer];state['id']='transform_'+digest([root['id'],kind])[:24]
        state['history']='history_'+digest([state['history'],kind])[:24]
        for piece in state['pieces']:
            if kind=='rotate':piece['cell']=[7-n for n in piece['cell']]
            elif kind=='reflect':piece['cell'][0]=7-piece['cell'][0]
            elif kind=='rename':piece['id']='renamed_'+digest(piece['id'])[:24]
            else:raise ValueError(kind)
    if kind=='rename':
        env['attacker']='renamed_'+digest(root['attacker'])[:24];env['target']='renamed_'+digest(root['target'])[:24]
    return env
