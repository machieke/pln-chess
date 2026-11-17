"""Post-hoc missing-support census; never changes native answers or thresholds."""
from collections import Counter
from pathlib import Path
from pln_chess.common import ROOT, read_json
from research.cycle15.native_reasoner import alpha_key, parse
from research.cycle16.evidence_audit import pair_diagnostic
from research.cycle16.records import record


def run(out):
    out = Path(out)
    reports = {}
    bishop_witness = None
    for panel in ('evaluation', 'historical-evaluation'):
        rows = read_json(out/panel/'results.json')
        reports[panel] = {}
        for split in sorted({r['split'] for r in rows}):
            subset = [r for r in rows if r['split'] == split]
            arms = {}
            for arm in subset[0]['arms']:
                stages = {}
                for name in ('Clear', 'Attack'):
                    counts = Counter(); statuses = Counter(); examples = {}
                    for row in subset:
                        compact = row['arms'][arm]['stages'][name]
                        statuses[compact['classification']] += 1
                        if compact['classification'] not in ('unknown', 'incomplete', 'conflicting'):
                            continue
                        native = read_json(compact['proof']['path'])
                        matching = [r for r in native['retained'] if r['term'] in (native['query'], native['contrary_query'])]
                        # The frozen primary census used orthogonal rook geometry.
                        # Recompute diagnostics for the actual registered shape,
                        # including the historical bishop. Answers stay unchanged.
                        causes = [c for c in row['arms'][arm]['failure_census'].get(name, []) if c not in (
                            'clearance or terminal partial absent',
                            'returned matching pair has overlapping stamps; native guard checked in minimal witness')]
                        if name == 'Attack':
                            clear_query = row['arms'][arm]['stages']['Clear']['query']
                            _, a, t, shape, state = parse(clear_query)
                            partial = alpha_key(f'(Implication (Clear {a} $target {shape} {state}) (Attack {a} $target {state}))')
                            clears = [r for r in native['retained'] if r['term']==clear_query]
                            terminals = [r for r in native['retained'] if alpha_key(r['term'])==partial]
                            if clears and terminals:
                                intersections = [set(c['stamps']) & set(p['stamps']) for c in clears for p in terminals]
                                if all(intersections):
                                    causes.append('returned structurally corresponding pair has shared ancestry; no scheduler attempt claimed')
                                    if panel=='historical-evaluation' and shape=='diagonal' and arm=='historical-shared' and bishop_witness is None:
                                        diagnostic = pair_diagnostic(max(terminals,key=lambda r:r['confidence']), max(clears,key=lambda r:r['confidence']), out/'supplement')
                                        assert diagnostic['markers'][0][1]=='false' and diagnostic['markers'][2][1]
                                        bishop_witness = dict(root=row['root'], endpoint=row['endpoint'], source=compact['proof'], diagnostic=diagnostic,
                                            scope='Actual historical diagonal query; separate native structural/guard witness, never a replacement answer')
                            else:
                                causes.append('clearance or terminal partial absent for actual query geometry')
                        if matching and not any(r['strength'] >= .6 and r['confidence'] >= .1 for r in matching):
                            causes.append('matching retained statement below threshold, including zero-confidence selector omission')
                        if not causes:
                            causes = ['no supported query statement returned']
                        for cause in set(causes):
                            counts[cause] += 1
                            examples.setdefault(cause, dict(root=row['root'], endpoint=row['endpoint'],
                                source=compact['proof'], matching_retained_values=[{k:r[k] for k in ('term','strength','confidence')} for r in matching]))
                    assert sum(statuses.values()) == len(subset)
                    stages[name] = dict(endpoints=len(subset), statuses=dict(statuses), nonexclusive_causes=dict(counts), representative_examples=examples)
                arms[arm] = stages
            reports[panel][split] = arms
    historical_roots = read_json(ROOT/'artifacts/cycle16/corpus-registration.json')['roots']
    kinds = {r['id']: next(p['kind'] for p in r['state']['pieces'] if p['id']==r['attacker']) for r in historical_roots}
    historical_rows = read_json(out/'historical-evaluation/results.json')
    from evaluation.cycle17_shared_evidence import metrics
    strata = {kind: {arm: {k:v for k,v in metrics([r for r in historical_rows if kinds[r['root']]==kind], arm).items() if k!='failure_census'}
        for arm in historical_rows[0]['arms']} for kind in sorted({kinds[r['root']] for r in historical_rows})}
    record(out/'historical-target-scope.json', dict(strata=strata,
        scope='Only rook-attack is learned in Cycle 17 pairs; the historical bishop root uses a supplied terminal in those models. Original Cycle 16 shared checkpoint remains distinct.'))
    assert bishop_witness is not None
    record(out/'supplement/historical-bishop-diagnostic.json', bishop_witness)
    return record(out/'failure-census.json', dict(panels=reports, native_processes=1,
        refinement='Frozen primary census assumed orthogonal rook shape; this authoritative post-hoc census uses actual query geometry and preserves the earlier summaries unchanged.',
        scope='Post-hoc analysis of exact returned records. A zero-confidence retained statement may be omitted by BestConfidenceCandidate. No new answer or scheduler event is constructed.'))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); run(p.parse_args().out)
