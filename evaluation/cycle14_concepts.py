"""Census historical abstentions and evaluate the untouched concept panel."""
import argparse
from collections import Counter
from pathlib import Path

from pln_chess.common import ROOT,digest,read_json
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle13.concepts import ForkModel,infer_concepts,ForkSession
from evaluation.cycle12_concepts import metrics
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out);runtime=Runtime(timeout=600)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    model=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime)
    fork=ForkModel.load(ROOT/'artifacts/cycle13/model/C13-fork-role.json',runtime)
    old=read_gzip(ROOT/'artifacts/cycle13/concepts/external.json.xz');census=[]
    for row in old:
        result=row['result']
        if result['classification']!='unknown':continue
        starting=result.get('starting_conditional',result);components=result.get('field_relations',[])
        missing=starting['rule_id'] not in model.hypotheses
        causes=dict(missing_learned_conditional=missing,
            missing_query_scope=not bool(components),
            descriptor_mismatch=missing,
            unsupported_joint_conjunction=not result['joint_proof_complete'],
            incomplete_field_evidence=any(c['classification'] in ('unknown','incomplete') for c in components),
            insufficient_independent_evidence=not bool(result.get('evidence_ids')),
            overly_specific_role_abstraction='Not independently isolated; missing exact descriptors are consistent with this explanation')
        census.append(dict(id=row['id'],concept=result['concept'],rule_id=result['rule_id'],proof_id=result['proof_id'],
            raw_stv=result['raw_stv'],causes=causes,gaps=result.get('gaps',[]),
            primary_observed_cause='missing-exact-learned-conditional' if missing else 'retained-unknown-conditional',
            caveat='Missing conditional and descriptor mismatch are related diagnostics, not separately identified causal effects. Unsupported conjunction limits strategic claims even when a conditional is answered.'))
    assert len(census)==68
    atomic_json(out/'concepts/historical-abstention-census.json',dict(cases=census,N=68,
        source_sha256=sha(ROOT/'artifacts/cycle13/concepts/external.json.xz'),
        complete_historical_panel=96,historical_correct=28,historical_wrong=0,
        historical_panel_status='Previously exposed diagnostic data'))
    data=read_json(out/'datasets/concept-holdout.json');session=ForkSession(runtime);options=FieldOptions(timeout_seconds=600)
    def query(case):
        answer=infer_concepts([case],model,field,fork_model=fork,runtime=runtime,options=options,session=session)
        assert not answer['execution']['truncated'];result=answer['concepts'][0]
        assert result['proof_id']==digest(result['proof_trace']) and not result['joint_proof_complete'];return result
    rows=[]
    for record in data['records']:
        rows.append(dict(id=record['id'],reference=record['reference'],result=query(record['input']),
            dependence_group=record['dependence_group'],source_game=record['source_game'],source=record['source']))
    pack(out/'concepts/independent-holdout.json.xz',rows)
    controls=[]
    for case in data['controls']:
        before,after=query(case['before']),query(case['after'])
        passed=(before['classification']==after['classification'] and before['raw_stv']==after['raw_stv'] and before['rule_id']==after['rule_id']) if case['expected']=='invariant' else after['classification']==case['expected']
        controls.append(dict(id=case['id'],operation=case['operation'],dependence_group=case['dependence_group'],
            before=before,after=after,passed=passed,expected=case['expected'],independent_example=False))
    pack(out/'concepts/holdout-controls.json.xz',controls)
    summary=dict(schema='c14-concept-transfer-v1',selection_hash=data['hash'],independent_groups=len({r['dependence_group'] for r in rows}),
        overall=metrics(rows),families={family:metrics([r for r in rows if r['result']['concept']==family]) for family in data['selection']},
        statuses=dict(Counter(r['result']['classification'] for r in rows)),
        controls=dict(N=len(controls),N_passed=sum(c['passed'] for c in controls),failures=[c['id'] for c in controls if not c['passed']]),
        models=dict(field=field.version,concept=model.version,fork=fork.version),new_concept_learning=False,
        complete_strategic_proofs=0,historical_preservation_receipt='baseline/research/verified.json',
        scope='New limited structural targets on independent source groups; geometric usefulness and legal recapture are not asserted.')
    atomic_json(out/'concepts/summary.json',summary);print('C14 CONCEPTS',summary['overall'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');run(parser.parse_args().out)
