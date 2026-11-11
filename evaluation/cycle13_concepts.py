"""Preserved concept answers, fork resolution, and independent external controls."""
import argparse
from collections import Counter
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from evaluation.cycle12_concepts import metrics
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def correct(row):
    return row['result']['classification'] == ('supported' if row['reference']['label'] else 'contradicted')


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle13.concepts import ForkModel, infer_concepts, ForkSession
    runtime = Runtime(timeout=600)
    options = FieldOptions(timeout_seconds=600)
    field = FieldModel.load(ROOT / 'artifacts/cycle11/model/C11-field-trained.json', runtime)
    model = ConceptModel.load(ROOT / 'artifacts/cycle12/model/C12-concept-trained.json', runtime)
    fork = ForkModel.load(out / 'model/C13-fork-role.json', runtime)
    session = ForkSession(runtime)

    def query(case):
        output = infer_concepts([case], model, field, fork_model=fork,
            options=options, runtime=runtime, session=session)
        assert not output['execution']['truncated'], case.get('id')
        result = output['concepts'][0]
        assert digest(result['proof_trace']) == result['proof_id']
        assert not result['joint_proof_complete']
        return result

    data = read_json(ROOT / 'artifacts/cycle12/datasets/concepts.json')
    baseline = {r['id']:r for r in read_gzip(out / 'baseline/research/concepts/rows.json.xz')}
    rows = []
    for record in data['records']:
        if record['split'] == 'train':
            continue
        result = query({**record['input'], 'id':record['id']})
        old = baseline[record['id']]
        legacy = result['starting_conditional']
        for name in ('classification', 'raw_stv', 'proof_id', 'proof_trace', 'rule_id', 'evidence_ids',
                     'dependence_groups', 'model_version', 'runtime_version'):
            assert legacy[name] == old['result'][name], (record['id'], name)
        current = dict(id=record['id'], split=record['split'], reference=record['reference'], result=result)
        if correct(old):
            assert correct(current), record['id']
        rows.append(current)
    assert len(rows) == len(baseline)
    pack(out / 'concepts/historical.json.xz', rows)
    outcomes = []
    for row in rows:
        if row['result']['concept'] != 'Fork' or baseline[row['id']]['result']['classification'] != 'unknown':
            continue
        outcomes.append(dict(id=row['id'], split=row['split'], before='unknown',
            after=row['result']['classification'], correct=correct(row),
            rule_id=row['result']['rule_id'], proof_id=row['result']['proof_id'],
            evidence_ids=row['result']['evidence_ids'], raw_stv=row['result']['raw_stv'],
            original_missing_rule=baseline[row['id']]['result']['rule_id'],
            cause='The original conditional retains attacker kind and component movement geometry; the new learned packet pools role occupancy/allegiance and separately inferred attack states.',
            joint_native_proof=False))
    external = read_json(out / 'datasets/external-concepts.json')
    independent = []
    for record in external['records']:
        result = query(record['input'])
        independent.append(dict(id=record['id'], reference=record['reference'], result=result,
            dependence_group=record['dependence_group'], source_game=record['source_game'], source=record['source']))
    pack(out / 'concepts/external.json.xz', independent)
    controls = []
    for case in external['controls']:
        before, after = query(case['before']), query(case['after'])
        if case['expected'] == 'invariant':
            passed = before['classification'] == after['classification'] and before['raw_stv'] == after['raw_stv'] and before['rule_id'] == after['rule_id']
        else:
            passed = after['classification'] == case['expected']
        controls.append(dict(case=case, before=before, after=after, passed=passed,
            independent_example=False, proof_identity_scope='Observation and coordinate identities may change under a transformation; learned key and TV are compared separately.'))
    pack(out / 'concepts/external-controls.json.xz', controls)
    generic = [dict(id=r['id'], reference=r['reference'], result=r['result']['fork_role_conditional'])
        for r in [*rows, *independent] if r['result']['concept'] == 'Fork']
    summary = dict(passed=True, historical={split:metrics([r for r in rows if r['split'] == split]) for split in ('calibration', 'test')},
        all_previous_correct_preserved=True, starting_native_proofs_unchanged=len(rows),
        original_test_abstentions=[r for r in outcomes if r['split'] == 'test'],
        calibration_abstentions=[r for r in outcomes if r['split'] == 'calibration'],
        external={name:metrics([r for r in independent if r['result']['concept'] == name]) for name in external['selection']},
        external_cases=len(independent), external_independent_games=len({r['source_game'] for r in independent}),
        generic_fork_evaluation_without_fallback=metrics(generic),
        controls=dict(cases=len(controls), passes=sum(r['passed'] for r in controls),
            by_operation={name:dict(cases=sum(r['case']['operation'] == name for r in controls),
                passes=sum(r['passed'] and r['case']['operation'] == name for r in controls))
                for name in sorted({r['case']['operation'] for r in controls})},
            failures=[r['case']['id'] for r in controls if not r['passed']]),
        external_statuses=dict(Counter(r['result']['classification'] for r in independent)),
        field_model_version=field.version, starting_concept_version=model.version, fork_model_version=fork.version,
        unknowns_retained=True, complete_joint_strategic_proofs=0,
        scope='Limited conditional targets only. External wrong answers and abstentions are research outcomes, not suppressed by the preservation gate.')
    write_json(out / 'concepts/summary.json', summary)
    write_json(out / 'forks/resolution.json', dict(outcomes=outcomes, previous_correct_preserved=True,
        test_abstentions=len([r for r in outcomes if r['split'] == 'test']),
        test_resolved_correctly=sum(r['correct'] and r['split'] == 'test' for r in outcomes)))
    print('CONCEPT EVALUATION', summary, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    run(parser.parse_args().out)
