"""Raw observations to pinned native reasoning. No evaluator imports."""
from dataclasses import asdict
from pln_chess.common import ROOT,digest,read_json
from research.cycle15.native_reasoner import NativeReasoner,save_result
from research.cycle15.knowledge import load_rules
from research.cycle16.experiments import observations,MEDIUM,support_status
from .lifecycle import POLICY

HISTORICAL=ROOT/'artifacts/cycle17/learning/S-AA/model.json'


def request(journal,environment,generation=None,*,arm='F',out,budgets=MEDIUM,
            remove=(),drop_empty=False,query_state=None,query_attacker=None,cache=None):
    node=journal.require(environment)
    if node['kind']!='environment':raise ValueError('Expected environment')
    env=node['payload'];state=env['observed'];attacker=env['attacker'];target=env['target']
    # Reference state and measurement payloads are deliberately inaccessible
    # below this boundary: only the strictly typed observed raw state is used.
    model=journal.require(generation)['payload'] if generation else read_json(HISTORICAL) if arm=='H' else None
    if generation and journal.node(generation)['kind']!='generation':raise ValueError('Expected generation')
    facts,scope=observations(state,attacker,target)
    if drop_empty:
        first=next((i for i,f in enumerate(facts) if f.term.startswith('(Empty ')),None)
        if first is not None:facts=facts[:first]+facts[first+1:]
    rules=load_rules(model,path=ROOT/'knowledge/cycle16/finite_two.metta',remove=remove)
    state_id=query_state or state['id'];a=query_attacker or attacker
    queries={'Clear':(f'(Clear {a} {target} {scope["shape"] or "unaligned"} {state_id})',None),
        'Attack':(f'(Attack {a} {target} {state_id})',f'(NoAttack {a} {target} {state_id})')}
    key=digest(dict(policy=POLICY,environment=environment,state=state,history=state['history'],
        generation=generation,model=model['version'] if model else 'supplied',runtime=read_json(ROOT/'configs/runtime-lock.json'),
        queries=queries,facts=[asdict(f) for f in facts],rules=[asdict(r) for r in rules],budgets=asdict(budgets)))
    if cache:
        cached=cache.get(key,journal)
        if cached is not None:return cached,dict(cache_hit=True,key=key,native_calls=0)
    reasoner=NativeReasoner();stages={}
    for name,(query,contrary) in queries.items():
        result=reasoner.infer(facts,rules,query,contrary=contrary,budgets=budgets)
        result['support_status']=support_status(result)
        semantic={k:result[k] for k in ('query','contrary_query','facts','rules','answer','contrary','classification','selected','retained','remaining')}
        stages[name]=dict(native=save_result(result,out),observable_sha256=digest(semantic),classification=result['classification'],
            support_status=result['support_status'],answer=result['answer'],contrary=result['contrary'],
            incomplete=result['incomplete'],completion=result['completion'])
    result=dict(schema='cycle19-native-consequence-v1',environment=environment,generation=generation,
        model=model['version'] if model else 'supplied',arm=arm,query=queries,stages=stages,
        scope=scope,cache_identity=key,proof_observability='Selected and retained statements; fired-rule parents not exposed',
        boundary='Both native invocations start from the same raw facts and full supplied templates; no answer bridging')
    parents=[environment]+([generation] if generation else [])
    application=journal.add('application',dict(cache_identity=key,observable_hashes={k:v['observable_sha256'] for k,v in stages.items()}),parents)
    result['application']=application
    if cache:cache.put(key,result,journal,[application])
    return result,dict(cache_hit=False,key=key,native_calls=2)
