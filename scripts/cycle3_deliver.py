"""Rebuild the complete feasible Cycle 3 package; never mutates remote state."""
import argparse,copy,hashlib,subprocess,tempfile,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.evidence import Ledger
from pln_chess.cycle3.model import train
from training.cycle3 import generate
from evaluation.cycle3 import evaluate,write_gzip,read_gzip,pack_reports
from evaluation.cycle3_native import audit
from evaluation.experiments import fit_calibrator,score_calibration

OUT=ROOT/'artifacts/cycle3'


def engine_hash():
    return digest({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for base in ('src','training','evaluation') for p in sorted((ROOT/base).rglob('*.py'))})


def evaluate_model(name,model,dataset,frozen,engine,resume):
    """Independent model workers write distinct files; benchmark runs later alone."""
    runtime=Runtime(timeout=180);reports={}
    jobs=[('frozen',frozen,'heldout-transfer'),('frozen',frozen,'adversarial'),('new',dataset,'challenge'),
          ('new',dataset,'independent-games'),('new',dataset,'validation')]
    for prefix,data,split in jobs:
        path=OUT/f'{name}-{prefix}-{split}.json.gz';report=None
        if resume and path.exists():
            cached=read_gzip(path)
            if cached.get('engine_hash')==engine and cached['model_version']==model.version and cached['dataset_hash']==data['hash']:report=cached
        if report is None:
            report=evaluate(data,model,split,runtime);report['engine_hash']=engine
            report['execution_context']='Up to three independent model workers; isolated same-model benchmarks reported separately.'
            write_gzip(path,report)
        if report['metrics']['incomplete_positions']:raise RuntimeError('Incomplete experiment '+str(path))
        reports[prefix+'-'+split]={'artifact':str(path.relative_to(ROOT)),'metrics':report['metrics'],'model_version':model.version}
        print('EVAL',name,prefix,split,{k:report['metrics'][k] for k in ('precision','recall','abstention_rate','self_check_false_legal','exact_move_set_accuracy')},flush=True)
    validation=read_gzip(OUT/f'{name}-new-validation.json.gz');mapping=fit_calibrator(validation)
    calibration={split:score_calibration(read_gzip(OUT/f'{name}-new-{split}.json.gz'),mapping) for split in ('challenge','independent-games')}
    return name,reports,calibration


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');parser.add_argument('--skip-baseline',action='store_true')
    parser.add_argument('--skip-tests',action='store_true');args=parser.parse_args();OUT.mkdir(exist_ok=True)
    started=time.time();runtime=Runtime(timeout=180)
    if not args.skip_baseline:
        from scripts.cycle3_baseline import main as baseline
        baseline()
    audit(OUT/'native-probes.json');dataset=generate(OUT/'dataset.json');frozen=read_json(ROOT/'artifacts/cycle2/dataset.json')
    engine=engine_hash();rows=[r for r in dataset['examples'] if r['split']=='train']
    models={name:Model.load(ROOT/f'artifacts/cycle2/{name}-model.json',runtime) for name in ('B1','B2')}
    models['B0']=Model.load(ROOT/'artifacts/model.json',runtime)
    for name,options in [('C3-full',{'induction':True}),('no-obstruction',{'variant':'no-obstruction','induction':True}),
                         ('no-dependence',{'dependence_aware':False,'induction':True}),('exact-context-only',{'variant':'exact-context-only'})]:
        with tempfile.TemporaryDirectory(prefix='pln-cycle3-train-') as tmp:
            ledger=Path(tmp)/'evidence.jsonl';model=train(rows,OUT/f'{name}-model.json',options,runtime,ledger)
            write_gzip(OUT/f'{name}-evidence.json.gz',Ledger(ledger).records())
        models[name]=model;print('TRAIN',name,len(model.hypotheses),len(model.induction),flush=True)
    for name,variant,induction in [('C3-local','C3-local',False),('C3-exposure','C3-exposure',False),
                                   ('C3-induction','C3-induction',True),('no-exposure','no-exposure',True),
                                   ('no-induction','C3-full',False),('no-arbitration','no-arbitration',True)]:
        model=copy.deepcopy(models['C3-full']);model.variant=variant
        if not induction:model.induction={}
        model.training_report={**model.training_report,'parent_model':models['C3-full'].version,
                               'controlled_variant':name,'induction_enabled':induction}
        model.export(OUT/f'{name}-model.json');models[name]=model
    reports={};calibration={}
    with ProcessPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(evaluate_model,name,model,dataset,frozen,engine,args.resume) for name,model in models.items()]
        for job in as_completed(jobs):
            name,model_reports,model_calibration=job.result();reports[name]=model_reports;calibration[name]=model_calibration
    for split in ('paired-color-flip','paired-reflection'):
        report=evaluate(dataset,models['C3-full'],split,runtime,OUT/f'C3-full-new-{split}.json.gz')
        reports['C3-full']['new-'+split]={'metrics':report['metrics']}
    write_json(OUT/'comparison.json',reports);write_json(OUT/'calibration.json',calibration)
    from evaluation.cycle3_research import research
    research(dataset,models,runtime)
    if not args.skip_tests:
        tests=subprocess.run([str(ROOT/'.venv/bin/pytest'),'-q'],cwd=ROOT,capture_output=True,text=True)
        (OUT/'pytest.txt').write_text(tests.stdout+tests.stderr);print(tests.stdout,flush=True)
        if tests.returncode:raise RuntimeError('Test suite failed')
    write_json(OUT/'run.json',{'dataset_hash':dataset['hash'],'runtime':runtime.manifest,'engine_hash':engine,
                              'models':{k:m.version for k,m in models.items()},'elapsed_seconds':time.time()-started,
                              'command':'bash scripts/cycle3_reproduce.sh'})
    pack_reports(OUT)
    from evaluation.cycle3_reporting import report
    report();print('CYCLE 3 COMPLETE',flush=True)

if __name__=='__main__':main()
