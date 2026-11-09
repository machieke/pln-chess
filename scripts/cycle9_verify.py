"""Fail-closed acceptance for an unchanged model and optimized implementation."""
import argparse
import ast
from pathlib import Path
import re
import shutil
import subprocess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle8.model import PromotionModel
from scripts.cycle9_baseline import sha,START


CHECKS=('baseline','historical_regression','negative_controls','native_boundary','proof_provenance',
        'cache_parity','tests','clean_bootstrap','dataset_integrity','evidence_replay','temporal_controls')


def run(out):
    out=Path(out);rt=Runtime();lock=read_json(out/'baseline/lock.json');cfg=read_json(ROOT/'configs/cycle9.json')
    assert lock['starting_head']==cfg['starting_head']==START
    assert read_json(out/'baseline/verified.json')['passed']
    baseline_entries=[entry for path in sorted((out/'baseline').glob('*-summary.json')) for entry in read_json(path).values()]
    assert len(baseline_entries)==26
    for entry in baseline_entries:
        assert entry['exact_native_proof_parity'] and sha(out/'baseline'/entry['artifact'])==entry['sha256']
    assert rt.manifest==lock['runtime']
    assert all(sha(ROOT/p)==value for p,value in lock['protected_files'].items())
    assert read_json(out/'regression/verified.json')==dict(passed=True,evaluations=26,all_native_proof_parity=True)
    regression=list((out/'regression').glob('*.receipt.json'));assert len(regression)==26
    historical_rows=0
    for path in regression:
        r=read_json(path);assert r['identity']['source_hash']==production_code_hash()
        assert r['exact_native_proof_parity'] and sha(out/r['artifact'])==r['sha256'];historical_rows+=r['rows']
        if path.name.startswith('C8-promotion-relative'):
            assert all(r['metrics'][k]==0 for k in ('false_positive','false_illegal','self_check_false_legal','incomplete'))
    negative=read_json(out/'C8-promotion-relative-negative-regressions.json')
    assert all(negative[k]==287 for k in ('cases','intact_negative','removed_unknown','exact_native_proof_parity'))
    for path in (ROOT/'src').rglob('*.py'):
        for n in ast.walk(ast.parse(path.read_text())):
            imports=[a.name for a in n.names] if isinstance(n,ast.Import) else [n.module or ''] if isinstance(n,ast.ImportFrom) else []
            assert all(name.split('.')[0]!='chess' for name in imports),path
            if path.parent.name=='cycle9':assert all(name.split('.')[0] not in ('evaluation','training') for name in imports),path
    assert read_json(out/'composition/review.json')['new_operator_enabled'] is False
    data=read_json(out/'datasets/dataset.json');copy=dict(data);claimed=copy.pop('hash');assert digest(copy)==claimed
    assert data['registration_hash']==digest(cfg)
    assert data['game_counts']['independent-games']>=100 and data['counts']['independent-games']>=500
    assert data['counts']['adversarial']>=100 and all(g['complete'] for g in data['games'])
    assert read_json(out/'dataset-replay.json')['exact_replay']
    evaluations=list((out/'evaluation').glob('*.receipt.json'));assert len(evaluations)==48,len(evaluations)
    for path in evaluations:
        r=read_json(path);assert sha(out/r['artifact'])==r['sha256'] and r['native_proofs_verified']
        assert r['identity']['production_code_hash']==production_code_hash()
        assert r['identity']['dataset_hash']==data['hash'] and not r['metrics']['incomplete']
    analysis=read_json(out/'analysis/verification.json');assert analysis['all_positions_accounted_for']
    before=read_json(out/'performance/C8-original.json');after=read_json(out/'performance/C9-optimized.json')
    assert len(before['records'])==len(after['records'])==6
    assert before['production_code_hash']==read_json(ROOT/'artifacts/cycle8/acceptance.json')['production_code_hash']
    assert after['production_code_hash']==production_code_hash()
    for a,b in zip(before['records'],after['records']):
        assert a['fixture']==b['fixture']
        assert a['full_candidate_proof_parity'] and b['full_candidate_proof_parity']
        assert len(a['samples'])==len(b['samples'])==21
        assert {r['candidate_digest'] for r in a['samples']}=={r['candidate_digest'] for r in b['samples']}
        assert all(not r['truncated'] and (r['mode']!='warm' or r['native_invocations']==0) for r in a['samples']+b['samples'])
    dependence=read_json(out/'dependence/summary.json')
    assert all(dependence[k] for k in ('deterministic_replay','checkpoint_roundtrip','duplicate_native_values_identical','correlated_ancestor_native_values_identical'))
    assert dependence['removed_hypotheses']==0 and dependence['ingestion']['records']==1
    assert read_json(out/'temporal/summary.json')['cases']==20
    assert read_json(out/'abstention/summary.json')['incorrect']==0
    bootstrap=read_json(out/'bootstrap-context.json')
    assert all(bootstrap[k] for k in ('fresh_venv','fresh_runtime','initial_clean_checkout','bootstrap_passed'))
    tests=(out/'pytest.txt').read_text();match=re.search(r'(\d+) passed',tests)
    assert match and not re.search(r'\d+ failed|ERRORS|FAILURES',tests)
    old=read_json(ROOT/'artifacts/cycle8/acceptance.json');model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    assert model.version in old['accepted_model_versions']
    checks={k:True for k in CHECKS};summary=read_json(out/'analysis/evaluation-summary.json')
    # This is an implementation-parity acceptance, never promotion of new learning.
    receipt=dict(passed=True,all_required_checks_executed=True,checks=checks,model_version=model.version,
        accepted_model_versions=old['accepted_model_versions'],accepted_legacy_model_versions=old['accepted_legacy_model_versions'],
        selected_variant='C8-promotion-relative',new_learning_promoted=False,default_mode='operational',
        production_code_hash=production_code_hash(),registration_hash=digest(cfg),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8)},runtime_version=rt.version,
        calibration_sha256=sha(out/'calibration/results.json'),
        new_cohort_errors={k:{metric:v['complete'][metric] for metric in ('false_positive','false_illegal','self_check_false_legal','incomplete')} for k,v in summary.items() if k.startswith('operational/')},
        scope='Same accepted C8 checkpoint, exact historical proofs and benchmark payloads. Expanded cohorts are finite empirical diagnostics; no new model, threshold or native operator promoted.')
    write_json(out/'acceptance.json',receipt)
    (out/'model').mkdir(exist_ok=True);shutil.copy2(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',out/'model/C9-default.json')
    write_json(out/'verification.json',dict(passed=True,checks=checks,test_count=int(match[1]),historical_proof_records=historical_rows,
        new_proof_records=analysis['proof_records_reconstructed'],baseline_evaluations=26,regression_evaluations=26,
        evaluation_shards=len(evaluations),benchmark_samples=252,protected_files=len(lock['protected_files']),
        runtime=rt.manifest,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        production_code_hash=production_code_hash(),dataset_hash=data['hash'],model_version=model.version))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
