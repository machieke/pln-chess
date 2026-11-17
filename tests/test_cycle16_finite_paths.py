from dataclasses import replace
import pytest
from research.cycle15.native_reasoner import NativeReasoner,Budgets
from research.cycle16.experiments import infer,fixture,observations,knowledge,GENEROUS


def test_finite_native_derivation_and_required_emptiness():
    state,a,t=fixture(tag='test_finite');r=NativeReasoner()
    result=infer(state,a,t,budgets=GENEROUS,reasoner=r)
    assert all(v['classification']=='supported-positive' for v in result['stages'].values())
    assert all('rule_clear-two' in v['answer']['stamps'] for v in result['stages'].values())
    facts,_=observations(state,a,t);query=result['stages']['Attack']['query']
    for empty in [f for f in facts if f.term.startswith('(Empty ')]:
        changed=[f for f in facts if f!=empty]
        assert r.infer(changed,knowledge('F'),query,budgets=GENEROUS)['classification']=='unknown'
    assert r.infer(facts,knowledge('F-minus'),query,budgets=GENEROUS)['classification']=='unknown'


def test_inference_has_no_oracle_dependency(monkeypatch):
    import research.cycle16.corpus as corpus
    def forbidden(*a,**kw):raise AssertionError('Oracle called during inference')
    monkeypatch.setattr(corpus,'reference',forbidden)
    state,a,t=fixture(tag='no_oracle')
    assert infer(state,a,t,budgets=GENEROUS)['stages']['Attack']['classification']=='supported-positive'


def test_native_errors_remain_incomplete():
    class Broken(NativeReasoner):
        def execute_program(self,program,timeout=10):
            return dict(program=program,stdout='',stderr='ERROR synthetic transport failure',incomplete=True)
    state,a,t=fixture(tag='broken')
    result=infer(state,a,t,reasoner=Broken())
    assert all(r['classification']=='incomplete' for r in result['stages'].values())


def test_incompatible_checkpoint_is_rejected():
    from pln_chess.common import ROOT,read_json
    with pytest.raises(ValueError,match='structure mismatch'):
        knowledge('L',read_json(ROOT/'artifacts/cycle15/learning/model.json'))


def test_no_host_path_length_rule_selection():
    class Capture:
        def __init__(self):self.rules=[]
        def infer(self,facts,rules,query,**kw):
            self.rules.append([r.metta() for r in rules])
            return dict(query=query,answer=None,contrary=None,incomplete=False,classification='unknown')
    capture=Capture()
    for length in (1,2,3,4):
        state,a,t=fixture('E'*(length-1),length=length,tag='capture_'+str(length))
        infer(state,a,t,reasoner=capture)
    assert len(capture.rules)==12 and all(r==capture.rules[0] for r in capture.rules)
