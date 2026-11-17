"""Read-only correspondence reports. These records never return to inference."""
from dataclasses import asdict
import json
from pathlib import Path
from .contracts import Application, canonical, identity, sha
from .source_mapping import ARMS


def correspondence(root,reference,native):
    root=Path(root);reference=Path(reference);native=Path(native)
    audit=json.loads((reference/'mappings/audit.json').read_text())
    members=json.loads((reference/'mappings/memberships.json').read_text())
    replay=json.loads((native/'summary.json').read_text())
    results={}
    for arm in ARMS:
        stages={}
        generations=[g for g in audit['native_parameter_generations'] if f'/{arm}/' in g['native_checkpoint_reference']]
        for name,stage in replay['arms'][arm]['stages'].items():
            path=native/'raw'/Path(stage['native']['path']).name
            assert sha(path)==stage['native']['sha256']
            record=json.loads(path.read_text())
            query=record['query'].strip('()').split()
            histories=[r['term'] for r in record['facts'] if r['term'].startswith('(History ')]
            events=[dict(event_id=f"c18-native-input:{arm}:{name}:{i}",
                kind='synthetic_fixture_environment',source_artifact_path=f'artifacts/cycle18/native/raw/{path.name}',
                source_artifact_hash=sha(path),source_locator=f'/facts/{i}',payload=fact,
                admission_status='context',training_admission=False) for i,fact in enumerate(record['facts'])]
            app=Application(f'c18-native-application:{arm}:{name}',tuple(g['parameter_generation_id'] for g in generations),
                canonical(dict(attacker=query[1],target=query[2])),tuple(e['event_id'] for e in events),
                identity([query[-1],histories]),record['query'],f'artifacts/cycle18/native/raw/{path.name}',None,
                'Native selections and retained beliefs exposed; fired-rule parents unobserved')
            stages[name]=dict(application=asdict(app),environmental_events=events,input_facts=record['facts'],
                input_rules=record['rules'],answer=record['answer'],contrary=record['contrary'],
                classification=record['classification'],selected_count=len(record['selected']),retained_count=len(record['retained']))
        references={}
        for model in ('M-F','M-J-copy','M-J-upper','M-J-lower'):
            relative=f'reference_cases/primary/{arm}/{model}/result.json'
            fit=json.loads((reference/relative).read_text())
            references[model]=dict(path='artifacts/cycle18/contract/'+relative,sha256=sha(reference/relative),
                probability=fit['predictive_probability'],assumptions_id=fit['assumptions_id'],
                posterior_identity=fit['posterior_identity'],query=fit['query'])
        results[arm]=dict(native=stages,native_stamp_overlap=replay['arms'][arm]['diagnostic']['diagnostic']['overlap'],
            external_event_components=members[arm],original_native_generations=generations,reference=references,
            parameter_meaning='Hypothetical future qualified pipeline positive-output propensities; copy primary ties both channels',
            directly_comparable_quantities=False,
            reason='Native evidential support/confidence and hypothetical predictive probability have no established shared scale; no reference value fills native unknown')
    return dict(schema='cycle18-native-reference-correspondence-v1',arms=results,
        dataflow='Read-only reporting join after independent native and reference execution',
        reference_source_sha256=sha(reference/'reference_cases/summary.json'),native_source_sha256=sha(native/'summary.json'))
