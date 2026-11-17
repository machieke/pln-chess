"""Pin inputs and preserve every starting tracked file before experiments."""
from pathlib import Path
import subprocess
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle15_baseline import sha

START = '63fbf4a198d15cc27c8ad15865be84bfdb871c28'


def run(out):
    out = Path(out)
    if (out/'baseline.json').exists():
        raise ValueError('Evidence generation already exists')
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == START
    runtime = Runtime()
    runtime.verify()
    files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], text=True).splitlines()
    write_json(out/'protected-files.json', {p: sha(ROOT/p) for p in files})
    inputs = ['configs/runtime-lock.json', 'artifacts/cycle12/model/C12-default.json',
        'knowledge/cycle16/finite_two.metta', 'artifacts/cycle16/learning/learned/model.json',
        'artifacts/cycle16/learning/shared-chain/model.json', 'artifacts/cycle16/corpus-registration.json',
        'artifacts/cycle16/acceptance.json', 'publication/cycle14/manifest.json',
        'publication/cycle15/manifest.json', 'publication/cycle16/manifest.json']
    hashes = {p: sha(ROOT/p) for p in inputs}
    assert hashes[inputs[1]] == '5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8'
    receipt = dict(starting_commit=START, branch='cycle17-shared-evidence-semantics',
        initial_worktree=subprocess.check_output(['git', 'status', '--short'], text=True),
        runtime=runtime.manifest, inputs=hashes, operational_source=production_code_hash(),
        legal_model_version=read_json(ROOT/inputs[1])['version'], protected_count=len(files),
        protected_manifest_sha256=sha(out/'protected-files.json'),
        authorized_remote='machieke/pln-chess', prior_remote_branch_exists=False,
        remote_audit='Single origin SSH URL; only rewrite is unrelated dhall-lang; no pushurl')
    write_json(out/'baseline.json', receipt)
    write_json(ROOT/'artifacts/cycle17/baseline.json', receipt)
    return receipt


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    print(run(p.parse_args().out))
