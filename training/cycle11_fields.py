"""Offline field learning through the existing native revision infrastructure.

This driver is prepared during unchanged-source replay and refuses to train
until that replay has passed. Production field modules are a separate layer.
"""
import argparse
from collections import defaultdict
from dataclasses import asdict
import lzma
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position, parse_square
from pln_chess.evidence import Ledger
from pln_chess.pln import Runtime, TV
from pln_chess.learning import PRIOR
from pln_chess.cycle3.native import NativeSession
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def independent_components(records):
    """Connected ancestry components, including contradictions discovered later.

    Components are a conservative ingestion policy, never a PLN TV operation.
    One representative of a consistent component contributes one native update.
    """
    parent = {}

    def root(key):
        parent.setdefault(key, key)
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for record in records:
        ancestry = sorted(set([record['dependence_group'], *record.get('transformation_lineage', [])]))
        for item in ancestry[1:]:
            a, b = root(ancestry[0]), root(item)
            parent[max(a, b)] = min(a, b)
        root(ancestry[0])
    groups = defaultdict(list)
    for record in records:
        groups[root(record['dependence_group'])].append(record)
    result = []
    for records in groups.values():
        unique = {r['evidence_id']: r for r in records}
        rows = sorted(unique.values(), key=lambda r: r['evidence_id'])
        ancestry = sorted({g for r in rows for g in [r['dependence_group'], *r.get('transformation_lineage', [])]})
        result.append(dict(records=rows, groups=ancestry, contradictory=len({r['label'] for r in rows}) != 1))
    return sorted(result, key=lambda c: c['groups'])


