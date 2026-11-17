import copy
import sys
import pytest
from research.cycle15.native_reasoner import NativeReasoner,Budgets
from research.cycle15.queries import infer_state,infer_consequence
from evaluation.cycle15_corpus import registration,episode


@pytest.fixture(scope='module')
def short():return episode(next(r for r in registration() if r['family']['length']==2))


def test_native_occupancy_consequence_without_oracle(short,monkeypatch):
    monkeypatch.setitem(sys.modules,'chess',None)
    result=infer_consequence(short['state'],short['candidate'],short['query'])
    assert result['before']['classification']=='supported-negative'
    assert result['after']['classification']=='supported-positive'
    assert result['endpoint_comparison']['native_change_truth_value'] is None
    assert result['after']['query'] not in [f['term'] for f in result['after']['facts']]


def test_role_correct_exposure_and_wrong_owner(short):
    query={**short['query'],'predicate':'KingExposed'}
    result=infer_state(short['after'],query,imported_attack=True,budgets=Budgets(128,256,512,30))
    assert result['classification']=='supported-positive'
    ordinary=copy.deepcopy(short['after']);ordinary['id']+='ordinary'
    next(p for p in ordinary['pieces'] if p['id']==query['target'])['kind']='knight'
    invalid=infer_state(ordinary,query,imported_attack=True,budgets=Budgets(128,256,512,30))
    assert invalid['classification']=='unknown'


def test_rule_removal_has_no_descriptor_fallback(short):
    result=infer_state(short['after'],short['query'],remove_rules=('rook-attack','bishop-attack','queen-orthogonal','queen-diagonal'))
    assert result['classification']=='unknown'


def test_requests_are_isolated(short):
    reasoner=NativeReasoner()
    first=infer_state(short['after'],short['query'],reasoner=reasoner)
    missing=copy.deepcopy(short['after']);missing['id']='missing'
    missing['pieces']=[p for p in missing['pieces'] if p['id']!=short['query']['attacker']]
    second=infer_state(missing,short['query'],reasoner=reasoner)
    assert first['classification']=='supported-positive'
    assert second['classification']=='unknown' and not second['query_domain_valid']
