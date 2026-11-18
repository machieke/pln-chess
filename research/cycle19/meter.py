"""Cross-process reservation and raw receipts for the registered native ceiling."""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
from unittest.mock import patch
from pln_chess.common import read_json, write_json
from research.cycle15.native_reasoner import NativeReasoner
from .records import external

CURRENT=None
PHASE=None


def reserved():
    return read_json(CURRENT/'counter.json')['reserved'] if CURRENT is not None and (CURRENT/'counter.json').exists() else 0


@contextmanager
def phase(name):
    global PHASE
    previous=PHASE;PHASE=name
    try:yield
    finally:PHASE=previous


@contextmanager
def metered(directory, category):
    global CURRENT
    directory=external(directory);directory.mkdir(parents=True,exist_ok=True)
    previous=CURRENT;CURRENT=directory
    original=NativeReasoner.execute_program
    def execute(self,program,timeout):
        with (directory/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            counter=directory/'counter.json'
            n=read_json(counter)['reserved'] if counter.exists() else 0
            if n>=4000:raise RuntimeError('Registered Cycle19 native ceiling exhausted')
            n+=1;write_json(counter,dict(reserved=n,ceiling=4000))
            label=category+'.'+PHASE if PHASE else category
            write_json(directory/f'{n:04d}-reservation.json',dict(category=label,pid=os.getpid()))
        result=original(self,program,timeout)
        write_json(directory/f'{n:04d}-receipt.json',dict(category=label,receipt=result))
        return result
    try:
        with patch.object(NativeReasoner,'execute_program',execute):yield
    finally:CURRENT=previous
