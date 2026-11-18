"""Immutable research artifacts and content identities."""
from pathlib import Path
import subprocess
import json
import os
import tempfile
from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from scripts.cycle15_baseline import sha


def record(path, value):
    path = Path(path)
    if path.exists():
        raise ValueError('Evidence generation already exists: ' + str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as stream:
            stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
            stream.flush();os.fsync(stream.fileno())
        # Hard-link creation atomically publishes a complete new generation
        # and fails if another writer has already claimed the destination.
        os.link(temporary,path)
    finally:os.unlink(temporary)
    return value


def external(path):
    path = Path(path).resolve()
    roots=[ROOT]
    listing=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True)
    roots.extend(Path(line[9:]).resolve() for line in listing.splitlines() if line.startswith('worktree '))
    for manifest in ROOT.glob('publication/cycle*/manifest.json'):
        value=read_json(manifest)
        if value.get('original_local_root'):roots.append(Path(value['original_local_root']).resolve())
    if any(path==root or root in path.parents for root in roots):
        raise ValueError('Executable outputs must be outside all source checkouts and sealed historical evidence')
    return path


def output(path):
    path=external(path)
    if path.exists():
        raise ValueError('Use a new output generation')
    path.mkdir(parents=True)
    return path
