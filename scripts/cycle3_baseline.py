"""Read-only baseline reproduction; outputs confined to artifacts/cycle3."""
import hashlib,platform,subprocess,sys
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from evaluation.cycle3 import evaluate
from evaluation.cycle2 import parity_and_benchmark


def main():
    out=ROOT/'artifacts/cycle3';out.mkdir(exist_ok=True)
    start='f80b27dc41e591c90ed7456f3730fb5c0ea5d28e'
    subprocess.run(['git','cat-file','-e',start+'^{commit}'],check=True)
    frozen={}
    for rel in subprocess.check_output(['git','ls-tree','-r','--name-only',start],text=True).splitlines():
        if rel.startswith(('artifacts/','fixtures/','vendor/','configs/','src/','tests/')):
            frozen[rel]=hashlib.sha256(subprocess.check_output(['git','show',start+':'+rel])).hexdigest()
    runtime=Runtime(timeout=180);dataset=read_json(ROOT/'artifacts/cycle2/dataset.json')
    receipt={'starting_commit':start,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             'initial_status':subprocess.check_output(['git','status','--short'],text=True),'python':sys.version,
             'hardware':platform.uname()._asdict(),'cpu':next(s for s in (ROOT/'/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),
             'runtime':runtime.manifest,'frozen_files':frozen,'frozen_files_source':'Git objects at the expected starting commit; source extensions are allowed, baseline artifacts must stay unchanged.',
             'dataset_hash':dataset['hash'],
             'command':'TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle3_baseline','results':{}}
    if not (out/'baseline-initial.json').exists():write_json(out/'baseline-initial.json',receipt)
    for name in ('B1','B2'):
        model=Model.load(ROOT/f'artifacts/cycle2/{name}-model.json',runtime);receipt['results'][name]={}
        for split in ('heldout-transfer','adversarial'):
            report=evaluate(dataset,model,split,runtime,out/f'baseline-{name}-{split}.json.gz')
            original=read_json(ROOT/f'artifacts/cycle2/{name}-{split}.json')
            fields=('precision','recall','f1','abstention_rate','exact_move_set_accuracy','self_check_false_legal','false_positive')
            parity=all(report['metrics'][k]==original['metrics'][k] for k in fields)
            old={(r['fixture'],r['move']):(r['classification'],r['truth_value']) for r in original['rows']}
            parity=parity and all(old[(r['fixture'],r['move'])]==(r['classification'],r['truth_value']) for r in report['rows'])
            receipt['results'][name][split]={'metrics':report['metrics'],'candidate_tv_class_parity':parity,
                'source':f'artifacts/cycle2/{name}-{split}.json','split_ids':[p['fixture'] for p in report['positions']]}
            print(name,split,parity,{k:report['metrics'][k] for k in fields},flush=True)
    receipt['benchmark']=parity_and_benchmark(model,out/'baseline-benchmark.json')
    write_json(out/'baseline.json',receipt)
    print('BASELINE COMPLETE',flush=True)

if __name__=='__main__':main()
