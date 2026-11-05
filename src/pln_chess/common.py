"""Serialization and project resources; no reasoning formulas."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("PLN_CHESS_ROOT", Path(__file__).resolve().parents[2]))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
