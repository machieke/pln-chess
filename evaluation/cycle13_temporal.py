"""Immediate versus continuation-conditioned beliefs on the fixed branch panel."""
import argparse
from collections import Counter
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from evaluation.cycle13_metrics import metrics, calibration, bootstrap, direction
from evaluation.cycle7_io import pack
from evaluation.cycle3 import read_gzip
from training.cycle13_features import training_records
from training.cycle13_learning import train


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle13.inference import infer_preferences, PreferenceNativeSession
    all_rows = training_records(out, temporal=True)
    source = read_json(out / 'datasets/temporal-plans.json')
    plans = {r['id']:r for r in source['records']}
    immediate = {r['id']:r for r in read_gzip(out / 'preferences/relational.json.xz')}
    temporal = [r for r in all_rows if r['temporal_context']['horizon'] > 1]
    runtime = Runtime(timeout=600)
    training = [r for r in all_rows if r['split'] == 'train']
    model = train(training, runtime, out / 'learning/with-temporal',
        dataset_hash=digest(training), baseline_root=out, variant='C13-preference-with-temporal')
    model.export(out / 'model/C13-preference-temporal.json')
    session = PreferenceNativeSession(runtime)
    rows = []
    for start in range(0,len(temporal),64):
        batch = temporal[start:start+64]
        result = infer_preferences([r['packet'] for r in batch], model, runtime=runtime,
            options=FieldOptions(timeout_seconds=600), session=session)
        assert not result['execution']['truncated']
        for row, preference in zip(batch, result['comparisons']):
            root_id = row['id'].rsplit('-ply',1)[0]
            rows.append({**row, 'result':preference, 'plan_id':root_id,
                'immediate_result':immediate[root_id]['result'], 'immediate_label':immediate[root_id]['label']})
    pack(out / 'temporal/preferences.json.xz', rows)
    summaries = {}
    for horizon in (2,3):
        for split in ('train','calibration','test'):
            selected = [r for r in rows if r['temporal_context']['horizon'] == horizon and r['split'] == split]
            immediate_arm = [{**r, 'result':r['immediate_result']} for r in selected]
            summaries[str(horizon) + '-' + split] = dict(continued=metrics(selected),
                immediate_without_continuation=metrics(immediate_arm), calibration=calibration(selected),
                uncertainty=bootstrap(selected),
                answered_at_both=sum(direction(r) is not None and direction({'result':r['immediate_result']}) is not None for r in selected),
                directional_reversals=sum(direction(r) is not None and direction({'result':r['immediate_result']}) is not None and
                    direction(r) != direction({'result':r['immediate_result']}) for r in selected),
                identical_statuses=sum(r['result']['status'] == r['immediate_result']['status'] for r in selected),
                reference_label_changes=sum(r['label'] != r['immediate_label'] for r in selected))
    demonstrations = []
    chosen = [r['id'] for r in source['records'] if r['split'] == 'test'][:10]
    for row in rows:
        if row['plan_id'] in chosen:
            plan = plans[row['plan_id']]
            horizon = row['temporal_context']['horizon']
            demonstrations.append(dict(id=row['id'], horizon=horizon, plan_id=row['plan_id'],
                branches={k:v[:horizon] for k,v in plan['branches'].items()}, fen=plan['fen'],
                immediate_result=row['immediate_result'], continued_result=row['result'],
                immediate_label=row['immediate_label'], continued_label=row['label'],
                source=plan['source'], selection_provenance=plan['response_selection'],
                feature_artifact=row['feature_artifact'], reference_evidence_id=row['reference_evidence_id'],
                dependence_group=row['dependence_group'], unknown_responses=plan['unexamined_responses'],
                selection='First ten registered test plans; independent of PLN results and endpoint preference labels.'))
    assert Counter(r['horizon'] for r in demonstrations) == {2:10,3:10}
    pack(out / 'temporal/demonstrations.json.xz', demonstrations)
    write_json(out / 'temporal/summary.json', dict(passed=True, plan_hash=source['hash'], model_version=model.version,
        source_games=len(plans), labeled_comparisons=len(rows), demonstrations=dict(Counter(r['horizon'] for r in demonstrations)),
        panels=summaries, native_joint_temporal_theorems=0, exhaustive_responses=False,
        branch_selection='Explicit offline source PV; one supplied branch per candidate; no production search.',
        scope='Conditional preferences and separate endpoint proofs. Status stability includes abstention and is not strategic correctness.'))
    write_json(out / 'ablations/temporal.json', dict(panels=summaries,
        fixed_branch_cohort=True, no_temporal_arm='Original immediate conditional evaluated against the same endpoint reference labels.',
        continued_arm='Separate horizon-conditioned model, trained only on registered training-source continuation labels.',
        limitation='The intervention changes available continuation observations and training evidence together; differences do not establish causal importance.',
        causal_claim=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    run(parser.parse_args().out)
