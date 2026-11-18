import copy
import pytest
from research.cycle19.lifecycle import Journal,StaleEvidence
from research.cycle19.metrics import summarize


def test_dependency_closure_atomicity_history_and_mutation_defense():
    j=Journal();env=j.add('environment',{'source':'same','occupancy':'E'})
    a=j.add('measurement',{'component':'Clear'},[env]);b=j.add('measurement',{'component':'Attack'},[env])
    other=j.add('unrelated',{'source':'same'});snap=j.snapshot()
    assert j.descendants(env)==j.full_descendants(env)=={env,a,b}
    tx=j.supersede(env,'environment',{'source':'same','occupancy':'O'})
    with pytest.raises(StaleEvidence):j.require(env)
    with pytest.raises(StaleEvidence):j.add('annotation',{},[a])
    with pytest.raises(StaleEvidence):j.snapshot()
    new=tx.draft.add('measurement',{'component':'Clear'},[tx.new]);tx.commit([tx.new,new])
    assert j.require(other)
    with pytest.raises(StaleEvidence):j.require(a)
    old=Journal.historical(snap);assert old.require(env)['payload']['occupancy']=='E'
    value=old.node(env);value['payload']['occupancy']='X'
    assert old.require(env)['payload']['occupancy']=='E'
    with pytest.raises(ValueError):j.add('environment',{'changed':True},ident=env)


def test_generation_replacement_is_required_for_atomic_commit():
    j=Journal();env=j.add('environment',{'version':1});g=j.add('generation',{'arm':'D-AB'},[env])
    tx=j.supersede(env,'environment',{'version':2})
    with pytest.raises(ValueError):tx.commit([tx.new])
    fresh=tx.draft.add('generation',{'arm':'D-AB'},[tx.new]);tx.commit([tx.new,fresh])
    with pytest.raises(StaleEvidence):j.require(g)


@pytest.mark.parametrize('status',['unknown','conflicting','incomplete'])
def test_undefined_precision_and_status_denominators(status):
    stage=dict(classification=status,answer=None,contrary=None,native={})
    row=dict(population='natural-test',split='test',arm='F',root='r',game='g',variant='natural',
        native=dict(stages={'Clear':stage,'Attack':stage}),
        measurement=dict(Clear={'value':True},Attack={'value':True},agreement='agree'))
    result=summarize([row])
    assert all(r['precision'] is None and r['recall']==0 and r['counts'][status]==1 and r['counts']['fn']==0 for r in result)
