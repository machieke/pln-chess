"""Serialization and project resources; no reasoning formulas."""
from __future__ import annotations
import hashlib
from dataclasses import fields, is_dataclass
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("PLN_CHESS_ROOT", Path(__file__).resolve().parents[2]))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def digest_dataclass(value):
    """Canonical model identity without a redundant deep copy of JSON fields.

    This is deliberately not memoized: mutable model evidence must always change
    its version. Nested dataclasses retain the same encoding as asdict().
    """
    def encode(node):
        if is_dataclass(node) and not isinstance(node, type):
            return {field.name: getattr(node, field.name) for field in fields(node)}
        raise TypeError(f'Object of type {type(node).__name__} is not JSON serializable')
    raw=json.dumps(value,default=encode,sort_keys=True,separators=(',', ':'),allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
