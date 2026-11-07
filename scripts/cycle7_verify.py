"""Fail-closed evidence checks and source/model-bound default acceptance."""
import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle7.model import BackoffModel
from evaluation.cycle3 import read_gzip
from scripts.cycle7_baseline import SPLITS, sha

OUT=Path(os.environ.get('C7_OUT',ROOT/'artifacts/cycle7'))

def verify(out=OUT):
    out=Path(out);rt=Runtime();lock=read_json(out/'baseline/lock.json')
    protected={p:sha(ROOT/p)==h for p,h in lock['protected_files'].items()}
    assert all(protected.values()),[p for p,v in protected.items() if not v]
    baseline=read_json(out/'baseline/comparison.json')
    assert set(baseline)=={'operational','strict','experimental'}
    for mode,entries in baseline.items():
        assert set(entries)=={s[0] for s in SPLITS}
        for e in entries.values():assert e['exact_native_proof_parity'] and sha(out/e['artifact'])==e['sha256']
    lab=read_json(out/'native/laboratory.json')
    assert lab['experiment_budget']==3 and len(lab['encodings'])==3 and lab['training_groups_disjoint'] and lab['combined_training_examples']==0
    assert lab['native_positive_composition']=='not demonstrated' and lab['stopped_after_budget']
    neg=read_json(out/'C7-frozen-negative-regressions.json')
    assert neg['cases']==neg['intact_negative']==neg['removed_unknown']==neg['exact_native_proof_parity']==287
    enhanced_neg=read_json(out/'C7-learned-8-negative-regressions.json')
    required={'C7-frozen','C7-strict','C7-experimental','C7-learned-8-locked',*(f'C7-learned-{i}' for i in (0,2,4,8)),
        *(f'ablation-{name}' for name in ('no-backoff','no-attack-exposure','no-temporal','no-dependence','no-new-training','no-learned-negatives'))}
    summaries={name:read_json(out/f'evaluation/{name}-summary.json') for name in sorted(required)}
    allkeys={s[0] for s in SPLITS}|{'cycle7-independent-games'}
    for name in ('C7-frozen','C7-strict','C7-learned-8-locked'):assert set(summaries[name])==allkeys
    independent={'cycle6-independent-games','cycle7-independent-games'}
    for name in required-{'C7-frozen','C7-strict','C7-learned-8-locked'}:assert set(summaries[name])==independent
    parity=[];proof_rows=0
    for name in ('C7-frozen','C7-strict'):
        for split in sorted(allkeys):
            mode='strict' if name=='C7-strict' else 'operational'
            ref=out/(f'evaluation/C6-{mode}-{split}.json.xz' if split.startswith('cycle7-') else f'baseline/{mode}-{split}.json.xz')
            before=read_gzip(ref);after=read_gzip(out/summaries[name][split]['artifact'])
            fields=('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids','dependence_groups')
            assert [{k:r[k] for k in fields} for r in before['rows']]==[{k:r[k] for k in fields} for r in after['rows']],(name,split)
            for a,b in zip(before['rows'],after['rows']):
                assert b['legacy_proof_status']==a['proof_status']
                assert digest([after['native_proof_dag'][i] for i in b['proof_refs']])==b['proof_id'];proof_rows+=1
            parity.append({'arm':name,'split':split,'candidate_count':len(after['rows']),'exact_native_proof_parity':True})
    checks={'baseline':True,'negatives':True,'native':True,'evaluation':True,'parity':True}
    for name,entries in summaries.items():
        for split,e in entries.items():
            assert e['metrics']['incomplete']==0,(name,split)
            assert sha(out/e['artifact'])
    for name in ('C6','C7'):
        bench=read_json(out/f'benchmarks/{name}.json')
        assert all(r['full_candidate_parity'] and r['runs']['warm']['native_invocations']==0 for r in bench['records'])
        assert bench['records'][0]['candidate_count']==214 and any(r['candidate_count']>214 for r in bench['records'])
    text=(out/'pytest.txt').read_text();match=re.search(r'(\d+) passed',text)
    checks['tests']=bool(match) and not re.search(r'\d+ failed|ERRORS|FAILURES',text)
    bootstrap=read_json(out/'bootstrap-context.json')
    checks['clean_bootstrap']=all(bootstrap.get(k) is True for k in ('fresh_venv','fresh_runtime','initial_clean_checkout','bootstrap_passed'))
    assert all(checks.values()),checks
    errors=('false_positive','false_illegal','self_check_false_legal','incomplete')
    assert all(not e['metrics'][k] for e in summaries['C7-frozen'].values() for k in errors),'Frozen model has observed errors on a new suite'
    eligible=enhanced_neg['intact_negative']==enhanced_neg['removed_unknown']==287
    reasons=[]
    for split,entry in summaries['C7-learned-8-locked'].items():
        old=summaries['C7-frozen'][split]['metrics'];new=entry['metrics']
        for k in errors:
            if new[k]:eligible=False;reasons.append([split,k,new[k]])
        for k in ('recall','exact_move_set_accuracy'):
            if new[k]<old[k]:eligible=False;reasons.append([split,k,new[k],old[k]])
    selected='C7-learned-8' if eligible else 'C7-frozen'
    shutil.copy2(out/f'model/{selected}.json',out/'model/C7-default.json')
    model=BackoffModel.load(out/'model/C7-default.json',rt);frozen=BackoffModel.load(out/'model/C7-frozen.json',rt)
    receipt={'passed':True,'all_required_checks_executed':True,'checks':checks,'default_mode':'operational','selected_variant':selected,
        'accepted_model_versions':sorted({model.version,frozen.version}),
        'accepted_legacy_model_versions':[frozen.source_model().version],
        'production_code_hash':production_code_hash(),'registration_hash':digest(read_json(ROOT/'configs/cycle7.json')),
        'legacy_registration_hash':digest(read_json(ROOT/'configs/cycle6.json')),'runtime_version':rt.version,
        'promotion_rejection_reasons':reasons,'new_learning_promoted':eligible,
        'scope':'Empirical selection on locked generated suites, not a universal safety or calibrated-probability guarantee.'}
    write_json(out/'acceptance.json',receipt)
    write_json(out/'verification.json',{'passed':True,'checks':checks,'protected_files':len(protected),'reconstructed_frozen_row_proofs':proof_rows,
        'parity':parity,'test_count':int(match[1]),'runtime':rt.manifest,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'source_hash':production_code_hash(),'selected_variant':selected})
    write_json(out/'comparison.json',summaries)
    return receipt

if __name__=='__main__':verify()
