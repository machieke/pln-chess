import pytest
from pln_chess.pln.audit import runtime_audit
from pln_chess.pln import TV,NativeError

def test_native_operator_smokes(tmp_path):
    report=runtime_audit(tmp_path/'audit.json')
    assert report['passed']
    assert len(report['tests'])==8

def test_native_revision_conflicts_and_finite_support(runtime):
    assert runtime.revision(TV(1,.5),TV(0,.5))==TV(.5,2/3)
    assert runtime.revision(TV(1,.5),TV(1,.5))==TV(1,2/3)
    with pytest.raises(NativeError): runtime.revision(TV(1,1),TV(0,.5))

@pytest.mark.parametrize('values',[(float('nan'),.1),(1.1,.2),(.2,-.1)])
def test_bad_truth_values_rejected(values):
    with pytest.raises(NativeError): TV(*values)


def test_native_dependency_across_batch_boundary(runtime):
    # Explicitly use a simpler direct native formula here to avoid intentionally
    # ambiguous A->A inference also matching revision. It verifies materialized
    # dependency bindings across separate native interpreter batches.
    nodes=[('n0','(stv 1.0 0.5)')]+[(f'n{i}',f'(Truth_ModusPonens (n{i-1}) (stv 1.0 0.999))') for i in range(1,402)]
    results=runtime.batch(nodes)
    assert results['n401'].strength==1
    assert results['n401'].confidence==pytest.approx(.5*(.999**401))
