"""Complete reproducible Cycle 4 research delivery, always local."""
import argparse,copy,hashlib,os,subprocess,tempfile,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.evidence import Ledger
from pln_chess.cycle4.model import train
from pln_chess.cycle4.inference import Cycle4Options
from training.cycle4 import generate
from evaluation.cycle4 import evaluate
from evaluation.cycle3 import read_gzip
from evaluation.experiments import fit_calibrator,score_calibration
from scripts.cycle4_baseline import pack

OUT=Path(os.environ.get('C4_OUT',ROOT/'artifacts/cycle4'))

def engine_hash():
    return digest({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for base in ('src','training','evaluation','scripts') for p in sorted((ROOT/base).rglob('*.py'))})

def worker(name,model,dataset,engine,resume):
    runtime=Runtime(timeout=180);reports={}
    frozen=read_json(ROOT/'artifacts/cycle2/dataset.json');old=read_json(ROOT/'artifacts/cycle3/dataset.json')
    jobs=[('frozen',frozen,'heldout-transfer'),('frozen',frozen,'adversarial'),('cycle3',old,'independent-games'),
          ('cycle4',dataset,'validation'),('cycle4',dataset,'structural-combination'),('cycle4',dataset,'independent-games')]
    if name=='C4-full':jobs+=[('cycle3',old,'challenge'),('cycle4',dataset,'translation-control')]
    config=read_json(ROOT/'configs/cycle4.json');options=None
    if name in ('C4-conservative','C4-coverage'):
        confidence,positive,negative=config['threshold_ablations'][name[3:]]
        options=Cycle4Options(min_confidence=confidence,supported_strength=positive,contradicted_strength=negative)
    for prefix,data,split in jobs:
        path=OUT/f'evaluation/{name}-{prefix}-{split}.json.xz';r=None
        if resume and path.exists():
            cached=read_gzip(path)
            if cached.get('engine_hash')==engine and cached['model_version']==model.version and cached['dataset_hash']==data['hash']:r=cached
        if r is None:
            r=evaluate(data,model,split,runtime,options=options,diagnostics=name in ('C3','C4-full'))
            r['engine_hash']=engine;r['execution_context']='Up to three independent model processes; isolated benchmarks run after pool exits.'
            pack(path,r)
        if r['metrics']['incomplete_positions']:raise RuntimeError('Incomplete evaluation '+str(path))
        reports[prefix+'-'+split]={'metrics':r['metrics'],'artifact':str(path.relative_to(OUT)),'model_version':model.version}
        print('EVAL',name,prefix,split,{k:r['metrics'][k] for k in ('precision','recall','abstention_rate','false_positive','false_illegal','self_check_false_legal','exact_move_set_accuracy')},flush=True)
    validation=read_gzip(OUT/f'evaluation/{name}-cycle4-validation.json.xz');mapping=fit_calibrator(validation)
    calibration={split:score_calibration(read_gzip(OUT/f'evaluation/{name}-cycle4-{split}.json.xz'),mapping) for split in ('structural-combination','independent-games')}
    return name,reports,calibration

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');parser.add_argument('--skip-baseline',action='store_true');parser.add_argument('--skip-tests',action='store_true')
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True);started=time.time();rt=Runtime(timeout=300)
    if not args.skip_baseline:
        from scripts.cycle4_baseline import main as baseline
        baseline()
    from evaluation.cycle4_native import audit
    audit(OUT/'native-probes/audit.json')
    dataset=generate(OUT/'datasets/dataset.json');models={'C3':Model.load(ROOT/'artifacts/cycle3/C3-full-model.json',rt)}
    for name,options in [('C4-full',{}),('C4-no-dependence',{'variant':'C4-no-dependence','dependence_aware':False})]:
        with tempfile.TemporaryDirectory(prefix='pln-c4-train-') as tmp:
            ledger=Path(tmp)/'evidence.jsonl';model=train(dataset['examples'],OUT/f'model/{name}.json',options,rt,ledger)
            # Timestamps are operational metadata; evidence IDs and payloads deterministically replay.
            pack(OUT/f'model/{name}-evidence.json.xz',Ledger(ledger).records())
        models[name]=model;print('TRAIN',name,model.version,len(model.hypotheses),flush=True)
    for name in ('C4-observations','C4-no-exposure','C4-no-induction'):
        model=copy.deepcopy(models['C4-full']);model.variant=name;model.export(OUT/f'model/{name}.json');models[name]=model
    for name in ('C4-conservative','C4-coverage'):models[name]=models['C4-full']
    engine=engine_hash();reports={};calibration={}
    # No-induction is an explicit equivalence control: production induction is disabled.
    with ProcessPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(worker,name,m,dataset,engine,args.resume) for name,m in models.items() if name!='C4-no-induction']
        for future in as_completed(futures):
            name,result,cal=future.result();reports[name]=result;calibration[name]=cal
    reports['C4-no-induction']=copy.deepcopy(reports['C4-full'])
    for r in reports['C4-no-induction'].values():r['equivalence_control']='C4-full has no induction rules. Identical inference program and data; alias, not an independent run.'
    write_json(OUT/'comparison.json',reports);write_json(OUT/'calibration.json',calibration)
    from evaluation.cycle4_research import research
    research(dataset,models,rt,OUT)
    if not args.skip_tests:
        tests=subprocess.run([str(ROOT/'.venv/bin/pytest'),'-q'],cwd=ROOT,capture_output=True,text=True)
        (OUT/'pytest.txt').write_text(tests.stdout+tests.stderr);print(tests.stdout,flush=True)
        if tests.returncode:raise RuntimeError('Test suite failed')
    write_json(OUT/'run.json',{'dataset_hash':dataset['hash'],'models':{k:m.version for k,m in models.items()},'runtime':rt.manifest,
                              'engine_hash':engine,'elapsed_seconds':time.time()-started,'command':'bash scripts/cycle4_reproduce.sh'})
    if not args.skip_tests:
        from evaluation.cycle4_reporting import report
        report(OUT)
    print('CYCLE 4 COMPLETE',flush=True)

if __name__=='__main__':main()
