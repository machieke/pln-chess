"""Relation-specific held-out evaluation and diagnostic calibration, offline."""
import argparse
from collections import Counter, defaultdict
import math
from pathlib import Path
import random
import time

from pln_chess.common import digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.pln import Runtime
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha

FAMILIES = ('geometry', 'attack', 'defense', 'mobility', 'king-exposure')


def metrics(rows):
    counts = Counter((r['label'], r['classification']) for r in rows)
    tp, fp = counts[True, 'supported'], counts[False, 'supported']
    positives = sum(r['label'] for r in rows)
    negatives = len(rows)-positives
    supported = tp+fp
    abstained = sum(r['classification'] in ('unknown', 'incomplete') for r in rows)
    contradicted = sum(r['classification'] == 'contradicted' for r in rows)
    return dict(relations=len(rows), positives=positives, negatives=negatives,
        true_positive=tp, false_positive=fp, false_negative=counts[True, 'contradicted'],
        true_negative=counts[False, 'contradicted'],
        precision=tp/supported if supported else None, recall=tp/positives if positives else None,
        negative_recall=counts[False, 'contradicted']/negatives if negatives else None,
        abstention_rate=abstained/len(rows) if rows else None,
        coverage=(supported+contradicted)/len(rows) if rows else None,
        unknown=sum(r['classification'] == 'unknown' for r in rows),
        incomplete=sum(r['classification'] == 'incomplete' for r in rows),
        supported_accuracy=(tp+counts[False, 'contradicted'])/(supported+contradicted) if supported+contradicted else None,
        complete_conditional_proofs=sum(r['conditional_proof_complete'] for r in rows),
        global_composition_proofs=sum(r.get('global_composition_complete', False) for r in rows))


def scores(rows, mapping=None):
    if not rows:
        return None
    values = [(mapping[min(9, int(r['truth_value']['strength']*10))] if mapping is not None
               else r['truth_value']['strength'], int(r['label'])) for r in rows]
    bins = [[] for _ in range(10)]
    for score, label in values:
        bins[min(9, int(score*10))].append((score, label))
    reliability = [dict(bin=i, count=len(items), mean_strength=sum(x for x, _ in items)/len(items) if items else None,
        observed_frequency=sum(y for _, y in items)/len(items) if items else None) for i, items in enumerate(bins)]
    return dict(brier=sum((x-y)**2 for x, y in values)/len(values),
        log_loss=-sum(y*math.log(max(1e-12, min(1-1e-12, x)))+(1-y)*math.log(max(1e-12, min(1-1e-12, 1-x))) for x, y in values)/len(values),
        ece=sum(abs(sum(x-y for x, y in items)) for items in bins)/len(values), bins=reliability,
        scope='Offline diagnostic use of raw strength as a score; PLN confidence is never treated as an empirical probability.')


