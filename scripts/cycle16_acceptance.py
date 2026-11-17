"""Bind completed local delivery receipts; never infer acceptance from partial gates."""
import argparse
from datetime import datetime, timezone
import re
import subprocess

from pln_chess.common import ROOT, read_json
from research.cycle16.records import record
from scripts.cycle15_baseline import sha


REPORTS = (
    'engineering-report', 'package-matrix', 'research-registration',
    'reuse-counterexample', 'finite-paths', 'learning-and-transfer',
    'evidence-semantics', 'performance-and-proofs', 'reproduction',
    'architecture-decision',
)


def run():
    receipts = {}

    def receipt(name):
        path = ROOT / 'artifacts/cycle16' / name
        value = read_json(path)
        receipts[str(path.relative_to(ROOT))] = sha(path)
        return value

    source = receipt('source-provenance.json')
    assert source['passed']
    for name, wanted in source['experimental_files'].items():
        assert sha(ROOT / name) == wanted, name
    preservation = receipt('preservation/cycle16-verification.json')
    expected = dict(passed=True, checkout_clean=True, legal_shards=206,
                    legal_rows=584112, exact_native_proof_parity=True,
                    classification_changes=0, negative_controls=287,
                    history_controls=27, recoveries=2, holdouts=76, tests=732)
    assert all(preservation.get(k) == v for k, v in expected.items())
    assert preservation['source_head'] == source['implementation_freeze']
    history = receipt('historical-final.json')
    assert history['passed'] and history['runtime_unchanged'] and not history['changed']
    assert history['cycle14']['passed'] and history['cycle15']['passed']
    assert history['accepted_checkpoint_sha256'] == preservation['accepted_checkpoint_sha256']
    reproduction = receipt('reproduction/verified.json')
    assert reproduction['passed'] and reproduction['checkout_clean']
    assert reproduction['source_head'] == source['implementation_freeze']
    assert reproduction['exact_learned_parameters_and_ancestry']
    assert receipt('supplement/proof-audit.json')['passed']
    assert receipt('performance/proof-integrity.json')['passed']
    performance = receipt('performance/summary.json')
    assert len(performance) == 9 and all(v['repetitions'] == 10 for v in performance.values())
    workloads = receipt('performance/workloads.json')
    assert len(workloads['workloads']) == 7
    assert all(v['repetitions'] == 10 for v in workloads['workloads'].values())
    resources = receipt('resource-census.json')
    assert resources['unique_retained_native_processes'] < 10000
    assert resources['cpu_seconds'] < 8 * 3600
    assert resources['preservation_measured_cpu_seconds'] < 24 * 3600
    assert resources['research_bytes'] < 2 * 1024**3
    assert resources['preservation_bytes'] < 8 * 1024**3
    restored = receipt('restoration.json')
    manifest_path = ROOT / 'publication/cycle16/manifest.json'
    manifest = read_json(manifest_path)
    receipts[str(manifest_path.relative_to(ROOT))] = sha(manifest_path)
    sample_entry = next(r for r in manifest['files'] if r['path'] == workloads['samples_path'])
    assert sample_entry['sha256'] == workloads['samples_sha256']
    assert restored['passed'] and not restored['missing_or_changed']
    assert restored['manifest_sha256'] == sha(manifest_path)
    assert restored['files'] == manifest['counts']['files']
    assert not restored['remote_write_performed'] and not manifest['remote_publication']
    assert all(a['bytes'] <= 512 * 1024**2 for a in manifest['assets'])
    evaluation = receipt('evaluation/summary.json')
    for arm in ('F', 'L'):
        result = evaluation['test'][arm]
        assert result['roots'] == 24 and result['correct'] == 72 and result['incorrect'] == 0
        assert result['Attack']['outcomes'] == {'supported-positive': 30, 'supported-negative': 42}
    for arm in ('R', 'F-minus', 'prior', 'shared-chain'):
        assert evaluation['test'][arm]['Attack']['outcomes'] == {'supported-negative': 42, 'unknown': 30}
    transfer = receipt('supplement/transfer-audit.json')
    assert not transfer['source_ancestry_overlap']
    assert transfer['unseen_test_query_identifiers'] == 48
    assert transfer['test_roots_with_unseen_endpoint_locations'] == 0
    assert evaluation['groups']['test_roots_wholly_unseen_geometry'] == 0
    for name in (
        'baseline.json', 'baseline-replay/baseline-replay.json', 'environment.json',
        'proof-comparison-resource-observation.json',
        'minimal/minimal.json', 'occupancy/occupancy.json',
        'interventions/interventions.json', 'structural/structural.json',
        'dependencies/dependencies.json', 'budgets/budgets-learning.json',
        'supplement/shared-training-witness.json', 'supplement/bounded-controls.json',
        'supplement/role-state-controls.json', 'supplement/below-threshold.json',
        'corpus-registration.json', 'learning/summary.json',
        'learning/learned/model.json', 'learning/prior/model.json',
        'learning/shared-chain/model.json', 'learning/leave-one/model.json',
    ):
        receipt(name)
    for name in REPORTS:
        path = ROOT / 'docs/cycle16' / (name + '.md')
        text = path.read_text()
        assert 'gates in progress' not in text and 'evidence sealing are running' not in text
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                destination = (path.parent / target.split('#')[0]).resolve()
                generated_here = (ROOT / 'artifacts/cycle16/acceptance.json').resolve()
                assert destination.exists() or destination == generated_here, (name, target)
        receipts[str(path.relative_to(ROOT))] = sha(path)
    branch = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD'], cwd=ROOT, text=True).strip()
    assert branch == 'cycle16-native-path-composition'
    changes = subprocess.check_output(['git', 'diff', '--name-status', source['starting_commit']], cwd=ROOT, text=True)
    assert all(line.startswith('A\t') for line in changes.splitlines())
    for helper in sorted((ROOT / 'scripts').glob('cycle16_*.py')):
        receipts[str(helper.relative_to(ROOT))] = sha(helper)
    destination = ROOT / 'artifacts/cycle16/acceptance.json'
    if destination.exists():
        previous = read_json(destination)
        assert previous['passed'] and previous['verified_receipt_sha256'] == receipts
        assert previous['implementation_freeze'] == source['implementation_freeze']
        return previous
    return record(destination, dict(
        schema='cycle16-local-acceptance-v1', passed=True,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        starting_commit=source['starting_commit'], implementation_freeze=source['implementation_freeze'],
        prepared_from_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        branch=branch, packages={f'C16-{i:02d}': 'engineering complete' for i in range(1, 9)},
        decision='Outcome A: finite composition works; generic reuse remains blocked',
        claims=dict(A='demonstrated', B='demonstrated', C='demonstrated', D='not demonstrated'),
        preservation=expected, preservation_execution='Resumed source-bound run; interrupted evidence retained',
        verified_receipt_sha256=receipts, evidence_counts=manifest['counts'],
        no_remote_write=True,
        authorization='Cycle 16 brief permits local commits only; no push, publication or runtime policy change',
        limitations=[
            'Supplied finite structure, not generic recursion or structure learning',
            'All admitted conditional labels positive; no probability calibration',
            'New source games and identifiers, but no unseen endpoint locations or coarse geometry',
            'Variants and common openings are dependent; no population confidence interval',
            'Selected tasks, beliefs and stamps are exposed, not a complete fired-rule tree',
            'Fresh checkout reproduction reuses verified installed dependencies',
            resources['accounting_scope'],
        ],
        scope='Receipt-bound engineering acceptance; final commit and Git object census are recorded after the local commit',
    ))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = run()
    print('Cycle 16 acceptance passed:', result['decision'])
