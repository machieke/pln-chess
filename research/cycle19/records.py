"""Immutable research artifacts and content identities."""
from pathlib import Path
from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from scripts.cycle15_baseline import sha


def record(path, value):
    path = Path(path)
    if path.exists():
        raise ValueError('Evidence generation already exists: ' + str(path))
    write_json(path, value)
    return value


def output(path):
    path = Path(path).resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError('Executable outputs must be outside the source checkout')
    if path.exists():
        raise ValueError('Use a new output generation')
    path.mkdir(parents=True)
    return path
