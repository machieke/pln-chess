"""Native preference boundaries, reversal, budgets and provenance integrity."""
import copy
from dataclasses import replace
import pytest
from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import NativeError
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle12.ontology import CONCEPTS
from pln_chess.cycle13.ontology import GRAMMAR,FIELDS,ABSTRACTIONS,CHANNELS,seal,project,reverse_packet,key
from pln_chess.cycle13.model import PreferenceModel
from pln_chess.cycle13.inference import infer_preferences,PreferenceNativeSession
from pln_chess.cycle13.evidence import PreferenceLedger


def packet(first=(2,2,2,2),second=(1,1,1,1),horizon=1):
    def counts(n):
        return dict(supported=n,contradicted=0,unknown=0,incomplete=0,queried=n)
    def profile(values):
        return dict(fields={f:counts(v) for f,v in zip(FIELDS,values)},
            concepts={c:counts(0) for c in CONCEPTS},concept_scope='bounded-role-candidates')
    return seal(dict(schema=GRAMMAR,profiles=dict(before=profile((0,0,0,0)),A=profile(first),B=profile(second)),
        horizon=horizon,complete=True,gaps=[],source='controlled-test-observation',provenance={},
        candidate_descriptors=dict(A={},B={})))


def model_for(runtime,p,abstraction='relational',contradiction=False):
    observation=project(p,abstraction);model=PreferenceModel(runtime.version,abstraction=abstraction)
    model.hypotheses[observation['rule_id']]=dict(id=observation['rule_id'],descriptor=observation['descriptor'],
        channels={c:dict(strength=.99 if c=='first' or (contradiction and c=='second') else .01,confidence=.9) for c in CHANNELS},
        evidence_ids=['controlled-evidence'],dependence_groups=['controlled-group'],
        supporting_evidence={c:['controlled-evidence'] if c=='first' else [] for c in CHANNELS})
    return model


def query(p,model,runtime,**kwargs):
    return infer_preferences([p],model,runtime=runtime,**kwargs)['comparisons'][0]


@pytest.mark.parametrize('abstraction',ABSTRACTIONS)
def test_reversal_retains_rule_evidence_and_swaps_native_channels(abstraction,runtime):
    p=packet(second=(0,0,0,0));model=model_for(runtime,p,abstraction)
    original=query(p,model,runtime);reverse=query(reverse_packet(p),model,runtime)
    assert original['rule_id']==reverse['rule_id']
    assert original['evidence_ids']==reverse['evidence_ids']
    assert original['channels']['A']==reverse['channels']['B']
    assert original['status']=='A-preferred' and reverse['status']=='B-preferred'


def test_native_trace_is_replayable_and_never_a_joint_theorem(runtime):
    p=packet();row=query(p,model_for(runtime,p),runtime)
    native=runtime.batch([(n['id'],n['native_expression']) for n in row['proof_trace']])
    assert row['proof_id']==digest(row['proof_trace'])
    assert all(native[n['id']].json()==n['truth_value'] for n in row['proof_trace'])
    assert row['conditional_proof_complete'] and not row['joint_proof_complete']
    assert row['actionable_move'] is None and row['strategic_score'] is None


def test_no_rule_and_no_transitive_rule_means_abstention(runtime):
    p=packet();model=model_for(runtime,p)
    unseen=packet((0,3,0,2),(2,0,2,0))
    assert query(unseen,model,runtime)['status']=='indeterminate'
    model.hypotheses.clear()
    assert not query(p,model,runtime)['conditional_proof_complete']


def test_supported_contradictions_remain_indeterminate(runtime):
    p=packet();row=query(p,model_for(runtime,p,contradiction=True),runtime)
    assert row['contradiction'] and row['status']=='indeterminate'
    assert row['conditional_proof_complete'] and len(row['proof_trace'])==3


def test_collapsed_descriptor_cannot_answer_directionally(runtime):
    p=packet((1,1,1,1),(1,1,1,1));row=query(p,model_for(runtime,p),runtime)
    assert not project(p)['distinguishable'] and row['status']=='indeterminate'


