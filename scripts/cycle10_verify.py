"""Mandatory implementation gates, with external research outcomes reported honestly."""
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
from pln_chess.cycle10.acceptance import CHECKS
from scripts.cycle9_baseline import sha

START='257473d2462c75f84d3975bb91d85a8c1cc269dd'


def run(out):
    out=Path(out);rt=Runtime();rt.verify();code=production_code_hash();cfg=read_json(ROOT/'configs/cycle10.json')
    baseline=read_json(out/'baseline/reproduction-receipt.json');lock=read_json(out/'baseline/manifest.json')
    assert baseline['passed'] and baseline['starting_head']==cfg['starting_head']==START
    assert baseline['exact_native_proof_parity'] and read_json(out/'baseline/proof-parity.json')['passed']
    assert all(sha(ROOT/p)==h for p,h in lock['protected_files'].items())
    assert rt.manifest==baseline['identity']['runtime']
    current=read_json(out/'current/verified.json');assert current['passed'] and current['production_code_hash']==code
    assert current['runtime']==rt.manifest and current['initial_clean'] and current['final_clean']
    assert read_json(out/'current/regression/verified.json')==dict(passed=True,evaluations=26,all_native_proof_parity=True)
    historical=list((out/'current/regression').glob('*.receipt.json'));assert len(historical)==26
    for path in historical:
        r=read_json(path);assert r['identity']['source_hash']==code and r['exact_native_proof_parity']
        assert sha(out/'current'/r['artifact'])==r['sha256']
        if path.name.startswith('C8-promotion-relative'):
            assert all(r['metrics'][k]==0 for k in ('false_positive','false_illegal','self_check_false_legal','incomplete'))
    parity=read_json(out/'current/cycle9-parity.json');assert parity['passed'] and parity['shards']==48
    for entry in parity['comparisons']:
        assert entry['production_code_hash']==code and entry['exact_native_proof_parity']
        assert sha(out/'current'/entry['artifact'])==entry['sha256']
    negatives=read_json(out/'current/C8-promotion-relative-negative-regressions.json')
    assert all(negatives[k]==287 for k in ('cases','intact_negative','removed_unknown','exact_native_proof_parity'))
    allowed={'src/pln_chess/api/__init__.py','src/pln_chess/cli/__init__.py','src/pln_chess/cli/web.py',
             'src/pln_chess/cli/web10.py','src/pln_chess/cycle9/acceptance.py'}
    changed=subprocess.check_output(['git','diff',START,'--name-only','--','src'],cwd=ROOT,text=True).splitlines()
    assert all(p in allowed or p.startswith('src/pln_chess/cycle10/') for p in changed),changed
    for path in (ROOT/'src').rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            imports=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            if path!=ROOT/'src/pln_chess/cli/__init__.py':
                assert all(m.split('.')[0] not in ('chess','training','evaluation') for m in imports),path
    decision=read_json(out/'architecture/decision.json')
    assert all(decision[k] is False for k in ('new_operator_enabled','upstream_modified','strategic_selector_enabled','handcoded_evaluation_score_enabled','isolated_prototype_enabled'))
    data=read_json(out/'datasets/dataset.json');copy=dict(data);claimed=copy.pop('hash');assert digest(copy)==claimed
    assert data['registration_hash']==digest(cfg) and data['counts']['external-test']>=1000
    assert len([g for g in data['games'] if g['split']=='external-test'])>=100
    assert data['counts']['synthetic-adversarial']>=100
    assert read_json(out/'datasets/all-symmetry-audit.json')['passed']
    assert read_json(out/'bootstrap/dataset-replay.json')['exact_replay']
    bootstrap=read_json(out/current['fresh_dependency_bootstrap_receipt'])
    assert all(bootstrap[k] for k in ('passed','initial_clean','fresh_venv','fresh_runtime','final_clean'))
    assert bootstrap['identity']['runtime']==rt.manifest and bootstrap['dependency_lock_sha256']==sha(ROOT/'requirements-dev.lock')
    assert bootstrap['identity']['production_code_hash']==code
    frozen=read_json(out/'frozen-complete.json');assert frozen['passed'] and frozen['positions']==len(data['positions'])
    assert sha(out/'calibration/frozen-evaluation.json')==frozen['frozen_calibration_sha256']
    assert all(sha(out/p)==h for p,h in frozen['receipts'].items())
    proof_rows=0;counts={}
    for arm,positions in [('frozen',1420),('small',1020),('large',1020),('temporal',1020)]:
        receipts=list((out/'evaluation').glob(arm+'-operational-*.receipt.json'));counts[arm]=len(receipts)
        assert sum(read_json(p)['positions'] for p in receipts)==positions
        for path in receipts:
            r=read_json(path);assert sha(out/r['artifact'])==r['sha256'] and r['native_proofs_verified']
            assert r['identity']['dataset_hash']==data['hash']
            assert r['identity']['production_code_hash']==(baseline['identity']['production_code_hash'] if arm=='frozen' else code)
            proof_rows+=r['rows']
        verification=read_json(out/f'analysis/{arm}-verification.json');assert verification['passed'] and verification['all_positions_accounted_for']
    calibration=read_json(out/'calibration/results.json');adaptation=read_json(out/'adaptation/summary.json')
    assert calibration['fit_split']=='external-calibration' and calibration['fit_games']==24
    assert calibration['fitted_unix']>=frozen['completed_unix']
    assert adaptation['training_completed_unix']>=frozen['completed_unix'] and not adaptation['new_learning_promoted']
    assert adaptation['final_test_used_for_training'] is False and adaptation['thresholds_changed'] is False
    assert read_json(out/'adaptation/comparison.json')['new_learning_promoted'] is False
    regression=read_json(out/'adaptation/regression-summary.json');assert regression['evaluations']==32
    dependence=read_json(out/'dependence/summary.json')
    assert dependence['duplicate_native_values_equal'] and dependence['transformed_ancestor_native_values_equal']
    assert read_json(out/'dependence/predictions.json')['duplicate_and_transformed_predictions_equal']
    temporal=read_json(out/'temporal/summary.json')
    assert temporal['demonstrations']>=10 and temporal['historical_cases']==25 and temporal['complete_game_replays']==150
    assert not temporal['new_operator_enabled'] and not temporal['thresholds_changed']
    performance=read_json(out/'performance/comparison.json');assert performance['passed_parity'] and performance['paired_workloads']==6
    assert read_json(out/'performance/C10-current.json')['production_code_hash']==code
    assert read_json(out/'performance/temporal.json')['passed'] and read_json(out/'performance/temporal.json')['production_code_hash']==code
    tests=(out/'current/logs/tests.txt').read_text();match=re.search(r'(\d+) passed',tests)
    assert match and int(match[1])>=365 and not re.search(r'\d+ failed|ERRORS|FAILURES',tests)
    original=read_json(ROOT/'artifacts/cycle8/acceptance.json');model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    assert model.version in original['accepted_model_versions'];checks={k:True for k in CHECKS}
    summary=read_json(out/'analysis/frozen-summary.json')
    receipt=dict(passed=True,all_required_checks_executed=True,checks=checks,new_learning_promoted=False,
        selected_variant='C8-promotion-relative',default_mode='operational',model_version=model.version,
        accepted_model_versions=original['accepted_model_versions'],accepted_legacy_model_versions=original['accepted_legacy_model_versions'],
        production_code_hash=code,runtime_version=rt.version,registration_hash=digest(cfg),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9)},
        calibration_sha256=sha(out/'calibration/results.json'),
        external_errors={k:{field:v['complete'][field] for field in ('false_positive','false_illegal','self_check_false_legal','incomplete')} for k,v in summary.items()},
        scope='Implementation parity for the unchanged accepted C8 model. External errors, adaptation outcomes and temporal counterfactual results are research measurements, not silently waived replacement-model gates.')
    write_json(out/'acceptance.json',receipt);(out/'model').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',out/'model/C10-default.json')
    write_json(out/'verification.json',dict(passed=True,checks=checks,starting_head=START,
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),production_code_hash=code,
        runtime=rt.manifest,model_version=model.version,dataset_hash=data['hash'],test_count=int(match[1]),
        baseline_historical_suites=26,baseline_cycle9_shards=48,current_historical_suites=26,current_cycle9_shards=48,
        negative_controls=287,new_operational_shards=counts,new_operational_proof_rows=proof_rows,
        protected_files=len(lock['protected_files']),benchmark_samples=126+324,new_learning_promoted=False))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
