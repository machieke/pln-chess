"""Summarize materialized inputs and observed queues from existing matched runs."""
import argparse
import hashlib
from pathlib import Path
import statistics

from pln_chess.common import read_json, write_json
from research.cycle15.native_reasoner import alpha_key


def span(values):
    return dict(min=min(values), median=statistics.median(values), max=max(values))


def run(results, out):
    rows = read_json(results)
    arms = {}
    for arm in 'ABCD':
        records = []
        for row in rows:
            proof = row['arms'][arm]['proof']
            path = Path(proof['path'])
            assert hashlib.sha256(path.read_bytes()).hexdigest() == proof['sha256']
            records.append(read_json(path))
        if arm == 'A':
            arms[arm] = dict(
                queries=len(records), persistent_conditionals=1764,
                materialization='Host-selected conditional and observation per specified attack query',
                native_knowledge_base=False,
                executed_operators=span([r['native_invocations'] for r in records]),
                logical_native_nodes=span([r['logical_native_nodes'] for r in records]),
                grounded_atom_appearances=span([r['grounded_atoms'] for r in records]),
            )
            continue
        stats = {key: span([r['usage'][key] for r in records]) for key in (
            'initial_tasks', 'initial_beliefs', 'selected_tasks', 'retained_tasks',
            'retained_beliefs', 'repeated_selected_terms', 'host_grounded_instances')}
        derived = []
        for record in records:
            initial = {alpha_key(s['term']) for s in record['facts'] + record['rules']}
            derived.append(sum(alpha_key(s['term']) not in initial for s in record['retained']))
        stats.update(derived_statements_alpha_normalized=span(derived),
                     supplied_facts=span([len(r['facts']) for r in records]),
                     supplied_rules=span([len(r['rules']) for r in records]),
                     native_processes=span([r['usage']['native_processes'] for r in records]),
                     output_bytes=span([r['receipt']['output_bytes'] for r in records]))
        arms[arm] = dict(queries=len(records), statistics=stats,
                        persistent_conditionals=1764 if arm == 'B' else 0,
                        persistent_templates=0 if arm == 'B' else 11,
                        learned_template_truth_values=5 if arm == 'D' else 0,
                        native_persistent_state=False)
    report = dict(arms=arms, passed=True,
                  scope='All 120 development/test endpoints per arm; descriptive access census, not independent sample counts or isolated latency measurements',
                  unobservable='Complete fired-operator, schema-instance and duplicate-derivation counts are not exposed by the interpreter; repeated selected terms are only a trace diagnostic')
    write_json(out, report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    run(args.results, args.out)
