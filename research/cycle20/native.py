"""One pinned native derivation and ground readouts over its returned tuple."""
from dataclasses import asdict
import time
from pln_chess.common import digest
from research.cycle15.native_reasoner import NativeReasoner, Budgets, parse, render
from research.cycle16.experiments import MEDIUM, channel, support_status
from .state import STAMP, query_list, seal, sentence, term, tv_stamps, validate


class ExecutionFailure(RuntimeError):
    def __init__(self,reason,receipt):
        super().__init__(reason)
        self.receipt=receipt


def selector(query):
    return ('(BestConfidenceCandidate (collapse (let (Sentence ($Term $TV) $Ev) '
            '(superpose $retained) (case (== $Term '+query+') ((True ($TV $Ev)))))))')


def prints(queries):
    return ' '.join(f'(println! (C20READ {i} {selector(q)}))' for i,q in enumerate(queries))


def materialize(expression, queries, *, save=False):
    actions='(println! (C20STATE $remaining $retained)) '+prints(queries)
    if save:actions+=' (change-state! &c20 ($remaining $retained))'
    return f'!(let ($remaining $retained) {expression} (progn {actions}))\n'


def derive_expression(tasks,beliefs,b):
    return f'(progn (println! (C20DERIVE)) (PLN.Derive {tasks} {beliefs} 1 {b.steps} {b.tasks} {b.beliefs}))'


def fresh_input(facts,rules,tasks=None):
    beliefs=[*facts,*rules]
    tasks=beliefs if tasks is None else list(tasks)
    if len(beliefs)>256 or len(tasks)>256:raise ValueError('Fresh input exceeds 256 sentences')
    for s in [*beliefs,*tasks]:
        term(parse(s.term))
        if not all(STAMP.fullmatch(stamp) for stamp in s.stamps):
            raise ValueError('Expected a namespaced evidence identifier')
    ids={name:[digest(asdict(s)) for s in rows] for name,rows in [('facts',facts),('rules',rules),('tasks',tasks)]}
    def definition(name,rows):return f'(= ({name}) ('+' '.join(s.metta() for s in rows)+'))\n'
    return ids,definition('c20beliefs',beliefs)+definition('c20tasks',tasks)


def decode(receipt,queries,derivations):
    if receipt['incomplete']:raise ExecutionFailure('Incomplete native execution',receipt)
    selected=[];states=[];answers=[];calls=0
    for line in receipt['stdout'].splitlines():
        if line=='(C20DERIVE)':calls+=1
        elif line.startswith('(SELECTED '):selected.append(sentence(parse(line)[1]))
        elif line.startswith('(C20STATE '):states.append(parse(line)[1:])
        elif line.startswith('(C20READ '):
            _,index,value=parse(line)
            if index!=str(len(answers)):raise ExecutionFailure('Misordered native readout',receipt)
            answers.append(tv_stamps(*value) if value else None)
    if len(states)!=1 or calls!=derivations or len(answers)!=len(queries) or (not calls and selected):
        raise ExecutionFailure('Missing or ambiguous native markers',receipt)
    return states[0],selected,answers,calls


def finish(receipt,queries,identity,inputs,budget,calls,parent=None):
    start=time.perf_counter()
    queues,selected,answers,actual=decode(receipt,queries,calls)
    ref=digest(receipt)
    steps=len(selected)+(parent['selected_steps'] if parent else 0)
    state=seal(identity,inputs,queues,budget,steps,ref,parent['snapshot'] if parent else None)
    validate(state,identity,state['snapshot'])
    return dict(state=state,selected=selected,receipt=receipt,derivations=actual,
                readouts=[dict(query=q,answer=a,snapshot=state['snapshot'],generation=state['identity'],
                               native_receipt=ref) for q,a in zip(queries,answers)],
                parse_seconds=time.perf_counter()-start)


def derive(facts,rules,queries,identity,budget=MEDIUM,*,tasks=None,reasoner=None):
    queries=query_list(queries)
    inputs,defs=fresh_input(facts,rules,tasks)
    reasoner=reasoner or NativeReasoner()
    body=materialize(derive_expression('(c20tasks)','(c20beliefs)',budget),queries)
    program=f'!(import! &self "{reasoner.runtime.library}")\n'+defs+body
    return finish(reasoner.execute_program(program,budget.timeout),queries,identity,inputs,budget,1)


def resume(state,identity,snapshot,queries,steps=None,*,timeout=30,reasoner=None):
    """None selects the serialized state directly. Zero invokes derive with allowance zero."""
    queries=query_list(queries);validate(state,identity,snapshot)
    b=Budgets(0 if steps is None else steps,**state['capacities'],timeout=timeout)
    reasoner=reasoner or NativeReasoner()
    prefix=f'!(import! &self "{reasoner.runtime.library}")\n(= (c20previous) {render(state["queues"])})\n'
    expression='(c20previous)'
    if steps is not None:
        expression='(let ($oldtasks $oldbeliefs) (c20previous) '+derive_expression('$oldtasks','$oldbeliefs',b)+')'
    result=finish(reasoner.execute_program(prefix+materialize(expression,queries),timeout),
                  queries,identity,state['inputs'],b,int(steps is not None),state)
    if steps is None and result['state']['queues']!=state['queues']:
        raise ExecutionFailure('Serialized readout changed native queues',result['receipt'])
    return result


def projection(result,query,contrary=None):
    by_query={v['query']:v['answer'] for v in result['readouts']}
    pos=by_query[query];neg=by_query[contrary] if contrary else None
    positive,negative=channel(pos),channel(neg)
    status=('conflicting' if positive and negative else 'supported-positive' if positive else
            'supported-negative' if negative else 'unknown')
    tasks,beliefs=result['state']['queues']
    value=dict(query=query,contrary_query=contrary,answer=pos,contrary=neg,classification=status,
               incomplete=False,selected=result['selected'],retained=list(map(sentence,beliefs)),
               remaining=list(map(sentence,tasks)),completion='bounded run; no completeness claim' if tasks else 'task queue exhausted')
    return dict(**value,support_status=support_status(value))