def train_queries(queries, runtime, out, *, dataset_hash, variant='C11-field-trained'):
    from pln_chess.cycle11.fields.ontology import observe_relation, GRAMMAR, TARGETS
    from pln_chess.cycle11.fields.model import FieldModel
    out = Path(out)
    payloads, positions = [], {}
    for query in queries:
        assert query['split'] == 'train', 'Held-out labels cannot enter field revision'
        position = positions.setdefault(query['fen'], Position.from_fen(query['fen']))
        piece = position.at(parse_square(query['piece_square']))
        target = parse_square(query['target_square'])
        targets = []
        for family, label in query['labels'].items():
            if label is None:
                continue
            observation = observe_relation(position, piece, target, family, source=query['source'])
            assert observation['complete'] and observation['applicable'], (query['id'], family)
            targets.append(dict(id=observation['rule_id'], target=TARGETS[family], family=family,
                descriptor=observation['descriptor'], label=label,
                observation_id=observation['id'], observation=observation))
        payloads.append(dict(position_id=position.id, candidate_id=query['id'], label=query['labels']['attack'],
            source=query['source'], dependence_group=query['dependence_group'],
            transformation_lineage=query['transformation_lineage'],
            relative_feature_fingerprint=digest([t['descriptor'] for t in targets]), targets=targets,
            observation_tv=TV(float(query['labels']['attack']), query['observation_confidence']).json(),
            runtime_version=runtime.version, model_version=GRAMMAR, input=query,
            scope='Offline reference labels for distinct local relation targets; no legal-move or strategic supervision.'))
    ledger_path = out / 'ledger.jsonl'
    archived_ledger = out / 'ledger.jsonl.xz'
    if archived_ledger.exists() and not ledger_path.exists():
        ledger_path.write_bytes(lzma.decompress(archived_ledger.read_bytes()))
    ledger = Ledger(ledger_path)
    ledger.append_many(payloads)
    records = ledger.records()
    expected = {digest(p) for p in payloads}
    assert {r['evidence_id'] for r in records} == expected, 'Use a separate ledger for each training arm'
    bykey = defaultdict(list)
    for record in records:
        payload = record['payload']
        for target in payload['targets']:
            bykey[target['id']].append(dict(evidence_id=record['evidence_id'], label=target['label'],
                dependence_group=payload['dependence_group'], transformation_lineage=payload['transformation_lineage'],
                confidence=payload['observation_tv']['confidence'], target=target))
    jobs, traces, states, excluded = [], [], {}, []
    for identifier, candidates in sorted(bykey.items()):
        refs = [PRIOR.metta(), PRIOR.metta()]
        ids, groups, positive, negative = [], set(), [], []
        for component in independent_components(candidates):
            if component['contradictory']:
                excluded.append(dict(hypothesis=identifier, reason='contradictory-dependent-component',
                    groups=component['groups'], evidence_ids=[r['evidence_id'] for r in component['records']]))
                continue
            representative = component['records'][0]
            # Different declared observation confidence in a component is not
            # silently fused. Deterministic identity chooses one finite sensor.
            evidence = representative['evidence_id']
            ids.append(evidence)
            groups.update(component['groups'])
            (positive if representative['label'] else negative).append(evidence)
            if len(component['records']) > 1:
                excluded.append(dict(hypothesis=identifier, reason='shared-dependence-component',
                    groups=component['groups'], representative=evidence,
                    evidence_ids=[r['evidence_id'] for r in component['records'][1:]]))
            for channel, label in enumerate((representative['label'], not representative['label'])):
                name = f'fieldrevision{len(jobs)}'
                tv = TV(float(label), representative['confidence'])
                expression = f'(Truth_Revision {refs[channel]} {tv.metta()})'
                jobs.append((name, expression))
                traces.append(dict(id=name, operator='Truth_Revision', native_expression=expression,
                    hypothesis=identifier, channel='positive' if channel == 0 else 'negative',
                    prior_or_previous=refs[channel], observation_tv=tv.json(), evidence_id=evidence,
                    dependence_groups=component['groups'], provenance='native-revision'))
                refs[channel] = f'({name})'
        if ids:
            target = candidates[0]['target']
            states[identifier] = dict(id=identifier, target=target['target'], family=target['family'],
                descriptor=target['descriptor'], refs=refs, evidence_ids=ids, dependence_groups=sorted(groups),
                supporting_evidence=positive, contradicting_evidence=negative,
                origin='learned-native-relative-conditional')
    session = NativeSession(runtime)
    session.bind(digest([runtime.manifest, dataset_hash, variant, sorted(expected)]))
    values = session.batch(jobs)
    model = FieldModel(runtime.version, variant=variant)
    for identifier, state in states.items():
        refs = state.pop('refs')
        model.hypotheses[identifier] = {**state,
            'positive': values[refs[0][1:-1]].json(), 'negative': values[refs[1][1:-1]].json()}
    model.ledger_digest = digest(sorted(expected))
    model.training_report = dict(dataset_hash=dataset_hash, training_queries=len(queries), records=len(records),
        dependence_components=True, hypotheses=len(states), native_revision_nodes=len(jobs),
        executed_native_operators=session.calls, native_math_cache_hits=session.hits,
        excluded_components=len(excluded), excluded_digest=digest(excluded),
        neutral_prior=PRIOR.json(), validation_or_test_labels_used=False,
        seeded_structure='Typed geometry/occupancy grammar and symmetry/distance pooling; no seeded positive influence label.',
        native_scope='Conditional local propositions, not conjunction, global legality, empirical probability, or strategic value.')
    model.export(out / 'checkpoint.json')
    assert FieldModel.load(out / 'checkpoint.json', runtime).version == model.version
    pack(out / 'native-training.json.xz', dict(traces=[{**t, 'truth_value': values[t['id']].json()} for t in traces],
        excluded=excluded, model_version=model.version, training_report=model.training_report,
        ledger_evidence_ids=sorted(expected), dataset_hash=dataset_hash))
    # Preserve the complete ledger byte-for-byte while keeping large proof-rich
    # records practical to archive. A resumed run restores these exact bytes.
    raw = ledger_path.read_bytes()
    compressed = lzma.compress(raw, preset=1)
    assert lzma.decompress(compressed) == raw
    archived_ledger.write_bytes(compressed)
    ledger_path.unlink()
    return model


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed'], 'Complete unchanged-source baseline before learning'
    from pln_chess.cycle11.fields.model import FieldModel
    dataset = read_gzip(out / 'datasets/field-queries.json.xz')
    expected = dataset.pop('hash')
    assert digest(dataset) == expected
    dataset['hash'] = expected
    runtime = Runtime(timeout=1200)
    rows = [r for r in dataset['queries'] if r['split'] == 'train']
    model = train_queries(rows, runtime, out / 'field-learning/main', dataset_hash=expected)
    (out / 'model').mkdir(exist_ok=True)
    model.export(out / 'model/C11-field-trained.json')
    empty = FieldModel(runtime.version, variant='C11-field-empty')
    empty.export(out / 'model/C11-field-empty.json')
    write_json(out / 'field-learning/summary.json', dict(passed=True, model_version=model.version,
        empty_model_version=empty.version, training_report=model.training_report, dataset_hash=expected,
        accepted_legal_model_changed=False, field_model_promoted_to_legal_default=False))
    print('Native field training complete', model.version, model.training_report, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