def test_incomplete_observation_and_zero_sensor_do_not_invent_counterevidence(runtime):
    p=packet();model=model_for(runtime,p)
    broken=seal({**p,'complete':False,'gaps':['Missing endpoint']})
    assert query(broken,model,runtime)['status']=='incomplete'
    zero=query(p,model,runtime,options=FieldOptions(sensor_confidence=0))
    assert zero['status']=='indeterminate' and not zero['proof_trace']
    assert all(c['raw_stv']==dict(strength=.5,confidence=0.) for c in zero['channels'].values())


def test_duplicate_queries_charge_logical_budget_even_with_native_cache(runtime):
    p=packet();model=model_for(runtime,p);session=PreferenceNativeSession(runtime)
    query(p,model,runtime,session=session)
    limited=infer_preferences([p,p],model,runtime=runtime,session=session,options=FieldOptions(max_native_invocations=3))
    assert [r['status'] for r in limited['comparisons']]==['A-preferred','incomplete']
    assert limited['execution']['truncated']
    assert query(p,model,runtime,session=session,options=FieldOptions(max_native_invocations=0))['status']=='incomplete'


def test_returned_mutation_and_changed_model_do_not_poison_reuse(runtime):
    p=packet();model=model_for(runtime,p);session=PreferenceNativeSession(runtime)
    row=query(p,model,runtime,session=session);expected=copy.deepcopy(row)
    row['proof_trace'].clear();row['channels']['A']['raw_stv']['strength']=0
    assert query(p,model,runtime,session=session)==expected
    model.hypotheses.clear()
    assert query(p,model,runtime,session=session)['status']=='indeterminate'


def test_native_failure_remains_incomplete_without_host_fallback(runtime,monkeypatch):
    p=packet();session=PreferenceNativeSession(runtime)
    def fail(*args):
        raise NativeError('controlled native failure')
    monkeypatch.setattr(session.native,'batch',fail)
    row=query(p,model_for(runtime,p),runtime,session=session)
    assert row['status']=='incomplete' and not row['conditional_proof_complete'] and not row['proof_trace']


def test_descriptor_rejects_absolute_coordinates_and_model_tampering(runtime,tmp_path):
    p=packet();d=project(p)['descriptor'];d['square']='e4'
    with pytest.raises(ValueError):
        key(d)
    path=tmp_path/'model.json';model_for(runtime,p).export(path)
    saved=read_json(path);saved['hypotheses'][next(iter(saved['hypotheses']))]['channels']['first']['strength']=.2
    write_json(path,saved)
    with pytest.raises(ValueError):
        PreferenceModel.load(path,runtime)


def payload(runtime,identifier='observation-one'):
    p=project(packet())
    return dict(observation_id=identifier,source_position='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',candidate_moves=['a1a2','a1b1'],
        descriptor=p['descriptor'],packet=p,label='A',canonical_label='first',source='controlled-test',
        source_game='controlled-game',dependence_group='controlled-group',transformation_lineage=['controlled-group'],
        temporal_context=dict(horizon=1),model_versions={},runtime_version=runtime.version,dataset_hash='test-data',
        reference_evidence_id='controlled-label',observation_confidence=.5,scope='Controlled test only')


def test_ledger_is_idempotent_and_rejects_whole_conflicting_batch(runtime,tmp_path):
    ledger=PreferenceLedger(tmp_path/'evidence.jsonl');p=payload(runtime)
    first=ledger.append_many([p,p]);before=ledger.path.read_bytes()
    assert first[0]==first[1] and ledger.append_many([p])==first[:1]
    assert ledger.path.read_bytes()==before
    changed={**p,'label':'B','canonical_label':'second'}
    with pytest.raises(ValueError):
        ledger.append_many([payload(runtime,'new-observation'),changed])
    assert ledger.path.read_bytes()==before


def test_horizon_and_partial_coverage_are_distinct_conditionals():
    p=packet();temporal=seal({**p,'horizon':2})
    partial=copy.deepcopy(p);partial['profiles']['A']['fields']['attack']['unknown']=1
    partial['profiles']['A']['fields']['attack']['queried']+=1;partial=seal(partial)
    assert len({project(v)['rule_id'] for v in (p,temporal,partial)})==3
    assert project(partial)['descriptor']['coverage']['attack']=='partial'
