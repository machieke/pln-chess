"""State-wide entity identities and evidence-preserving union of structural rays."""
from dataclasses import dataclass,replace
from pln_chess.common import ROOT,digest,read_json
from research.cycle15.observations import validate_state, identifier
from research.cycle15.native_reasoner import Budgets,parse,render
from research.cycle16.experiments import observations,knowledge
from .state import Identity, MAP

COMBINED=Budgets(64,128,256,30)
CELL_SLOTS={'Occupies':(2,), 'Occupied':(1,), 'Empty':(1,), 'UnknownOccupancy':(1,),
            'RayMember':(3,), 'OrderedRayCell':(4,)}
PIECE_SLOTS={'Occupies':(1,), 'PieceKind':(1,), 'Owner':(1,), 'RelativeOffset':(1,2),
             'RayMember':(1,2), 'RayPath':(1,2), 'OrderedRayCell':(1,2)}

def eligible(state):
    validate_state(state)
    return sorted((a['id'],t['id']) for a in state['pieces'] if a['kind']=='rook'
                  for t in state['pieces'] if sorted(abs(x-y) for x,y in zip(a['cell'],t['cell']))==[0,3])

def path_names(node,names):
    if node=='Nil':return node
    return ['Cons',names[node[1]],path_names(node[2],names)]

def queries(state,a,t,shape):
    return [f'(Clear {a} {t} {shape or "unaligned"} {state})',f'(Attack {a} {t} {state})',f'(NoAttack {a} {t} {state})']

@dataclass
class Workspace:
    identity: Identity
    facts: list
    rules: list
    rays: list
    queries: list
    lineage: dict

def build(state,rays,model=None,*,events=None):
    """Events are independent identified deliveries of this raw capture. Replay is idempotent."""
    validate_state(state)
    state_ref=digest(state)
    event_ids=sorted({identifier(e) for e in (events if events is not None else ['capture_'+digest([state['root'],state['id'],state['history']])])})
    if not event_ids:raise ValueError('At least one identified observation event required')
    coords={(x,y):'c_'+digest([MAP,state_ref,x,y])[:24] for x in range(8) for y in range(8)}
    pieces={p['id']:'p_'+digest([MAP,state_ref,p['id']])[:24] for p in state['pieces']}
    if len(set(coords.values()))!=64 or len(set(pieces.values()))!=len(pieces):raise ValueError('Identity collision')
    roles=sorted(set(tuple(r) for r in rays))
    if not roles:raise ValueError('At least one structural ray required')
    facts={};origins={};local_maps={};targets=[]
    for a,t in roles:
        local,scope=observations(state,a,t)
        if a not in pieces or t not in pieces:raise ValueError('Missing observed endpoint')
        mapping={name:coords[tuple(cell)] for name,cell in scope['cell_roles'].items()}
        local_maps[render([a,t])]=mapping
        targets.extend(queries(state['id'],pieces[a],pieces[t],scope['shape']))
        for old,origin in zip(local,scope['fact_origins']):
            value=parse(old.term);pred=value[0]
            for slot in CELL_SLOTS.get(pred,()):value[slot]=mapping[value[slot]]
            for slot in PIECE_SLOTS.get(pred,()):value[slot]=pieces[value[slot]]
            if pred=='RayPath':value[3]=path_names(value[3],mapping)
            text=render(value)
            for event in event_ids:
                stamp='obs_'+digest([event,state_ref,origin['source'],text])[:28]
                fact=replace(old,term=text,stamps=(stamp,))
                if stamp in facts and facts[stamp]!=fact:raise ValueError('Conflicting immutable observation')
                facts[stamp]=fact
                row=origins.setdefault(stamp,dict(event=event,category=origin['source'],term=text,legacy=[]))
                row['legacy'].append(dict(ray=[a,t],stamp=old.stamps[0],term=old.term))
    model_id=model['version'] if model else 'supplied'
    identity=Identity.create(state['id'],digest([state_ref,event_ids,sorted(facts)]),model_id)
    return Workspace(identity,list(facts.values()),knowledge('L',model) if model else knowledge('F'),
                     roles,targets,dict(schema=MAP,state=state_ref,source_events=event_ids,
                     cells={name:list(cell) for cell,name in coords.items()},pieces=pieces,
                     legacy_cell_maps=local_maps,observations=origins))

def fixture(dense=False):
    def piece(name,xy,kind='rook',owner='white'):
        return dict(id=name,cell=list(xy),kind=kind,owner=owner)
    if dense:
        pieces=[piece(f'entity_{i}_{j}',(i,j)) for i in (1,4,7) for j in (1,4,7)]
    else:
        pieces=[piece('rowrook',(1,3)),piece('rowtarget',(4,3),'king','black'),
                piece('colrook',(2,2)),piece('coltarget',(2,5),'bishop','black'),
                piece('blocker',(2,4),'knight','black')]
    label='dense' if dense else 'cross'
    state=dict(id='state_'+label,root='root_'+label,history='history_'+label,actor='white',pieces=pieces,unknown=[])
    return state,eligible(state)[:8] if dense else [('rowrook','rowtarget'),('colrook','coltarget')]

def models():
    values=read_json(ROOT/'artifacts/cycle19/learning/models.json')
    return {'F':None,**{arm:values[arm]['model'] for arm in ('D-AB','S-AA')}}
