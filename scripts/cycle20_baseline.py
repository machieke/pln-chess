"""Read-only Cycle 20 baseline inventory, including the registered Cycle 19 proofs."""
from pathlib import Path
import subprocess
import sys
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle15_baseline import sha

START='7c06d8e15972e5db2e0932160102dda329c304ab'
BRANCH='cycle20-native-belief-workspaces'


def run(out):
    out=Path(out)
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==START
    assert not (out/'baseline.json').exists()
    runtime=Runtime();runtime.verify()
    assert sys.version_info[:3]==(3,12,12)
    protected={p:sha(ROOT/p) for p in subprocess.check_output(['git','ls-tree','-r','--name-only',START],text=True).splitlines()}
    prior=read_json(ROOT/'artifacts/cycle19/acceptance.json')
    for p,h in prior['verified_receipt_sha256'].items(): assert sha(ROOT/p)==h,p
    index=read_json(ROOT/'artifacts/cycle19/evaluation-index.json')
    archive=Path(read_json(ROOT/'publication/cycle19/manifest.json')['original_local_root'])
    assert len(index)==1256
    for row in index:
        assert set(row['stages'])=={'Clear','Attack'}
        for stage in row['stages'].values():
            entry=stage['native']
            assert sha(archive/entry['path'].removeprefix('local-pack:'))==entry['sha256']
    checkpoint=ROOT/'artifacts/cycle12/model/C12-default.json'
    assert sha(checkpoint)=='5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8'
    assert read_json(checkpoint)['version']=='a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d'
    assert production_code_hash()=='e88ff7969885be101af2ceedbbdf5d5499f4253b361a8cee18ff1814f055282c'
    write_json(out/'protected-files.json',protected)
    r=dict(starting_commit=START,branch=BRANCH,protected_files=len(protected),archived_pairs=len(index),verified_native_proofs=2*len(index),
        protected_manifest_sha256=sha(out/'protected-files.json'),runtime=runtime.manifest,
        python=sys.version.split()[0],operational_source=production_code_hash(),
        legal_checkpoint_sha256=sha(checkpoint),legal_semantic_identity=read_json(checkpoint)['version'],
        cycle19_acceptance_sha256=sha(ROOT/'artifacts/cycle19/acceptance.json'),prior_acceptance_verified=True,
        worktree=str(ROOT),original_checkout='/data/pln-chess-cycle6-delivery',
        initial_state='Dedicated branch from the verified Cycle 19 remote tip. Supplied brief copied intact from original checkout.',
        historical_manifests={str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob('publication/cycle*/manifest.json')})
    write_json(out/'baseline.json',r);write_json(ROOT/'artifacts/cycle20/registration/baseline.json',r)
    return r


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();run(a.out)
