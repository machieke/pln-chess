"""Lossless, content-bound queues at the PeTTa transport boundary."""
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from pln_chess.common import digest, read_json, ROOT
from pln_chess.pln import TV
from research.cycle15.native_reasoner import Budgets, parse, render
from research.cycle19.records import record

SCHEMA = 'cycle20-native-state-v1'
POLICY = 'cycle20-bounded-native-v1'
MAP = 'cycle20-state-cells-v1'
ARITIES = {'State':1, 'OriginalActor':2, 'History':2, 'PieceKind':3, 'Owner':3,
           'Occupies':3, 'Empty':2, 'Occupied':2, 'UnknownOccupancy':2, 'RelativeOffset':5,
           'RayPath':5, 'RayMember':4, 'OrderedRayCell':5, 'PathEmpty':2,
           'Clear':4, 'Attack':3, 'NoAttack':3, 'KingExposed':3, 'Implication':2, 'Cons':2}
DIGEST = re.compile(r'[0-9a-f]{64}')
ATOM = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,127}|-?[0-9]{1,3}')
VAR = re.compile(r'\$[A-Za-z_][A-Za-z0-9_]{0,63}')
STAMP = re.compile(r'(?:obs|rule|train|audit)_[A-Za-z0-9_-]{1,120}')
NUMBER = re.compile(r'-?[0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?')


def term(node, *, ground=False, depth=0):
    if depth > 32 or not isinstance(node,list) or not node or not isinstance(node[0],str):
        raise ValueError('Expected bounded chess proposition')
    head,*args = node
    if ARITIES.get(head) != len(args):
        raise ValueError(f'Unknown constructor or arity: {head}')
    for i, arg in enumerate(args):
        if isinstance(arg,list):
            if head != 'Implication' and not ((head,i) in {('Cons',1),('PathEmpty',0),('RayPath',2)} and arg and arg[0]=='Cons'):
                raise ValueError('Unexpected nested data')
            term(arg, ground=ground, depth=depth+1)
        elif not isinstance(arg,str) or not (ATOM.fullmatch(arg) or (not ground and VAR.fullmatch(arg))):
            raise ValueError('Invalid chess term argument')
    return node


def query_list(queries):
    if not isinstance(queries,(tuple,list)) or not 1 <= len(queries) <= 64:
        raise ValueError('Expected 1–64 ground readouts')
    if any(not isinstance(q,str) or len(q)>8192 for q in queries):
        raise ValueError('Invalid readout')
    return [render(term(parse(q),ground=True)) for q in queries]


def tv_stamps(tv, stamps):
    if not isinstance(tv,list) or len(tv)!=3 or tv[0]!='stv' or not all(isinstance(v,str) and NUMBER.fullmatch(v) for v in tv[1:]):
        raise ValueError('Invalid native truth value')
    value=TV(*map(float,tv[1:]))
    if not isinstance(stamps,list) or not stamps or not all(isinstance(s,str) and STAMP.fullmatch(s) for s in stamps) or len(set(stamps))!=len(stamps):
        raise ValueError('Invalid evidence tuple')
    return dict(**value.json(), stamps=stamps)


def sentence(row):
    if not isinstance(row,list) or len(row)!=3 or row[0]!='Sentence' or not isinstance(row[1],list) or len(row[1])!=2:
        raise ValueError('Invalid native sentence')
    prop,tv=row[1]
    return dict(term=render(term(prop)), **tv_stamps(tv,row[2]))


@dataclass(frozen=True)
class Identity:
    state: str
    evidence: str
    model: str
    identity_map: str
    runtime: str
    policy: str = POLICY

    @classmethod
    def create(cls,state,evidence,model,identity_map=MAP):
        return cls(state,evidence,model,identity_map,digest(read_json(ROOT/'configs/runtime-lock.json')))


def seal(identity, inputs, queues, budget, selected, receipt, parent=None):
    payload=dict(schema=SCHEMA, identity=asdict(identity), inputs=inputs, queues=queues,
                 capacities=dict(tasks=budget.tasks,beliefs=budget.beliefs),
                 selected_steps=selected, resource_status='successful',
                 completion='bounded' if queues[0] else 'exhausted', native_receipt=receipt,
                 parent=parent, transport='native-ordered-tuples')
    return dict(**payload,snapshot=digest(payload))


def validate(state, expected, snapshot):
    fields={'schema','identity','inputs','queues','capacities','selected_steps','resource_status',
            'completion','native_receipt','parent','transport','snapshot'}
    if not isinstance(state,dict) or set(state)!=fields or state['schema']!=SCHEMA or state['transport']!='native-ordered-tuples':
        raise ValueError('Unsupported or incomplete snapshot')
    if state['snapshot']!=snapshot or digest({k:v for k,v in state.items() if k!='snapshot'})!=snapshot:
        raise ValueError('Native snapshot content mismatch')
    if state['identity']!=asdict(expected) or expected.runtime!=digest(read_json(ROOT/'configs/runtime-lock.json')) or expected.policy!=POLICY:
        raise ValueError('Workspace generation mismatch')
    if state['resource_status']!='successful' or type(state['selected_steps']) is not int or state['selected_steps']<0:
        raise ValueError('Partial state cannot be restored')
    if not isinstance(state['inputs'],dict) or set(state['inputs'])!={'facts','rules','tasks'}:
        raise ValueError('Missing ordered input identities')
    for ids in state['inputs'].values():
        if not isinstance(ids,list) or len(ids)>256 or not all(isinstance(v,str) and DIGEST.fullmatch(v) for v in ids):
            raise ValueError('Invalid input identities')
    for ref in [state['native_receipt']]+([state['parent']] if state['parent'] is not None else []):
        if not isinstance(ref,str) or not DIGEST.fullmatch(ref):
            raise ValueError('Invalid provenance reference')
    caps=state['capacities']
    if not isinstance(caps,dict) or set(caps)!={'tasks','beliefs'}:
        raise ValueError('Invalid capacities')
    Budgets(0,caps['tasks'],caps['beliefs'])
    queues=state['queues']
    if not isinstance(queues,list) or len(queues)!=2:
        raise ValueError('Missing native queues')
    for queue,cap in zip(queues,(caps['tasks'],caps['beliefs'])):
        if not isinstance(queue,list) or len(queue)>cap:
            raise ValueError('Returned queue exceeds recorded capacity')
        for row in queue: sentence(row)
    if state['completion']!=('bounded' if queues[0] else 'exhausted'):
        raise ValueError('Invalid completion status')
    return state


def export(path, state, expected):
    validate(state,expected,state['snapshot'])
    record(Path(path),state)


def restore(path,expected,snapshot):
    return validate(read_json(path),expected,snapshot)
