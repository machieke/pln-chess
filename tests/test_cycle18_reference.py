from fractions import Fraction as F
import pytest
from pln_chess.common import ROOT
from research.cycle18.source_mapping import map_sources, RULES
from research.cycle18.reference_joint import fit, table, likelihood, GRIDS, MODELS, Limits
from research.cycle18.reference_bounds import coupling, posterior_bounds, unidentified


@pytest.fixture(scope='module')
def mapped():
    return map_sources(ROOT)


def test_complete_likelihood_tables_share_conditional_marginals():
    for model in MODELS:
        for a in GRIDS['primary']:
            for b in GRIDS['primary']:
                if model=='M-J-copy' and a!=b:continue
                t=table(a,b,model)
                assert sum(t.values())==1 and min(t.values())>=0
                assert t[1,0]+t[1,1]==a and t[0,1]+t[1,1]==b
    assert likelihood(F(1,2),F(1,2),dict(zip(RULES,(True,True))),'M-J-copy')==F(1,2)
    assert likelihood(F(1,2),F(1,2),dict(zip(RULES,(True,True))),'M-F')==F(1,4)


def test_actual_events_give_known_exact_copy_posterior(mapped):
    r,arms,_=mapped;d=fit(r,arms['S-AA'],'M-J-copy','two').json()
    # Twelve real evaluations, not twenty-four independent successes.
    high=F(3**12,1+3**12);low=1-high
    assert F(d['predictive_probability'])==low*F(1,16)+high*F(9,16)
    assert F(d['repeated_same_event_probability'])==low*F(1,4)+high*F(3,4)
    assert d['resources']['likelihood_evaluations']==24
    assert len(d['event_to_likelihood'])==12


def test_factorized_actual_arm_predictions_match_without_asserting_independence(mapped):
    r,arms,_=mapped
    values={a:fit(r,m,'M-F','two').json()['predictive_probability'] for a,m in arms.items()}
    assert len(set(values.values()))==1
    mean=F(1+3**13,4*(1+3**12))
    assert F(values['D-AB'])==mean**2
    copy=fit(r,arms['S-AA'],'M-J-copy','two').json()
    assert copy['predictive_probability']!=values['S-AA']


def test_joint_assumptions_differ_on_same_recorded_vectors(mapped):
    r,arms,_=mapped
    upper=fit(r,arms['S-AA'],'M-J-upper').json();lower=fit(r,arms['S-AA'],'M-J-lower').json()
    assert upper['event_ids']==lower['event_ids']
    assert upper['predictive_probability']!=lower['predictive_probability']
    assert upper['posterior_identity']!=lower['posterior_identity']


def test_sharp_marginal_coupling_witnesses_attain_bounds(mapped):
    r,arms,_=mapped;f=fit(r,arms['S-AA'],'M-F');d=f.json();b=posterior_bounds(f).json()
    for name,side in [('lower_witness',0),('upper_witness',1)]:
        witness=b[name]
        assert sum(F(p['probability']) for p in witness)==1
        assert sum(F(p['probability'])*F(p['theta_clear'])*F(p['theta_attack']) for p in witness)==F(b['bounds'][side])
        for parameter,info in d['parameter_uncertainty'].items():
            for marginal in info['distribution']:
                assert sum(F(p['probability']) for p in witness if p[parameter]==marginal['value'])==F(marginal['probability'])
    assert F(b['bounds'][0])<=F(d['predictive_probability'])<=F(b['bounds'][1])
    assert unidentified().json()['status']=='not_identified'
    with pytest.raises(ValueError):coupling([dict(value='1/2',probability='2')],[dict(value='1/2',probability='1')])


def test_resource_failure_does_not_produce_prediction(mapped):
    r,arms,_=mapped
    for limit in (Limits(states=1),Limits(groups=1),Limits(likelihood_evaluations=1),Limits(rational_bits=1)):
        d=fit(r,arms['S-AA'],limits=limit).json()
        assert d['status']=='resource_incomplete' and d['predictive_probability'] is None


def test_marginal_coupling_matches_all_two_by_two_feasible_extrema():
    # The entire 2x2 transportation polytope is parameterized by p11.
    a=[dict(value='1/4',probability='1/3'),dict(value='3/4',probability='2/3')]
    b=[dict(value='1/5',probability='3/5'),dict(value='4/5',probability='2/5')]
    feasible=[]
    for p11 in (max(F(0),F(2,3)+F(2,5)-1),min(F(2,3),F(2,5))):
        feasible.append(p11*F(3,4)*F(4,5)+(F(2,3)-p11)*F(3,4)*F(1,5)+(F(2,5)-p11)*F(1,4)*F(4,5)+(1-F(2,3)-F(2,5)+p11)*F(1,4)*F(1,5))
    assert coupling(a,b,True)[1]==min(feasible) and coupling(a,b)[1]==max(feasible)
