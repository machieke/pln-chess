"""Prediction effects of dependence policies on a fixed, small external panel."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import Cycle8Options
from evaluation.cycle8 import evaluate
from scripts.cycle9_baseline import sha


def worker(job):
    out,name,data,checkpoint=job;out=Path(out);rt=Runtime(timeout=300)
    model=PromotionModel.load(checkpoint,rt);path=out/f'dependence/evaluation/{name}.json.xz'
    report=evaluate(data,model,'external-test',rt,Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180),path)
    for row in report['rows']:
        assert digest([report['native_proof_dag'][i] for i in row['proof_refs']])==row['proof_id']
    return name,dict(model_version=model.version,metrics=report['metrics'],checkpoint_bytes=Path(checkpoint).stat().st_size,
        artifact=str(path.relative_to(out)),sha256=sha(path),native_proofs_verified=True,
        row_values=[dict(fixture=r['fixture'],move=r['move'],classification=r['classification'],truth_value=r['truth_value']) for r in report['rows']])


def run(out):
    out=Path(out).resolve();data=read_json(out/'datasets/dataset.json');positions=[]
    for source in sorted({g['source_collection'] for g in data['games']}):
        games=sorted(g['id'] for g in data['games'] if g['split']=='external-test' and g['source_collection']==source)[:4]
        for game in games:positions.append(min((f for f in data['positions'] if f.get('source_game')==game),key=lambda f:digest(f['id'])))
    assert len(positions)==12 and len({p['source_game'] for p in positions})==12
    selected={**data,'positions':positions};models={'frozen':ROOT/'artifacts/cycle8/model/C8-promotion-relative.json'}
    models.update({name:out/f'dependence/model/dependence-{name}.json' for name in
        ('base','duplicates','transformed','shared-conflict','independent-conflict','unsafe','game-only')})
    with ProcessPoolExecutor(max_workers=3) as pool:
        results=dict(pool.map(worker,[(str(out),name,selected,str(path)) for name,path in models.items()]))
    assert results['base']['row_values']==results['duplicates']['row_values']==results['transformed']['row_values']
    for name,record in results.items():
        reference=results['frozen']['row_values']
        record['changed_classifications_from_frozen']=sum(a['classification']!=b['classification'] for a,b in zip(reference,record['row_values'],strict=True))
    write_json(out/'dependence/predictions.json',dict(passed=True,positions=12,games=12,fixtures=[p['id'] for p in positions],
        selection='First four lexicographic final-test game IDs per source, one content-hash-selected position per game; no prediction-based selection.',
        models=results,duplicate_and_transformed_predictions_equal=True,
        limits='Small descriptive panel, not a model selection or promotion test. Full final-test evaluation is reported separately for the registered small and large adaptations. Contradictory labels are explicitly synthetic interventions.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
