"""Gated study of piece-independent fork packets using only C12 training data."""
import argparse
from collections import defaultdict
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.learning import PRIOR
from pln_chess.pln import Runtime, TV
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.model import ConceptModel
from pln_chess.cycle12.inference import infer_concepts
from training.cycle11_fields import independent_components
from evaluation.cycle7_io import pack


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle13.concepts import ForkModel, fork_packet
    data = read_json(ROOT / 'artifacts/cycle12/datasets/concepts.json')
    expected = data.pop('hash')
    assert digest(data) == expected
    data['hash'] = expected
    rows = [r for r in data['records'] if r['split'] == 'train' and r['input']['concept'] == 'Fork']
    runtime = Runtime(timeout=600)
    field = FieldModel.load(ROOT / 'artifacts/cycle11/model/C11-field-trained.json', runtime)
    concept = ConceptModel.load(ROOT / 'artifacts/cycle12/model/C12-concept-trained.json', runtime)
    observed = infer_concepts([r['input'] for r in rows], concept, field,
        runtime=runtime, options=FieldOptions(timeout_seconds=600))
    assert not observed['execution']['truncated']
    ledger = []
    grouped = defaultdict(list)
    for row, result in zip(rows, observed['concepts']):
        packet = fork_packet(result)
        assert packet['complete'], row['id']
        payload = dict(example_id=row['id'], input=row['input'], packet=packet, label=row['reference']['label'],
            reference=row['reference'], dependence_group=row['dependence_group'],
            transformation_lineage=row['transformation_lineage'], dataset_hash=data['hash'],
            field_model_version=field.version, starting_concept_version=concept.version, runtime_version=runtime.version,
            source='Original registered Cycle 12 training labels only', observation_confidence=.5)
        evidence = 'fork-role-evidence:' + digest(payload)
        ledger.append(dict(evidence_id=evidence, payload=payload))
        grouped[packet['rule_id']].append(dict(evidence_id=evidence, label=payload['label'],
            dependence_group=payload['dependence_group'], transformation_lineage=payload['transformation_lineage'],
            packet=packet))
    jobs = []
    traces = []
    states = {}
    excluded = []
    for identifier, records in sorted(grouped.items()):
        refs = [PRIOR.metta(), PRIOR.metta()]
        evidence = []
        groups = set()
        supporting = []
        contradicting = []
        for component in independent_components(records):
            if component['contradictory']:
                excluded.append(dict(rule_id=identifier, reason='contradictory-dependent-component',
                    evidence_ids=[r['evidence_id'] for r in component['records']], dependence_groups=component['groups']))
                continue
            record = component['records'][0]
            evidence.append(record['evidence_id'])
            groups.update(component['groups'])
            (supporting if record['label'] else contradicting).append(record['evidence_id'])
            if len(component['records']) > 1:
                excluded.append(dict(rule_id=identifier, reason='shared-ancestry', representative=record['evidence_id'],
                    evidence_ids=[r['evidence_id'] for r in component['records'][1:]], dependence_groups=component['groups']))
            for channel, label in enumerate((record['label'], not record['label'])):
                name = 'forkrolerevision' + str(len(jobs))
                value = TV(float(label), .5)
                expression = '(Truth_Revision {} {})'.format(refs[channel], value.metta())
                jobs.append((name, expression))
                traces.append(dict(id=name, operator='Truth_Revision', native_expression=expression,
                    rule_id=identifier, channel='positive' if channel == 0 else 'negative',
                    previous=refs[channel], observation_tv=value.json(), evidence_id=record['evidence_id'],
                    dependence_groups=component['groups']))
                refs[channel] = '(' + name + ')'
        if evidence:
            states[identifier] = dict(id=identifier, descriptor=records[0]['packet']['descriptor'], refs=refs,
                evidence_ids=evidence, dependence_groups=sorted(groups),
                supporting_evidence=supporting, contradicting_evidence=contradicting)
    session = NativeSession(runtime)
    session.bind(digest([runtime.manifest, data['hash'], 'c13-fork-role-study']))
    values = session.batch(jobs)
    model = ForkModel(runtime.version)
    for identifier, state in states.items():
        refs = state.pop('refs')
        model.hypotheses[identifier] = {**state, 'positive': values[refs[0][1:-1]].json(),
            'negative': values[refs[1][1:-1]].json()}
    model.ledger_digest = digest(sorted(r['evidence_id'] for r in ledger))
    model.training_report = dict(training_examples=len(rows), dataset_hash=data['hash'],
        hypotheses=len(states), native_revision_nodes=len(jobs), executed_native_operators=session.calls,
        native_cache_hits=session.hits, excluded_components=len(excluded), heldout_labels_used=False,
        field_model_version=field.version, starting_concept_model_version=concept.version,
        scope='Learned piece-independent conditionals on supplied occupancy/allegiance and separately inferred attack states; no conjunction or hardcoded fork verdict.')
    model.export(out / 'model/C13-fork-role.json')
    assert ForkModel.load(out / 'model/C13-fork-role.json', runtime).version == model.version
    pack(out / 'forks/training-observations.json.xz', observed)
    pack(out / 'forks/ledger.json.xz', ledger)
    pack(out / 'forks/native-training.json.xz', dict(model_version=model.version,
        traces=[{**node, 'truth_value': values[node['id']].json()} for node in traces], excluded=excluded))
    write_json(out / 'forks/training-summary.json', dict(passed=True, model_version=model.version,
        training_report=model.training_report, legal_default_eligible=False))
    print('FORK ROLE TRAINING', model.version, model.training_report, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    run(parser.parse_args().out)
