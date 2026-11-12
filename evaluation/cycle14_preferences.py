"""Registered model fitting and a freeze barrier before final predictions."""
import argparse
import copy
from pathlib import Path
import shutil

from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle13.model import PreferenceModel as FrozenModel
from pln_chess.cycle13.inference import infer_preferences as infer_frozen
from pln_chess.cycle14.model import PreferenceModel
from pln_chess.cycle14.inference import infer_preferences
from pln_chess.cycle14.ontology import ABSTRACTIONS,omit_context
from training.cycle14_features import training_records
from training.cycle14_learning import train
from training.cycle14_labels import atomic_json
from evaluation.cycle14_metrics import counts,clustered_intervals,fit_calibration,calibration_metrics
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


def data_identity(records):
    return digest([dict(id=r['id'],packet=r['packet']['id'],label=r['label'],reference=r['reference_evidence_id'],
        split=r['split'],ancestry=r['dependence_group'],models=r['model_versions']) for r in records])


def predict(records,model,runtime):
    predictions=[];native=infer_preferences if isinstance(model,PreferenceModel) else infer_frozen
    for start in range(0,len(records),64):
        selected=records[start:start+64]
        packets=[r['packet'] if isinstance(model,PreferenceModel) else r['packet']['base'] for r in selected]
        result=native(packets,model,runtime=runtime,options=FieldOptions())
        if result['execution']['truncated']:raise ValueError('Registered preference evaluation truncated')
        predictions.extend(dict(id=r['id'],label=r['label'],split=r['split'],source_game=r['source_game'],
            dependence_group=r['dependence_group'],source_collection=r['source'].get('collection','unspecified'),
            horizon=r['temporal_context']['horizon'],reference_evidence_id=r['reference_evidence_id'],
            prediction=p) for r,p in zip(selected,result['comparisons']))
    return predictions


def fit(out):
    out=Path(out).resolve();runtime=Runtime();new=training_records(out);old=training_records(out,labels='old')
    revised_train=[r for r in new if r['split']=='train'];old_train=[r for r in old if r['split']=='train']
    old_ids={r['id'] for r in old_train};historical=[r for r in revised_train if r['id'] in old_ids]
    development=[r for r in new if r['split']=='development'];registry={}

    def fitted(name,records,abstraction='c13-relational',concepts=False,dependence=True):
        model=train(records,runtime,out/'learning'/name,dataset_hash=data_identity(records),abstraction=abstraction,
            concepts=concepts,dependence=dependence,baseline_root=out,variant='C14-'+name)
        path=out/'model'/(name+'.json');path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():assert sha(path)==sha(out/'learning'/name/'checkpoint.json')
        else:shutil.copy2(out/'learning'/name/'checkpoint.json',path)
        registry[name]=dict(path=str(path.relative_to(out)),version=model.version,sha256=sha(path),
            training_cases=len(records),training_identity=data_identity(records),abstraction=abstraction,
            concepts=concepts,dependence=dependence,final_labels_used=False)
        print('C14 MODEL',name,len(records),model.training_report['hypotheses'],flush=True)
        return model

    frozen=ROOT/'artifacts/cycle13/model/C13-preference-relational.json'
    registry['frozen-c13']=dict(path='artifacts/cycle13/model/C13-preference-relational.json',historical=True,version=FrozenModel.load(frozen,runtime).version,
        sha256=sha(frozen),training_cases=222,abstraction='relational',concepts=False,dependence=True,final_labels_used=False)
    fitted('old-labels-old-descriptor',old_train)
    fitted('revised-labels-historical-only',historical)
    candidates=[]
    for index,abstraction in enumerate(ABSTRACTIONS):
        name='immediate-'+abstraction;model=fitted(name,revised_train,abstraction)
        rows=predict(development,model,runtime);measurement=counts(rows)
        pack(out/'development'/(name+'.json.xz'),rows)
        candidates.append(dict(name=name,abstraction=abstraction,index=index,counts=measurement))
    winner=min(candidates,key=lambda c:(-(c['counts']['correct_answer_yield'] or 0),
        -(c['counts']['answered_accuracy'] if c['counts']['answered_accuracy'] is not None else -1),c['index']))
    selected=winner['abstraction']
    atomic_json(out/'development/selection.json',dict(selected=winner,candidates=candidates,
        rule='Development correct-answer yield, then answered accuracy, then registered simpler descriptor',
        development_ids=sorted(r['id'] for r in development),final_predictions_observed=False))
    fitted('immediate-selected-concepts',revised_train,selected,concepts=True)
    fitted('source-family-heldout',[r for r in revised_train if r['source'].get('collection')!='tcec-season26-divisionp'],selected)
    # Dependent copies inherit every ancestry key; this is a registered diagnostic.
    copies=historical+[dict(r,id=r['id']+'/dependent-copy') for r in historical]
    fitted('historical-dependent-repeat',copies)
    fitted('historical-unsafe-repeat',copies,dependence=False)
    temporal=training_records(out,temporal=True);temporal_train=[r for r in temporal if r['split']=='train']
    fitted('temporal-old-descriptor',temporal_train)
    fitted('temporal-selected',temporal_train,selected)
    fitted('temporal-selected-concepts',temporal_train,selected,concepts=True)
    temporal_old=training_records(out,temporal=True,labels='old')
    temporal_old=[r for r in temporal_old if r['split']=='train'];temporal_ids={r['id'] for r in temporal_old}
    fitted('temporal-old-labels',temporal_old)
    fitted('temporal-revised-historical',[r for r in temporal_train if r['id'] in temporal_ids])
    omitted=[dict(r,id=r['id']+'/context-omitted',packet=omit_context(r['packet'])) for r in temporal_train if r['temporal_context']['horizon']>1]
    fitted('temporal-omission-robust',temporal_train+omitted,selected)
    payload=dict(schema='c14-model-registry-v1',models=registry,selected_descriptor=selected,
        primary_immediate='immediate-'+selected,primary_temporal='temporal-selected',
        fit_input_hash=data_identity(temporal),selection_sha256=sha(out/'development/selection.json'),
        test_predictions_run=False,legal_checkpoint_modified=False,automatic_move_selection=False)
    payload['hash']=digest(payload);atomic_json(out/'model/registry.json',payload)


