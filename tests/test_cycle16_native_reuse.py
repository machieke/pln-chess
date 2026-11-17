from research.cycle15.native_reasoner import NativeReasoner,Sentence,parse
from research.cycle16.experiments import knowledge,GENEROUS
from research.cycle16.evidence_audit import pair_diagnostic


def test_recursion_keeps_rule_identity_and_guard_rejects_overlap(tmp_path):
    r=NativeReasoner()
    facts=[Sentence('(State test_state)',stamps=('obs_test_state',)),
        Sentence('(Empty c1 test_state)',stamps=('obs_test_c1',)),
        Sentence('(Empty c2 test_state)',stamps=('obs_test_c2',))]
    rules=[s for s in knowledge('R') if s.stamps[0] in ('rule_empty-tail','rule_extend-empty')]
    result=r.infer(facts,rules,'(PathEmpty (Cons c1 (Cons c2 Nil)) test_state)',budgets=GENEROUS)
    assert result['classification']=='unknown' and not result['incomplete']
    extension=next(s for s in result['retained'] if s['term']=='(PathEmpty (Cons c2 Nil) test_state)')
    assert 'rule_extend-empty' in extension['stamps']
    partial=next(s for s in result['retained'] if s['term'].startswith('(Implication (PathEmpty ') and '(Cons c1 ' in s['term'])
    diag=pair_diagnostic(partial,extension,tmp_path)
    assert diag['overlap']==['rule_extend-empty']
    assert diag['markers'][0][1]=='false'
    assert diag['markers'][2][1]  # Direct structural witness bypasses the guard.


def test_rule_files_preserve_the_complete_historical_knowledge():
    from pln_chess.common import ROOT
    from research.cycle15.knowledge import templates
    original=templates();recursive=templates(ROOT/'knowledge/cycle16/recursive.metta')
    finite=templates(ROOT/'knowledge/cycle16/finite_two.metta')
    assert recursive==original and len(original)==11 and len(finite)==12
    assert {k:v for k,v in finite.items() if k!='clear-two'}==original
    assert knowledge('R')==knowledge('F-minus')
    assert len({s.stamps[0] for s in knowledge('F')})==12
