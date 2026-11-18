import ast
from pathlib import Path
import pytest
from pln_chess.common import ROOT
from research.cycle19.records import output
from research.cycle19.corpus import roots


def test_native_path_cannot_import_measurement_or_reference():
    tree=ast.parse((ROOT/'research/cycle19/native.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom):
            assert not any(x in (node.module or '').split('.') for x in ('measurements','reference','learning','chess'))
    assert 'Board.attacks' not in (ROOT/'research/cycle19/native.py').read_text()


def test_frozen_sampling_and_source_holdout():
    items=roots();assert len(items)==128 and len({r['game_identity'] for r in items})==128
    assert all(r['direction']!='-y' for r in items if r['split'] in ('A','B'))
    assert sum(r['split']=='test' for r in items)==56


def test_output_fence_resolves_symlinks(tmp_path):
    link=tmp_path/'source';link.symlink_to(ROOT)
    with pytest.raises(ValueError):output(link/'artifacts/cycle19/bad')
    path=output(tmp_path/'new')
    with pytest.raises(ValueError):output(path)
