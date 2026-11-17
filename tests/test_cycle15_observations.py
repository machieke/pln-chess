import copy
import pytest
from evaluation.cycle15_corpus import registration,episode
from research.cycle15.observations import observe,successor,validate_state
from research.cycle15.knowledge import templates,load_rules


def example():return episode(next(r for r in registration() if r['family']['length']==2))


def test_raw_facts_keep_roles_and_exclude_answers():
    e=example();facts,scope=observe(e['state'],e['query']['attacker'],e['query']['target'])
    assert any(e['query']['attacker'] in f.term and e['query']['target'] in f.term for f in facts)
    assert all(e['state']['id'] in f.term for f in facts)
    assert not any(word in f.term for f in facts for word in ('Attack','Clear','Legal','Exposed','Pinned'))
    assert all(f.origin=='environmental-observation' for f in facts)
    assert all('$' in rule for rule in templates().values())


def test_unknown_not_empty_and_structural_successor():
    e=example();a=e['after'];lookup={p['id']:p for p in a['pieces']}
    from research.cycle15.observations import ray
    cell=ray(lookup[e['query']['attacker']]['cell'],lookup[e['query']['target']]['cell'])[1][0]
    a['unknown']=[list(cell)]
    facts,scope=observe(a,e['query']['attacker'],e['query']['target'])
    assert any(f.term.startswith('(UnknownOccupancy ') for f in facts)
    unknown=next(f.term.split()[1] for f in facts if f.term.startswith('(UnknownOccupancy '))
    assert not any(f.term.startswith('(Empty '+unknown+' ') for f in facts)
    assert a['actor']==e['state']['actor'] and a['history']!=e['state']['history']


@pytest.mark.parametrize('key',['label','engine_score','Attacks','reference'])
def test_labels_cannot_enter_state(key):
    state=example()['state'];state[key]=True
    with pytest.raises(ValueError):validate_state(state)


def test_invalid_occupancy_rejected():
    state=example()['state'];state['unknown']=[state['pieces'][0]['cell']]
    with pytest.raises(ValueError):validate_state(state)


def test_state_and_history_change_identity():
    e=example();facts,scope=observe(e['state'],e['query']['attacker'],e['query']['target'])
    changed=copy.deepcopy(e['state']);changed['id']='anotherstate';changed['history']='differenthistory'
    other,other_scope=observe(changed,e['query']['attacker'],e['query']['target'])
    assert scope['state_identity']!=other_scope['state_identity']
    assert not ({s for f in facts for s in f.stamps}&{s for f in other for s in f.stamps})


def test_rule_file_is_separable_data(tmp_path):
    path=tmp_path/'rules.metta';path.write_text('(Rule independent (Implication (P $x) (Different $x)))\n')
    assert load_rules(path=path)[0].term=='(Implication (P $x) (Different $x))'
