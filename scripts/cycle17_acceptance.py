"""Bind completed scientific/preservation gates; remote delivery is verified later."""
from datetime import datetime, timezone
import re
import subprocess
import xml.etree.ElementTree as ET
from pln_chess.common import ROOT, read_json
from pln_chess.pln import Runtime
from research.cycle16.records import record
from scripts.cycle15_baseline import sha
from scripts.cycle17_baseline import START

REPORTS = ('engineering-report', 'package-matrix', 'research-registration', 'shared-chain-baseline',
    'training-design', 'composition-results', 'reference-semantics', 'evidence-policy-decision',
    'performance-and-proofs', 'reproduction', 'publication')


def run():
    receipts = {}
    def receipt(name):
        path = ROOT/'artifacts/cycle17'/name
        value = read_json(path); receipts[str(path.relative_to(ROOT))] = sha(path)
        return value
    Runtime().verify()
    source = receipt('source-provenance.json')
    for name, expected in source['files'].items():
        assert sha(ROOT/name) == expected, name
    preservation = receipt('preservation/cycle17-verification.json')
    expected = dict(passed=True, checkout_clean=True, legal_shards=206, legal_rows=584112,
        exact_native_proof_parity=True, classification_changes=0, negative_controls=287,
        history_controls=27, recoveries=2, holdouts=76, tests=748)
    assert all(preservation.get(k) == v for k,v in expected.items())
    assert preservation['source_head'] == source['source_head']
    junit = ROOT/'artifacts/cycle17/preservation/tests.xml'
    suites = list(ET.parse(junit).getroot().iter('testsuite'))
    assert sum(int(s.get('tests', 0)) for s in suites) == 748
    assert all(int(s.get(k, 0)) == 0 for s in suites for k in ('failures', 'errors', 'skipped'))
    receipts[str(junit.relative_to(ROOT))] = sha(junit)
    historical = receipt('historical-final.json')
    assert historical['passed'] and historical['runtime_unchanged'] and not historical['changed']
    assert all(r['passed'] for r in historical['historical'].values())
    assert historical['accepted_checkpoint_sha256'] == preservation['accepted_checkpoint_sha256']
    reproduced = receipt('reproduction/verified.json')
    assert reproduced['passed'] and reproduced['checkout_clean'] and reproduced['exact_native_refit']
    assert reproduced['historical_bulk_and_pgn_access_denied'] and reproduced['source_head'] == source['source_head']
    baseline = receipt('baseline-replay/summary.json')
    assert baseline['passed'] and baseline['eleven_stamp_intersection'] and baseline['exact_baseline_channels']
    minimal = receipt('minimal-final/summary.json')['arms']
    for arm, overlap in [('S-AA',12),('S-BB',12),('D-AB',0),('D-BA',0),('overlap-1',1),('overlap-6',6)]:
        result = minimal[arm]
        assert result['result']['stages']['Clear']['classification'] == 'supported-positive'
        assert result['result']['stages']['Attack']['classification'] == ('unknown' if overlap else 'supported-positive')
        d = result['witness']['diagnostic']
        assert len(d['overlap']) == overlap and d['markers'][0][1] == ('false' if overlap else 'true')
        assert d['markers'][2][1] and not d['incomplete']
    learning = receipt('learning/summary.json')
    training_audit = receipt('training-audit.json')
    assert training_audit['preparation_rows']==432 and training_audit['eligible']==48 and training_audit['excluded']==384
    assert learning['duplicate_replay_equal'] and learning['all_admitted_positive']
    for arm in ('S-AA','S-BB','D-AB','D-BA','overlap-1','overlap-6'):
        result = learning['arms'][arm]
        assert result['admitted_counts'] == {'clear-two':12,'rook-attack':12}
        assert result['parameters']['clear-two'] == result['parameters']['rook-attack'] == learning['arms']['D-AB']['parameters']['clear-two']
        assert len(training_audit['arms'][arm]['actual_native_stamp_intersection']) == len(result['overlap'])
    evaluation = receipt('evaluation/summary.json')
    for value in evaluation['test'].values():
        assert value['roots'] == 24 and value['endpoints'] == 96
        assert value['reference'] == {'positive':39, 'negative':33, 'unknown':24}
        assert value['wrong_classified'] == 0
        for stage in ('Clear','Attack'):
            assert sum(value[stage]['outcomes'].values()) == 96
            assert value[stage]['outcomes']['conflicting'] == value[stage]['outcomes']['incomplete'] == 0
    for arm in ('D-AB', 'D-BA'):
        value = evaluation['test'][arm]
        assert value['correct_positive'] == {'numerator':39, 'denominator':39}
        assert value['correct_negative'] == {'numerator':33, 'denominator':33}
        assert value['Attack']['outcomes']['unknown'] == 24
    for arm in ('S-AA', 'S-BB'):
        value = evaluation['test'][arm]
        assert value['Clear']['outcomes']['supported-positive'] == 39
        assert value['Attack']['outcomes']['supported-positive'] == 0
        assert value['Attack']['outcomes']['unknown'] == 63
    assert evaluation['transfer']['unseen_source_roots'] == 24
    regression = receipt('historical-evaluation/summary.json')
    assert all(v['roots']==24 and v['endpoints']==72 for v in regression['test'].values())
    failure_audit = receipt('failure-census.json')
    assert failure_audit['native_processes'] == 1
    assert all(v['Attack']['endpoints']==96 for v in failure_audit['panels']['evaluation']['test'].values())
    strata = receipt('historical-target-scope.json')['strata']
    assert strata['rook']['D-AB']['roots']==23 and strata['bishop']['D-AB']['roots']==1
    bishop = receipt('supplement/historical-bishop-diagnostic.json')
    assert bishop['diagnostic']['markers'][0][1]=='false' and bishop['diagnostic']['markers'][2][1]
    assert len(bishop['diagnostic']['overlap']) == 1
    controls = receipt('controls/summary.json'); rows = controls['interventions']
    def attack(name): return rows[name]['stages']['Attack']
    for name in ('remove-clear-two','remove-rook-attack','remove-empty-0','remove-empty-1','prior-clearance',
                 'prior-terminal','remove-A-refit','wrong-role','wrong-state','missing-query-entity'):
        assert attack(name)['classification'] == 'unknown', name
    for name in ('duplicate-inference','replayed-training'):
        assert attack(name)['answer'] == attack('baseline')['answer']
    assert attack('leave-one-A')['answer']['confidence'] < attack('baseline')['answer']['confidence']
    assert attack('low-level-conflict')['classification'] == 'conflicting'
    for occupancy in ('EE','EO','EU','OE','OO','OU','UE','UO','UU'):
        expected_class = 'supported-positive' if occupancy=='EE' else 'supported-negative' if 'O' in occupancy else 'unknown'
        assert attack('occupancy-'+occupancy)['classification'] == expected_class
    assert controls['low_level']['actual-timeout']['classification'] == 'incomplete'
    assert controls['low_level']['low-confidence-supplied-diagnostic']['answer']['confidence'] < .1
    assert receipt('supplement/proof-audit.json')['passed']
    assert receipt('performance/proof-integrity.json')['passed']
    performance = receipt('performance/summary.json')
    assert len(performance)==8 and all(v['repetitions']==10 for v in performance.values())
    workloads = receipt('performance/workloads.json')
    assert set(workloads['workloads'])==set(performance)
    for name, value in workloads['workloads'].items():
        assert value['repetitions']==10
        assert value['statistics']['wall_seconds']['median']==performance[name]['median_seconds']
        assert value['native_processes_per_request']==performance[name]['native_processes_per_request']
    benchmark_command = receipt('benchmark-command.json')
    assert benchmark_command['returncode']==0 and benchmark_command['source_head']==source['source_head']
    resources = receipt('resource-census.json')
    observed = receipt('preservation-resource-observation.json')
    assert observed['samples'] > 0 and observed['comparison_observed_max_process_rss_kib'] > 0
    assert resources['unique_retained_native_processes'] < 10000 and resources['cpu_seconds'] < 8*3600
    assert resources['preservation_measured_cpu_seconds'] < 24*3600
    assert resources['research_bytes'] < 2*1024**3 and resources['preservation_bytes'] < 8*1024**3
    reference = receipt('reference-final/results.json')
    assert reference['native_processes'] == 0
    assert reference['parameter_reuse']['shared_parameter']=='5/16'
    assert reference['controls']['missing_dependence']['point_estimate'] is None
    witness_index = receipt('witnesses/index.json')
    for kinds in witness_index.values():
        for proof in kinds.values():
            assert sha(ROOT/proof['path']) == proof['sha256']
            receipts[proof['path']] = proof['sha256']
    manifest_path = ROOT/'publication/cycle17/manifest.json'
    manifest = read_json(manifest_path); receipts[str(manifest_path.relative_to(ROOT))] = sha(manifest_path)
    samples = next(row for row in manifest['files'] if row['path']==workloads['samples_path'])
    assert samples['sha256']==workloads['samples_sha256']
    restored = receipt('restoration.json')
    assert restored['passed'] and not restored['missing_or_changed']
    assert restored['manifest_sha256']==sha(manifest_path) and restored['files']==manifest['counts']['files']
    assert not manifest['remote_publication'] and not restored['bulk_remote_publication']
    assert all(a['bytes'] <= 512*1024**2 for a in manifest['assets'])
    receipt('baseline.json'); receipt('corpus-registration.json')
    for report in REPORTS:
        path = ROOT/'docs/cycle17'/(report+'.md'); content = path.read_text()
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if '://' not in target and not target.startswith('#'):
                destination = (path.parent/target.split('#')[0]).resolve()
                assert destination.exists() or destination==(ROOT/'artifacts/cycle17/acceptance.json').resolve(), (report,target)
        receipts[str(path.relative_to(ROOT))] = sha(path)
    for path in (ROOT/'scripts').glob('cycle17_*.py'):
        receipts[str(path.relative_to(ROOT))] = sha(path)
    destination = ROOT/'artifacts/cycle17/acceptance.json'
    if destination.exists():
        previous = read_json(destination)
        assert previous['passed'] and previous['verified_receipt_sha256']==receipts
        return previous
    return record(destination, dict(passed=True, completed_utc=datetime.now(timezone.utc).isoformat(),
        starting_commit=START, scientific_source_head=source['source_head'],
        prepared_from_head=subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
        decision='A: bounded disjoint learned chains work; C: shared joint uncertainty not identified by current representation',
        generic_recursive_reuse='unresolved; retained native counterexample',
        preservation=expected, verified_receipt_sha256=receipts,
        publication='Engineering contents accepted; final push and independent canonical fetch must be verified separately outside tracked checkout',
        scope='Source/evidence-bound acceptance; not an operational model promotion or proof of statistical independence'))


if __name__ == '__main__':
    result = run()
    print('Cycle 17 engineering acceptance passed:', result['decision'])
