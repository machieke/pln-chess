"""Controlled duplicate delivery, ancestry contradiction and naive revision."""
import argparse
import copy
import json
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from evaluation.cycle13_metrics import metrics
from evaluation.cycle7_io import pack
from evaluation.cycle3 import read_gzip
from scripts.cycle9_baseline import sha
from training.cycle13_features import training_records
from training.cycle13_learning import train


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.evidence import PreferenceLedger
    from pln_chess.cycle13.inference import infer_preferences
    from pln_chess.cycle13.ontology import project
    runtime = Runtime(timeout=600)
    original = PreferenceModel.load(out / 'model/C13-preference-relational.json', runtime)
    records = training_records(out)
    training = [r for r in records if r['split'] == 'train']
    test = [r for r in records if r['split'] == 'test']
    copies = []
    for row in training:
        copies.append(row)
        for index in (1,2):
            copies.append({**row, 'id':row['id'] + '-controlled-delivery-' + str(index),
                'source':{**row['source'], 'controlled_delivery':index,
                    'scope':'Repeated delivery of the same reference label; not another independent game or outcome.'}})
    data_hash = digest(copies)
    handled = train(copies, runtime, out / 'learning/replicated-with-dependence', dataset_hash=data_hash,
        baseline_root=out, variant='C13-replicated-with-dependence')
    naive = train(copies, runtime, out / 'learning/replicated-without-dependence', dataset_hash=data_hash,
        baseline_root=out, variant='C13-replicated-without-dependence', dependence=False)
    assert set(original.hypotheses) == set(handled.hypotheses) == set(naive.hypotheses)
    comparisons = []
    for identifier, hypothesis in original.hypotheses.items():
        assert hypothesis['channels'] == handled.hypotheses[identifier]['channels']
        comparisons.append(dict(rule_id=identifier, original=hypothesis['channels'],
            handled=handled.hypotheses[identifier]['channels'], naive=naive.hypotheses[identifier]['channels'],
            independent_groups=len(hypothesis['dependence_groups']),
            naive_deliveries=len(naive.hypotheses[identifier]['dependence_groups'])))
    ledger_path = out / 'learning/replicated-with-dependence/ledger.jsonl'
    entries = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    before = sha(ledger_path)
    delivered = PreferenceLedger(ledger_path).append_many([row['payload'] for row in entries])
    assert sha(ledger_path) == before
    assert [r['evidence_id'] for r in delivered] == [r['evidence_id'] for r in entries]
    target = next(r for r in training if r['label'] in ('A','B') and project(r['packet'],'relational')['distinguishable'])
    conflict = {**target, 'id':target['id'] + '-controlled-opposing-delivery',
        'label':'B' if target['label'] == 'A' else 'A',
        'source':{**target['source'], 'scope':'Injected contradictory delivery from the same ancestry; diagnostic control, not external supervision.'}}
    contradictory = train([*training,conflict],runtime,out / 'learning/contradictory-dependent',
        dataset_hash=digest([*training,conflict]), baseline_root=out, variant='C13-contradictory-dependent-control')
    evidence = read_gzip(out / 'learning/contradictory-dependent/native-training.json.xz')
    withheld = [r for r in evidence['excluded'] if r['reason'] == 'contradictory-dependent-component']
    assert withheld and any(target['dependence_group'] in r['dependence_groups'] for r in withheld)
    natural_contradictions = [dict(rule_id=key, channels=h['channels'], supporting_evidence=h['supporting_evidence'],
        dependence_groups=h['dependence_groups']) for key,h in original.hypotheses.items()
        if h['supporting_evidence']['first'] and h['supporting_evidence']['second']]
    results = {}
    for name,model in (('ordinary',original),('replicated-handled',handled),('replicated-naive',naive),('dependent-conflict',contradictory)):
        inference = infer_preferences([r['packet'] for r in test],model,runtime=runtime,options=FieldOptions(timeout_seconds=600))
        assert not inference['execution']['truncated']
        rows = [{**row,'result':result} for row,result in zip(test,inference['comparisons'])]
        pack(out / 'dependence' / (name + '.json.xz'),rows)
        results[name] = dict(model_version=model.version,metrics=metrics(rows),training_report=model.training_report)
    increased = sum(any(r['naive'][channel]['confidence'] > r['original'][channel]['confidence']
        for channel in r['original']) for r in comparisons)
    assert increased > 0
    pack(out / 'dependence/conditional-comparisons.json.xz',comparisons)
    write_json(out / 'dependence/summary.json',dict(passed=True,original_training_pairs=len(training),
        delivered_records=len(copies),independent_source_groups=len({r['dependence_group'] for r in training}),
        duplicate_append_byte_identical=True,handled_native_tvs_identical=True,
        native_confidence_increased_without_dependence=increased,total_hypotheses=len(comparisons),
        contradictory_dependent_components_withheld=withheld,observed_independent_opposing_evidence=natural_contradictions,
        fixed_test_results=results,controlled_copies_are_not_independent=True,
        scope='Controlled delivery and ancestry interventions, separate from independent empirical sample counts. Native operators compute every revised TV.'))
    write_json(out / 'ablations/dependence.json',dict(results=results,
        paired_control='Same repeated deliveries; only dependence grouping changes.',
        native_confidence_inflation_rules=increased,additional_independent_observations=0,
        causal_scope='Confidence inflation caused by counting repeated inputs in this controlled replay; no claim of causal strategic importance.'))
    print('DEPENDENCE CONTROLS PASSED',increased,'inflated rules without grouping',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',default='artifacts/cycle13')
    run(parser.parse_args().out)
