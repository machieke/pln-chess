"""Registered field transformations, evidence controls and successor examples."""
import argparse
import copy
from dataclasses import replace
from pathlib import Path

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position, Piece
from pln_chess.pln import Runtime
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from training.cycle11_fields import train_queries
from training.cycle11_data import labels


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, infer_queries
    from pln_chess.cycle11.fields.comparison import compare_candidate
    runtime = Runtime(timeout=600)
    model = FieldModel.load(out / 'model/C11-field-trained.json', runtime)
    empty = FieldModel.load(out / 'model/C11-field-empty.json', runtime)
    options = FieldOptions(timeout_seconds=600, max_native_invocations=100000)
    controls = read_json(out / 'datasets/worked-controls.json')

    def query(position, source, target, family, checkpoint=model, observation_source='controlled-field-query'):
        result = infer_queries([dict(id='controlled-query', position=position, source_square=source,
            target_square=target, families=[family], source=observation_source)], checkpoint, options, runtime, FieldSession(runtime))
        relation = result['relations'][0]
        assert digest(relation['proof_trace']) == relation['proof_id']
        return relation

    transformations = []
    for case in controls['transformations']:
        before = Position.from_fen(case['before_fen'])
        after = Position.from_fen(case['after_fen'], unknown_squares=case.get('unknown_squares', []))
        if 'before_pieces' in case:
            before = replace(before, pieces=tuple(Piece(**p) for p in case['before_pieces']))
            after = replace(after, pieces=tuple(Piece(**p) for p in case['after_pieces']))
        source = case['dependence_group']
        a = query(before, case['before_source'], case['before_target'], case['field'], observation_source=source)
        b = query(after, case['after_source'], case['after_target'], case['field'], observation_source=source)
        same = a['raw_stv'] == b['raw_stv'] and a['classification'] == b['classification']
        if case['expectation'] == 'invariant-relative-conditional':
            passed = same and a['rule_id'] == b['rule_id']
        elif case['expectation'] == 'unknown-required-observation':
            passed = b['classification'] == 'unknown'
        else:
            passed = not same and a['classification'] == 'supported' and b['classification'] == 'contradicted'
        transformations.append(dict(case=case, before=a, after=b, passed=passed,
            supported_on_both=a['classification'] == b['classification'] == 'supported',
            same_native_truth_value=a['raw_stv'] == b['raw_stv'], same_native_proof=a['proof_id'] == b['proof_id']))
    pack(out / 'fields/transformations.json.xz', transformations)
    transfers = []
    for case in controls['transfers']:
        position = Position.from_fen(case['fen'])
        before = query(position, case['source'], case['target'], case['field'], empty)
        learned = query(position, case['source'], case['target'], case['field'])
        removed_model = copy.deepcopy(model)
        removed_model.hypotheses.pop(learned['rule_id'], None)
        removed_model.variant = 'C11-field-selected-hypothesis-removed'
        removed = query(position, case['source'], case['target'], case['field'], removed_model)
        transfers.append(dict(case=case, empty=before, learned=learned, removed_hypothesis=removed,
            successful=before['classification'] == 'unknown' and learned['classification'] == 'supported' and removed['classification'] == 'unknown',
            training_hypothesis=model.hypotheses.get(learned['rule_id']),
            input_audit=next(t for t in read_json(out / 'datasets/audit.json')['dedicated_transfers'] if t['id'] == case['id']),
            interpretation='Native conditional learned from different raw relative distances under an explicit shared geometry/occupancy projection.'))
    pack(out / 'fields/learning-transfers.json.xz', transfers)
    examples = []
    for case in controls['worked']:
        position = Position.from_fen(case['fen'], unknown_squares=case['unknown_squares'])
        comparison = compare_candidate(position, case['move'], model,
            legal_checkpoint=ROOT / 'artifacts/cycle10/model/C10-default.json',
            history_input=case['history_input'], options=options, runtime=runtime)
        assert comparison['after']['fen'] == case['reference_successor_fen']
        for side in ('before', 'after'):
            for relation in comparison[side]['relations']:
                assert digest(relation['proof_trace']) == relation['proof_id']
        assert all(change['change_truth_value'] is None and change['proof_status'] == 'host-diagnostic' for change in comparison['differences'])
        examples.append(dict(case=case, comparison=comparison))
        print('Worked field comparison', case['id'], len(comparison['differences']), flush=True)
    pack(out / 'fields/worked-examples.json.xz', examples)
    write_json(out / 'fields/controls-summary.json', dict(schema=11, model_version=model.version,
        transformations=len(transformations), transformation_passes=sum(t['passed'] for t in transformations),
        transformations_supported_on_both=sum(t['supported_on_both'] for t in transformations),
        transformation_failures=[t['case']['id'] for t in transformations if not t['passed']],
        transfer_attempts=len(transfers), successful_learning_transfers=sum(t['successful'] for t in transfers),
        transfer_failures=[t['case']['id'] for t in transfers if not t['successful']],
        worked_examples=[dict(id=e['case']['id'], candidate_classification=e['comparison']['candidate']['classification'],
            reference_legal=e['case']['reference_legal'], before_relations=len(e['comparison']['before']['relations']),
            after_relations=len(e['comparison']['after']['relations']), differences=len(e['comparison']['differences']),
            incremental=e['comparison']['after']['execution']) for e in examples],
        differences_are_native_conclusions=False, field_conditionals_use_native_rules=True,
        accepted_legal_checkpoint_unchanged=True))