def bootstrap(rows, seed, repetitions=400):
    groups = defaultdict(list)
    for row in rows:
        groups[row['dependence_group']].append(row)
    names = sorted(groups)
    if not names:
        return None
    rng = random.Random(seed)
    values = defaultdict(list)
    # Aggregate integer counts first: resampling groups does not repeat large
    # proof payloads or mistake each related candidate for an independent unit.
    counts = {name: Counter((r['label'], r['classification']) for r in group) for name, group in groups.items()}
    for _ in range(repetitions):
        aggregate = Counter()
        for name in rng.choices(names, k=len(names)):
            aggregate.update(counts[name])
        n = sum(aggregate.values())
        tp, fp = aggregate[True, 'supported'], aggregate[False, 'supported']
        positive = sum(v for (label, _), v in aggregate.items() if label)
        unknown = sum(v for (_, classification), v in aggregate.items() if classification in ('unknown', 'incomplete'))
        if tp+fp:
            values['precision'].append(tp/(tp+fp))
        if positive:
            values['recall'].append(tp/positive)
        if n:
            values['abstention_rate'].append(unknown/n)
    intervals = {}
    for name, samples in values.items():
        samples.sort()
        intervals[name] = [samples[int(.025*(len(samples)-1))], samples[int(.975*(len(samples)-1))]]
    return dict(groups=len(names), replicates=repetitions, percentile_95=intervals,
        limitations='Source/generator-group bootstrap. Two controlled generator groups provide weak uncertainty resolution; source games can share residual dependencies. Zero-error intervals do not certify universal correctness.')


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    assert read_json(out / 'datasets/audit.json')['passed']
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, infer_queries
    data = read_gzip(out / 'datasets/field-queries.json.xz')
    runtime = Runtime(timeout=600)
    model = FieldModel.load(out / 'model/C11-field-trained.json', runtime)
    empty = FieldModel.load(out / 'model/C11-field-empty.json', runtime)
    options = FieldOptions(timeout_seconds=600, max_native_invocations=100000)
    sessions = {'trained': FieldSession(runtime), 'empty': FieldSession(runtime)}
    all_rows, costs, receipts = [], [], []
    for split in ('calibration', 'test'):
        selected = [r for r in data['queries'] if r['split'] == split]
        for offset in range(0, len(selected), 200):
            queries = selected[offset:offset+200]
            jobs = [dict(id=r['id'], position=Position.from_fen(r['fen']), source_square=r['piece_square'],
                target_square=r['target_square'], families=[f for f in FAMILIES if r['labels'][f] is not None],
                source=r['source']) for r in queries]
            original = {r['id']: r for r in queries}
            for arm, checkpoint in (('trained', model), ('empty', empty)):
                # Empty-model control on the entire test population; calibration
                # fitting is meaningful only for the trained model.
                if arm == 'empty' and split == 'calibration':
                    continue
                name = f'{arm}-{split}-{offset:05}'
                path = out / f'field-evaluation/{name}.json.xz'
                started = time.time()
                result = infer_queries(jobs, checkpoint, options, runtime, sessions[arm])
                rows = []
                for relation in result['relations']:
                    query = original[relation['query_id']]
                    assert digest(relation['proof_trace']) == relation['proof_id']
                    assert relation['family'] in query['labels'] and query['labels'][relation['family']] is not None
                    if relation['classification'] in ('supported', 'contradicted'):
                        assert relation['proof_trace'] and relation['conditional_proof_complete']
                    rows.append(dict(query=query['id'], family=relation['family'], split=split, arm=arm,
                        label=query['labels'][relation['family']], classification=relation['classification'],
                        truth_value=relation['raw_stv'], proof_id=relation['proof_id'],
                        conditional_proof_complete=relation['conditional_proof_complete'],
                        global_composition_complete=relation['global_composition_complete'],
                        rule_id=relation['rule_id'], evidence_ids=relation['evidence_ids'],
                        dependence_group=query['dependence_group'], transformation_lineage=query['transformation_lineage'],
                        population=query['metadata']['generator_family'], reference_board_valid=query['reference_board_valid'],
                        source=query['source']))
                assert len(rows) == sum(sum(v is not None for v in r['labels'].values()) for r in queries)
                pack(path, dict(rows=rows, result=result, model_version=checkpoint.version, dataset_hash=data['hash'],
                    queries=queries, oracle_scope='Labels are joined only after production inference returns.'))
                receipt = dict(artifact=str(path.relative_to(out)), sha256=sha(path), model_version=checkpoint.version,
                    dataset_hash=data['hash'], queries=len(queries), relations=len(rows),
                    native_proofs_verified=True, ordered_proof_hash=digest([r['proof_id'] for r in rows]),
                    elapsed_seconds=time.time()-started, mode='experimental-field-conditional')
                write_json(path.with_suffix('.receipt.json'), receipt)
                receipts.append(receipt)
                all_rows.extend(rows)
                costs.append(dict(name=name, **{k: result[k] for k in ('native_invocations','scheduled_invocations','cache_hits',
                    'relation_cache_hits','relation_cache_invalidations','grounded_atoms','proof_bytes','elapsed_seconds','truncated')}))
            print('Field evaluation', split, offset+len(queries), '/', len(selected), flush=True)
    summaries = {}
    for arm in ('trained', 'empty'):
        summaries[arm] = {}
        for population in ('all', 'controlled-relative-context', 'external-game-panel', 'reference-valid-only'):
            rows = [r for r in all_rows if r['arm'] == arm and r['split'] == 'test' and
                    (population == 'all' or r['population'] == population or (population == 'reference-valid-only' and r['reference_board_valid']))]
            summaries[arm][population] = {family: dict(metrics=metrics([r for r in rows if r['family'] == family]),
                uncertainty=bootstrap([r for r in rows if r['family'] == family], 111111+i)) for i, family in enumerate(FAMILIES)}
    calibration = {}
    for family in FAMILIES:
        fitted = [r for r in all_rows if r['arm'] == 'trained' and r['split'] == 'calibration' and r['family'] == family]
        test = [r for r in all_rows if r['arm'] == 'trained' and r['split'] == 'test' and r['family'] == family]
        bins = [[] for _ in range(10)]
        for row in fitted:
            bins[min(9, int(row['truth_value']['strength']*10))].append(row['label'])
        mapping = [(sum(items)+1)/(len(items)+2) for items in bins]
        calibration[family] = dict(calibration_relations=len(fitted), test_relations=len(test), mapping=mapping,
            raw_all=scores(test), raw_covered=scores([r for r in test if r['classification'] in ('supported', 'contradicted')]),
            mapped_all=scores(test, mapping), fitted_only_on_calibration=True,
            thresholds_changed=False, classification_changed=False,
            population='Registered mixture of synthetic controlled and published-game relation queries',
            scope='Ten-bin Laplace diagnostic fitted after the field model was frozen. Not a probability of legal play or strategic success.')
    pack(out / 'field-evaluation/rows.json.xz', all_rows)
    write_json(out / 'field-evaluation/summary.json', dict(schema=11, model_version=model.version, empty_model_version=empty.version,
        dataset_hash=data['hash'], summaries=summaries, costs=costs, shard_receipts=receipts,
        no_reference_labels_in_production=True, accepted_legal_model_changed=False,
        inference_semantics='Native local conditional influence; no global composition or strategic competence.'))
    write_json(out / 'field-evaluation/calibration.json', dict(model_version=model.version, families=calibration,
        raw_confidence_is_not_empirical_probability=True, production_classification_changed=False))
    print('Field evaluation complete', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
