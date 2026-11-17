"""Public opt-in local consequence interface; candidate is supplied, never chosen."""
from pln_chess.common import digest
from .knowledge import load_rules
from .native_reasoner import Budgets, NativeReasoner, Sentence
from .observations import observe, successor


def infer_state(state, target_relation, knowledge_checkpoint=None, budgets=None, *,
                reasoner=None, full_scope=False, candidate=None, remove_rules=(), omit_terms=(), imported_attack=False):
    if set(target_relation)!={'attacker','target','predicate'} or target_relation['predicate'] not in ('Attack','KingExposed'):
        raise ValueError('Only explicit attack or own-king exposure queries are supported')
    reasoner=reasoner or NativeReasoner()
    a,t=target_relation['attacker'],target_relation['target'];sid=state['id']
    facts,scope=observe(state,a,t,full_scope=full_scope,candidate=candidate)
    facts=[f for f in facts if f.term not in omit_terms]
    if imported_attack:
        if target_relation['predicate']!='KingExposed':raise ValueError('Stage A is an exposure diagnostic')
        facts.append(Sentence(f'(Attack {a} {t} {sid})',1.,.99,('import_'+digest([sid,a,t])[:24],),
                              'stage-a-imported-premise',(state['root'],)))
    if target_relation['predicate']=='Attack':
        query=f'(Attack {a} {t} {sid})';contrary=f'(NoAttack {a} {t} {sid})'
    else:
        query=f'(KingExposed {t} {state["actor"]} {sid})';contrary=f'(NotKingExposed {t} {state["actor"]} {sid})'
    rules=load_rules(knowledge_checkpoint,remove=remove_rules)
    result=reasoner.infer(facts,rules,query,contrary=contrary,budgets=budgets or Budgets(64,128,256,15))
    result.update(observation_scope=scope,stage='A-imported-attack' if imported_attack else 'B-raw-observations',
        model_identity=digest([s.metta() for s in rules]),query_domain_valid=scope['attacker_present'] and scope['target_present'],
        target_semantics='Occupancy-constrained sliding influence, including friendly destination; no legal capture or move legality',
        supplied_fact_count=len(facts),supplied_rule_count=len(rules),native_resident_state=False)
    return result


def infer_consequence(observed_state, supplied_candidate, target_relation, knowledge_checkpoint=None,
                      budgets=None, proof_mode='full', *, reasoner=None):
    if proof_mode not in ('full','summary'):raise ValueError('Choose full or summary proof')
    reasoner=reasoner or NativeReasoner()
    after=successor(observed_state,supplied_candidate)
    before_result=infer_state(observed_state,target_relation,knowledge_checkpoint,budgets,reasoner=reasoner,candidate=supplied_candidate)
    after_result=infer_state(after,target_relation,knowledge_checkpoint,budgets,reasoner=reasoner,candidate=supplied_candidate)
    result=dict(before=before_result,after=after_result,supplied_candidate=supplied_candidate,
        transition=dict(before_state=observed_state['id'],after_state=after['id'],kind='structural-hypothetical'),
        endpoint_comparison=dict(before=before_result['classification'],after=after_result['classification'],
                                 origin='host-diagnostic',native_change_truth_value=None))
    if proof_mode=='summary':
        for endpoint in ('before','after'):
            result[endpoint]={k:v for k,v in result[endpoint].items() if k not in ('facts','rules','selected','retained','remaining','receipt')}
    return result
