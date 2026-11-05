"""Static and runtime oracle boundaries, split leakage, and rule-key audits."""
import ast
import builtins
import re
from pathlib import Path
from pln_chess.common import ROOT,canonical
from pln_chess.api import explain_move
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.observations import observe


def test_production_dependency_boundary():
    # Development CLI deliberately imports evaluation only in explicit commands.
    for file in (ROOT/'src/pln_chess').rglob('*.py'):
        if file==ROOT/'src/pln_chess/cli/__init__.py': continue
        tree=ast.parse(file.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): modules=[n.name for n in node.names]
            elif isinstance(node,ast.ImportFrom): modules=[node.module or '']
            else: modules=[]
            assert not any(m.split('.')[0] in ('chess','training','evaluation') for m in modules),str(file)
            if isinstance(node,ast.Attribute):
                assert node.attr not in ('legal_moves','is_check','is_attacked_by','is_legal','is_pseudo_legal','attackers'),str(file)
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                assert node.name not in ('is_legal','is_check','is_attacked','king_safe','ray_clear'),str(file)


def test_inference_with_oracle_imports_disabled(runtime,monkeypatch):
    original=builtins.__import__
    def no_oracle(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'): raise AssertionError('Oracle leakage')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',no_oracle)
    r=explain_move('7k/8/8/8/8/8/2R5/2K5 w - - 0 1','c2e2',runtime=runtime)
    assert r['error'] is None


def test_splits_and_relative_rule_descriptors(dataset):
    groups={}
    for p in dataset['positions']:
        if p['split']=='controlled-transfer': continue
        groups.setdefault(p['family'],set()).add(p['split'])
    assert all(len(s)==1 for s in groups.values())
    for p in dataset['positions']:
        pos=Position.from_fen(p['fen'])
        for move in candidates(pos):
            obs=observe(pos,move)
            text=canonical(obs['context'])
            assert not re.search(r'"[a-h][1-8]"',text)
            assert pos.id not in text and move.id not in text
