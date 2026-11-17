import sys
from unittest.mock import patch
import pytest
from pln_chess.common import ROOT, read_json
from research.cycle16.experiments import fixture
from research.cycle17.study import infer
from research.cycle17.provenance import witness, audit


@pytest.mark.parametrize('arm,expected,overlap', [('S-AA', 'unknown', 12), ('S-BB', 'unknown', 12),
    ('D-AB', 'supported-positive', 0), ('D-BA', 'supported-positive', 0), ('overlap-1', 'unknown', 1)])
def test_guarded_composition_from_published_models(tmp_path, arm, expected, overlap):
    model = read_json(ROOT/'artifacts/cycle17/learning'/arm/'model.json')
    state, a, t = fixture(tag='c17_test')
    # An oracle call would fail; inference consumes only raw environmental facts.
    with patch('chess.Board.attacks', side_effect=AssertionError('Oracle forbidden')):
        result = infer(state, a, t, checkpoint=model)
    assert result['stages']['Clear']['classification'] == 'supported-positive'
    assert result['stages']['Attack']['classification'] == expected
    audit(result)
    w = witness(result, tmp_path)
    assert len(w['diagnostic']['overlap']) == overlap
    assert w['diagnostic']['markers'][0][1] == ('false' if overlap else 'true')
    assert w['diagnostic']['markers'][2][1]


def test_removals_preserve_negative_support_and_unknown(tmp_path):
    model = read_json(ROOT/'artifacts/cycle17/learning/D-AB/model.json')
    for occupancy, expected in [('EE', 'unknown'), ('OE', 'supported-negative'), ('EU', 'unknown')]:
        state, a, t = fixture(occupancy, tag='remove_'+occupancy)
        result = infer(state, a, t, checkpoint=model, remove=('rook-attack',))
        assert result['stages']['Attack']['classification'] == expected
        assert not result['stages']['Attack']['incomplete']
