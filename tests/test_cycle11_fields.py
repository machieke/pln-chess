"""Native relation contracts, epistemic boundaries and exact cache invalidation."""
import builtins
import copy
from dataclasses import replace

import chess
import pytest

from pln_chess.common import digest, read_json, write_json
from pln_chess.domain import Position, Piece, parse_square
from pln_chess.api import find_move
from pln_chess.pln import NativeError
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle11.fields.ontology import observe_relation
from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, infer_queries, build_field
from pln_chess.spatial import translate, reflect_files, color_flip

CLEAR = '7k/8/8/8/R6p/8/8/6K1 w - - 0 1'
BLOCKED = '7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1'


@pytest.fixture(scope='module')
def field_model(runtime, tmp_path_factory):
    from training.cycle11_fields import train_queries
    from training.cycle11_data import labels
    # Declared synthetic unit controls, never part of the registered study.
    cases = [(CLEAR,'a4','h4'), (BLOCKED,'a4','h4'),
        ('7k/8/8/8/R6N/8/8/6K1 w - - 0 1','a4','h4'),
        ('8/8/8/8/R6k/8/8/6K1 b - - 0 1','a4','h4'),
        ('7k/8/8/8/3N4/8/8/6K1 w - - 0 1','d4','f5'),
        ('7k/8/8/8/3N4/8/8/6K1 w - - 0 1','d4','d5')]
    rows = []
    for group in range(3):
        for index, (fen, source, target) in enumerate(cases):
            row = dict(split='train', fen=fen, piece_square=source, target_square=target,
                labels=labels(chess.Board(fen), chess.parse_square(source), chess.parse_square(target)),
                source=f'declared-unit-observation-{group}-{index}', dependence_group=f'unit-control-{group}',
                transformation_lineage=[], observation_confidence=.5)
            row['id'] = digest(row)
            rows.append(row)
    return train_queries(rows, runtime, tmp_path_factory.mktemp('field-unit-learning'), dataset_hash=digest(rows), variant='unit-fixture-not-study')


def query(position, model, runtime, family='attack', source='a4', target='h4', session=None, options=None, provenance='unit-query'):
    position = Position.from_fen(position) if isinstance(position,str) else position
    return infer_queries([dict(id='unit-query', position=position, source_square=source, target_square=target,
        families=[family], source=provenance)], model, options or FieldOptions(timeout_seconds=180), runtime, session or FieldSession(runtime))


def relation(*args, **kwargs):
    return query(*args, **kwargs)['relations'][0]


def test_empty_model_does_not_supply_attack_from_geometry(runtime):
    row = relation(CLEAR, FieldModel(runtime.version), runtime)
    assert row['classification'] == 'unknown' and row['raw_stv'] == dict(strength=.5,confidence=0.)
    assert not row['conditional_proof_complete']


def test_learned_positive_and_negative_have_replayable_native_nodes(field_model,runtime):
    for fen, classification in ((CLEAR,'supported'),(BLOCKED,'contradicted')):
        row = relation(fen,field_model,runtime)
        assert row['classification'] == classification and row['conditional_proof_complete']
        assert not row['global_composition_complete'] and len(row['proof_trace']) == 4
        assert row['proof_id'] == digest(row['proof_trace'])
        trace = row['proof_trace']
        values = runtime.batch([(node['id'],node['native_expression']) for node in trace])
        assert all(values[node['id']].json() == node['truth_value'] for node in trace)


def test_geometry_is_separate_from_occupancy_and_legal_play(field_model,runtime):
    geometry = relation(BLOCKED,field_model,runtime,family='geometry')
    attack = relation(BLOCKED,field_model,runtime)
    assert geometry['classification'] == 'supported' and attack['classification'] == 'contradicted'
    assert geometry['rule_id'] != attack['rule_id']


def test_defense_domain_and_king_exposure_are_typed(field_model,runtime):
    defense = relation('7k/8/8/8/R6N/8/8/6K1 w - - 0 1',field_model,runtime,family='defense')
    exposure = relation('8/8/8/8/R6k/8/8/6K1 b - - 0 1',field_model,runtime,family='king-exposure')
    assert defense['classification'] == exposure['classification'] == 'supported'
    assert relation(CLEAR,field_model,runtime,family='defense')['classification'] == 'unknown'
    assert relation(CLEAR,field_model,runtime,family='king-exposure')['classification'] == 'unknown'