def load_model(out,entry,runtime):
    path=(ROOT if entry.get('historical') else Path(out))/entry['path']
    if sha(path)!=entry['sha256']:raise ValueError('Frozen model bytes changed')
    kind=PreferenceModel if read_json(path)['schema']=='relative-preference-model-v14' else FrozenModel
    model=kind.load(path,runtime);assert model.version==entry['version'];return model


def freeze(out):
    out=Path(out).resolve();registry=read_json(out/'model/registry.json');runtime=Runtime()
    all_records=training_records(out,temporal=True);mappings={}
    for name,entry in registry['models'].items():
        records=[r for r in all_records if r['split']=='calibration' and (name.startswith('temporal-') or r['temporal_context']['horizon']==1)]
        model=load_model(out,entry,runtime);rows=predict(records,model,runtime)
        pack(out/'calibration'/name/'native-predictions.json.xz',rows)
        mappings[name]={}
        for horizon in sorted({r['horizon'] for r in rows}):
            selected=[r for r in rows if r['horizon']==horizon];mapping=fit_calibration(selected)
            path=out/'calibration'/name/f'mapping-h{horizon}.json';atomic_json(path,mapping)
            mappings[name][str(horizon)]=dict(path=str(path.relative_to(out)),sha256=sha(path),mapping_hash=mapping['hash'],N=len(selected))
    freeze=dict(schema='c14-final-evaluation-freeze-v1',registry_sha256=sha(out/'model/registry.json'),
        models=registry['models'],calibration=mappings,selected_descriptor=registry['selected_descriptor'],
        thresholds=read_json(ROOT/'configs/cycle14.json')['thresholds'],
        partitions_sha256=sha(out/'datasets/partitions.json'),reversal_registration_sha256=sha(out/'datasets/reversal-registration.json'),
        source_sha256=sha(__file__),final_predictions_observed=False,
        scope='No model, threshold, descriptor or calibration revision after final-test execution.')
    freeze['hash']=digest(freeze);atomic_json(out/'evaluation-freeze.json',freeze)


def evaluate(out):
    out=Path(out).resolve();freeze=read_json(out/'evaluation-freeze.json');runtime=Runtime()
    assert freeze['hash']==digest({k:v for k,v in freeze.items() if k!='hash'})
    assert freeze['source_sha256']==sha(__file__),'Use the frozen evaluation driver'
    all_records=training_records(out,temporal=True);results={}
    for name,entry in freeze['models'].items():
        model=load_model(out,entry,runtime)
        records=[r for r in all_records if r['split'] in ('test','source-holdout','historical-test','historical-calibration')
            and (name.startswith('temporal-') or r['temporal_context']['horizon']==1)]
        rows=predict(records,model,runtime);pack(out/'evaluation'/name/'native-predictions.json.xz',rows)
        summaries=[]
        for split in sorted({r['split'] for r in rows}):
            for horizon in sorted({r['horizon'] for r in rows if r['split']==split}):
                selected=[r for r in rows if r['split']==split and r['horizon']==horizon]
                mapping=read_json(out/freeze['calibration'][name][str(horizon)]['path'])
                summaries.append(dict(split=split,horizon=horizon,counts=counts(selected),
                    intervals=clustered_intervals(selected),calibration=calibration_metrics(selected,mapping)))
        source_summaries=[dict(collection=collection,horizon=horizon,counts=counts([r for r in rows if r['split'] in ('test','source-holdout') and r['source_collection']==collection and r['horizon']==horizon]))
            for collection in sorted({r['source_collection'] for r in rows}) for horizon in sorted({r['horizon'] for r in rows})]
        result=dict(model_version=model.version,freeze_hash=freeze['hash'],cohorts=summaries,sources=source_summaries,
            final_model_selection=False,unknown_references_scored=False)
        atomic_json(out/'evaluation'/name/'summary.json',result);results[name]=result
        print('C14 FINAL EVALUATION',name,flush=True)
    atomic_json(out/'evaluation/summary.json',dict(freeze_hash=freeze['hash'],models=results))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('fit','freeze','test'))
    parser.add_argument('--out',default='artifacts/cycle14');args=parser.parse_args()
    {'fit':fit,'freeze':freeze,'test':evaluate}[args.stage](args.out)
