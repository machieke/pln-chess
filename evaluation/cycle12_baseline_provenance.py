"""Reproduce the provenance and derivation of the quoted starting measurements.

This is distinct from the new complete native replay, which has its own pending
receipt. No old receipt is represented as a newly executed acceptance gate.
"""
import argparse
from pathlib import Path
import subprocess

from pln_chess.common import read_json, write_json
from scripts.cycle9_baseline import sha


def run(out,source):
    out,source=Path(out).resolve(),Path(source).resolve()
    manifest=read_json(out/'manifest.json');identity=manifest['identity']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==manifest['starting_head']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    cohorts={};receipts=[]
    for group,cycle in (('historical',9),('external',10)):
        data=read_json(source/f'artifacts/cycle{cycle}/datasets/dataset.json')
        fixtures={p['id']:p for p in data['positions']}
        for path in sorted((source/f'artifacts/cycle11/current/{group}/evaluation').glob('*.receipt.json')):
            r=read_json(path);binding=r['identity'];artifact=path.parent.parent/r['artifact']
            assert r['native_proofs_verified'] and sha(artifact)==r['sha256']
            assert binding['production_code_hash']==identity['production_code_hash']
            assert binding['model_version']==identity['accepted_model']
            assert all(i in fixtures for i in binding['fixtures'])
            assert r['positions']==len(binding['fixtures'])
            split=fixtures[binding['fixtures'][0]]['split']
            name=f'cycle{cycle}/{split}/'+binding['mode']+'/'+('history' if binding.get('arm')=='temporal' else 'fen')
            counts=cohorts.setdefault(name,dict(positions=0,exact=0,true_positive=0,missed_legal=0,false_legal=0,false_illegal=0,shards=0))
            counts['positions']+=r['positions'];counts['shards']+=1
            counts['exact']+=(r['metrics']['exact_positions'] if 'exact_positions' in r['metrics'] else
                              r['metrics']['nonempty_exact']+r['metrics']['empty_terminal_exact'])
            for target,key in (('true_positive','true_positive'),('missed_legal','false_negative_including_abstention'),
                               ('false_legal','false_positive'),('false_illegal','false_illegal')):
                counts[target]+=r['metrics'][key]
            receipts.append(dict(path=str(path.relative_to(source)),sha256=sha(path),artifact_sha256=r['sha256'],
                source_head=r['source_head'],source_code_hash=binding['production_code_hash'],native_proofs_previously_verified=True))
    expected={'cycle10/external-test/operational/fen':(793,1020),
        'cycle10/external-test/operational/history':(1018,1020),
        'cycle9/adversarial/operational/fen':(112,128),
        'cycle9/special-moves/operational/fen':(71,80),
        'cycle10/synthetic-adversarial/operational/fen':(98,112)}
    for name,pair in expected.items():
        row=cohorts[name];assert (row['exact'],row['positions'])==pair,(name,row)
        row['recall']=row['true_positive']/(row['true_positive']+row['missed_legal'])
        assert row['false_legal']==row['false_illegal']==0
    models=[source/'artifacts/cycle10/model/C10-default.json',*sorted((source/'artifacts/cycle11/model').glob('*.json'))]
    write_json(out/'model-identities.json',{str(p.relative_to(source)):dict(sha256=sha(p),version=read_json(p).get('version')) for p in models})
    write_json(out/'dataset-identities.json',{str(p.relative_to(source)):sha(p) for p in sorted((source/'artifacts/cycle11/datasets').glob('*')) if p.is_file()})
    write_json(out/'starting-provenance.json',dict(passed=True,starting_head=manifest['starting_head'],
        source_identity=identity,source_clean=True,quoted_measurements={k:cohorts[k] for k in expected},
        verified_prior_native_receipts=receipts,verified_cycle11_manifest=manifest['cycle11_manifest_sha256'],
        fresh_bootstrap_passed=read_json(out.parent/'baseline-bootstrap/verified.json')['passed'],
        fresh_tests_passed=read_json(out/'commands/tests.json')['returncode']==0,
        fresh_historical_suites_passed=read_json(out/'commands/historical-suites.json')['returncode']==0,
        fresh_cycle9_evaluation_passed=read_json(out/'commands/cycle9-evaluation.json')['returncode']==0,
        fresh_full_baseline_complete=False,new_learning_authorized=False,
        scope='Reproduced source/model/data/runtime provenance and metric derivations from the immutable starting proof archives, plus already completed fresh bootstrap/tests/historical executions. Complete fresh external proof replay remains a separate mandatory gate.'))
    print('STARTING MEASUREMENT PROVENANCE REPRODUCED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--source',required=True)
    args=parser.parse_args();run(args.out,args.source)
