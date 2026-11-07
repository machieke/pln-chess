"""Cycle 7 offline experiments; original evidence is read-only."""
import argparse
import copy
import os
from dataclasses import replace
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import Cycle7Options
from evaluation.cycle7 import evaluate
from evaluation.cycle6 import evaluate as baseline_evaluate
from pln_chess.cycle6.inference import Cycle6Options
from scripts.cycle7_baseline import SPLITS
from training.cycle7 import generate, select, train, structural_audit
from evaluation.cycle7_io import pack

OUT=Path(os.environ.get('C7_OUT',ROOT/'artifacts/cycle7'))

def training():
    rt=Runtime(timeout=600);data=generate(OUT/'datasets/dataset.json')
    source=Model.load(ROOT/'artifacts/cycle6/model/C6-full.json',rt);frozen=BackoffModel.migrate(source);frozen.export(OUT/'model/C7-frozen.json')
    rows,selection=select(data,frozen);write_json(OUT/'training/selection.json',selection)
    pack(OUT/'training/examples.json.xz',rows);write_json(OUT/'datasets/structural-audit.json',structural_audit(data))
    for budget in read_json(ROOT/'configs/cycle7.json')['independent_group_budgets']:
        model=train(frozen,rows,rt,OUT,budget);print('TRAIN',model.variant,model.training_report,flush=True)
    model=train(frozen,rows,rt,OUT,8,False);print('TRAIN',model.variant,model.training_report,flush=True)

def evaluate_arm(name,model,options,jobs):
    options=replace(options,max_native_invocations=read_json(ROOT/'configs/cycle7.json')['evaluation_max_native_invocations'])
    rt=Runtime(timeout=180);summary={}
    for key,data,split in jobs:
        r=evaluate(data,model,split,rt,options=options)
        path=OUT/f'evaluation/{name}-{key}.json.xz';pack(path,r)
        summary[key]={'metrics':r['metrics'],'model_version':model.version,'dataset_hash':data['hash'],'artifact':str(path.relative_to(OUT)),
            'positions':len(r['positions']),'proof_coverage':{s:sum(x['proof_status']==s for x in r['rows']) for s in sorted({x['proof_status'] for x in r['rows']})}}
        print('EVAL',name,key,{k:r['metrics'][k] for k in ('recall','exact_move_set_accuracy','false_positive','false_illegal','self_check_false_legal','unknown','incomplete')},flush=True)
        if r['metrics']['incomplete']:raise RuntimeError('Incomplete evaluation '+name+' '+key)
        write_json(OUT/f'evaluation/{name}-summary.json',summary)
    return summary

def jobs(independent=False):
    selected=[s for s in SPLITS if not independent or s[0]=='cycle6-independent-games']
    return [(k,read_json(ROOT/f'artifacts/{p}/dataset.json'),s) for k,p,s in selected]+[('cycle7-independent-games',read_json(OUT/'datasets/dataset.json'),'independent-games')]

def evaluations(stage):
    rt=Runtime(timeout=180)
    if stage=='pilot':
        for budget in (0,2,4,8):
            model=BackoffModel.load(OUT/f'model/C7-learned-{budget}.json',rt)
            evaluate_arm(model.variant,model,Cycle7Options(mode='operational'),jobs(True))
    elif stage.startswith('matrix'):
        frozen=BackoffModel.load(OUT/'model/C7-frozen.json',rt)
        if stage in ('matrix','matrix-frozen'):
            evaluate_arm('C7-frozen',frozen,Cycle7Options(mode='operational'),jobs())
        if stage in ('matrix','matrix-strict'):
            evaluate_arm('C7-strict',frozen,Cycle7Options(mode='strict'),jobs())
            evaluate_arm('C7-experimental',frozen,Cycle7Options(mode='experimental'),jobs(True))
        # Frozen C6 on the new family split is an actual run, not inferred from C7.
        if stage in ('matrix','matrix-baselines'):
            data=read_json(OUT/'datasets/dataset.json')
            for mode in ('operational','strict','experimental'):
                r=baseline_evaluate(data,frozen.source_model(),'independent-games',rt,options=Cycle6Options(mode=mode))
                pack(OUT/f'evaluation/C6-{mode}-cycle7-independent-games.json.xz',r)
        if stage in ('matrix','matrix-learned'):
            model=BackoffModel.load(OUT/'model/C7-learned-8.json',rt)
            evaluate_arm('C7-learned-8-locked',model,Cycle7Options(mode='operational'),jobs())
    elif stage=='ablations':
        model=BackoffModel.load(OUT/'model/C7-learned-8.json',rt)
        arms=[('no-backoff',model,Cycle7Options(mode='operational',backoff=False)),
              ('no-attack-exposure',model,Cycle7Options(mode='operational',suppress_families=('exposure',))),
              # Game suites have FEN-only metadata and no supplied history.
              # The explicit no-history arm is therefore a measured null control;
              # event-backed temporal effects are tested in the causal suite.
              ('no-temporal',model,Cycle7Options(mode='operational',temporal_mode='fen-only',temporal_evidence=None)),
              ('no-dependence',BackoffModel.load(OUT/'model/C7-learned-8-no-dependence.json',rt),Cycle7Options(mode='operational',dependence_aware=False)),
              ('no-new-training',BackoffModel.load(OUT/'model/C7-learned-0.json',rt),Cycle7Options(mode='operational'))]
        no=copy.deepcopy(model);no.source['variant']='C6-no-new-negatives'
        # Both old and new negative-premise observations are removed in this
        # destructive ablation, which is never eligible for promotion.
        no.source['source']['hypotheses']={k:h for k,h in no.source['source']['hypotheses'].items() if h['family']=='geometry'}
        no.source['source']['base']['hypotheses']={k:h for k,h in no.source['source']['base']['hypotheses'].items() if h['target'] not in ('Bridge','Attack','Obstruction','DestinationConflict','BoundaryConflict')}
        arms.append(('no-learned-negatives',no,Cycle7Options(mode='operational')))
        for name,m,o in arms:evaluate_arm('ablation-'+name,m,o,jobs(True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=('training','pilot','matrix','matrix-frozen','matrix-strict','matrix-learned','matrix-baselines','ablations'),required=True);a=p.parse_args()
    if a.stage=='training':training()
    else:evaluations(a.stage)
