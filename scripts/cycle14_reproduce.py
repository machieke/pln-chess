"""Fresh pinned environment, complete native proof replay and research refits.

All compact feature archives are replayed, with complete fresh observation
extraction on hash-selected strata. Selected raw references are searched again;
the full immutable reference generation remains an explicit scientific input.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from pln_chess.common import ROOT,digest,read_json
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha
from training.cycle14_labels import atomic_json
from evaluation.cycle3 import read_gzip


def scientific(value):
    if isinstance(value,dict):return {k:scientific(v) for k,v in value.items() if k!='elapsed_seconds'}
    if isinstance(value,list):return [scientific(v) for v in value]
    return value


def run(out,checkout,commit,workers=2):
    out=Path(out).resolve();checkout=Path(checkout).resolve();target=out/'clean-research';runout=target/'run'
    if not (target/'bootstrap/verified.json').exists():bootstrap(target/'bootstrap',checkout,commit)
    boot=read_json(target/'bootstrap/verified.json')
    actual_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
    assert actual_head==commit
    # A fresh dependency/runtime bootstrap may precede local verification-only
    # driver additions. Bind that advancement explicitly, retaining both heads.
    subprocess.run(['git','merge-base','--is-ancestor',boot['initial_source_head'],commit],cwd=checkout,check=True)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    code=read_json(out/'source-freeze.json')['production_code_hash'];assert boot['identity']['production_code_hash']==code
    atomic_json(target/'source-checkout.json',dict(passed=True,bootstrap_head=boot['initial_source_head'],
        verification_head=commit,production_code_hash=code,checkout_clean=True,
        scope='Fresh pinned dependencies and runtime retained across a local source advancement; frozen production code identity is unchanged.'))
    py=str(checkout/'.venv/bin/python');env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}',C14_OUT=str(runout),TMPDIR='/dev/shm')
    for i in range(6,14):env.pop(f'C{i}_OUT',None)
    inputs=[]
    def source_input(relative):
        src,dst=out/relative,runout/relative;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert sha(src)==sha(dst)
        else:shutil.copy2(src,dst)
        inputs.append(dict(path=relative,sha256=sha(src)))
    def command(name,module,args=(),has_out=True):
        path=target/'commands'/f'{name}.json';log=target/'logs'/f'{name}.txt'
        argv=[py,'-u','-m',module,*(['--out',str(runout)] if has_out else []),*map(str,args)]
        identity=dict(source_head=commit,production_code_hash=code,argv=argv,driver_sha256=sha(checkout/(module.replace('.','/')+'.py')))
        if path.exists():
            previous=read_json(path);assert previous['identity']==identity
            if previous['returncode']==0:return
            attempt=1
            while log.with_suffix(f'.attempt-{attempt}.txt').exists():attempt+=1
            if log.exists():log.rename(log.with_suffix(f'.attempt-{attempt}.txt'))
            shutil.copy2(path,path.with_suffix(f'.attempt-{attempt}.json'))
        log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
        with log.open('w') as stream:result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipt=dict(identity=identity,returncode=result.returncode,started_unix=started,elapsed_seconds=time.time()-started,
            log=str(log.relative_to(target)),log_sha256=sha(log));path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        if result.returncode:raise RuntimeError(str(log))
        print('C14 CLEAN REPLAY',name,flush=True)
    for relative in ('baseline/research/verified.json','baseline/reproduction-receipt.json','source-freeze.json'):source_input(relative)
    command('reference-bootstrap','scripts.cycle13_reference_bootstrap',['--directory',str(checkout/'.runtime/cycle13-reference'),'--out',str(target/'reference-bootstrap')],False)
    assert read_json(target/'reference-bootstrap/verified.json')['byte_identical_binary']
    command('source-partitions','training.cycle14_sources')
    command('concept-partition','training.cycle14_concept_sources')
    for relative in ('datasets/source-pairs.json','datasets/partitions.json','datasets/concept-holdout.json'):
        assert sha(out/relative)==sha(runout/relative),relative
    # Explicit fixed supervision inputs. They are neither model predictions nor
    # claims that every engine analysis was independently re-searched here.
    for kind in ('immediate','temporal'):
        source_input(f'labels/{kind}-g1/index.json')
    for path in sorted((out/'labels/immediate-g1/records').glob('*.json')):source_input(str(path.relative_to(out)))
    command('temporal-partition','training.cycle14_temporal_sources',['bind'])
    command('response-partition','training.cycle14_response_sources',['bind'])
    for relative in ('datasets/temporal-registration.json','datasets/temporal-plans.json','datasets/temporal-comparisons.json','datasets/response-panel-registration.json','datasets/response-plans.json'):
        assert sha(out/relative)==sha(runout/relative),relative
    source_input('features/selected-generations.json')
    generations=read_json(out/'features/selected-generations.json')
    for kind in ('immediate','temporal'):source_input(f'features/{generations[kind]}/index.json')
    source_input('datasets/reversal-registration.json')
    # Native replay reads full archives in the delivered generation directly;
    # a disjoint clean output tree receives all replay receipts.
    command('complete-native-proof-corpus','evaluation.cycle14_proof_replay',['--source',str(out),'--out',str(target/'proof-replay')],False)
    command('selected-fresh-observations-and-labels','scripts.cycle14_reproduce',['--selected','--out',str(out),'--replay-output',str(target/'selected')],False)
    command('representation','evaluation.cycle14_studies',['representation'])
    command('fit','evaluation.cycle14_preferences',['fit'])
    command('calibration-freeze','evaluation.cycle14_preferences',['freeze'])
    command('final-predictions','evaluation.cycle14_preferences',['test'])
    command('factorial','evaluation.cycle14_studies',['factorial'])
    command('dependence','evaluation.cycle14_studies',['dependence'])
    command('reversals','evaluation.cycle14_studies',['reversals'])
    command('concept-holdout','evaluation.cycle14_concepts')
    command('native-locality','evaluation.cycle14_locality')
    comparisons=[]
    for folder in ('model','learning','development','calibration','evaluation','ablations','temporal','dependence','reversals','concepts','representation'):
        paths=[p for p in (runout/folder).rglob('*') if p.is_file() and p.name.endswith(('.json','.jsonl','.json.xz'))]
        for b in sorted(paths):
            relative=b.relative_to(runout);a=out/relative
            if not a.exists():raise ValueError('Missing primary comparison: '+str(relative))
            if b.name.endswith('.json.xz'):
                equal=digest(scientific(read_gzip(a)))==digest(scientific(read_gzip(b)));method='canonical-json-excluding-elapsed-seconds'
            else:equal=sha(a)==sha(b);method='exact-bytes'
            comparisons.append(dict(path=str(relative),exact=equal,method=method,primary_sha256=sha(a),replay_sha256=sha(b)))
            assert equal,'Changed scientific evidence: '+str(relative)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    atomic_json(target/'comparison.json',dict(passed=True,artifacts=comparisons,inputs=inputs,
        scope='Complete model, ledger, native training/inference, calibration and matched study parity. Fixed supervision is an input; selected raw analyses are independently repeated.'))
    atomic_json(target/'verified.json',dict(passed=True,production_code_hash=code,source_head=commit,checkout=str(checkout),
        fresh_venv=True,fresh_runtime=True,fresh_reference_build=True,complete_native_feature_proof_replay=True,
        proof_replay_sha256=sha(target/'proof-replay/verified.json'),selected_fresh_extraction_sha256=sha(target/'selected/verified.json'),
        model_checkpoint_byte_parity=True,evidence_ledger_byte_parity=True,comparison_sha256=sha(target/'comparison.json'),
        compared_artifacts=len(comparisons),legal_regression_required_separately=True,browser_workflow_required_separately=True,
        scope='Clean native proof and research reproduction; legal and real-browser receipts are separately joined by final acceptance.'))


def selected(source,out):
    from pln_chess.pln import Runtime
    from training.cycle14_features import worker as feature,source_closure
    from training.cycle14_labels import worker as label
    source,out=Path(source),Path(out);closure=source_closure();receipts=[];references=[]
    generation_names=read_json(source/'features/selected-generations.json')
    for kind,filename in (('immediate','source-pairs.json'),('temporal','temporal-plans.json')):
        data=read_json(source/'datasets'/filename);groups={}
        for row in sorted(data['records'],key=lambda r:digest(['c14-clean-observation-selection',r['id']])):
            key=(row['source'].get('collection'),row['split']=='test',bool(row.get('short_branches')))
            groups.setdefault(key,row)
        original={r['id']:r for r in read_json(source/'features'/generation_names[kind]/'index.json')['records']}
        for row in groups.values():
            fresh=feature((str(out),row,data['hash'],'selected-'+kind,kind,closure))
            old=original[row['id']];assert fresh['semantic_sha256']==old['semantic_sha256'] and fresh['observations']==old['observations']
            receipts.append(dict(id=row['id'],kind=kind,exact_native_proof_and_observation_parity=True,semantic_sha256=fresh['semantic_sha256']))
    for kind,filename,oldname in (('immediate','source-pairs.json','reference-labels.json'),('temporal','temporal-comparisons.json','temporal-labels.json')):
        data=read_json(source/'datasets'/filename);sources={r['id']:r for r in data['records']}
        previous={r['id']:r['evidence_id'] for r in read_json(ROOT/'artifacts/cycle13/datasets'/oldname)['records']}
        generation=read_json(source/f'labels/{kind}-g1/index.json');chosen={}
        for row in sorted(generation['records'],key=lambda r:digest(['c14-clean-reference-selection',r['id']])):
            chosen.setdefault((row['label'],row['reason'],row['original_actor'],row['horizon']),row)
        for old in chosen.values():
            row={**sources[old['id']],'previous_reference_evidence_id':previous.get(old['id'])}
            fresh=label((str(out),kind+'-g1',row,data['hash'],kind))
            assert fresh['evidence_id']==old['evidence_id']
            references.append(dict(id=old['id'],kind=kind,evidence_id=old['evidence_id'],exact_semantic_search_parity=True,
                actual_reported_nodes=fresh['actual_reported_nodes'],raw_sha256=fresh['raw_sha256']))
    atomic_json(out/'verified.json',dict(passed=True,features=receipts,reference_analyses=references,
        selected_from_all_registered_strata_before_replay=True,source_closure=closure,
        scope='Fresh observation construction by source/split/missingness strata; fresh raw UCI runs by actor/horizon/label/cause strata. Selection concerns verification coverage, never fitted-model performance.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/cycle14');p.add_argument('--checkout');p.add_argument('--commit');p.add_argument('--workers',type=int,default=2);p.add_argument('--selected',action='store_true');p.add_argument('--replay-output');a=p.parse_args()
    selected(a.out,a.replay_output) if a.selected else run(a.out,a.checkout,a.commit,a.workers)
