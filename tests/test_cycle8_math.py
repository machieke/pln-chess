"""Mathematical reference checks; this never authorizes a native operator."""
from fractions import Fraction as F
import pytest
from evaluation.cycle8_composition_lab import Bounds, UNKNOWN, frechet, consequent, independent, intersection, coverage, check_mathematics


def test_same_marginals_allow_distinct_joint_probabilities():
    # Product is one possible joint, not a uniquely identified conjunction.
    a=Bounds(F(4,5),F(4,5));bounds=frechet(a,a)
    assert bounds==Bounds(F(3,5),F(4,5))
    with pytest.raises(ValueError,match='independence'):
        independent(a,a,{'source_files':['a.json','b.json']})


def test_conclusion_needs_conditional_and_complement_model():
    joint=Bounds(F(1,2),F(1,2))
    assert consequent(joint)==UNKNOWN
    assert consequent(joint,Bounds(1,1))==Bounds(F(1,2),1)
    assert consequent(joint,Bounds(1,1),Bounds(0,0))==joint


def test_conflicting_constraints_are_not_zero_probability():
    with pytest.raises(ValueError):intersection(Bounds(F(4,5),1),Bounds(0,F(1,5)))
    assert Bounds(0,0)!=UNKNOWN


def test_certificate_identity_prevents_duplicate_confidence():
    a={'id':'a','alpha':'1/20'};b={'id':'b','alpha':'1/10'}
    assert coverage([a,a])==coverage([a])==F(19,20)
    assert coverage([a,b])==coverage([b,a])==F(17,20)
    assert coverage([]) is None
    with pytest.raises(ValueError,match='immutable'):
        coverage([a,{'id':'a','alpha':'0'}])


def test_exact_probability_table_validation():
    result=check_mathematics()
    assert result['passed']
    assert result['pairwise_not_mutual_counterexample']['even_parity_P111']=='0'
    assert result['pairwise_not_mutual_counterexample']['odd_parity_P111']=='1/4'
