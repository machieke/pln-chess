from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import pytest
from pln_chess.common import ROOT
from research.cycle18.contracts import Kind, Registry, observation, identity, canonical, ParameterGeneration
from research.cycle18.source_mapping import map_sources, ARMS, RULES


@pytest.fixture(scope='module')
def mapped():
    return map_sources(ROOT)


def test_all_original_rows_and_revision_receipts_are_reconciled(mapped):
    registry, arms, audit=mapped
    assert (audit['preparation_records'],audit['admitted_annotations'],audit['excluded_annotations'])==(432,48,384)
    assert audit['admitted_vector_events']==24 and audit['revision_receipts_verified']==144
    assert audit['unique_admitted_annotation_ids_across_arms']==48
    assert len(registry.all())==864
    assert {a:len(m) for a,m in arms.items()}==dict(zip(ARMS,(12,12,24,24,23,18)))
    assert {a:sum(len(c) for c in m.values()) for a,m in arms.items()}==dict.fromkeys(ARMS,24)


def test_actual_two_annotations_share_one_evaluation_and_environment(mapped):
    registry,arms,audit=mapped
    for eid in arms['S-AA']:
        vector=registry.get(eid)
        annotations=[e for e in registry.all() if eid in e.parent_event_ids]
        assert len(annotations)==2 and {e.payload['rule'] for e in annotations}==set(RULES)
        assert annotations[0].payload['reference']==annotations[1].payload['reference']
        assert vector.payload['label_relationship']=='same-result-copied'
        assert registry.get(vector.parent_event_ids[0]).observation_kind==Kind.ENVIRONMENT
        assert vector.historical_measurement_time is None


def test_payload_and_event_and_source_identities_are_distinct():
    registry=Registry()
    def event(name,group='same-source'):
        return observation(name,dict(value=True),episode='episode',groups=[group],kind=Kind.ENVIRONMENT,method='control')
    a=event('event1');b=event('event2')
    assert a.payload_hash==b.payload_hash and a.event_id!=b.event_id
    assert registry.register(a) and registry.register(b) and not registry.register(a)
    assert len(registry.active())==2
    with pytest.raises(FrozenInstanceError):a.event_id='other'
    with pytest.raises(ValueError):replace(a,ancestry_groups=['mutable-source'])
    payload=a.payload;payload['value']=False
    assert a.payload['value'] is True
    with pytest.raises(ValueError):registry.register(replace(a,observed_variables_json=canonical(payload),payload_hash=identity(payload)))


def test_explicit_supersession_retains_original_and_rejects_fork():
    registry=Registry()
    a=observation('a',{'value':False},episode='e',groups=['g'],kind=Kind.ENVIRONMENT,method='old')
    registry.register(a)
    b=observation('b',{'value':True},episode='e',groups=['g'],kind=Kind.SUPERSEDED,method='corrected',supersedes='a')
    registry.register(b)
    assert registry.get('a')==a and registry.active()==(b,)
    with pytest.raises(ValueError):registry.register(replace(b,event_id='c'))
    with pytest.raises(ValueError):registry.register(replace(b,event_id='d',parent_event_ids=('missing',)))


def test_reference_generation_cannot_target_native_checkpoint():
    with pytest.raises(ValueError):
        ParameterGeneration.create(namespace='reference-only',schema_id='s',events=[],excluded=[],groups=[],
            learner='l',assumptions='m',uncertainty='{}',checkpoint='native-model.json')


def test_source_hash_or_payload_tampering_fails(tmp_path):
    # Copy only a modified corpus; mapper detects identity change before model reads.
    import json
    from research.cycle18.source_mapping import CORPUS,EVIDENCE
    for name in (CORPUS,EVIDENCE,'training/cycle17_shared_evidence.py','research/cycle16/corpus.py','research/cycle17/corpus.py'):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    p=tmp_path/CORPUS;d=json.loads(p.read_text());d['roots'][0]['state']['actor']='changed';p.write_text(json.dumps(d))
    with pytest.raises(AssertionError):map_sources(tmp_path)
