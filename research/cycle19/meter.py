"""Cross-process reservation and raw receipts for the registered native ceiling."""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
from unittest.mock import patch
from pln_chess.common import read_json, write_json
from research.cycle15.native_reasoner import NativeReasoner


@contextmanager
def metered(directory, category):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    original=NativeReasoner.execute_program
    def execute(self,program,timeout):
        with (directory/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            counter=directory/'counter.json'
            n=read_json(counter)['reserved'] if counter.exists() else 0
            if n>=4000:raise RuntimeError('Registered Cycle19 native ceiling exhausted')
            n+=1;write_json(counter,dict(reserved=n,ceiling=4000))
            write_json(directory/f'{n:04d}-reservation.json',dict(category=category,pid=os.getpid()))
        result=original(self,program,timeout)
        write_json(directory/f'{n:04d}-receipt.json',dict(category=category,receipt=result))
        return result
    with patch.object(NativeReasoner,'execute_program',execute):yield
