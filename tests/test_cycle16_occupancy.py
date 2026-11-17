import copy
import pytest
from research.cycle16.experiments import fixture,observations,infer,GENEROUS
from research.cycle16.corpus import reference


@pytest.mark.parametrize('occupancy,expected', [('EE',True),('EO',False),('OE',False),('OO',False),
    ('OU',False),('UO',False),('EU',None),('UE',None),('UU',None)])
def test_partial_state_reference_uses_all_completions(occupancy,expected):
    state,a,t=fixture(occupancy,tag='completion_'+occupancy)
    assert reference(state,a,t)['label'] is expected
    facts,scope=observations(state,a,t)
    unknown={f.term.replace('UnknownOccupancy','Empty') for f in facts if 'UnknownOccupancy' in f.term}
    assert not unknown & {f.term for f in facts}


@pytest.mark.parametrize('mutation',['duplicate-unknown','duplicate-piece-cell','known-unknown','invalid-coordinate','label'])
def test_malformed_public_occupancy_rejected(mutation):
    state,a,t=fixture('UU',tag='invalid')
    if mutation=='duplicate-unknown':state['unknown'].append(state['unknown'][0])
    elif mutation=='duplicate-piece-cell':state['pieces'][1]['cell']=state['pieces'][0]['cell']
    elif mutation=='known-unknown':state['unknown'].append(state['pieces'][0]['cell'])
    elif mutation=='invalid-coordinate':state['unknown']=[[8,1]]
    else:state['label']=True
    with pytest.raises(ValueError):observations(state,a,t)


def test_missing_endpoint_does_not_become_negative_attack():
    state,a,t=fixture(tag='absent');state['pieces']=state['pieces'][:1]
    result=infer(state,a,t,budgets=GENEROUS)
    assert not result['query_domain_valid'] and result['stages']['Attack']['classification']=='unknown'


def test_state_and_occurrence_identities_do_not_leak():
    state,a,t=fixture(tag='identity');facts,_=observations(state,a,t)
    changed=copy.deepcopy(state);changed['id']='another_state'
    other,_=observations(changed,a,t)
    assert not {s for f in facts for s in f.stamps}&{s for f in other for s in f.stamps}
