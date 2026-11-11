"""Inventory the completed, locally committed engineering package."""
import argparse
from pathlib import Path
import subprocess
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out).resolve();code=production_code_hash()
    gates=('baseline/reproduction-receipt.json','current/verified.json','acceptance.json','datasets/integrity.json',
        'architecture/boundary.json','clean-research/verified.json','performance/summary.json','ui/verification.json',
        'cli-smoke/verified.json','verified-transfer/summary.json','final-checks/verified.json','reports.json')
    for path in gates:assert read_json(out/path)['passed'],path
    assert code==read_json(out/'source-freeze.json')['production_code_hash']
    assert code==read_json(out/'final-checks/verified.json')['production_code_hash']
    assert code==read_json(out/'ui/verification.json')['production_code_hash']
    assert read_json(out/'reports.json')['required_documents']==16
    baseline=read_json(out/'baseline/manifest.json')
    assert all(sha(ROOT/path)==value for path,value in baseline['protected_files'].items())
    for directory in ('features','temporal/features','current/legal/evaluation','performance/raw'):
        assert not list((out/directory).glob('*.tmp')),directory
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    # The inventory excludes only its own manifest and the receipt binding it.
    # Self-referential file hashes cannot be constructed.
    files={p for p in out.rglob('*') if p.is_file() and p not in (out/'artifact-manifest.json',out/'delivery.json')}
    files.update(p for p in (ROOT/'docs/cycle13').glob('*.md'))
    files.update(p for p in (ROOT/'src/pln_chess').rglob('*.py'))
    for folder in ('training','evaluation','scripts','tests'):
        files.update(p for p in (ROOT/folder).glob('*cycle13*') if p.is_file())
    files.update(ROOT/path for path in ('README.md','proofshot.config.json','configs/cycle13.json','requirements-dev.lock','configs/runtime-lock.json','vendor/pln/lib_pln.metta'))
    entries={str(path.relative_to(ROOT)):dict(sha256=sha(path),bytes=path.stat().st_size) for path in sorted(files)}
    write_json(out/'artifact-manifest.json',dict(schema='cycle13-delivery-inventory-v1',files=entries,
        file_count=len(entries),bytes=sum(row['bytes'] for row in entries.values()),
        exclusions=['artifacts/cycle13/artifact-manifest.json','artifacts/cycle13/delivery.json'],
        protected_historical_files=len(baseline['protected_files']),production_code_hash=code))
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    commits=subprocess.check_output(['git','log','--reverse','--format=%H %s','b000898a0a1f46e556f161982f2c0e6d3944c322..HEAD'],cwd=ROOT,text=True).splitlines()
    write_json(out/'delivery.json',dict(passed=True,packages_delivered=20,required_reports=16,
        starting_head='b000898a0a1f46e556f161982f2c0e6d3944c322',production_freeze_head='3e5aae6b6e4989cc8f0a5ad4eafcbd7df352f9dc',
        content_head_before_final_package_commit=head,production_code_hash=code,local_commits_through_content_snapshot=commits,
        final_commit_scope='The final packaging commit and clean working-tree status are recorded by repository HEAD and the delivery message; the receipt does not pretend to contain its own future commit hash.',
        gate_receipts={path:sha(out/path) for path in gates},manifest_sha256=sha(out/'artifact-manifest.json'),
        artifact_count=len(entries),artifact_bytes=sum(row['bytes'] for row in entries.values()),
        tests=read_json(out/'final-checks/verified.json')['tests'],
        legal_model_version=read_json(out/'acceptance.json')['default_model_version'],
        preference_model_version=read_json(out/'preferences/summary.json')['model_version'],
        temporal_model_version=read_json(out/'temporal/summary.json')['model_version'],
        inspectable_successful_transfer_demonstrations=read_json(out/'verified-transfer/summary.json')['demonstrations'],
        successful_transfer_illustrations_are_posthoc=True,
        cycle14_recommendation='A: continue preference learning',preferences_promoted=False,
        automatic_move_selection=False,github_push_performed=False,external_deployment_performed=False,
        upstream_modified=False,new_native_operators=False,
        limitations=['Native preference proofs condition on host-assembled categorical observations; no joint strategic theorem.',
            'Conservative reference bounds leave many unknown labels; the source corpus and answered test subsets are limited.',
            'Concept coverage, probability calibration and exhaustive response coverage remain insufficient for automatic selection.',
            'Full endpoint/proof computation and JSON exports are expensive.']))
    print('COMPLETE ENGINEERING PACKAGE INVENTORIED',len(entries),'files',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
