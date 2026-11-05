"""Reconstruct the complete local Cycle 5 experiment package from locked inputs."""
import argparse,copy,hashlib,os,subprocess,tempfile,time,resource
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.evidence import Ledger
from pln_chess.cycle5.model import train
from pln_chess.cycle5.inference import Cycle5Options
from training.cycle5 import generate
from evaluation.cycle4 import evaluate
from evaluation.cycle3 import read_gzip
from evaluation.experiments import summarize,fit_calibrator,score_calibration
from scripts.cycle4_baseline import pack
from scripts.cycle5_baseline import SPLITS

OUT=Path(os.environ.get('C5_OUT',ROOT/'artifacts/cycle5'))

def engine_hash():
    return digest({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in ('src','training','evaluation','scripts') for p in sorted((ROOT/base).rglob('*.py'))})

def worker(name,model,dataset,engine,resume):
    runtime=Runtime(timeout=180);results={}
    jobs=[(name,read_json(ROOT/f'artifacts/{path}/dataset.json'),split) for name,path,split in SPLITS]
    jobs += [('cycle5-'+s,dataset,s) for s in ('validation','combination-holdout','structural-holdout','independent-games')]
    for key,data,split in jobs:
        path=OUT/f'evaluation/{name}-{key}.json.xz';report=None
        if name=='C4' and key in dict((s[0],None) for s in SPLITS):report=read_gzip(OUT/f'baseline/{key}.json.xz')
        if report is None and resume and path.exists():
            existing=read_gzip(path)
            if existing.get('engine_hash')==engine and existing['model_version']==model.version and existing['dataset_hash']==data['hash']:report=existing
        if report is None:report=evaluate(data,model,split,runtime,diagnostics=name=='C5-full')
        report['metrics']['in_board_only']=summarize([r for r in report['rows'] if r['destination_exists']],report['positions'])
        report['metrics']['per_family']={f:summarize([r for r in report['rows'] if r['family']==f],[]) for f in sorted({r['family'] for r in report['rows']})}
        report['engine_hash']=engine;report['execution_context']='Up to three independent research processes; performance corpus measured separately after workers finish.'
        pack(path,report)
        results[key]={'metrics':report['metrics'],'model_version':model.version,'dataset_hash':data['hash'],'artifact':str(path.relative_to(OUT))}
        print('EVAL',name,key,{k:report['metrics'][k] for k in ('candidates','true_positive','true_negative','unknown','false_positive','false_illegal','incomplete','recall','exact_move_set_accuracy')},flush=True)
        if report['metrics']['incomplete']:raise RuntimeError('Incomplete evaluation '+str(path))
    validation=read_gzip(OUT/f'evaluation/{name}-cycle5-validation.json.xz');cal=fit_calibrator(validation)
    calibration={s:score_calibration(read_gzip(OUT/f'evaluation/{name}-cycle5-{s}.json.xz'),cal) for s in ('combination-holdout','structural-holdout','independent-games')}
    return name,results,calibration

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');parser.add_argument('--skip-baseline',action='store_true');parser.add_argument('--skip-tests',action='store_true')
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True);started=time.time();runtime=Runtime(timeout=300)
    if not args.skip_baseline:
        from scripts.cycle5_baseline import main as baseline
        baseline(OUT)
    from evaluation.cycle5_native import audit
    audit(OUT/'native-probes/audit.json')
    dataset=generate(runtime,OUT/'datasets/dataset.json');base=Model.load(ROOT/'artifacts/cycle4/model/C4-full.json',runtime)
    with tempfile.TemporaryDirectory(prefix='pln-c5-train-') as tmp:
        ledger=Path(tmp)/'evidence.jsonl';model=train(dataset['examples'],base,runtime,ledger);model.export(OUT/'model/C5-full.json')
        pack(OUT/'model/evidence.json.xz',Ledger(ledger).records())
    models={'C4':base,'C5-full':model}
    for name in ('C5-abstract-only','C5-no-new-negatives'):
        m=copy.deepcopy(model);m.variant=name;m.export(OUT/f'model/{name}.json');models[name]=m
    print('TRAIN',model.version,len(model.hypotheses),flush=True)
    engine=engine_hash();results={};calibration={}
    with ProcessPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(worker,name,m,dataset,engine,args.resume) for name,m in models.items()]
        for future in as_completed(jobs):
            name,r,c=future.result();results[name]=r;calibration[name]=c
    write_json(OUT/'comparison.json',results);write_json(OUT/'calibration.json',calibration)
    # Display-only confidence curves: the detection floor remains .25. Raising
    # confidence can remove support, never create an unsupported positive proof.
    report=read_gzip(OUT/'evaluation/C5-full-cycle5-independent-games.json.xz');curves=[]
    for threshold in read_json(ROOT/'configs/cycle5.json')['confidence_sweep']:
        rows=[{**r,'classification':r['classification'] if r['truth_value']['confidence']>=threshold else 'unknown'} for r in report['rows']]
        curves.append({'min_confidence':threshold,'metrics':summarize(rows,[]),'detection_floor':.25})
    write_json(OUT/'selective-risk.json',curves)
    from evaluation.cycle5_research import research
    research(dataset,model,runtime,OUT)
    positions=read_json(ROOT/'artifacts/cycle4/benchmarks/positions.json')
    positions.append({'id':'c5-new-game','fen':next(p['fen'] for p in dataset['positions'] if p['split']=='independent-games')})
    write_json(OUT/'benchmarks/positions.json',positions)
    for name,path in [('C4',ROOT/'artifacts/cycle4/model/C4-full.json'),('C5',OUT/'model/C5-full.json')]:
        subprocess.run([str(ROOT/'.venv/bin/python'),'-m','evaluation.cycle4_benchmark','--checkpoint',str(path),'--positions',str(OUT/'benchmarks/positions.json'),'--output',str(OUT/f'benchmarks/{name}.json')],check=True)
    if not args.skip_tests:
        tests=subprocess.run([str(ROOT/'.venv/bin/python'),'-m','pytest','-q'],capture_output=True,text=True)
        (OUT/'pytest.txt').write_text(tests.stdout+tests.stderr);print(tests.stdout,flush=True)
        if tests.returncode:raise RuntimeError('Test suite failed')
    write_json(OUT/'run.json',{'runtime':runtime.manifest,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'dataset_hash':dataset['hash'],'model_version':model.version,'engine_hash':engine,'elapsed_seconds':time.time()-started,
        'research_parent_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'tests_executed':not args.skip_tests,'command':'TMPDIR=/dev/shm bash scripts/cycle5_reproduce.sh'})
    from evaluation.cycle5_reporting import report
    report(OUT)
    print('CYCLE 5 COMPLETE',flush=True)

if __name__=='__main__':main()