def test_unknown_required_ray_cell_withholds_context(field_model,runtime):
    position = Position.from_fen(CLEAR,unknown_squares=[parse_square('d4')])
    row = relation(position,field_model,runtime)
    assert row['classification'] == 'unknown' and not row['conditional_proof_complete']
    assert relation(position,field_model,runtime,family='geometry')['classification'] == 'supported'


def test_unknown_endpoint_is_not_empty_or_a_negative(field_model,runtime):
    position = Position.from_fen(CLEAR,unknown_squares=[parse_square('h4')])
    assert relation(position,field_model,runtime)['classification'] == 'unknown'


def test_distant_edit_preserves_local_proof_and_changes_state_binding(field_model,runtime):
    original = Position.from_fen(CLEAR)
    changed = replace(original,pieces=original.pieces+(Piece('distant','Bishop','Black',(1,6)),))
    session = FieldSession(runtime)
    a = query(original,field_model,runtime,session=session)
    b = query(changed,field_model,runtime,session=session)
    assert a['relations'][0]['proof_id'] == b['relations'][0]['proof_id']
    assert a['relations'][0]['raw_stv'] == b['relations'][0]['raw_stv']
    assert a['relations'][0]['snapshot_id'] != b['relations'][0]['snapshot_id']
    assert b['relation_cache_hits'] == 1


def test_long_ray_blocker_invalidates_and_matches_fresh_native_proof(field_model,runtime):
    position = Position.from_fen(CLEAR)
    changed = replace(position,pieces=position.pieces+(Piece('far-blocker','Knight','White',(6,3)),))
    session = FieldSession(runtime)
    query(position,field_model,runtime,session=session)
    cached = query(changed,field_model,runtime,session=session)
    fresh = query(changed,field_model,runtime)
    assert cached['relations'] == fresh['relations']
    assert cached['relation_cache_invalidations'] == 1
    assert cached['relations'][0]['classification'] == 'contradicted'


def test_source_provenance_change_rebinds_proof(field_model,runtime):
    session = FieldSession(runtime)
    a = query(CLEAR,field_model,runtime,session=session,provenance='observer-a')
    b = query(CLEAR,field_model,runtime,session=session,provenance='observer-b')
    fresh = query(CLEAR,field_model,runtime,provenance='observer-b')
    assert b['relations'] == fresh['relations'] and a['relations'][0]['proof_id'] != b['relations'][0]['proof_id']
    assert a['relations'][0]['raw_stv'] == b['relations'][0]['raw_stv']


def test_piece_identity_renaming_keeps_relative_knowledge(field_model,runtime):
    before = Position.from_fen(CLEAR)
    after = replace(before,pieces=tuple(replace(p,id='renamed-'+p.id) for p in before.pieces))
    a,b = relation(before,field_model,runtime),relation(after,field_model,runtime)
    assert (a['raw_stv'],a['rule_id']) == (b['raw_stv'],b['rule_id'])
    assert a['proof_id'] != b['proof_id'] and a['snapshot_id'] != b['snapshot_id']


def test_reflection_and_owner_orientation_transfer(field_model,runtime):
    before = Position.from_fen(CLEAR)
    a = relation(before,field_model,runtime)
    b = relation(reflect_files(before),field_model,runtime,source='h4',target='a4')
    c = relation(color_flip(before),field_model,runtime,source='a5',target='h5')
    assert a['rule_id'] == b['rule_id'] == c['rule_id']
    assert a['raw_stv'] == b['raw_stv'] == c['raw_stv']


def test_caller_cannot_mutate_cached_proof(field_model,runtime):
    session = FieldSession(runtime)
    first = query(CLEAR,field_model,runtime,session=session)
    expected = copy.deepcopy(first['relations'])
    first['relations'][0]['proof_trace'][0]['truth_value']['strength'] = .123
    first['relations'][0]['evidence_ids'].append('caller-forgery')
    assert query(CLEAR,field_model,runtime,session=session)['relations'] == expected


def test_checkpoint_mutation_invalidates_session(field_model,runtime):
    model = copy.deepcopy(field_model)
    session = FieldSession(runtime)
    before = query(CLEAR,model,runtime,session=session)
    hypothesis = model.hypotheses[before['relations'][0]['rule_id']]
    hypothesis['positive'] = dict(strength=0.,confidence=.9)
    hypothesis['negative'] = dict(strength=1.,confidence=.9)
    changed = query(CLEAR,model,runtime,session=session)
    assert changed['relations'] == query(CLEAR,model,runtime)['relations']
    assert changed['relations'][0]['classification'] == 'contradicted'
    assert changed['relations'][0]['proof_id'] != before['relations'][0]['proof_id']


