"""Exact incremental reuse, graph provenance and supplied-sequence gaps."""
import copy
from dataclasses import replace
import pytest

from pln_chess.common import ROOT, digest, read_json
from pln_chess.domain import Position, Piece, parse_square
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle11.fields.inference import FieldOptions, build_field
from pln_chess.cycle12.incremental import IncrementalFieldSession, structural_successor
from pln_chess.cycle12.graph import build_graph, validate_graph, compare_fields
from pln_chess.cycle12.temporal import replay_fields, semantic_replay


@pytest.fixture(scope='module')
def evolution_model(runtime):
    return FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)


@pytest.mark.parametrize('fen,move',[
    ('7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1','d4f5'),
    ('7k/8/8/R4pP1/8/8/8/6K1 w - f6 0 2','g5f6'),
    ('7k/1P6/8/8/8/8/8/6K1 w - - 0 1','b7b8n'),
    ('6k1/8/8/8/8/8/8/4K2R w K - 0 1','e1g1'),
    ('7k/8/8/8/3rp3/2B5/8/1K2R3 w - - 0 1','c3d4'),
])
def test_incremental_fields_match_every_full_record(fen,move,evolution_model,runtime):
    position=Position.from_fen(fen);session=IncrementalFieldSession(runtime)
    session.build(position,evolution_model,source='unit-evolution')
    successor=structural_successor(position,move)
    cached=session.build(successor,evolution_model,source='unit-evolution')
    full=build_field(successor,evolution_model,runtime=runtime,source='unit-evolution')
    assert cached['relations']==full['relations']
    assert cached['directional_index']==full['directional_index'] and cached['projection']==full['projection']
    assert cached['incremental']['reused_relations']>0
    assert cached['incremental']['scheduled_relations']<len(cached['relations'])
    graph=build_graph(cached);assert validate_graph(graph)
    assert graph==build_graph(full)


def test_unknown_status_edit_invalidates_every_affected_ray(evolution_model,runtime):
    initial=Position.from_fen('7k/8/8/8/R6p/8/8/6K1 w - - 0 1')
    changed=replace(initial,unknown_squares=[parse_square('g4')])
    session=IncrementalFieldSession(runtime);session.build(initial,evolution_model,source='unit-evolution')
    cached=session.build(changed,evolution_model,source='unit-evolution')
    full=build_field(changed,evolution_model,runtime=runtime,source='unit-evolution')
    assert cached['relations']==full['relations']
    ray=next(r for r in cached['relations'] if r['source_square']=='a4' and r['target_square']=='h4' and r['family']=='attack')
    assert ray['classification']=='unknown'


def test_ep_metadata_alone_invalidates_ordinary_mobility_domain(evolution_model,runtime):
    initial=Position.from_fen('7k/8/8/R4pP1/8/8/8/6K1 w - f6 0 2')
    changed=replace(initial,ep=None)
    session=IncrementalFieldSession(runtime);session.build(initial,evolution_model,source='unit-evolution')
    cached=session.build(changed,evolution_model,source='unit-evolution')
    full=build_field(changed,evolution_model,runtime=runtime,source='unit-evolution')
    assert cached['relations']==full['relations']
    assert cached['incremental']['metadata_invalidations']>0


def test_incremental_rebinds_source_model_and_selection(evolution_model,runtime):
    position=Position.from_fen('7k/8/8/8/R6p/8/8/6K1 w - - 0 1');session=IncrementalFieldSession(runtime)
    initial=session.build(position,evolution_model,source='source-a')
    for model,source,families in ((evolution_model,'source-b',None),(FieldModel(runtime.version),'source-b',None),
                                   (evolution_model,'source-a',['defense'])):
        cached=session.build(position,model,source=source,families=families)
        full=build_field(position,model,runtime=runtime,source=source,families=families)
        assert cached['relations']==full['relations']
    # A returned field is a client-owned copy, including nested proof nodes.
    initial['relations'][0]['gaps'].append('client modification')
    assert all('client modification' not in r['gaps'] for r in session.build(position,evolution_model,source='source-a')['relations'])


def test_incremental_logical_budget_is_not_bypassed(evolution_model,runtime):
    position=Position.from_fen('7k/8/8/8/R6p/8/8/6K1 w - - 0 1');session=IncrementalFieldSession(runtime)
    session.build(position,evolution_model)
    options=FieldOptions(max_native_invocations=0)
    reused=session.build(position,evolution_model,options=options)
    full=build_field(position,evolution_model,runtime=runtime,options=options)
    assert reused['relations']==full['relations'] and reused['execution']['truncated']


