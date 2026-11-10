"""Controlled concept dependence, contradictory evidence and retraction arms."""
import argparse
import copy
from pathlib import Path
from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import Runtime
from training.cycle12_learning import train
from training.cycle12_controls import transform


def run(out):
    out=Path(out);assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    data=read_json(out/'datasets/concepts.json');rows=[]
    for concept in data['targets']:
        rows.extend([r for r in data['records'] if r['split']=='train' and r['input']['concept']==concept][:4])
    transformed=[];unsafe=[]
    for record in rows:
        row=copy.deepcopy(record);row['input']=transform(record['input'],'identity-renaming')
        row['input']['source']='declared-identity-transform';row['id']='transform:'+digest(row)
        row['dependence_group']=record['dependence_group']+'/transform';row['transformation_lineage']=[record['dependence_group'],*record['transformation_lineage']]
        transformed.append(row)
        row=copy.deepcopy(record);row['input']['source']='deliberately-unsafe-duplicate';row['id']='unsafe:'+digest(row)
        row['dependence_group']=record['dependence_group']+'/unsafe';row['transformation_lineage']=[];unsafe.append(row)
    shared=copy.deepcopy(rows[0]);shared['reference']['label']=not shared['reference']['label']
    shared['input']['source']='declared-injected-conflict';shared['id']='conflict:'+digest(shared)
    independent=copy.deepcopy(shared);independent['dependence_group']='declared-independent-conflict';independent['transformation_lineage']=[]
    independent['id']='independent:'+digest(independent)
    removed_group=rows[0]['dependence_group'];retracted=[r for r in rows if r['dependence_group']!=removed_group]
    arms=dict(base=rows,duplicate=rows+rows,transformed=rows+transformed,unsafe=rows+unsafe,
        shared_conflict=rows+[shared],independent_conflict=rows+[independent],retracted=retracted)
    runtime=Runtime(timeout=600);models={}
    for name,records in arms.items():
        models[name]=train(records,runtime,out/'learning/dependence'/name,dataset_hash=digest(records),variant='C12-dependence-'+name)
    values=lambda m:{k:(h['positive'],h['negative']) for k,h in m.hypotheses.items()}
    checks=dict(duplicate_values_identical=values(models['base'])==values(models['duplicate']),
        declared_transform_values_identical=values(models['base'])==values(models['transformed']),
        unsafe_duplicates_change_values=values(models['base'])!=values(models['unsafe']),
        shared_conflict_changes_values=values(models['base'])!=values(models['shared_conflict']),
        independent_conflict_changes_values=values(models['base'])!=values(models['independent_conflict']),
        retraction_changes_values=values(models['base'])!=values(models['retracted']),
        retracted_group_absent=all(removed_group not in h['dependence_groups'] for h in models['retracted'].hypotheses.values()))
    write_json(out/'learning/dependence.json',dict(passed=all(checks.values()),checks=checks,
        arms={name:dict(version=model.version,report=model.training_report,values=values(model)) for name,model in models.items()},
        scope='Injected contradictions and deliberately unreported ancestry are controls, not naturally observed reference labels. Correlations outside declared provenance remain an assumption.'))
    assert all(checks.values()),checks
    print('Concept dependence controls passed',checks,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