def dependence(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    data = read_gzip(out / 'datasets/field-queries.json.xz')
    runtime = Runtime(timeout=600)
    rows = [r for r in data['queries'] if r['split'] == 'train'][:24]
    transformed = []
    for record in rows:
        row = copy.deepcopy(record)
        board = chess.Board(row['fen']).mirror()
        source = chess.square_mirror(chess.parse_square(row['piece_square']))
        target = chess.square_mirror(chess.parse_square(row['target_square']))
        assert labels(board, source, target) == row['labels']
        row.update(fen=board.fen(en_passant='fen'), piece_square=chess.square_name(source), target_square=chess.square_name(target),
            source='declared-color-transform/'+row['source'], dependence_group=row['dependence_group']+'/transformed',
            transformation_lineage=[record['dependence_group'], *row['transformation_lineage']])
        row['id'] = 'controlled-transform:'+digest(row)[:24]
        transformed.append(row)
    unsafe = []
    for record in rows:
        row = copy.deepcopy(record)
        row.update(source='deliberately-uncorrected-duplicate/'+row['source'], dependence_group=row['dependence_group']+'/unsafe-copy', transformation_lineage=[])
        row['id'] = 'unsafe-copy:'+digest(row)[:24]
        unsafe.append(row)
    shared = copy.deepcopy(rows[0])
    shared['labels']['attack'] = not shared['labels']['attack']
    shared['source'] = 'declared-injected-contradictory-label'
    shared['id'] = 'injected-conflict:'+digest(shared)[:24]
    independent = copy.deepcopy(shared)
    independent.update(dependence_group='declared-independent-contradiction', transformation_lineage=[])
    independent['id'] = 'independent-conflict:'+digest(independent)[:24]
    arms = dict(base=rows, duplicate=rows+rows, transformed=rows+transformed,
        unsafe=rows+unsafe, shared_conflict=rows+[shared], independent_conflict=rows+[independent])
    models = {}
    for name, examples in arms.items():
        models[name] = train_queries(examples, runtime, out / 'field-learning/dependence' / name,
            dataset_hash=digest(examples), variant='C11-field-dependence-'+name)
    values = lambda model: {k:(h['positive'],h['negative']) for k,h in model.hypotheses.items()}
    checks = dict(duplicate_values_identical=values(models['base']) == values(models['duplicate']),
        transformed_ancestor_values_identical=values(models['base']) == values(models['transformed']),
        unsafe_duplicates_change_values=values(models['base']) != values(models['unsafe']),
        shared_contradiction_changes_values=values(models['base']) != values(models['shared_conflict']),
        independent_contradiction_changes_values=values(models['base']) != values(models['independent_conflict']))
    assert all(checks.values()), checks
    write_json(out / 'field-learning/dependence.json', dict(passed=True, checks=checks,
        models={name:dict(version=model.version, training_report=model.training_report, values=values(model)) for name,model in models.items()},
        limits='Declared injected contradiction and unsafe ancestry ablations are controls, not observed source labels. Shared templates and unreported correlation remain external assumptions.'))
    print('Field dependence controls passed', checks, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--dependence', action='store_true')
    args = parser.parse_args()
    dependence(args.out) if args.dependence else run(args.out)
