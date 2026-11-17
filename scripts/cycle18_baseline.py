"""Read-only baseline capture before the source-bound semantics study."""
from pathlib import Path
import subprocess
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle15_baseline import sha

START = '24f30ce8d4e0631f8937404929485dfdc0032f93'
BRANCH = 'cycle18-shared-parameter-contract'


def run(out):
    out = Path(out)
    assert not (out/'baseline.json').exists()
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == START
    runtime = Runtime(); runtime.verify()
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], text=True).splitlines()
    protected = {p: sha(ROOT/p) for p in paths}
    write_json(out/'protected-files.json', protected)
    prior = read_json(ROOT/'artifacts/cycle17/acceptance.json')
    for p, h in prior['verified_receipt_sha256'].items():
        assert sha(ROOT/p) == h, p
    base = read_json(ROOT/'artifacts/cycle17/baseline.json')
    assert production_code_hash() == base['operational_source']
    assert sha(ROOT/'artifacts/cycle12/model/C12-default.json') == base['inputs']['artifacts/cycle12/model/C12-default.json']
    models = {p.parent.name: dict(path=str(p.relative_to(ROOT)), sha256=sha(p), identity=read_json(p)['version'])
              for p in (ROOT/'artifacts/cycle17/learning').glob('*/model.json')}
    receipt = dict(starting_commit=START, branch=BRANCH, initial_worktree=subprocess.check_output(['git','status','--short'],text=True),
        protected_files=len(paths), protected_manifest_sha256=sha(out/'protected-files.json'),
        runtime=runtime.manifest, operational_source=production_code_hash(),
        legal_checkpoint_sha256=sha(ROOT/'artifacts/cycle12/model/C12-default.json'),
        legal_semantic_identity=read_json(ROOT/'artifacts/cycle12/model/C12-default.json')['version'],
        models=models, prior_acceptance_verified=True, prior_acceptance_sha256=sha(ROOT/'artifacts/cycle17/acceptance.json'),
        source_inputs={p:protected[p] for p in paths if p in ('artifacts/cycle17/learning/evidence.json','artifacts/cycle17/corpus-registration.json','artifacts/cycle17/witnesses/index.json','configs/runtime-lock.json')})
    write_json(out/'baseline.json', receipt)
    write_json(ROOT/'artifacts/cycle18/registration/baseline.json', receipt)
    return receipt


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--out',required=True); run(p.parse_args().out)
