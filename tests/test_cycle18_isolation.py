import ast
import json
import subprocess
from pathlib import Path
import pytest
from pln_chess.common import ROOT
from research.cycle18.cli import output_directory


def test_reference_imports_never_reach_native_or_operational_code():
    forbidden=('reference_joint','reference_bounds','research.cycle18')
    for directory in ('src','training','evaluation','research','scripts'):
        for path in (ROOT/directory).rglob('*.py'):
            if path.is_relative_to(ROOT/'research/cycle18') or path.name.startswith('cycle18_'):
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                names=[]
                if isinstance(node,ast.ImportFrom):names=[node.module or '',*(a.name for a in node.names)]
                if isinstance(node,ast.Import):names=[a.name for a in node.names]
                if isinstance(node,ast.Constant) and isinstance(node.value,str):names=[node.value]
                assert not any(n==f or n.startswith(f+'.') for n in names for f in forbidden),path
    native=ast.parse((ROOT/'research/cycle18/native_comparison.py').read_text())
    for node in ast.walk(native):
        if isinstance(node,ast.ImportFrom):assert 'reference' not in (node.module or '')
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            assert node.value not in ('reference_joint','research.cycle18.reference_joint','reference_bounds','research.cycle18.reference_bounds')


def test_output_fence_rejects_native_historical_paths_and_symlinks(tmp_path):
    for path in (ROOT,ROOT/'artifacts/cycle12/model/ref.json',ROOT/'src/new',ROOT/'artifacts/cycle17/new'):
        with pytest.raises(ValueError):output_directory(ROOT,path)
    link=tmp_path/'escape';link.symlink_to(ROOT/'artifacts/cycle12')
    with pytest.raises(ValueError):output_directory(ROOT,link/'model/new')
    output_directory(ROOT,tmp_path/'valid')
    with pytest.raises(ValueError):output_directory(ROOT,tmp_path/'valid')


def test_reference_runtime_does_not_import_or_execute_native(tmp_path):
    code='''import sys
from pathlib import Path
def fence(event,args):
    if event in ('subprocess.Popen','os.system'): raise AssertionError('native process forbidden')
    if event=='open' and isinstance(args[0],str) and args[0].endswith('.pgn'): raise AssertionError('PGN not needed')
sys.addaudithook(fence)
from research.cycle18.cli import contract
out=Path(sys.argv[1]);out.mkdir()
contract(Path(sys.argv[2]),out)
assert not any(m.startswith(('research.cycle15.native_reasoner','pln_chess.pln','training.')) for m in sys.modules)
'''
    completed=subprocess.run([str(ROOT/'.venv/bin/python'),'-c',code,str(tmp_path/'reference'),str(ROOT)],capture_output=True,text=True)
    assert completed.returncode==0,completed.stderr
    for path in (tmp_path/'reference/reference_cases').rglob('*.json'):
        text=path.read_text()
        assert '(stv ' not in text and 'supported-positive' not in text
        assert 'native_checkpoint_reference": "' not in text
