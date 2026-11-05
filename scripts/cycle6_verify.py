"""Execute quantitative gates and bind default promotion to verified source/inputs."""
import argparse,hashlib,os,subprocess
from pathlib import Path
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import REQUIRED_CHECKS,production_code_hash
from pln_chess.cycle6.model import POLICY
from evaluation.cycle3 import read_gzip
from scripts.cycle6_baseline import SPLITS

OUT=Path(os.environ.get('C6_OUT',ROOT/'artifacts/cycle6'))

def benchmarks():
    positions=read_json(ROOT/'artifacts/cycle5/benchmarks/positions.json');write_json(OUT/'benchmarks/positions.json',positions)
    for name,module,path,mode in [('C4','evaluation.cycle4_benchmark',ROOT/'artifacts/cycle4/model/C4-full.json',None),
                                  ('C5','evaluation.cycle4_benchmark',ROOT/'artifacts/cycle5/model/C5-full.json',None)]+[(f'C6-{m}','evaluation.cycle6_benchmark',OUT/'model/C6-full.json',m) for m in ('operational','strict','experimental')]:
        command=[str(ROOT/'.venv/bin/python'),'-m',module,'--checkpoint',str(path),'--positions',str(OUT/'benchmarks/positions.json'),'--output',str(OUT/f'benchmarks/{name}.json')]
        if mode:command+=['--mode',mode]
        subprocess.run(command,check=True);print('BENCHMARK',name,flush=True)

