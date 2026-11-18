import copy
import pytest
from research.cycle16.experiments import fixture
from research.cycle19.lifecycle import Journal
from research.cycle19.measurements import environment,measure,matrix


def root(occupancy='EE',friendly=False,reverse=False):
    state,a,t=fixture(occupancy,tag='c19_hand')
    if friendly:state['pieces'][1]['owner']=state['pieces'][0]['owner']
    if reverse:
        for p in state['pieces']:p['cell']=[7-c for c in p['cell']]
    return dict(id=state['root'],state=state,attacker=a,target=t,source_collection='hand-fixture',
        game_identity='hand-fixture',source_ancestry='hand-fixture',split='A')


@pytest.mark.parametrize('occupancy,expected',[('EE',True),('OE',False),('EO',False),('OO',False)])
@pytest.mark.parametrize('friendly,reverse',[(False,False),(True,False),(False,True)])
def test_hand_inspectable_clear_and_influence(occupancy,expected,friendly,reverse):
    j=Journal();event=j.add('environment',environment(root(occupancy,friendly,reverse)))
    value=measure(j,event)
    assert value['Clear']['value'] is expected and value['Attack']['value'] is expected
    assert value['Clear']['method']!=value['Attack']['method']
    assert value['agreement']=='agree'
    assert j.node(value['annotations']['Clear'])['payload']['admitted'] is expected


def test_withholding_preserves_hidden_truth_and_unknown_antecedent():
    r=root('OE');env=matrix(r,'UE');j=Journal();value=measure(j,j.add('environment',env))
    assert value['Clear']['value'] is False and value['Attack']['value'] is False
    assert value['raw_antecedent'] is None
    assert env['reference']['unknown']==[] and len(env['observed']['unknown'])==1


@pytest.mark.parametrize('fault',['state','role'])
def test_mismatched_binding_is_unresolved(fault):
    j=Journal();env=environment(root())
    if fault=='role':env['attacker']='absent_attacker'
    event=j.add('environment',env)
    result=measure(j,event,expected_state='other_state' if fault=='state' else None)
    assert result['unresolved'] and result['Clear']['value'] is None and result['Attack']['value'] is None


def test_observed_state_mismatch_cannot_train():
    j=Journal();env=environment(root());env['observed']['id']='wrong_state'
    m=measure(j,j.add('environment',env))
    assert m['unresolved']
    assert all(not j.node(k)['payload']['admitted'] for k in m['annotations'].values())


def test_measurements_are_distinct_and_disagreement_is_not_hidden(monkeypatch):
    monkeypatch.setattr('chess.Board.attacks',lambda *args:set())
    j=Journal();m=measure(j,j.add('environment',environment(root())))
    assert m['Clear']['value'] is True and m['Attack']['value'] is False
    assert m['agreement']=='disagree'
    assert all(not j.node(k)['payload']['admitted'] for k in m['annotations'].values())
