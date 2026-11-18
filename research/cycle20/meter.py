"""Reserve native inference starts across cooperating research processes."""
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
import os
import sqlite3
from research.cycle15.native_reasoner import NativeReasoner
from research.cycle19.records import record

def reserve(root, phase):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(root/'starts.sqlite',timeout=60) as db:
        db.execute('CREATE TABLE IF NOT EXISTS starts (n INTEGER PRIMARY KEY, phase TEXT, pid INTEGER)')
        db.execute('BEGIN IMMEDIATE')
        n=db.execute('SELECT count(*) FROM starts').fetchone()[0]+1
        if n>6000:raise RuntimeError('Cycle 20 research ceiling reached')
        if phase.startswith('residency-probe') and db.execute("SELECT count(*) FROM starts WHERE phase LIKE 'residency-probe%'").fetchone()[0]>=24:
            raise RuntimeError('Residency probe ceiling reached')
        db.execute('INSERT INTO starts VALUES (?,?,?)',(n,phase,os.getpid()))
    return n

@contextmanager
def metered(root,phase):
    original=NativeReasoner.execute_program
    def execute(self,program,timeout=10):
        n=reserve(root,phase)
        result=original(self,program,timeout)
        record(Path(root)/f'{n:05d}.json',dict(phase=phase,pid=os.getpid(),receipt=result))
        return result
    with patch.object(NativeReasoner,'execute_program',execute): yield
