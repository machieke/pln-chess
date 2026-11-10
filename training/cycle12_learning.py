"""Native revision of limited concept conditionals, with ancestry controls."""
import argparse
from collections import defaultdict
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from pln_chess.learning import PRIOR
from pln_chess.pln import Runtime, TV
from pln_chess.cycle3.native import NativeSession
from training.cycle11_fields import independent_components
from evaluation.cycle7_io import pack


def train(records,runtime,out,*,dataset_hash,variant='C12-concept-trained'):
    from pln_chess.cycle12.ontology import observe_concept, CONCEPTS
    from pln_chess.cycle12.model import ConceptModel
    out=Path(out);bykey=defaultdict(list);ledger=[]
    for record in records:
        if record['split']!='train':raise ValueError('Only registered training records may update a concept model')
        observation=observe_concept(record['input'])
        if not observation['complete']:raise ValueError('Training observation is incomplete')
        payload=dict(example_id=record['id'],input=record['input'],observation=observation,
            label=record['reference']['label'],target=record['reference']['target'],
            dependence_group=record['dependence_group'],transformation_lineage=record['transformation_lineage'],
            observation_confidence=.5,dataset_hash=dataset_hash,
            source='offline-limited-concept-reference',reference=record['reference'],
            runtime_version=runtime.version)
        identifier=digest(payload)
        ledger.append(dict(evidence_id=identifier,payload=payload))
        bykey[observation['rule_id']].append(dict(evidence_id=identifier,label=payload['label'],
            dependence_group=payload['dependence_group'],transformation_lineage=payload['transformation_lineage'],
            confidence=payload['observation_confidence'],observation=observation))
    jobs=[];traces=[];states={};excluded=[]
    for identifier,rows in sorted(bykey.items()):
        refs=[PRIOR.metta(),PRIOR.metta()];ids=[];groups=set();positive=[];negative=[]
        for component in independent_components(rows):
            if component['contradictory']:
                excluded.append(dict(rule_id=identifier,reason='contradictory-dependent-component',groups=component['groups'],
                    evidence_ids=[r['evidence_id'] for r in component['records']]))
                continue
            representative=component['records'][0];evidence=representative['evidence_id']
            ids.append(evidence);groups.update(component['groups'])
            (positive if representative['label'] else negative).append(evidence)
            if len(component['records'])>1:
                excluded.append(dict(rule_id=identifier,reason='shared-ancestry',representative=evidence,
                    evidence_ids=[r['evidence_id'] for r in component['records'][1:]],groups=component['groups']))
            for channel,label in enumerate((representative['label'],not representative['label'])):
                name=f'conceptrevision{len(jobs)}';observation=TV(float(label),representative['confidence'])
                expression=f'(Truth_Revision {refs[channel]} {observation.metta()})'
                jobs.append((name,expression))
                traces.append(dict(id=name,operator='Truth_Revision',native_expression=expression,
                    rule_id=identifier,channel='positive' if channel==0 else 'negative',previous=refs[channel],
                    observation_tv=observation.json(),evidence_id=evidence,dependence_groups=component['groups']))
                refs[channel]=f'({name})'
        if ids:
            observed=rows[0]['observation']
            states[identifier]=dict(id=identifier,concept=observed['concept'],target=CONCEPTS[observed['concept']]['target'],
                descriptor=observed['descriptor'],refs=refs,evidence_ids=ids,dependence_groups=sorted(groups),
                supporting_evidence=positive,contradicting_evidence=negative,
                origin='learned-native-conditional-on-host-supplied-structural-packet')
    session=NativeSession(runtime);session.bind(digest([runtime.manifest,dataset_hash,variant,sorted(bykey)]))
    values=session.batch(jobs);model=ConceptModel(runtime.version,variant=variant)
    for identifier,state in states.items():
        refs=state.pop('refs')
        model.hypotheses[identifier]={**state,'positive':values[refs[0][1:-1]].json(),'negative':values[refs[1][1:-1]].json()}
    model.ledger_digest=digest(sorted({r['evidence_id'] for r in ledger}))
    model.training_report=dict(dataset_hash=dataset_hash,training_examples=len(records),
        unique_evidence=len({r['evidence_id'] for r in ledger}),hypotheses=len(states),
        native_revision_nodes=len(jobs),executed_native_operators=session.calls,native_cache_hits=session.hits,
        excluded_components=len(excluded),heldout_labels_used=False,neutral_prior=PRIOR.json(),
        seeded_structure='Typed role packets and local relative observation pooling; no positive strategic rule is supplied.',
        complete_native_concept_theorems=0,
        scope='Learned conditionals on observed composite packets. No conjunction rule, strategic score, overload proof or safe-mobility theorem is learned.')
    model.export(out/'checkpoint.json')
    assert ConceptModel.load(out/'checkpoint.json',runtime).version==model.version
    pack(out/'ledger.json.xz',ledger)
    pack(out/'native-training.json.xz',dict(model_version=model.version,dataset_hash=dataset_hash,
        traces=[{**node,'truth_value':values[node['id']].json()} for node in traces],excluded=excluded,
        training_report=model.training_report))
    return model


def run(out):
    from pln_chess.cycle12.model import ConceptModel
    out=Path(out)
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    assert read_json(out/'datasets/audit.json')['passed']
    data=read_json(out/'datasets/concepts.json')
    expected=data.pop('hash');assert digest(data)==expected;data['hash']=expected
    runtime=Runtime(timeout=600)
    records=[r for r in data['records'] if r['split']=='train']
    model=train(records,runtime,out/'learning/main',dataset_hash=expected)
    model.export(out/'model/C12-concept-trained.json')
    empty=ConceptModel(runtime.version,variant='C12-concept-empty')
    empty.export(out/'model/C12-concept-empty.json')
    write_json(out/'learning/summary.json',dict(passed=True,model_version=model.version,empty_model_version=empty.version,
        dataset_hash=expected,training_report=model.training_report,legal_default_eligible=False))
    print('Native concept training complete',model.version,model.training_report,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
