"""Freeze the starting publication identities without modifying old evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

from pln_chess.common import ROOT, write_json
from pln_chess.pln import Runtime

START = 'd2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(out):
    out = Path(out)
    if (out / 'baseline.json').exists():
        raise ValueError('Baseline is immutable; choose a new output directory')
    runtime = Runtime()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['git', 'merge-base', '--is-ancestor', START, head], check=True)
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], text=True).splitlines()
    protected = {p: sha(ROOT / p) for p in paths}
    # Externalized Cycle 14 files are protected as well, without re-downloading.
    external = json.loads((ROOT / 'publication/cycle14/manifest.json').read_text())
    models = {}
    for path in sorted((ROOT / 'artifacts').glob('cycle*/model/*.json')):
        if path.name.startswith(('C11-field', 'C12-', 'C13-', 'C14-')):
            data = json.loads(path.read_text())
            models[str(path.relative_to(ROOT))] = {'sha256': sha(path), 'version': data.get('version')}
    write_json(out / 'protected-files.json', protected)
    write_json(out / 'baseline.json', dict(starting_head=head, publication_baseline=START,
        initial_worktree=subprocess.check_output(['git', 'status', '--short'], text=True),
        runtime=runtime.manifest, python=subprocess.check_output(['.venv/bin/python', '--version'], text=True).strip(),
        models=models, protected_count=len(protected), protected_manifest_sha256=sha(out / 'protected-files.json'),
        publication_manifest_sha256=sha(ROOT / 'publication/cycle14/manifest.json'),
        publication_summary=external.get('summary'), registration_sha256=sha(ROOT / 'docs/cycle15/research-registration.md'),
        completed_unix=time.time(), historical_receipts_rewritten=False))
    print('BASELINE', head, len(protected), 'protected tracked files', flush=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
