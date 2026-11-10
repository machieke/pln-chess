"""Held-out limited concept conditionals, controls and explicit proof limits."""
import argparse
from collections import Counter, defaultdict
import copy
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.pln import Runtime
from evaluation.cycle7_io import pack


def metrics(rows):
    counts=Counter()
    for row in rows:
        label=row['reference']['label'];prediction=row['result']['classification']
        if prediction=='supported':counts['tp' if label else 'fp']+=1
        elif prediction=='contradicted':counts['fn' if label else 'tn']+=1
        else:
            counts['abstention']+=1;counts['abstained_positive' if label else 'abstained_negative']+=1
            if prediction=='incomplete':counts['incomplete']+=1
    n=len(rows);positive=sum(r['reference']['label'] for r in rows);negative=n-positive
    precision=counts['tp']/(counts['tp']+counts['fp']) if counts['tp']+counts['fp'] else None
    recall=counts['tp']/positive if positive else None
    denominator=2*counts['tp']+counts['fp']+counts['fn']+counts['abstained_positive']
    f1=2*counts['tp']/denominator if denominator else None
    return dict(n=n,positive=positive,negative=negative,**{k:counts[k] for k in
        ('tp','fp','tn','fn','abstention','abstained_positive','abstained_negative','incomplete')},
        precision=precision,recall_including_abstention=recall,f1=f1,
        false_positive_rate=counts['fp']/negative if negative else None,
        false_negative_rate_supported_only=counts['fn']/positive if positive else None,
        missed_positive_rate_including_abstention=(positive-counts['tp'])/positive if positive else None,
        abstention_rate=counts['abstention']/n if n else None,
        native_conditional_proofs=sum(r['result']['conditional_proof_complete'] for r in rows),
        complete_joint_concept_proofs=sum(r['result']['joint_proof_complete'] for r in rows))


