import copy
import pytest

from pln_chess.common import digest
from pln_chess.cycle13 import ontology as old
from pln_chess.cycle14 import ontology as role
from pln_chess.cycle14.evidence import EvidenceLedger
from pln_chess.cycle14.model import PreferenceModel
from pln_chess.cycle14.inference import infer_preferences


def packet():
    def count():return dict(supported=0,contradicted=1,unknown=0,incomplete=0,queried=1)
    def profile():return dict(fields={f:count() for f in old.FIELDS},concepts={c:count() for c in old.CONCEPTS},concept_scope='bounded-role-candidates')
    base=old.seal(dict(schema=old.GRAMMAR,profiles={s:profile() for s in ('before','A','B')},horizon=1,
        complete=True,gaps=[],source='test-relative-observation',provenance={},candidate_descriptors={'A':{},'B':{}}))
    profiles={s:{r:{**count(),'available':True} for r in role.ROLES} for s in ('beforeA','beforeB','A','B')}
    profiles['A']['mover-attack'].update(supported=1,contradicted=0)
    return role.seal(dict(schema=role.GRAMMAR,base=base,role_profiles=profiles,
        observation_kind='separate-native-endpoint-projections',scope='Controlled unit fixture'))


def payload(label='A',identifier='observation-one'):
    observed=role.project(packet(),'role-change-v1')
    return dict(observation_id=identifier,source_position='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',candidate_moves=['a1a2','a1b1'],
        descriptor=observed['descriptor'],packet=observed,label=label,canonical_label='first' if label=='A' else 'second' if label=='B' else label,
        source='unit-fixture',source_game='independent-game',dependence_group='shared-root',transformation_lineage=['shared-root'],
        temporal_context={'horizon':1},model_versions={},runtime_version='pinned-test-runtime',dataset_hash='unit-dataset',
        reference_evidence_id='reference-'+label,observation_confidence=.5,scope='Controlled ledger fixture')


def test_roles_distinguish_aggregate_collision_and_reversal_is_equivariant():
    p=packet();assert not role.project(p)['distinguishable']
    for abstraction in role.ABSTRACTIONS[1:]:
        first=role.project(p,abstraction);second=role.project(role.reverse_packet(p),abstraction)
        assert first['distinguishable'] and first['rule_id']==second['rule_id']
        assert first['canonical_order']==list(reversed(second['canonical_order']))
        changed=copy.deepcopy(p);changed['base']['source']='another-source'
        changed['base']['provenance']={'source_game':'unseen-game','fen':'not a predictive feature','proof_id':'other-proof'}
        changed['base']=old.seal(changed['base']);changed=role.seal(changed)
        assert role.project(changed,abstraction)['rule_id']==first['rule_id']
        illegal=copy.deepcopy(first['descriptor']);illegal['features']['square:e4']=1
        with pytest.raises(ValueError):role.key(illegal)


def test_missing_context_does_not_become_zero_mobility():
    omitted=role.omit_context(packet());observed=role.project(omitted,'role-change-v1')
    assert omitted['base']['profiles']['A']['fields']['mobility']['unknown']==1
    assert observed['descriptor']['coverage']['role:mover-mobility']=='unqueried'
    assert observed['descriptor']['coverage']['mobility']=='partial'
    assert not observed['distinguishable']


def test_generation_replay_idempotence_rollback_and_atomic_conflict(tmp_path):
    ledger=EvidenceLedger(tmp_path/'ledger.jsonl');original=payload('unknown');revised=payload('A')
    ledger.append_many([original,original],generation='g1');first=ledger.path.read_bytes()
    ledger.append_many([original],generation='g1');assert ledger.path.read_bytes()==first
    ledger.append_many([revised],generation='g2')
    assert len(ledger.records())==1 and ledger.records()[0]['generation']=='g2'
    assert len(ledger.snapshot()['versions'])==2
    ledger.activate('g1',['observation-one'],rollback=True)
    assert ledger.records()[0]['payload']['label']=='unknown'
    before=ledger.path.read_bytes()
    with pytest.raises(ValueError,match='Conflicting'):
        ledger.append_many([payload('B','new-observation'),payload('B')],generation='g2')
    assert ledger.path.read_bytes()==before
    with pytest.raises(ValueError,match='missing'):
        ledger.transact([dict(action='ingest',generation='g3',payloads=[revised]),
            dict(action='activate',generation='g3',observations=['does-not-exist'])])
    assert ledger.path.read_bytes()==before
    assert EvidenceLedger.replay(ledger.history())['active_digest']==ledger.snapshot()['active_digest']


def test_generation_chain_is_deterministic_and_tampering_is_rejected(tmp_path):
    a=EvidenceLedger(tmp_path/'a.jsonl');b=EvidenceLedger(tmp_path/'b.jsonl')
    for ledger in (a,b):
        ledger.append_many([payload('unknown')],generation='old')
        ledger.append_many([payload('B')],generation='new')
    assert a.path.read_bytes()==b.path.read_bytes()
    a.path.write_text(a.path.read_text().replace('reference-B','reference-A'))
    with pytest.raises(ValueError,match='Corrupt'):a.snapshot()


def test_refined_native_conditionals_preserve_three_channels_and_no_joint_claim(runtime):
    p=packet();observation=role.project(p,'role-change-v1');model=PreferenceModel(runtime.version,abstraction='role-change-v1')
    model.hypotheses[observation['rule_id']]=dict(id=observation['rule_id'],descriptor=observation['descriptor'],
        channels={c:dict(strength=.99 if c=='first' else .01,confidence=.9) for c in role.CHANNELS},
        evidence_ids=['independent-one'],dependence_groups=['root-one'],
        supporting_evidence={c:['independent-one'] if c=='first' else [] for c in role.CHANNELS})
    rows=infer_preferences([p,role.reverse_packet(p)],model,runtime=runtime)['comparisons']
    assert [r['status'] for r in rows]==['A-preferred','B-preferred']
    assert rows[0]['channels']['A']==rows[1]['channels']['B']
    for row in rows:
        assert row['conditional_proof_complete'] and not row['joint_proof_complete']
        assert row['proof_id']==digest(row['proof_trace']) and row['actionable_move'] is None
        values=runtime.batch([(n['id'],n['native_expression']) for n in row['proof_trace']])
        assert all(values[n['id']].json()==n['truth_value'] for n in row['proof_trace'])
