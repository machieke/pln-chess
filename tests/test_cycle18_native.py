from unittest.mock import patch
import pytest
from pln_chess.common import ROOT,read_json
from research.cycle15.native_reasoner import NativeReasoner,Sentence,Budgets


@pytest.mark.parametrize('arm,expected',[('S-AA','unknown'),('D-AB','supported-positive')])
def test_unchanged_native_minimal_channels_with_evaluation_disabled(arm,expected):
    original=read_json(ROOT/f'artifacts/cycle17/witnesses/{arm}-native.json')['stages']['Attack']
    with patch('chess.Board.attacks',side_effect=AssertionError('oracle forbidden')):
        current=NativeReasoner().infer([Sentence(**r) for r in original['facts']],
            [Sentence(**r) for r in original['rules']],original['query'],contrary=original['contrary_query'],
            budgets=Budgets(**original['budgets']),marginals=original['marginals'],mode=original['api'])
    assert current['classification']==expected
    assert current['answer']==original['answer'] and current['contrary']==original['contrary']
