"""Lock the delivered C6 evidence, then independently execute all three modes."""
import argparse
import hashlib
import platform
import subprocess
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle6.inference import Cycle6Options
from evaluation.cycle6 import evaluate
from evaluation.cycle3 import read_gzip
from scripts.cycle6_baseline import SPLITS as OLD_SPLITS
from evaluation.cycle7_io import pack

START = 'ebe58a980d601ad8b8167a6533619c383109e08d'
SPLITS = OLD_SPLITS + [('cycle6-'+s, 'cycle6/datasets', s) for s in ('validation', 'adversarial', 'independent-games')]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def lock(out):
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], cwd=ROOT, text=True).splitlines()
    protected = {p: sha(ROOT/p) for p in tracked if p.startswith(('artifacts/', 'fixtures/', 'vendor/', 'configs/', 'tests/', 'docs/cycle6/')) or p.endswith('.lock')}
    result = {'expected_head': START, 'actual_head': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'branch': subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        'working_tree': subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        'python': platform.python_version(), 'runtime': Runtime().manifest,
        'petta_head': subprocess.check_output(['git','-C',str(ROOT/'.runtime/petta'),'rev-parse','HEAD'],text=True).strip(),
        'test_command': '.venv/bin/python -m pytest -q', 'ci': 'No CI workflow present at starting HEAD.',
        'protected_files': protected, 'reported_baselines': read_json(ROOT/'artifacts/cycle6/comparison.json'),
        'reported_negative_controls': read_json(ROOT/'artifacts/cycle6/negative-regressions.json'),
        'source_files': {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src').rglob('*.py'))}}
    write_json(out/'baseline/lock.json', result)
    return result

def job(out,mode,key,source,split):
    out=Path(out);rt=Runtime(timeout=180);model=Model.load(ROOT/'artifacts/cycle6/model/C6-full.json',rt)
    data=read_json(ROOT/f'artifacts/{source}/dataset.json')
    report=evaluate(data,model,split,rt,options=Cycle6Options(mode=mode))
    oldmode='strict' if mode=='experimental' else mode
    old=read_gzip(ROOT/f'artifacts/cycle6/evaluation/C6-{oldmode}-{key}.json.xz')
    fields=('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids','proof_status','dependence_groups')
    assert [{k:r[k] for k in fields} for r in report['rows']]==[{k:r[k] for k in fields} for r in old['rows']],(mode,key)
    assert [p['predicted'] for p in report['positions']]==[p['predicted'] for p in old['positions']]
    for row in report['rows']:
        assert digest([report['native_proof_dag'][i] for i in row['proof_refs']])==row['proof_id']
    assert not report['metrics']['incomplete']
    report['baseline_parity']=True
    path=out/f'baseline/{mode}-{key}.json.xz';pack(path,report)
    entry={'metrics':report['metrics'],'dataset_hash':data['hash'],'model_version':model.version,
        'artifact':str(path.relative_to(out)),'sha256':sha(path),'exact_native_proof_parity':True,
        'comparison': 'C6 strict; experimental differs only in explicit acceptance reason' if mode=='experimental' else 'C6 delivered report'}
    return mode,key,entry

def run(out):
    out=Path(out);receipt=read_json(out/'baseline/lock.json') if (out/'baseline/lock.json').exists() else lock(out);rt=Runtime(timeout=180)
    assert receipt['runtime']==rt.manifest
    assert all(sha(ROOT/p)==h for p,h in receipt['source_files'].items()),'Cannot resume baseline after frozen source changes'
    model=Model.load(ROOT/'artifacts/cycle6/model/C6-full.json',rt)
    summary=read_json(out/'baseline/comparison.json') if (out/'baseline/comparison.json').exists() else {}
    pending=[]
    for mode in ('operational','strict','experimental'):
        summary.setdefault(mode,{})
        for key, source, split in SPLITS:
            data=read_json(ROOT/f'artifacts/{source}/dataset.json')
            previous=summary[mode].get(key)
            if previous and previous['exact_native_proof_parity'] and previous['model_version']==model.version and previous['dataset_hash']==data['hash'] and sha(out/previous['artifact'])==previous['sha256']:
                print('VERIFIED RESUME',mode,key,flush=True);continue
            pending.append((str(out),mode,key,source,split))
    from concurrent.futures import ProcessPoolExecutor,as_completed
    with ProcessPoolExecutor(max_workers=3) as pool:
        for future in as_completed([pool.submit(job,*args) for args in pending]):
            mode,key,entry=future.result();summary[mode][key]=entry
            write_json(out/'baseline/comparison.json',summary)
            print(mode,key,entry['metrics']['recall'],entry['metrics']['exact_move_set_accuracy'],flush=True)
    assert all(sha(ROOT/p)==h for p,h in receipt['source_files'].items()),'C6 source changed during reproduction'
    write_json(out/'baseline/verified.json',{'passed':True,'evaluations':33,'source_unchanged':True,'runtime':rt.manifest})
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);a=parser.parse_args();run(a.out)
