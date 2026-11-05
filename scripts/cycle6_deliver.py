"""Reproducible Cycle 6 evaluation/research runner; never pushes or alters old artifacts."""
import argparse,copy,os,subprocess,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cycle6.model import ModeModel
from pln_chess.cycle6.inference import Cycle6Options
from evaluation.cycle6 import evaluate
from evaluation.cycle4 import evaluate as baseline_evaluate
from evaluation.cycle3 import read_gzip
from evaluation.experiments import fit_calibrator,score_calibration
from scripts.cycle4_baseline import pack
from scripts.cycle6_baseline import SPLITS
from scripts.cycle5_deliver import engine_hash
from training.cycle6 import generate

OUT=Path(os.environ.get('C6_OUT',ROOT/'artifacts/cycle6'))
def worker(name,model,data):
    rt=Runtime(timeout=180);reports={}
    jobs=[(key,read_json(ROOT/f'artifacts/{path}/dataset.json'),split) for key,path,split in SPLITS] if model.schema==6 else []
    jobs += [('cycle6-'+s,data,s) for s in ('validation','adversarial','independent-games')]
    for key,d,split in jobs:
        mode='strict' if name=='C6-strict' else 'operational'
        r=evaluate(d,model,split,rt,options=Cycle6Options(mode=mode)) if model.schema==6 else baseline_evaluate(d,model,split,rt,diagnostics=True)
        pack(OUT/f'evaluation/{name}-{key}.json.xz',r)
        reports[key]={'metrics':r['metrics'],'model_version':model.version,'dataset_hash':d['hash'],'artifact':f'evaluation/{name}-{key}.json.xz'}
        print('EVAL',name,key,{k:r['metrics'].get(k) for k in ('candidates','true_positive','true_negative','unknown','false_positive','false_illegal','incomplete','recall','exact_move_set_accuracy')},flush=True)
        if r['metrics']['incomplete']:raise RuntimeError('Incomplete evaluation '+name+' '+key)
    calibration=fit_calibrator(read_gzip(OUT/f'evaluation/{name}-cycle6-validation.json.xz'))
    return name,reports,{s:score_calibration(read_gzip(OUT/f'evaluation/{name}-cycle6-{s}.json.xz'),calibration) for s in ('adversarial','independent-games')}

def evaluations():
    OUT.mkdir(parents=True,exist_ok=True);rt=Runtime();data=generate(OUT/'datasets/dataset.json')
    c5=Model.load(ROOT/'artifacts/cycle5/model/C5-full.json',rt);model=ModeModel.migrate(c5);model.export(OUT/'model/C6-full.json')
    no=copy.deepcopy(model);no.variant='C6-no-new-negatives';no.export(OUT/'model/C6-no-new-negatives.json')
    models={'C6-operational':model,'C6-strict':model,'C6-no-new-negatives':no,'C4':c5.base_model(),'C5':c5}
    results={};cal={}
    with ProcessPoolExecutor(max_workers=2) as pool:
        for f in as_completed([pool.submit(worker,k,m,data) for k,m in models.items()]):
            name,r,c=f.result();results[name]=r;cal[name]=c
            write_json(OUT/'comparison-in-progress.json',results)
    write_json(OUT/'comparison.json',results);write_json(OUT/'calibration.json',cal)
    return data,model

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=('evaluation','research','all'),default='all');a=parser.parse_args();start=time.time()
    if a.stage in ('evaluation','all'):data,model=evaluations()
    else:data=read_json(OUT/'datasets/dataset.json');model=Model.load(OUT/'model/C6-full.json',Runtime())
    if a.stage in ('research','all'):
        from evaluation.cycle6_research import research
        research(data,model,Runtime(timeout=180),OUT)
    write_json(OUT/f'run-{a.stage}.json',{'elapsed_seconds':time.time()-start,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'engine_hash':engine_hash(),'model_version':model.version,'dataset_hash':data['hash']})

if __name__=='__main__':main()
