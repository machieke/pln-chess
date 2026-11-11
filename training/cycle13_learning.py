"""Prepared native preference revision driver, gated on starting verification.

External labels update only the separate experimental preference checkpoint.
Production inference never imports this module or its source-engine evidence.
"""
from collections import Counter, defaultdict
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import TV
from pln_chess.learning import PRIOR
from pln_chess.cycle3.native import NativeSession
from training.cycle11_fields import independent_components
from evaluation.cycle7_io import pack


def train(records, runtime, out, *, dataset_hash, abstraction='relational', dependence=True,
          baseline_root='artifacts/cycle13', variant=None):
    """Fit three independent native channels; missing supervision is not false."""
    assert read_json(Path(baseline_root) / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle13.ontology import project
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.evidence import PreferenceLedger
    variant = variant or ('C13-preference-' + abstraction)
    out = Path(out)
    by_key = defaultdict(list)
    payloads = []
    excluded = []
    for record in records:
        if record['split'] != 'train':
            raise ValueError('Held-out supervision cannot update a preference model')
        packet = project(record['packet'], abstraction)
        label = record['label']
        if label not in ('A', 'B', 'no-demonstrated-preference', 'unknown'):
            raise ValueError('Invalid preference label')
        canonical_label = ('first' if packet['canonical_order'][0] == label else 'second') if label in ('A', 'B') else label
        payload = dict(observation_id=record['id'], source_position=record['fen'],
            candidate_moves=record['moves'], descriptor=packet['descriptor'], packet=packet,
            label=label, canonical_label=canonical_label, source=record['source'],
            source_game=record['source_game'], dependence_group=record['dependence_group'],
            transformation_lineage=record.get('transformation_lineage', [record['dependence_group']]),
            temporal_context=record['temporal_context'], model_versions=record['model_versions'],
            runtime_version=runtime.version, dataset_hash=dataset_hash,
            reference_evidence_id=record['reference_evidence_id'], observation_confidence=.5,
            scope='External preference supervision on a supplied relational comparison; not a legal-move observation.')
        payloads.append(payload)
    ledger = PreferenceLedger(out / 'ledger.jsonl')
    ingested = ledger.append_many(payloads)
    assert len(ingested) == len(payloads)
    for payload, entry in zip(payloads, ingested):
        packet = payload['packet']
        reason = None
        if payload['label'] == 'unknown':
            reason = 'unresolved-reference-label'
        elif not packet['complete']:
            reason = 'incomplete-comparison-observation'
        elif not packet['distinguishable'] and payload['label'] in ('A', 'B'):
            reason = 'direction-collapses-under-relative-abstraction'
        if reason:
            excluded.append(dict(evidence_ids=[entry['evidence_id']], reason=reason,
                rule_id=packet['rule_id'], dependence_groups=[payload['dependence_group']]))
            continue
        by_key[packet['rule_id']].append(dict(evidence_id=entry['evidence_id'],
            label=payload['canonical_label'], descriptor=packet['descriptor'], confidence=payload['observation_confidence'],
            dependence_group=payload['dependence_group'] if dependence else 'uncontrolled-delivery:' + entry['evidence_id'],
            transformation_lineage=payload['transformation_lineage'] if dependence else [],
            original_dependence_group=payload['dependence_group']))
    jobs = []
    traces = []
    states = {}
    channels = ('first', 'second', 'no-demonstrated-preference')
    for identifier, rows in sorted(by_key.items()):
        refs = {channel: PRIOR.metta() for channel in channels}
        evidence = []
        groups = set()
        supporting = {channel: [] for channel in channels}
        for component in independent_components(rows):
            if component['contradictory']:
                excluded.append(dict(rule_id=identifier, reason='contradictory-dependent-component',
                    evidence_ids=[r['evidence_id'] for r in component['records']], dependence_groups=component['groups']))
                continue
            representative = component['records'][0]
            evidence.append(representative['evidence_id'])
            groups.update(component['groups'])
            supporting[representative['label']].append(representative['evidence_id'])
            if len(component['records']) > 1:
                excluded.append(dict(rule_id=identifier, reason='shared-ancestry', representative=representative['evidence_id'],
                    evidence_ids=[r['evidence_id'] for r in component['records'][1:]], dependence_groups=component['groups']))
            for channel in channels:
                name = 'preferencerevision' + str(len(jobs))
                observation = TV(float(representative['label'] == channel), representative['confidence'])
                expression = '(Truth_Revision {} {})'.format(refs[channel], observation.metta())
                jobs.append((name, expression))
                traces.append(dict(id=name, operator='Truth_Revision', native_expression=expression,
                    rule_id=identifier, channel=channel, previous=refs[channel], observation_tv=observation.json(),
                    evidence_id=representative['evidence_id'], dependence_groups=component['groups']))
                refs[channel] = '(' + name + ')'
        if evidence:
            states[identifier] = dict(id=identifier, descriptor=rows[0]['descriptor'], refs=refs,
                evidence_ids=evidence, dependence_groups=sorted(groups), supporting_evidence=supporting,
                origin='Native revision from external supervision; conditional on a host-assembled relative packet.')
    session = NativeSession(runtime)
    session.bind(digest([runtime.manifest, dataset_hash, variant, abstraction, dependence]))
    values = session.batch(jobs)
    model = PreferenceModel(runtime.version, abstraction=abstraction, variant=variant)
    for identifier, state in states.items():
        refs = state.pop('refs')
        model.hypotheses[identifier] = {**state, 'channels': {channel: values[refs[channel][1:-1]].json() for channel in channels}}
    model.ledger_digest = digest(sorted({entry['evidence_id'] for entry in ingested}))
    model.training_report = dict(dataset_hash=dataset_hash, training_examples=len(records),
        unique_evidence=len({entry['evidence_id'] for entry in ingested}), hypotheses=len(states),
        native_revision_nodes=len(jobs), executed_native_operators=session.calls, native_cache_hits=session.hits,
        excluded_observations=dict(Counter(row['reason'] for row in excluded)), dependence_handling=dependence,
        heldout_labels_used=False, neutral_prior=PRIOR.json(), observation_confidence=.5,
        label_counts=dict(Counter(r['label'] for r in records)), native_joint_strategic_theorems=0,
        scope='Three independent conditional channels, not normalized probabilities or a move-selection utility.')
    model.export(out / 'checkpoint.json')
    assert PreferenceModel.load(out / 'checkpoint.json', runtime).version == model.version
    pack(out / 'native-training.json.xz', dict(model_version=model.version, dataset_hash=dataset_hash,
        traces=[{**node, 'truth_value': values[node['id']].json()} for node in traces], excluded=excluded,
        training_report=model.training_report))
    write_json(out / 'summary.json', dict(passed=True, model_version=model.version,
        ledger_digest=model.ledger_digest, training_report=model.training_report, legal_default_eligible=False))
    return model