def test_unknown_moved_entity_stays_unknown():
    p=Position.from_fen('6k1/8/8/8/8/8/8/4K2R w K - 0 1',unknown_squares=[parse_square('h1')])
    next_state=structural_successor(p,'e1g1')
    assert parse_square('f1') in next_state.unknown_squares


def test_comparison_never_assigns_native_truth_to_host_deltas(evolution_model,runtime):
    p=Position.from_fen('7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1')
    before=build_field(p,evolution_model,runtime=runtime)
    after=build_field(structural_successor(p,'d4f5'),evolution_model,runtime=runtime)
    changes=compare_fields(before,after)
    assert changes
    assert all(d['truth_value'] is None and d['origin']=='host-comparison' for d in changes)
    assert any(d['predicate']=='OpensAttack' for d in changes)


def test_graph_edges_keep_native_and_scheduler_claims_distinct(evolution_model,runtime):
    p=Position.from_fen('7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1')
    graph=build_graph(build_field(p,evolution_model,runtime=runtime))
    assert validate_graph(graph)
    assert any(e['origin']=='native' for e in graph['edges'])
    assert any(e['origin']=='host-scheduling' for e in graph['edges'])
    assert all(e['truth_value'] is None for e in graph['edges'] if e['origin']!='native')
    tampered=copy.deepcopy(graph)
    next(e for e in tampered['edges'] if e['origin']=='host-scheduling')['truth_value']={'strength':1.,'confidence':1.}
    with pytest.raises(ValueError):validate_graph(tampered)


@pytest.fixture(scope='module')
def supplied_sequence():
    return next(r['input'] for r in read_json(ROOT/'artifacts/cycle12/datasets/sequences.json')['sequences']
                if r['input']['id']=='promotion-threat')


def test_actual_sequence_replay_is_deterministic(supplied_sequence,evolution_model,runtime):
    a=replay_fields(supplied_sequence,evolution_model,runtime=runtime)
    b=replay_fields(supplied_sequence,evolution_model,runtime=runtime)
    assert semantic_replay(a)==semantic_replay(b)
    assert len(a['states'])==len(supplied_sequence['events'])+1
    assert all(t['status']=='observed-structural-transition' for t in a['transitions'])
    assert a['planned_moves'] is False and a['complete_history'] is True


def test_missing_event_keeps_observed_snapshot_but_not_transition(supplied_sequence,evolution_model,runtime):
    partial=copy.deepcopy(supplied_sequence);partial['events'][1]['move']=None
    replay=replay_fields(partial,evolution_model,runtime=runtime)
    assert not replay['complete_history']
    assert replay['transitions'][1]['status']=='missing-event-observed-state'
    assert replay['transitions'][1]['native_temporal_proof'] is False
    assert replay['states'][2]['field']['fen']==partial['events'][1]['observed_fen']
    assert replay['transitions'][1]['changes']==[]


def test_missing_event_without_snapshot_does_not_invent_states(supplied_sequence,evolution_model,runtime):
    partial=copy.deepcopy(supplied_sequence);partial['events'][1]['move']=None;partial['events'][1].pop('observed_fen')
    replay=replay_fields(partial,evolution_model,runtime=runtime)
    assert replay['states'][2]['field'] is None
    assert replay['transitions'][1]['status']=='missing-event-unknown-state'
    assert not replay['complete_history']


def test_conflicting_observed_successor_is_not_silently_replaced(supplied_sequence,evolution_model,runtime):
    conflict=copy.deepcopy(supplied_sequence);conflict['events'][0]['observed_fen']=conflict['initial_fen']
    replay=replay_fields(conflict,evolution_model,runtime=runtime)
    assert replay['transitions'][0]['status']=='conflicting-successor'
    assert replay['conflicts'] and not replay['complete_history']
    assert replay['transitions'][0]['changes']==[]


def test_zero_confidence_event_does_not_gain_certain_fields(supplied_sequence,evolution_model,runtime):
    partial=copy.deepcopy(supplied_sequence);partial['events'][0]['confidence']=0
    replay=replay_fields(partial,evolution_model,runtime=runtime)
    assert all(r['classification']=='unknown' for r in replay['states'][1]['field']['relations'])
    assert all(r['raw_stv']['confidence']==0 for r in replay['states'][1]['field']['relations'])


@pytest.mark.parametrize('change',[{'index':99},{'move':'x'},{'confidence':-1},{'confidence':True}])
def test_malformed_history_events_are_rejected(change,supplied_sequence,evolution_model,runtime):
    bad=copy.deepcopy(supplied_sequence);bad['events'][0].update(change)
    with pytest.raises(ValueError):replay_fields(bad,evolution_model,runtime=runtime)
