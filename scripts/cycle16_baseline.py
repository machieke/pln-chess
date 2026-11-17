"""Freeze actual Cycle 16 inputs, without touching historical receipts."""
from pathlib import Path
import subprocess
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle15_baseline import sha

START = 'e349c9c8c7c6506a367c28623e30373c59ffc59e'


def run(out):
    out = Path(out)
    if (out/'baseline.json').exists():
        raise ValueError('Choose an unused evidence generation')
    subprocess.run(['git', 'merge-base', '--is-ancestor', START, 'HEAD'], check=True)
    paths = subprocess.check_output(['git','ls-tree','-r','--name-only',START], text=True).splitlines()
    protected = {p: sha(ROOT/p) for p in paths}
    write_json(out/'protected-files.json', protected)
    inputs = ['configs/runtime-lock.json','artifacts/cycle12/model/C12-default.json',
        'artifacts/cycle15/learning/model.json','knowledge/cycle15/domain_rules.metta',
        'publication/cycle14/manifest.json','publication/cycle15/manifest.json',
        'artifacts/cycle14/current/legal/panel.json','docs/cycle16/research-registration.md']
    hashes = {p: sha(ROOT/p) for p in inputs}
    assert hashes[inputs[1]] == '5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8'
    receipt = dict(starting_commit=START, starting_branch='cycle15-native-consequences',
        branch=subprocess.check_output(['git','symbolic-ref','--short','HEAD'],text=True).strip(),
        initial_worktree=subprocess.check_output(['git','status','--short'],text=True),
        runtime=Runtime().manifest, operational_source=production_code_hash(), inputs=hashes,
        legal_model_version=read_json(ROOT/inputs[1])['version'],
        cycle15_model_version=read_json(ROOT/inputs[2])['version'],
        protected_count=len(protected), protected_manifest_sha256=sha(out/'protected-files.json'),
        remote_write_performed=False)
    write_json(out/'baseline.json', receipt)
    write_json(ROOT/'artifacts/cycle16/baseline.json', receipt)
    return receipt


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    print(run(p.parse_args().out))
