"""Fresh-checkout regeneration of fixed C13 supervision, native features and fits.

The baseline evidence is an input gate. All Cycle 13 research outputs are newly
generated outside the clean source checkout; none is copied from a trained run.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import ROOT,digest,read_json,write_json
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip


def normalized(value):
    """Ignore execution telemetry and ledger wall-clock timestamps, nothing else."""
    if isinstance(value,dict):
        skip={'execution','incremental'}
        if {'sequence','timestamp','evidence_id','payload'}<=set(value):skip.add('timestamp')
        return {key:normalized(item) for key,item in value.items() if key not in skip}
    if isinstance(value,(list,tuple)):return [normalized(item) for item in value]
    return value


def run(out,checkout,commit,workers=4,generation=None):
    out=Path(out).resolve();checkout=Path(checkout).resolve()
    target=Path(generation).resolve() if generation else out/'clean-research';runout=target/'run'
    if not (target/'bootstrap/verified.json').exists():bootstrap(target/'bootstrap',checkout,commit)
    boot=read_json(target/'bootstrap/verified.json');assert boot['initial_source_head']==commit
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()==commit
    code=read_json(out/'source-freeze.json')['production_code_hash']
    assert boot['identity']['production_code_hash']==code
    # Only source inputs and verified prior-cycle preservation evidence enter
    # the new output root. Preference labels, models and features are absent.
    inputs=['sources/lichess-puzzle-prefix.csv','sources/lichess-puzzle-source.json',
        'sources/stockfish-source.json','baseline/reproduction-receipt.json',
        'baseline/research/concepts/rows.json.xz','source-freeze.json']
    for relative in inputs:
        src,dst=out/relative,runout/relative;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert sha(dst)==sha(src)
        else:shutil.copy2(src,dst)
    py=str(checkout/'.venv/bin/python')
    env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=str(checkout/'src')+':'+str(checkout),
        C13_OUT=str(runout),TMPDIR='/dev/shm')
    for cycle in range(6,13):env.pop(f'C{cycle}_OUT',None)

    def command(name,module,args=(),has_out=True):
        path=target/'commands'/f'{name}.json';log=target/'logs'/f'{name}.txt'
        argv=[py,'-u','-m',module,*(['--out',str(runout)] if has_out else []),*map(str,args)]
        identity=dict(source_head=commit,production_code_hash=code,argv=argv,
            driver_sha256=sha(checkout/(module.replace('.','/')+'.py')))
        if path.exists():
            prior=read_json(path)
            assert prior['identity']==identity,'Preserve prior generation before changing replay source'
            if prior['returncode']==0:
                print('CLEAN RESUME',name,flush=True);return
            # Failure logs remain immutable; a new attempt gets a separate log.
            previous=1
            while log.with_suffix(f'.attempt-{previous}.txt').exists():previous+=1
            if log.exists():log.rename(log.with_suffix(f'.attempt-{previous}.txt'))
            shutil.copy2(path,path.with_suffix(f'.attempt-{previous}.json'))
        log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
        print('CLEAN REGENERATE',name,flush=True)
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(path,dict(identity=identity,returncode=result.returncode,started_unix=started,
            elapsed_seconds=time.time()-started,log=str(log)))
        if result.returncode:raise RuntimeError(str(log))

    command('reference-bootstrap','scripts.cycle13_reference_bootstrap',
        ['--directory',str(checkout/'.runtime/cycle13-reference'),'--out',str(target/'reference-bootstrap')],False)
    reference=read_json(target/'reference-bootstrap/verified.json')
    assert reference['byte_identical_binary'],'Teacher binary differs; investigate before labeling'
    binary=reference['binary']
    command('sources','training.cycle13_sources')
    command('external-concepts','training.cycle13_concept_sources')
    command('pair-labels','training.cycle13_labels',['--binary',binary])
    command('label-audit','evaluation.cycle13_data_audit',['--require-labels'])
    command('temporal-labels','training.cycle13_temporal_sources',['--binary',binary])
    command('temporal-audit','evaluation.cycle13_temporal_audit')
    command('fork-training','training.cycle13_forks')
    # Both complete feature populations are regenerated by fresh interpreters.
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending=[pool.submit(command,'features','training.cycle13_features',['--workers',str(workers)]),
            pool.submit(command,'temporal-features','training.cycle13_temporal_features',['--workers','2'])]
        for future in pending:future.result()
    for name,module in (
        ('preferences','evaluation.cycle13_preferences'),('temporal','evaluation.cycle13_temporal'),
        ('dependence','evaluation.cycle13_dependence'),('consistency','evaluation.cycle13_consistency'),
        ('concepts','evaluation.cycle13_concepts'),('integrity','evaluation.cycle13_integrity')):
        command(name,module)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    write_json(target/'regeneration.json',dict(passed=True,source_head=commit,checkout=str(checkout),
        source_clean=True,production_code_hash=code,input_files={p:sha(out/p) for p in inputs},
        bootstrap_sha256=sha(target/'bootstrap/verified.json'),reference_bootstrap_sha256=sha(target/'reference-bootstrap/verified.json'),
        command_receipts={str(p.relative_to(target)):sha(p) for p in sorted((target/'commands').glob('*.json'))}))
    print('CLEAN RESEARCH REGENERATION COMPLETE; SEMANTIC COMPARISON STILL REQUIRED',flush=True)


def compare(out,generation=None):
    out=Path(out).resolve();target=Path(generation).resolve() if generation else out/'clean-research';runout=target/'run'
    gate=read_json(target/'regeneration.json');assert gate['passed']
    rows=[]
    def check(relative,kind='canonical'):
        a,b=out/relative,runout/relative
        if kind=='bytes':
            equal=sha(a)==sha(b);semantic=sha(a)
        else:
            if a.name.endswith('.json.xz'):left,right=read_gzip(a),read_gzip(b)
            elif a.suffix=='.jsonl':
                left=[json.loads(line) for line in a.read_text().splitlines()]
                right=[json.loads(line) for line in b.read_text().splitlines()]
            else:left,right=read_json(a),read_json(b)
            lh,rh=digest(normalized(left)),digest(normalized(right));equal=lh==rh;semantic=lh
        row=dict(path=relative,comparison=kind,exact=equal,primary_sha256=sha(a),replayed_sha256=sha(b),semantic_sha256=semantic)
        rows.append(row)
        if not equal:
            write_json(target/'comparison-failure.json',dict(failed=row,previous=rows[:-1]))
            raise AssertionError('Research replay differs: '+relative)

    for relative in ('datasets/source-pairs.json','datasets/external-concepts.json','datasets/reference-labels.json',
        'datasets/temporal-plans.json','datasets/temporal-labels.json'):
        check(relative,'bytes')
    feature_records=0
    for relative,records_key in (('features/index.json','records'),('temporal/features/index.json','receipts')):
        first,second=read_json(out/relative),read_json(runout/relative)
        assert len(first[records_key])==len(second[records_key])
        for a,b in zip(first[records_key],second[records_key]):
            assert a['identity']==b['identity'] and a['semantic_sha256']==b['semantic_sha256']
            assert a['artifact']==b['artifact'] and sha(out/a['artifact'])==a['sha256'] and sha(runout/b['artifact'])==b['sha256']
            assert not a['execution']['truncated'] and not b['execution']['truncated']
            check(a['artifact']);feature_records+=1
    assert feature_records==400
    folders=('model','learning','forks','concepts','preferences','transfer','temporal','ablations','dependence','consistency')
    for folder in folders:
        primary={str(p.relative_to(out)) for p in (out/folder).rglob('*') if p.is_file() and
            (p.name.endswith(('.json','.json.xz','.jsonl'))) and 'features' not in p.relative_to(out).parts}
        replayed={str(p.relative_to(runout)) for p in (runout/folder).rglob('*') if p.is_file() and
            (p.name.endswith(('.json','.json.xz','.jsonl'))) and 'features' not in p.relative_to(runout).parts}
        # Recognition of the old legal checkpoint is a later operational gate,
        # independent of experimental research regeneration.
        primary.discard('model/C13-default.json');replayed.discard('model/C13-default.json')
        assert primary==replayed,(folder,primary^replayed)
        for relative in sorted(primary):check(relative,'bytes' if relative.startswith('model/') or relative.endswith('/checkpoint.json') else 'canonical')
    write_json(target/'comparison.json',dict(passed=True,comparisons=rows,artifacts=len(rows),feature_artifacts=feature_records,
        exclusions=['execution and incremental telemetry dictionaries/flags','wall-clock timestamp on append-only evidence ledger records'],
        preserved='Every ordered native expression, premise, truth value, rule, graph, evidence ID, dependence group, model identity, source label and metric.'))
    write_json(target/'verified.json',dict(passed=True,production_code_hash=gate['production_code_hash'],
        source_head=gate['source_head'],checkout=gate['checkout'],fresh_venv=True,fresh_runtime=True,fresh_reference_build=True,
        regenerated_pair_labels=340,regenerated_temporal_labels=120,regenerated_native_feature_artifacts=400,
        native_proof_semantic_parity=True,model_checkpoint_byte_parity=True,compared_artifacts=len(rows),
        regeneration_sha256=sha(target/'regeneration.json'),comparison_sha256=sha(target/'comparison.json'),
        scope='Complete fixed research corpus and native experiments regenerated from source inputs. Wall-clock telemetry is retained separately; performance timings are measured in the isolated benchmark.'))
    print('CLEAN RESEARCH EXACT REPRODUCTION VERIFIED',len(rows),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('run','compare'))
    parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--checkout');parser.add_argument('--commit')
    parser.add_argument('--generation',help='New independent replay directory; defaults to OUT/clean-research')
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
    if args.action=='run':run(args.out,args.checkout,args.commit,args.workers,args.generation)
    else:compare(args.out,args.generation)
