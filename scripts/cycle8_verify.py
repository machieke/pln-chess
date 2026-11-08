"""Fail-closed registered selection, immutable evidence and source-bound acceptance."""
from pathlib import Path
import argparse
import ast
import hashlib
import re
import shutil
import subprocess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import CHECKS
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle3 import read_gzip
from evaluation.cycle8_analysis import reference
from scripts.cycle8_evaluate import ARMS,jobs


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(out):
    out=Path(out);rt=Runtime(timeout=180);lock=read_json(out/'baseline/lock.json');config=read_json(ROOT/'configs/cycle8.json')
    assert all(sha(ROOT/p)==h for p,h in lock['protected_files'].items()),'Historical artifact changed'
    assert read_json(out/'baseline/verified.json')['passed'] is True
    assert lock['starting_head']==config['starting_head']
    assert rt.manifest==lock['runtime'],'Native operator/runtime changed'
    for arm in ('C7-frozen','C7-learned-8-locked','C7-strict','C7-experimental'):
        for entry in read_json(out/f'baseline/{arm}-summary.json').values():
            assert entry['exact_native_proof_parity'] is True and sha(out/'baseline'/entry['artifact'])==entry['sha256']
    summaries=read_json(out/'comparison.json');assert set(summaries)==set(ARMS)
    parity=[];proof_rows=0;native_operators=set()
    fields=('fixture','move','label','classification','truth_value','proof_id','rule_ids','evidence_ids','dependence_groups')
    for arm,entries in summaries.items():
        assert set(entries)=={j[0] for j in jobs(out,arm)},arm
        for split,entry in entries.items():
            assert sha(out/entry['artifact'])==entry['sha256'],(arm,split)
            report=read_gzip(out/entry['artifact']);assert not report['metrics']['incomplete'],(arm,split)
            for row in report['rows']:
                nodes=[report['native_proof_dag'][i] for i in row['proof_refs']]
                assert digest(nodes)==row['proof_id'];proof_rows+=1
                assert row['runtime_version']==rt.version and row['model_version']==entry['model_version']
                assert not row['positive_proof_complete'] and row['proof_status']!='native-compositional'
                native_operators.update(n['operator'] for n in nodes)
                assert all(k in row for k in ('rule_ids','evidence_ids','dependence_groups','typed_premises'))
            if arm=='C8-frozen':
                prior=read_gzip(reference(out,split))
                assert [{k:r[k] for k in fields} for r in prior['rows']]==[{k:r[k] for k in fields} for r in report['rows']],split
                assert [p['predicted'] for p in prior['positions']]==[p['predicted'] for p in report['positions']]
                parity.append({'split':split,'candidates':len(report['rows']),'native_proof_parity':True})
    # Production modules may route offline train/evaluate commands, but no module imports the oracle.
    imports=[]
    for path in (ROOT/'src').rglob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            for name in names:
                if name.split('.')[0]=='chess':raise AssertionError(('production oracle import',path,name))
                if path.parent.name=='cycle8' and name.split('.')[0] in ('training','evaluation'):
                    raise AssertionError(('research imported by production',path,name))
                if names:imports.extend(names)
    assert read_json(out/'composition/laboratory.json')['production_operator_enabled'] is False
    assert read_json(out/'composition/mathematical-validation.json')['passed'] is True
    negative_checks={}
    for variant in ('C8-frozen',*config['eligible_candidates_in_order']):
        negative_checks[variant]=read_json(out/f'{variant}-negative-regressions.json')
        n=negative_checks[variant]
        assert n['cases']==n['intact_negative']==n['removed_unknown']==n['exact_native_proof_parity']==287,variant
        temporal=read_gzip(out/f'{variant}-temporal.json.xz');assert len(temporal)==36
        assert all(not r['candidate']['positive_proof_complete'] for r in temporal)
        assert all(r['candidate']['classification']=='unknown' for r in temporal if r['condition']=='inconsistent-history')
        assert len(read_json(out/f'{variant}-temporal-validation.json'))==4
    for variant in ('C7-frozen','C8-frozen',*config['eligible_candidates_in_order']):
        b=read_json(out/f'benchmarks/{variant}.json');assert len(b['records'])==4
        assert b['production_code_hash']==production_code_hash()
        for record in b['records']:
            assert record['full_candidate_and_native_proof_parity']
            assert len(record['samples'])==15
            assert all(not s['truncated'] and (s['arm']!='warm' or s['native_invocations']==0) for s in record['samples'])
    tests=(out/'pytest.txt').read_text();match=re.search(r'(\d+) passed',tests)
    assert match and not re.search(r'\d+ failed|ERRORS|FAILURES',tests)
    bootstrap=read_json(out/'bootstrap-context.json')
    assert all(bootstrap.get(k) is True for k in ('fresh_venv','fresh_runtime','initial_clean_checkout','bootstrap_passed'))
    expected=read_json(ROOT/'configs/cycle8-replay.json');data=read_json(out/'datasets/dataset.json')
    assert data['hash']==expected['dataset_hash'],'Data replay differs'
    for variant,version in expected['model_versions'].items():
        assert PromotionModel.load(out/f'model/{variant}.json',rt).version==version,('Training replay differs',variant)
    checks={k:True for k in CHECKS}
    changes=read_json(out/'paired-summary.json');errors=('false_positive','false_illegal','self_check_false_legal','incomplete')
    # Keeping the prior checkpoint is allowed even if new diagnostic suites expose a limitation;
    # such findings remain in the receipt. Neither candidate may bypass any new-suite gate.
    decisions={};selected='C8-frozen'
    for variant in config['eligible_candidates_in_order']:
        reasons=[]
        for split,entry in summaries[variant].items():
            old=summaries['C8-frozen'][split]['metrics'];new=entry['metrics']
            for k in errors:
                if new[k]:reasons.append({'split':split,'gate':k,'observed':new[k]})
            for k in ('recall','exact_move_set_accuracy'):
                if old[k] is not None and (new[k] is None or new[k]<old[k]):reasons.append({'split':split,'gate':k,'before':old[k],'after':new[k]})
            if changes[variant][split]['lost_prior_supported_decisions']:
                reasons.append({'split':split,'gate':'lost_prior_supported_decisions','observed':changes[variant][split]['lost_prior_supported_decisions']})
        decisions[variant]={'eligible':not reasons,'rejection_reasons':reasons}
        if selected=='C8-frozen' and not reasons:selected=variant
    shutil.copy2(out/f'model/{selected}.json',out/'model/C8-default.json')
    model=PromotionModel.load(out/'model/C8-default.json',rt);frozen=PromotionModel.load(out/'model/C8-frozen.json',rt)
    old=frozen.source_model()
    receipt={'passed':True,'all_required_checks_executed':True,'checks':checks,'selected_variant':selected,'default_mode':'operational',
        'new_learning_promoted':selected!='C8-frozen','accepted_model_versions':sorted({model.version,frozen.version}),
        'accepted_legacy_model_versions':[old.version,old.source_model().version],
        'production_code_hash':production_code_hash(),'registration_hash':digest(config),
        'legacy_registrations':{str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7)},
        'runtime_version':rt.version,'candidate_decisions':decisions,
        'preserved_model_new_suite_errors':{s:{k:e['metrics'][k] for k in errors} for s,e in summaries['C8-frozen'].items() if s.startswith('cycle8-')},
        'scope':'Empirical acceptance on registered synthetic suites; positive claims remain partial native conditionals, not universal safety or calibrated probability guarantees.'}
    write_json(out/'acceptance.json',receipt)
    write_json(out/'verification.json',{'passed':True,'checks':checks,'protected_files':len(lock['protected_files']),
        'reconstructed_row_proofs':proof_rows,'frozen_parity':parity,'observed_native_operators':sorted(native_operators),
        'test_count':int(match[1]),'runtime':rt.manifest,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'production_code_hash':production_code_hash(),'dataset_hash':data['hash'],'training_replay_exact':True,
        'selected_variant':selected,'evaluations':sum(len(e) for e in summaries.values()),'baseline_evaluations':38})
    print(selected,decisions,flush=True);return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
