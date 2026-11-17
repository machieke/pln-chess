import json
from pathlib import Path
import pytest
from research.cycle15.native_reasoner import Budgets, NativeReasoner, Sentence, proposition, alpha_key
from evaluation.cycle15_capabilities import cases


@pytest.fixture(scope='module')
def reasoner():return NativeReasoner()


@pytest.mark.parametrize('name,expected',[('one-rule','supported-positive'),('two-rules','supported-positive'),
    ('missing-premise','unknown'),('removed-rule','unknown'),('shared-role','supported-positive'),
    ('swapped-role','unknown'),('shared-diamond','unknown'),('independent-join','supported-positive'),
    ('opposing-channels','conflicting'),('query-variable','unknown')])
def test_capability_interventions(reasoner,name,expected):
    spec=dict(next(row for row in cases() if row['name']==name));spec.pop('name')
    result=reasoner.infer(**spec)
    assert result['classification']==expected
    assert not result['incomplete']
    if expected=='supported-positive':assert result['answer']['stamps']


def test_exact_queue_and_order_boundaries(reasoner):
    facts=[Sentence('P',1,.5,('p',)),Sentence('P',0,.5,('n',))]
    a=reasoner.infer(facts,[],'P',budgets=Budgets(0))
    b=reasoner.infer(list(reversed(facts)),[],'P',budgets=Budgets(0))
    assert a['answer']['strength']==1 and b['answer']['strength']==0
    bounded=reasoner.infer(facts,[],'P',budgets=Budgets(1,1,1))
    assert bounded['usage']['retained_beliefs']==0


def test_native_failure_remains_incomplete(reasoner,monkeypatch):
    actual=reasoner.execute_program
    def fail(program,timeout):
        result=actual('!(println! unrelated)\n',timeout)
        result.update(incomplete=True,returncode=1,stderr='synthetic failure')
        return result
    monkeypatch.setattr(reasoner,'execute_program',fail)
    result=reasoner.infer([Sentence('P',stamps=('p',))],[],'P')
    assert result['classification']=='incomplete' and result['answer'] is None


@pytest.mark.parametrize('bad',['(P a) !(system x)','(= (P x) (Q x))','(P (Truth_Revision x y))','(P "evil")'])
def test_executable_input_rejected(bad):
    with pytest.raises(ValueError):proposition(bad)


def test_no_zero_queue_hang():
    with pytest.raises(ValueError):Budgets(tasks=0)


def test_native_variable_renaming_does_not_count_as_inference():
    assert alpha_key('(Implication (P $x) (Q $x))')==alpha_key('(Implication (P $_0) (Q $_0))')
    assert alpha_key('(Pair $x $x)')!=alpha_key('(Pair $x $y)')


def test_invalid_native_truth_value_is_incomplete(reasoner,monkeypatch):
    original=reasoner.execute_program
    def malformed(program,timeout):
        receipt=original('!(println! malformed)\n',timeout)
        receipt['stdout']='(C15STATE () ((Sentence (P (stv 2.0 0.5)) (p))))\n'
        return receipt
    monkeypatch.setattr(reasoner,'execute_program',malformed)
    result=reasoner.infer([Sentence('P',stamps=('p',))],[],'P')
    assert result['classification']=='incomplete'
    assert 'Invalid native STV' in result['receipt']['parse_error']