def test_pure_native_math_cache_matches_uncached_ground_proofs(field_model,runtime):
    before=Position.from_fen(CLEAR)
    jobs=[dict(id='before',position=before,source_square='a4',target_square='h4',families=['attack'],source='unit-cache'),
          dict(id='flipped',position=color_flip(before),source_square='a5',target_square='h5',families=['attack'],source='unit-cache')]
    settings=FieldOptions(timeout_seconds=180)
    cached=infer_queries(jobs,field_model,settings,runtime,FieldSession(runtime))
    fresh=infer_queries(jobs,field_model,settings,runtime,FieldSession(runtime,optimized=False))
    assert cached['relations']==fresh['relations']
    assert cached['native_invocations']<fresh['native_invocations']


def test_warm_cache_cannot_bypass_zero_native_budget(field_model,runtime):
    session = FieldSession(runtime)
    query(CLEAR,field_model,runtime,session=session)
    limited = query(CLEAR,field_model,runtime,session=session,options=FieldOptions(max_native_invocations=0))
    fresh = query(CLEAR,field_model,runtime,options=FieldOptions(max_native_invocations=0))
    assert limited['relations'] == fresh['relations']
    assert limited['truncated'] and limited['relations'][0]['classification'] == 'incomplete'


def test_runtime_failure_never_falls_back_to_host_geometry(field_model,runtime,monkeypatch):
    def unavailable(nodes):
        raise NativeError('declared unit runtime failure')
    monkeypatch.setattr(runtime,'batch',unavailable)
    result = query(CLEAR,field_model,runtime)
    assert result['truncated'] and result['relations'][0]['classification'] == 'incomplete'
    assert not result['relations'][0]['conditional_proof_complete']


@pytest.mark.parametrize('fen,notation',[
    ('7k/1P6/8/8/8/8/8/6K1 w - - 0 1','b7b8n'),
    ('7k/8/8/R4pP1/8/8/8/6K1 w - f6 0 2','g5f6'),
    ('6k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1','e1g1'),
    ('7k/8/8/8/R6p/8/8/6K1 w - - 0 1','a4h4'),
])
def test_structural_special_edits_reuse_only_exact_dependencies(field_model,runtime,fen,notation):
    position = Position.from_fen(fen)
    successor = position.successor(find_move(position,notation))
    session = FieldSession(runtime)
    options = FieldOptions(timeout_seconds=180,max_native_invocations=100000)
    build_field(position,field_model,options=options,runtime=runtime,session=session,source='structural-test')
    cached = build_field(successor,field_model,options=options,runtime=runtime,session=session,source='structural-test')
    fresh = build_field(successor,field_model,options=options,runtime=runtime,source='structural-test')
    assert cached['relations'] == fresh['relations']
    assert cached['execution']['relation_cache_hits'] > 0


def test_model_export_load_and_recomputed_absolute_key_tamper(field_model,runtime,tmp_path):
    path = tmp_path/'field.json'
    field_model.export(path)
    assert FieldModel.load(path,runtime).version == field_model.version
    damaged = copy.deepcopy(field_model)
    identifier = next(iter(damaged.hypotheses))
    damaged.hypotheses[identifier]['descriptor']['absolute_square'] = 'a4'
    damaged.export(path)
    with pytest.raises(ValueError):
        FieldModel.load(path,runtime)


def test_production_fields_do_not_import_reference_or_training(field_model,runtime,monkeypatch):
    original = builtins.__import__
    def block(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):
            raise AssertionError('Oracle leakage')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',block)
    assert relation(CLEAR,field_model,runtime)['classification'] == 'supported'


def test_provenance_is_not_interpolated_as_native_code(field_model,runtime):
    row = relation(CLEAR,field_model,runtime,provenance='observer ) !(untrusted-code) (')
    assert row['classification'] == 'supported'
    assert all('untrusted-code' not in node['native_expression'] for node in row['proof_trace'])


@pytest.mark.parametrize('options',[dict(sensor_confidence=float('nan')),dict(sensor_confidence=1),
    dict(max_native_invocations=-1),dict(max_native_invocations=True),dict(timeout_seconds=float('inf'))])
def test_invalid_field_options_fail_closed(options):
    with pytest.raises(ValueError):
        FieldOptions(**options)
