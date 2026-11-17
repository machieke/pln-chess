"""Frozen matched evaluation; references are computed only after predictions."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pln_chess.common import ROOT, read_json, digest
from research.cycle16.corpus import variant, reference
from research.cycle16.records import compact, record
from research.cycle17.corpus import roots
from research.cycle17.study import infer
from research.cycle17.provenance import audit, failure_census

PRIMARY = ('S-AA', 'S-BB', 'D-AB', 'D-BA', 'F', 'learned-clearance', 'prior', 'historical-shared')


def metrics(rows, arm):
    result = dict(roots=len({r['root'] for r in rows}), endpoints=len(rows))
    for stage in ('Clear', 'Attack'):
        stages = [r['arms'][arm]['stages'][stage] for r in rows]
        counts = Counter(r['classification'] for r in stages)
        result[stage] = dict(outcomes={k: counts[k] for k in ('supported-positive', 'supported-negative', 'unknown', 'conflicting', 'incomplete')},
            raw_positive_support=sum(r['answer'] is not None for r in stages),
            raw_contrary_support=sum(r['contrary'] is not None for r in stages),
            below_threshold=sum(r['classification']=='unknown' and bool(r['answer'] or r['contrary']) for r in stages),
            denominator=len(stages))
    result['reference'] = dict(Counter('unknown' if r['reference']['label'] is None else 'positive' if r['reference']['label'] else 'negative' for r in rows))
    for label, name in [(True, 'positive'), (False, 'negative')]:
        selected = [r for r in rows if r['reference']['label'] is label]
        result['correct_'+name] = dict(numerator=sum(r['arms'][arm]['stages']['Attack']['classification']=='supported-'+name for r in selected), denominator=len(selected))
    result['wrong_classified'] = sum(r['reference']['label'] is not None and r['arms'][arm]['stages']['Attack']['classification'] in ('supported-positive', 'supported-negative') and
        (r['arms'][arm]['stages']['Attack']['classification']=='supported-positive') != r['reference']['label'] for r in rows)
    result['failure_census'] = {stage: dict(Counter(cause for row in rows
        for cause in row['arms'][arm]['failure_census'].get(stage, []))) for stage in ('Clear', 'Attack')}
    return result


def transfer(items):
    prior = [r for r in items if r['split'] != 'test']; test = [r for r in items if r['split']=='test']
    def location(r):
        p = {x['id']: x['cell'] for x in r['state']['pieces']}
        return tuple(p[r['attacker']]), tuple(p[r['target']])
    locations = {location(r) for r in prior}; entities = {r[k] for r in prior for k in ('attacker', 'target')}
    ancestry = {r['source_ancestry'] for r in prior}
    return dict(test_roots=len(test), unseen_source_roots=sum(r['source_ancestry'] not in ancestry for r in test),
        unseen_entity_bindings=sum(r[k] not in entities for r in test for k in ('attacker', 'target')),
        entity_binding_denominator=2*len(test), unseen_endpoint_pairs=sum(location(r) not in locations for r in test),
        unseen_coarse_geometry=sum(r['coarse_geometry'] not in {p['coarse_geometry'] for p in prior} for r in test),
        unseen_query_ancestry=sum(r['id'] not in {p['id'] for p in prior} for r in test),
        new_publishers=0, new_collections=0, fallbacks=sum(r['selection_fallback'] for r in items),
        phases=dict(Counter(str(r['phase']) for r in test)), directions=dict(Counter(r['direction'] for r in test)),
        openings=dict(Counter(r['source_headers'].get('ECO', 'unrecorded') for r in items)),
        limitation='One TCEC collection with shared engines/openings; distinct registered ancestry does not establish independence')


def run(out, learning, workers=4, historical=False):
    out = Path(out); learning = Path(learning)
    models = {a: read_json(learning/a/'model.json') for a in PRIMARY if a not in ('F', 'historical-shared')}
    models['historical-shared'] = read_json(ROOT/'artifacts/cycle16/learning/shared-chain/model.json')
    items = read_json(ROOT/'artifacts/cycle16/corpus-registration.json')['roots'] if historical else roots()
    selected = [r for r in items if r['split'] in (('test',) if historical else ('development', 'test'))]
    arms = ('S-AA', 'S-BB', 'D-AB', 'D-BA', 'F', 'historical-shared') if historical else PRIMARY
    def worker(root):
        target = out/'roots'/(root['id']+'.json')
        if target.exists():
            saved = read_json(target)
            expected = {a: models[a]['version'] if a in models else None for a in arms}
            assert saved['model_versions'] == expected
            return saved['rows']
        rows = []
        endpoints = [('original', root['state']), ('EE', variant(root, 'EE')), ('OE', variant(root, 'OE'))]
        if not historical:
            endpoints.append(('EU', variant(root, 'EU')))
        for name, state in endpoints:
            results = {}
            for arm in arms:
                native = infer(state, root['attacker'], root['target'], checkpoint=models.get(arm))
                audit(native)
                results[arm] = compact(native, out)
                results[arm]['failure_census'] = failure_census(native)
            rows.append(dict(root=root['id'], split=root['split'], endpoint=name, source_ancestry=root['source_ancestry'],
                state_identity=digest(state), arms=results, reference=reference(state, root['attacker'], root['target'])))
        record(target, dict(model_versions={a: models[a]['version'] if a in models else None for a in arms}, rows=rows))
        print('C17 EVALUATED', root['split'], root['id'], flush=True)
        return rows
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = [row for chunk in pool.map(worker, selected) for row in chunk]
    summary = {split: {a: metrics([r for r in rows if r['split']==split], a) for a in arms} for split in sorted({r['split'] for r in selected})}
    summary['scope'] = 'Historical regression' if historical else 'New source roots; dependent endpoints'
    if not historical:
        summary['transfer'] = transfer(items)
    record(out/'results.json', rows)
    return record(out/'summary.json', summary)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); p.add_argument('--learning', required=True)
    p.add_argument('--workers', type=int, default=4); p.add_argument('--historical', action='store_true')
    a = p.parse_args(); run(a.out, a.learning, a.workers, a.historical)
