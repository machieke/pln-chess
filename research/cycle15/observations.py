"""Connected geometry/occupancy observations, with no attack adjudication."""
import copy
import re
from pln_chess.common import digest
from .native_reasoner import Sentence, render

KINDS={'rook','bishop','queen','king','knight','pawn'}
SIDES={'white','black'}


def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',value):
        raise ValueError('Unsafe episode identifier')
    return value


def coordinate(cell):
    if not isinstance(cell,(list,tuple)) or len(cell)!=2 or any(type(n) is not int or not 0<=n<8 for n in cell):
        raise ValueError('Expected in-board coordinate')
    return tuple(cell)


def validate_state(state):
    if set(state)!={'id','root','actor','history','pieces','unknown'}:
        raise ValueError('Only raw state fields are accepted; labels and scores are excluded')
    for key in ('id','root','history'):identifier(state[key])
    if state['actor'] not in SIDES:raise ValueError('Invalid actor')
    ids=set();cells=set()
    for piece in state['pieces']:
        if set(piece)!={'id','kind','owner','cell'} or piece['kind'] not in KINDS or piece['owner'] not in SIDES:
            raise ValueError('Invalid typed piece')
        ident=identifier(piece['id']);cell=coordinate(piece['cell'])
        if ident in ids or cell in cells:raise ValueError('Duplicate piece identity or cell')
        ids.add(ident);cells.add(cell)
    for cell in state['unknown']:coordinate(cell)
    if cells & {tuple(c) for c in state['unknown']}:
        raise ValueError('Competing known/unknown occupancy must be resolved by the caller')
    return True


def successor(state, candidate):
    """Structural displacement only: no legality or attack calls."""
    validate_state(state)
    if set(candidate)!={'id','piece','destination'}:raise ValueError('Only a supplied displacement is permitted')
    identifier(candidate['id']);identifier(candidate['piece']);destination=coordinate(candidate['destination'])
    moved=next((p for p in state['pieces'] if p['id']==candidate['piece']),None)
    if moved is None:raise ValueError('Moved piece must be observed')
    result=copy.deepcopy(state)
    result['id']='after_'+digest([state,candidate])[:24]
    result['history']='hypothetical_'+digest([state['history'],candidate])[:24]
    result['pieces']=[p for p in result['pieces'] if tuple(p['cell'])!=destination or p['id']==moved['id']]
    next(p for p in result['pieces'] if p['id']==moved['id'])['cell']=list(destination)
    result['unknown']=[c for c in result['unknown'] if tuple(c)!=destination]
    validate_state(result)
    return result


def ray(start,end):
    dx,dy=end[0]-start[0],end[1]-start[1]
    shape='orthogonal' if (dx==0) != (dy==0) else 'diagonal' if dx and abs(dx)==abs(dy) else None
    if not shape:return None,[]
    length=max(abs(dx),abs(dy));sx=(dx>0)-(dx<0);sy=(dy>0)-(dy<0)
    return shape,[(start[0]+sx*i,start[1]+sy*i) for i in range(1,length)]


def observe(state, attacker, target, *, full_scope=False, candidate=None):
    validate_state(state);identifier(attacker);identifier(target)
    if attacker==target:raise ValueError('Distinct endpoint roles are required')
    by_id={p['id']:p for p in state['pieces']};by_cell={tuple(p['cell']):p for p in state['pieces']}
    a,t=by_id.get(attacker),by_id.get(target)
    shape,cells=ray(a['cell'],t['cell']) if a and t else (None,[])
    relevant={attacker,target}
    relevant.update(by_cell[c]['id'] for c in cells if c in by_cell)
    if candidate:relevant.add(candidate['piece'])
    pieces=state['pieces'] if full_scope else [p for p in state['pieces'] if p['id'] in relevant]
    state_id=state['id'];facts=[];origins=[]
    def add(term, origin='raw-observation'):
        text=render(term);stamp='obs_'+digest([state['root'],state_id,text])[:28]
        facts.append(Sentence(text,1.,.99,(stamp,),'environmental-observation',(state['root'],)))
        origins.append(dict(term=text,category='environmental-observation',source=origin,stamp=stamp,
                            ancestry=state['root'],state=state_id))
    add(['State',state_id]);add(['OriginalActor',state_id,state['actor']]);add(['History',state_id,state['history']])
    # Cell names are episode-local structural roles, never absolute squares.
    all_cells=sorted(set(cells)|{tuple(p['cell']) for p in pieces}|{tuple(c) for c in state['unknown']})
    names={cell:'cell_'+str(i) for i,cell in enumerate(all_cells)}
    for piece in pieces:
        add(['PieceKind',piece['id'],piece['kind'],state_id])
        add(['Owner',piece['id'],piece['owner'],state_id])
        add(['Occupies',piece['id'],names[tuple(piece['cell'])],state_id])
    unknown={tuple(c) for c in state['unknown']}
    for cell in all_cells:
        add(['UnknownOccupancy' if cell in unknown else 'Occupied' if cell in by_cell else 'Empty',names[cell],state_id])
    if a and t:
        add(['RelativeOffset',attacker,target,str(t['cell'][0]-a['cell'][0]),str(t['cell'][1]-a['cell'][1]),state_id], 'structural-geometry')
        if shape:
            path='Nil'
            for cell in reversed(cells):path=['Cons',names[cell],path]
            add(['RayPath',attacker,target,path,shape,state_id],'structural-geometry')
            for index,cell in enumerate(cells):
                add(['RayMember',attacker,target,names[cell],state_id],'structural-geometry')
                add(['OrderedRayCell',attacker,target,str(index),names[cell],state_id],'structural-geometry')
    if candidate:
        add(['SuppliedCandidate',candidate['id'],candidate['piece'],state_id],'hypothetical-input')
    return facts,dict(state_id=state_id,history=state['history'],root=state['root'],attacker=attacker,target=target,
        target_present=t is not None,attacker_present=a is not None,shape=shape,
        relevant_ray_cells=[list(c) for c in cells],cell_roles={name:list(cell) for cell,name in names.items()},
        full_scope=full_scope,pieces=len(pieces),fact_origins=origins,
        selection='Whole structural endpoint ray and supplied moved piece; independent of occupancy answer and labels',
        state_identity=digest(state), scope_kind='host-selected dependency neighborhood, not a proof')
