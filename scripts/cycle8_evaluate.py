"""Registered C8 evaluation arms, resumable only against identical inputs."""
from dataclasses import replace
from pathlib import Path
import argparse
import hashlib
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.pln import Runtime
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import Cycle7Options
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import Cycle8Options
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle7_baseline import SPLITS
from evaluation.cycle8 import evaluate

ARMS=('C7-frozen','C7-learned-8','C8-frozen','C8-promotion-relative','C8-no-promotion-training',
      'C8-no-destination-context','C8-no-choice-context','C8-no-dependence','C8-strict','C8-experimental')
NEW_SPLITS=('validation','combination-holdout','adversarial','independent-games')


def jobs(out, arm):
    historical=[(name,ROOT/f'artifacts/{source}/dataset.json',split) for name,source,split in SPLITS]
    historical.append(('cycle7-independent-games',ROOT/'artifacts/cycle7/datasets/dataset.json','independent-games'))
    new=[('cycle8-'+s,Path(out)/'datasets/dataset.json',s) for s in NEW_SPLITS]
    if arm.startswith('C7-'):return new
    if arm in ('C8-no-destination-context','C8-no-choice-context','C8-no-dependence'):
        return [r for r in historical if r[0]=='cycle7-independent-games']+new
    if arm=='C8-strict':
        return [r for r in historical if r[0] in ('cycle6-independent-games','cycle7-independent-games')]+new
    if arm=='C8-experimental':
        return [r for r in historical if r[0] in ('cycle6-independent-games','cycle7-independent-games')]+[r for r in new if r[2] in ('combination-holdout','adversarial')]
    return historical+new


def run(out,arm,only=None):
    out=Path(out);rt=Runtime(timeout=180);config=read_json(ROOT/'configs/cycle8.json')
    mode={'C8-strict':'strict','C8-experimental':'experimental'}.get(arm,'operational')
    name='C8-promotion-relative' if arm in ('C8-strict','C8-experimental') else arm
    path=ROOT/f'artifacts/cycle7/model/{name}.json' if name.startswith('C7-') else out/f'model/{name}.json'
    model=BackoffModel.load(path,rt) if name.startswith('C7-') else PromotionModel.load(path,rt)
    option_type=Cycle7Options if model.schema==7 else Cycle8Options
    options=option_type(mode=mode,max_native_invocations=config['evaluation_max_native_invocations'],
        timeout_seconds=config['evaluation_timeout_seconds'],dependence_aware=arm!='C8-no-dependence')
    code_hash=digest({'production':production_code_hash(),'evaluator':hashlib.sha256((ROOT/'evaluation/cycle8.py').read_bytes()).hexdigest(),
        'driver':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    summary_path=out/f'evaluation/{arm}-summary.json'
    summary=read_json(summary_path) if summary_path.exists() else {}
    for name,data_path,split in jobs(out,arm):
        if only and name!=only:continue
        data=read_json(data_path);target=out/f'evaluation/{arm}-{name}.json.xz';old=summary.get(name)
        if old and old.get('execution_code_hash')==code_hash and old['model_version']==model.version and old['dataset_hash']==data['hash'] and target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==old['sha256']:
            print('VERIFIED RESUME',arm,name,flush=True);continue
        report=evaluate(data,model,split,rt,options,target)
        summary[name]={'metrics':report['metrics'],'model_version':model.version,'dataset_hash':data['hash'],
            'artifact':str(target.relative_to(out)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'positions':len(report['positions']),'execution_code_hash':code_hash,'mode':mode}
        write_json(summary_path,summary)
        print(arm,name,{k:report['metrics'][k] for k in ('recall','exact_move_set_accuracy','false_positive','false_illegal','unknown','incomplete')},flush=True)
        if report['metrics']['incomplete']:raise RuntimeError('Incomplete registered evaluation: '+arm+' '+name)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--arm',required=True,choices=ARMS);parser.add_argument('--only')
    args=parser.parse_args();run(args.out,args.arm,args.only)
