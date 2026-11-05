import pytest
from pln_chess.pln import Runtime
from pln_chess.common import ROOT,read_json

@pytest.fixture(scope='session')
def runtime(): return Runtime()

@pytest.fixture(scope='session')
def dataset(): return read_json(ROOT/'fixtures/dataset.json')
