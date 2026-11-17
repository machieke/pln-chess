from dataclasses import replace
import pytest
from pln_chess.common import ROOT
from research.cycle18.source_mapping import map_sources, RULES
from research.cycle18.controls import run, measurement_noise
from research.cycle18.reference_joint import fit
from research.cycle18.contracts import observation,Kind
from research.cycle18.applications import ApplicationJournal


def test_source_bound_replay_application_revision_conflict_and_cycle_controls():
    registry,arms,_=map_sources(ROOT);d=run(registry,arms)
    assert d['passed'] and d['duplicate_added']==d['cycle_evidence_added']==0
    assert [d['application_repeats'][str(n)]['applications'] for n in (1,10,100)]==[1,10,100]
    assert d['copy_conflict']['status']=='inconsistent_evidence'
    assert d['full_recomputation_order_parity']


def test_derived_annotation_not_an_external_update_and_unknown_not_false():
    registry,arms,_=map_sources(ROOT)
    annotation=next(e for e in registry.all() if e.observation_kind==Kind.DERIVED and e.admission_status=='admitted')
    with pytest.raises(ValueError):fit(registry,{annotation.event_id:RULES})
    original=registry.get(next(iter(arms['S-AA'])))
    unknown=observation('unknown',dict(origin='quarantined-external-measurement',labels=dict(zip(RULES,(None,True)))),
        episode='new',groups=['new'],kind=Kind.EVALUATION,method='quarantined unknown',admission='admitted')
    registry.register(unknown)
    with pytest.raises(ValueError):fit(registry,{unknown.event_id:RULES})


def test_same_source_distinct_measurements_need_declared_joint_model():
    registry,arms,_=map_sources(ROOT);eid=next(iter(arms['S-AA']));original=registry.get(eid)
    other=replace(original,event_id='another-genuine-event')
    registry.register(other)
    with pytest.raises(ValueError,match='joint observation contract'):
        fit(registry,{eid:RULES,other.event_id:RULES})


def test_application_budget_and_unknown_parent_rejected():
    registry,arms,_=map_sources(ROOT);f=fit(registry,arms['D-AB']);j=ApplicationJournal(limit=1)
    args=dict(bindings={},environment=[],state='s',history='h',query='q')
    with pytest.raises(ValueError):j.apply(f,parents=['absent'],**args)
    j.apply(f,**args)
    with pytest.raises(ValueError,match='resource limit'):j.apply(f,**args)
