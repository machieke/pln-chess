"""Idempotent isolated Cycle 2 delivery; never writes Cycle 1 artifacts."""
import argparse,gzip,hashlib,json,shutil,subprocess,tarfile,tempfile,time
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle2.model import train
from training.cycle2 import generate
from evaluation.cycle2_native import audit
from evaluation.cycle2 import evaluate,baselines,demonstrations,parity_and_benchmark
from evaluation.experiments import fit_calibrator,score_calibration

OUT=ROOT/'artifacts/cycle2'

def source_hash():
    return digest({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for base in ('src/pln_chess/cycle2','evaluation','training') for p in sorted((ROOT/base).rglob('*.py'))})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);started=time.time()
    if not (OUT/'baseline/manifest.json').exists():
        (OUT/'baseline').mkdir(exist_ok=True)
        with tarfile.open(ROOT/'fixtures/cycle1-baseline.tar.gz') as archive:archive.extractall(OUT/'baseline',filter='data')
    baseline=read_json(OUT/'baseline/manifest.json')
    # All frozen inputs remain byte-identical to their initial snapshot.
    for rel,sha in baseline['files'].items():
        assert hashlib.sha256((OUT/'baseline/historical'/rel).read_bytes()).hexdigest()==sha
    if not (ROOT/'artifacts/model.json').exists():
        shutil.copyfile(OUT/'baseline/historical/artifacts/model.json',ROOT/'artifacts/model.json')
        print('Restored absent frozen Cycle 1 checkpoint for unchanged regression tests',flush=True)
    if not (OUT/'upstream-audit.json').exists():
        with tarfile.open(ROOT/'fixtures/cycle2-research.tar.gz') as archive:archive.extractall(OUT,filter='data')
    runtime=Runtime(timeout=300);audit(OUT/'native-probes.json');print('C2 native probes verified',flush=True)
    dataset=generate(OUT/'dataset.json');rows=[r for r in dataset['examples'] if r['split']=='train' and r['training_eligible']]
    engine=source_hash();models={'B0':Model.load(OUT/'baseline/historical/artifacts/model.json',runtime)}
    configs={'B1':{'variant':'hierarchical'},'B2':{'variant':'hierarchical','induction':True},
             'B3':{'variant':'no-obstruction'},'B4':{'variant':'no-exposure'},
             'B5':{'variant':'hierarchical','dependence_aware':False},'B7':{'variant':'no-exact'}}
    for name,options in configs.items():
        with tempfile.TemporaryDirectory(prefix='pln-cycle2-train-') as tmp:
            ledger=Path(tmp)/'evidence.jsonl';model=train(rows,OUT/f'{name}-model.json',options,runtime,ledger)
            if name=='B2':shutil.copyfile(ledger,OUT/'evidence.jsonl')
            else:
                with (OUT/f'{name}-evidence.jsonl.gz').open('wb') as f:
                    with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as z:z.write(ledger.read_bytes())
        models[name]=model;print(name,'trained',len(model.hypotheses),'hypotheses;',len(model.induction),'induced',flush=True)
    reports={};splits=sorted({p['split'] for p in dataset['positions']})
    for name,model in models.items():
        reports[name]={}
        for split in splits:
            path=OUT/f'{name}-{split}.json';report=read_json(path) if args.resume and path.exists() else None
            if not report or report.get('dataset_hash')!=dataset['hash'] or report.get('model_version')!=model.version or report.get('engine_hash')!=engine:
                report=evaluate(dataset,model,split,runtime);report['engine_hash']=engine;write_json(path,report)
            reports[name][split]=report
            print(name,split,{k:report['metrics'][k] for k in ('precision','recall','abstention_rate')},flush=True)
            if any(p['truncated'] for p in report['positions']):raise RuntimeError('Incomplete evaluation '+name+' '+split)
    write_json(OUT/'B6-baselines.json',baselines(dataset))
    calibration={name:score_calibration(result['heldout-transfer'],fit_calibrator(result['validation'])) for name,result in reports.items()}
    write_json(OUT/'calibration.json',calibration)
    parity_and_benchmark(models['B2'],OUT/'benchmark.json');demonstrations(dataset,models['B2'],OUT/'demonstrations.json')
    tests=subprocess.run([str(ROOT/'.venv/bin/pytest'),'-q'],cwd=ROOT,capture_output=True,text=True)
    (OUT/'pytest.txt').write_text(tests.stdout+tests.stderr);print(tests.stdout,flush=True)
    if tests.returncode:raise RuntimeError('Test suite failed; see artifacts/cycle2/pytest.txt')
    write_json(OUT/'run-summary.json',{'baseline_head':baseline['head'],'dataset_hash':dataset['hash'],'seed':dataset['seed'],
               'runtime':runtime.manifest,'engine_hash':engine,'models':{k:m.version for k,m in models.items()},
               'metrics':{k:{s:r['metrics'] for s,r in v.items()} for k,v in reports.items()},'tests':tests.stdout.strip().splitlines()[-1],
               'elapsed_seconds':time.time()-started,'reproduction_command':'bash scripts/cycle2_reproduce.sh','configs':configs})
    from evaluation.cycle2_reporting import report
    report();print('CYCLE 2 DELIVERY VERIFIED',flush=True)

if __name__=='__main__':main()