def verify():
    model=Model.load(OUT/'model/C6-full.json',Runtime());comparison=read_json(OUT/'comparison.json');base=read_json(OUT/'baseline/comparison.json');neg=read_json(OUT/'negative-regressions.json')
    proofs=[];parity=[];changed=[];errors=[];strict_positive=0;baseline_ok=True
    for key,_,_ in SPLITS:
        c4=read_gzip(OUT/f'baseline/C4-{key}.json.xz');c5=read_gzip(OUT/f'baseline/C5-{key}.json.xz')
        op=read_gzip(OUT/f'evaluation/C6-operational-{key}.json.xz');strict=read_gzip(OUT/f'evaluation/C6-strict-{key}.json.xz');no=read_gzip(OUT/f'evaluation/C6-no-new-negatives-{key}.json.xz')
        fields=lambda r:(r['fixture'],r['move'])
        assert list(map(fields,c4['rows']))==list(map(fields,c5['rows']))==list(map(fields,op['rows']))==list(map(fields,strict['rows']))==list(map(fields,no['rows']))
        for a,b,c,d,e in zip(c4['rows'],c5['rows'],op['rows'],strict['rows'],no['rows']):
            assert e['legacy_classification']==a['classification'],(key,fields(a),'no-new-negative mismatch')
            assert d['legacy_classification']==b['classification'],(key,fields(a),'strict mismatch')
            assert c['proof_id']==b['proof_id']==d['proof_id'],(key,fields(a),'native proof mismatch')
            if c['legacy_classification']!=a['classification']:
                changed.append({'split':key,'fixture':c['fixture'],'move':c['move'],'from':a['classification'],'to':c['classification'],'decision':op['policy_decisions'][c['decision_ref']],'proof_id':c['proof_id']})
        baseline_ok &= base['C4'][key]['proof_parity'] and base['C5'][key]['proof_parity']
        parity.append({'split':key,'C4_projection_parity':True,'C5_strict_classification_parity':True,'native_proof_parity':True})
    provenance_ok=True
    for name,reports in comparison.items():
        if not name.startswith('C6-'):continue
        for key,info in reports.items():
            report=read_gzip(OUT/info['artifact']);nodes=report['native_proof_dag']
            iterable=nodes.values() if isinstance(nodes,dict) else nodes
            provenance_ok &= all(all(field in node for field in ('id','operator','native_expression','truth_value','premises','matched_rule_ids','evidence_ids','dependence_groups')) for node in iterable)
            for row in report['rows']:
                trace=[nodes[x] for x in row['proof_refs']]
                if digest(trace)!=row['proof_id']:raise AssertionError('Proof reconstruction mismatch')
                assert all(k in row for k in ('mode','proof_status','evidence_ids','dependence_groups','rule_ids','observation_sources','model_version','runtime_version'))
                if name=='C6-strict':strict_positive+=row['classification']=='supported-legal'
                if row['classification']=='incomplete' or (row['classification']=='supported-legal' and not row['label']) or (row['classification']=='supported-illegal' and row['label']):errors.append({'variant':name,'split':key,'row':row})
            proofs.append({'variant':name,'split':key,'candidates':len(report['rows']),'complete_proof_reconstruction':True})
    protected=read_json(OUT/'baseline/start.json')['protected_files']
    unchanged=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in protected.items())
    assert unchanged,'Historical evidence changed'
    c4game=read_gzip(OUT/'baseline/C4-cycle4-independent-games.json.xz')['metrics'];frozen=read_gzip(OUT/'baseline/C4-frozen-heldout-transfer.json.xz')['metrics']
    op=comparison['C6-operational'];native=read_json(OUT/'native-probes/audit.json')
    tests=(OUT/'pytest.txt').read_text();bootstrap=read_json(OUT/'bootstrap-context.json') if (OUT/'bootstrap-context.json').exists() else {}
    checks={
        'baseline':bool(baseline_ok and unchanged),
        'frozen_utility':op['frozen-heldout-transfer']['metrics']['recall']>=frozen['recall'] and op['cycle4-independent-games']['metrics']['recall']>=c4game['recall'] and op['frozen-heldout-transfer']['metrics']['true_positive']>0,
        'frozen_errors':not any(e['split'] in [x[0] for x in SPLITS] for e in errors),
        'new_adversarial_errors':not any(e['split'].startswith('cycle6-') for e in errors),
        'negatives':neg['historical_preserved']==49 and neg['new_preserved']==238 and neg['historical_removal_changes']==49 and neg['new_removal_changes']==238 and neg['new_proof_parity'],
        'strict_abstention':strict_positive==0,
        'native_probes':native['training_groups_disjoint'] and native['native_composition_achieved'] is False and len(native['records'])>=20,
        'provenance':bool(provenance_ok),
        'cache_parity':all(all(p['full_proof_parity'] for p in read_json(OUT/f'benchmarks/{name}.json')['corpus']) for name in ('C4','C5','C6-operational','C6-strict','C6-experimental')),
        'tests':'passed' in tests and 'failed' not in tests and 'error' not in tests.lower(),
        'clean_bootstrap':bootstrap.get('fresh_venv') is True and bootstrap.get('fresh_runtime') is True and bootstrap.get('initial_clean_checkout') is True and (OUT/'logs/bootstrap.txt').exists()
    }
    receipt={'model_version':model.version,'runtime_version':model.runtime_version,'policy':POLICY,'production_code_hash':production_code_hash(),
        'registration_hash':digest(read_json(ROOT/'configs/cycle6.json')),'dataset_hash':read_json(OUT/'datasets/dataset.json')['hash'],
        'checks':checks,'all_required_checks_executed':all(k in checks for k in REQUIRED_CHECKS),'passed':all(checks.values()),
        'default_mode':'operational' if all(checks.values()) else 'strict','blockers':[k for k,v in checks.items() if not v],
        'scope':'Empirical acceptance on named datasets, not a universal chess-legality theorem.'}
    write_json(OUT/'verification.json',{'checks':checks,'baseline_parity':parity,'proof_reconstruction':proofs,'classification_changes_from_C4':changed,'errors':errors,
        'protected_file_count':len(protected),'protected_files_unchanged':unchanged,'tests_summary':tests.strip().splitlines()[-1]})
    write_json(OUT/'acceptance.json',receipt);print('ACCEPTANCE',receipt['passed'],receipt['blockers'],flush=True)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--benchmarks-only',action='store_true');p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    if not a.verify_only:benchmarks()
    if not a.benchmarks_only:verify()
