"""Summarize executed complete legal comparisons without reinterpreting claims."""
import argparse
from collections import defaultdict
from pathlib import Path

from pln_chess.common import read_json, write_json
from scripts.cycle9_baseline import sha


def run(directory):
    directory = Path(directory)
    panel = read_json(directory/'legal/panel.json')
    parity = read_json(directory/'proof-parity.json')
    assert parity['passed'] and parity['exact_native_proof_parity']
    jobs = {row['id']:row for row in panel['jobs']}
    grouped = defaultdict(list)
    for comparison in parity['comparisons']:
        identifier = Path(comparison['artifact']).name.removesuffix('.json.xz')
        job = jobs[identifier]
        grouped[job['cohort'], job['mode']].append(comparison)
    groups = []
    for (cohort, mode), rows in sorted(grouped.items()):
        exact = sum(r['metrics']['exact_positions'] if 'exact_positions' in r['metrics'] else
            r['metrics']['empty_terminal_exact'] + r['metrics']['nonempty_exact'] for r in rows)
        groups.append(dict(cohort=cohort, mode=mode, positions=sum(r['positions'] for r in rows),
            exact_legal_move_sets=exact, candidate_rows=sum(r['rows'] for r in rows),
            **{key:sum(r['metrics'][key] for r in rows) for key in
               ('false_positive','false_illegal','self_check_false_legal','incomplete','unknown')},
            exact_native_proof_parity=all(r['exact_native_proof_parity'] for r in rows)))
    required = {'cycle10/external-test/operational/fen':(793,1020),
        'cycle10/external-test/operational/history':(1020,1020),
        'cycle9/adversarial/operational/fen':(112,128),
        'cycle9/special-moves/operational/fen':(71,80),
        'cycle10/synthetic-adversarial/operational/fen':(98,112)}
    for name, expected in required.items():
        row = next(r for r in groups if r['cohort'] == name and r['mode'] == 'operational')
        assert (row['exact_legal_move_sets'],row['positions']) == expected, name
    assert all(not r[key] for r in groups for key in ('false_positive','false_illegal','self_check_false_legal','incomplete'))
    result = dict(passed=True, groups=groups, jobs=len(jobs), candidate_rows=sum(r['candidate_rows'] for r in groups),
        required_cohorts_unchanged=True, full_proof_comparison_sha256=sha(directory/'proof-parity.json'),
        scope='Exact supplied acceptance cohorts and modes only; no universal legality guarantee.')
    write_json(directory/'legal-summary.json',result)
    print({k:v for k,v in result.items() if k!='groups'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',required=True)
    run(parser.parse_args().directory)
