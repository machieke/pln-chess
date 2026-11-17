from fractions import Fraction as F
import ast
from pathlib import Path
import pytest
from pln_chess.common import ROOT
from research.cycle17.reference_models import joint_cases, parameter_reuse, observations, controls, bounds


def test_same_marginals_do_not_identify_joint():
    cases = joint_cases()
    assert {v['marginal_a'] for v in cases.values()} == {F(1, 2)}
    assert {v['marginal_b'] for v in cases.values()} == {F(1, 2)}
    assert [v['joint'] for v in cases.values()] == [F(1, 4), F(1, 2), F(0)]
    assert bounds(F(1, 2), F(1, 2)) == (0, F(1, 2))


def test_parameter_event_and_observation_reuse_are_distinct():
    r = parameter_reuse()
    assert (r['shared_parameter'], r['independently_redrawn'], r['same_event']) == (F(5, 16), F(1, 4), F(1, 2))
    o = observations()
    assert o['posterior_once'] == o['same_observation_replayed_posterior'] == (F(1, 4), F(3, 4))
    assert o['duplicate_likelihood_posterior'] == (F(1, 10), F(9, 10))
    assert o['predictive_once'] == F(5, 8)
    assert o['duplicate_likelihood_prediction'] == F(7, 10)
    assert o['two_predictions_after_one_update'] == F(7, 16)
    assert o['factorized_vector_record_joint'] == F(25, 64)


def test_dependence_controls_and_missing_information():
    c = controls()
    assert c['diamond']['joint'] == F(1, 3) != c['diamond']['incorrect_independent_product']
    assert c['cycle']['before'] == c['cycle']['after']
    assert c['unequal']['bounds'] == (0, F(1, 4))
    assert c['false_hypothesis']['posterior'] == (0, 1)
    assert c['missing_dependence']['point_estimate'] is None
    with pytest.raises(ValueError):
        bounds(F(2), F(1, 2))


def test_strict_reference_import_boundary():
    allowed = ROOT/'research/cycle17/reference_cli.py'
    laboratory = ROOT/'research/cycle17/reference_models.py'
    for directory in ('src', 'training', 'evaluation', 'research', 'scripts'):
        for path in (ROOT/directory).rglob('*.py'):
            if path in (allowed, laboratory):
                continue
            # Include constant strings to catch dynamic import_module/__import__.
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom):
                    assert 'reference_models' not in (node.module or ''), path
                    assert all(a.name != 'reference_models' for a in node.names), path
                if isinstance(node, ast.Import):
                    assert all('reference_models' not in a.name for a in node.names), path
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    assert node.value not in ('reference_models', 'research.cycle17.reference_models'), path
