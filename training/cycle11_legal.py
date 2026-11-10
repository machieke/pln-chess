"""Native exact-local revision experiment; accepted C8 remains unchanged."""
import argparse
from collections import defaultdict
import copy
from dataclasses import asdict
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.pln import Runtime, TV
from pln_chess.learning import PRIOR
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle10.temporal import replay
from evaluation.cycle7_io import pack
from training.cycle11_fields import independent_components


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    dataset = read_json(out / 'datasets/legal-curriculum.json')
    expected = dataset.pop('hash')
    assert digest(dataset) == expected
    runtime = Runtime(timeout=600)
    frozen = PromotionModel.load(ROOT / 'artifacts/cycle10/model/C10-default.json', runtime)
    model = copy.deepcopy(frozen)
    source = model.source_model()
    original_source = copy.deepcopy(source.source)
    ledger, bykey = [], defaultdict(list)
    for row in dataset['examples']:
        if row['split'] != 'train':
            continue
        history = replay(**row['history_input'], model_version=frozen.version, runtime_version=runtime.version)
        assert not history['conflicts'] and history['resulting_fen'] == row['fen']
        payload = dict(input=dict(fen=row['fen'], move=row['move']), descriptor=row['descriptor'],
            target='LocalAdmissibility', source=row['source'], source_kind=row['source_kind'],
            dependence_group=row['dependence_group'], transformation_lineage=row['transformation_lineage'],
            local_transition_label=row['movement_label'], global_reference_label=row['label'],
            observation_tv=TV(float(row['movement_label']), row['confidence']).json(),
            temporal_transport_id=history['id'], temporal_input=row['history_input'],
            local_context_observation='Known supplied board plus explicit predecessor/metadata; no zero-confidence missing-history record is reused as new evidence.',
            runtime_version=runtime.version, dataset_hash=expected,
            supervision='Offline reference pseudo-legality; castling pseudo-legality retains the reference library attack-path conditions.',
            scope='Declared synthetic training context. Local conditional support is not a universal king-safety proof.')
        evidence = digest(payload)
        ledger.append(dict(evidence_id=evidence, payload=payload))
        bykey[row['identifier']].append(dict(evidence_id=evidence, label=row['movement_label'],
            confidence=row['confidence'], dependence_group=row['dependence_group'],
            transformation_lineage=row['transformation_lineage'], descriptor=row['descriptor']))
    jobs, traces, revisions, excluded = [], [], [], []
    for identifier, records in sorted(bykey.items()):
        original = copy.deepcopy(source.hypotheses.get(identifier))
        refs = [TV.from_json(original[k]).metta() if original else PRIOR.metta() for k in ('positive', 'negative')]
        ids = list(original['evidence_ids']) if original else []
        groups = set(original['dependence_groups']) if original else set()
        positive = list(original['supporting_evidence']) if original else []
        negative = list(original['contradicting_evidence']) if original else []
        changed = False
        for component in independent_components(records):
            if component['contradictory'] or groups.intersection(component['groups']):
                excluded.append(dict(hypothesis=identifier, groups=component['groups'],
                    evidence_ids=[r['evidence_id'] for r in component['records']],
                    reason='contradictory-dependent-component' if component['contradictory'] else 'existing-ancestry-overlap'))
                continue
            representative = component['records'][0]
            changed = True
            evidence = representative['evidence_id']
            ids.append(evidence)
            groups.update(component['groups'])
            (positive if representative['label'] else negative).append(evidence)
            if len(component['records']) > 1:
                excluded.append(dict(hypothesis=identifier, groups=component['groups'], representative=evidence,
                    evidence_ids=[r['evidence_id'] for r in component['records'][1:]], reason='shared-dependence-component'))
            for channel, label in enumerate((representative['label'], not representative['label'])):
                name = f'legalrevision{len(jobs)}'
                observation = TV(float(label), representative['confidence'])
                expression = f'(Truth_Revision {refs[channel]} {observation.metta()})'
                jobs.append((name, expression))
                traces.append(dict(id=name, operator='Truth_Revision', native_expression=expression,
                    hypothesis=identifier, channel='positive' if channel == 0 else 'negative',
                    prior_or_previous=refs[channel], observation_tv=observation.json(),
                    evidence_id=evidence, dependence_groups=component['groups']))
                refs[channel] = f'({name})'
        if changed:
            revisions.append(dict(identifier=identifier, before=original, refs=refs, after=dict(id=identifier,
                target='LocalAdmissibility', descriptor=records[0]['descriptor'], tier=4, level=0,
                evidence_ids=ids, dependence_groups=sorted(groups), supporting_evidence=positive,
                contradicting_evidence=negative, new_training=True, origin='C11-native-exact-special-move-revision')))
    session = NativeSession(runtime)
    session.bind(digest([runtime.manifest, expected, frozen.version]))
    values = session.batch(jobs)
    for change in revisions:
        refs = change.pop('refs')
        change['after'].update(positive=values[refs[0][1:-1]].json(), negative=values[refs[1][1:-1]].json())
        source.hypotheses[change['identifier']] = change['after']
    source.variant = 'C11-special-local-experimental'
    source.training_report = {**source.training_report, 'C11_exact_special_revision': True}
    assert source.source == original_source, 'The frozen native source is never changed'
    model.source = asdict(source)
    model.variant = 'C11-special-local-experimental'
    model.training_report = dict(base_model_version=frozen.version, dataset_hash=expected,
        records=len(ledger), revised_hypotheses=len(revisions), native_revision_nodes=len(jobs),
        executed_native_operators=session.calls, dependence_components=True,
        excluded_components=len(excluded), ledger_digest=digest(ledger), frozen_source_preserved=True,
        new_learning_promoted=False, thresholds_changed=False, final_external_positions_used_for_training=False,
        old_failures_are_development_diagnostics=True,
        scope='Experimental exact local conditionals using new event-backed synthetic supervision. Full safety remains the existing native negative-proof and conservative observation policy.')
    model.export(out / 'model/C11-special-local.json')
    assert PromotionModel.load(out / 'model/C11-special-local.json', runtime).version == model.version
    pack(out / 'legal/training.json.xz', dict(records=ledger, revisions=revisions, excluded=excluded,
        native_revision_trace=[{**t, 'truth_value': values[t['id']].json()} for t in traces],
        training_report=model.training_report, model_version=model.version))
    write_json(out / 'legal/training-summary.json', dict(model_version=model.version, training_report=model.training_report,
        hypotheses=[dict(id=r['identifier'], before=None if r['before'] is None else
            {k:r['before'][k] for k in ('positive','negative','evidence_ids')},
            after={k:r['after'][k] for k in ('descriptor','positive','negative','evidence_ids','dependence_groups')}) for r in revisions]))
    print('Native legal completion experiment trained', model.version, model.training_report, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