def run(out):
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle12.ontology import observe_concept
    from pln_chess.cycle12.inference import infer_concepts, ConceptSession
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions
    out=Path(out)
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    assert read_json(out/'datasets/audit.json')['passed']
    data=read_json(out/'datasets/concepts.json');controls=read_json(out/'datasets/concept-controls.json')
    runtime=Runtime(timeout=600);options=FieldOptions(timeout_seconds=600)
    model=ConceptModel.load(out/'model/C12-concept-trained.json',runtime)
    empty=ConceptModel.load(out/'model/C12-concept-empty.json',runtime)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    no_field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-empty.json',runtime)
    session=ConceptSession(runtime)

    def query(case,checkpoint=model,field_checkpoint=field):
        result=infer_concepts([case],checkpoint,field_checkpoint,options=options,runtime=runtime,session=session)['concepts'][0]
        assert result['proof_id']==digest(result['proof_trace'])
        assert result['joint_proof_complete'] is False
        for component in result['field_relations']:
            assert component['proof_id']==digest(component['proof_trace'])
        return result

    rows=[]
    # Calibration is reported with the same preregistered thresholds. It never
    # changes the model or tunes the held-out decision threshold.
    for record in data['records']:
        if record['split']=='train':continue
        result=query({**record['input'],'id':record['id']})
        rows.append(dict(id=record['id'],split=record['split'],family=record['structural_family'],
            reference=record['reference'],result=result))
    pack(out/'concepts/rows.json.xz',rows)
    summary={}
    for split in ('calibration','test'):
        summary[split]={concept:metrics([r for r in rows if r['split']==split and r['result']['concept']==concept]) for concept in data['targets']}
    train_keys={observe_concept(r['input'])['rule_id'] for r in data['records'] if r['split']=='train'}
    key_audit=dict(train_unique_keys=len(train_keys),heldout_examples=len(rows),
        heldout_shared_conditional_keys=sum(r['result']['rule_id'] in train_keys for r in rows),
        heldout_unseen_conditional_keys=sum(r['result']['rule_id'] not in train_keys for r in rows),
        note='Raw structural-family overlap is zero. Shared pooled keys are a supplied representational abstraction, not discovery of symmetry or a new logical rule.')
    write_json(out/'concepts/summary.json',dict(model_version=model.version,field_model_version=field.version,
        dataset_hash=data['hash'],metrics=summary,key_audit=key_audit,
        conditional_target_names=data['targets'],complete_joint_concept_theorems=0,
        threshold_tuning=False,strategic_accuracy_claimed=False,
        scope='Precision and recall concern the named limited conditional targets. Overload, strategic trapping and a joint fork theorem remain unsupported.'))
    transformations=[]
    for case in controls['transformations']:
        a=query(case['before']);b=query(case['after'])
        equal=a['raw_stv']==b['raw_stv'] and a['classification']==b['classification']
        passed=(equal and a['rule_id']==b['rule_id']) if case['expected']=='invariant-relative-conditional' else b['classification']=='unknown'
        transformations.append(dict(case=case,before=a,after=b,passed=passed,
            same_truth_value=a['raw_stv']==b['raw_stv'],same_proof=a['proof_id']==b['proof_id'],
            proof_comparison_scope='Identity/coordinate observation provenance may change even when the learned rule and native TV remain invariant.'))
    pack(out/'concepts/transformations.json.xz',transformations)
    counterfactuals=[]
    for case in controls['counterfactuals']:
        a=query(case['before']);b=query(case['after'])
        removed=copy.deepcopy(model);removed.hypotheses.pop(a['rule_id'],None);removed.variant='C12-selected-conditional-removed'
        without=query(case['before'],removed)
        without_fields=query(case['before'],field_checkpoint=no_field)
        counterfactuals.append(dict(case=case,before=a,after=b,removed_conditional=without,removed_field_learning=without_fields,
            distinguishes_registered_change=a['classification']=='supported' and b['classification']=='contradicted',
            rule_changed=a['rule_id']!=b['rule_id'],proof_changed=a['proof_id']!=b['proof_id'],
            conditional_removal_abstains=without['classification']=='unknown',
            field_removal_scope='The concept rule is conditional on a named host-observed structural packet. Removing independent field learning need not retract that different conditional; it removes the associated field proofs. Neither arm establishes joint strategic support.'))
    pack(out/'concepts/counterfactuals.json.xz',counterfactuals)
    transfers=[]
    for concept,cases in controls['transfers'].items():
        for case in cases:
            learned=query(case['input']);before=query(case['input'],empty)
            removed=copy.deepcopy(model);removed.hypotheses.pop(learned['rule_id'],None);removed.variant='C12-transfer-conditional-removed'
            after=query(case['input'],removed)
            transfers.append(dict(case=case,concept=concept,empty=before,learned=learned,removed=after,
                successful=before['classification']=='unknown' and learned['classification']=='supported' and after['classification']=='unknown',
                conditional_seen_in_training=learned['rule_id'] in train_keys,
                structural_family_seen_in_training=case['structural_family'] in {r['structural_family'] for r in data['records'] if r['split']=='train'},
                joint_native_proof=False))
    pack(out/'concepts/transfers.json.xz',transfers)
    write_json(out/'concepts/controls-summary.json',dict(transformations=len(transformations),
        transformation_passes=sum(r['passed'] for r in transformations),
        transformation_failures=[r['case']['id'] for r in transformations if not r['passed']],
        counterfactuals=len(counterfactuals),counterfactuals_distinguished=sum(r['distinguishes_registered_change'] for r in counterfactuals),
        conditional_removal_abstains=sum(r['conditional_removal_abstains'] for r in counterfactuals),
        transfers={concept:dict(attempts=sum(r['concept']==concept for r in transfers),
            successes=sum(r['concept']==concept and r['successful'] for r in transfers),
            failures=[r['case']['id'] for r in transfers if r['concept']==concept and not r['successful']]) for concept in ('Pin','Fork')},
        complete_joint_concept_proofs=0,failures_preserved=True))
    print('Held-out concepts and controls complete',summary,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
