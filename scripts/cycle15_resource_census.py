"""Account for retained execution records without treating copies as new runs."""
import argparse
import json
from pathlib import Path
import re

from pln_chess.common import digest, write_json
from scripts.cycle15_evidence import GROUPS


def run(root):
    root = Path(root)
    receipts = {}
    legacy = {}
    sizes = {'research': 0, 'preservation': 0}

    def visit(value):
        if isinstance(value, dict):
            if {'program_sha256', 'stdout', 'stderr', 'wall_seconds', 'runtime'} <= value.keys():
                receipts[digest(value)] = value
                return
            if value.get('schema') == 'relative-field-query-result-v11':
                legacy[digest(value)] = value
                return
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for group in GROUPS:
        for path in (root / group).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path.is_relative_to(root / 'reproduction/source'):
                continue
            sizes['preservation' if group == 'preservation' else 'research'] += path.stat().st_size
            if group != 'preservation' and path.suffix == '.json':
                visit(json.loads(path.read_text()))
    preservation_cpu = []
    for path in (root / 'preservation/logs').glob('*.log'):
        values = re.findall(r'(?:User|System) time \(seconds\): ([\d.]+)', path.read_text())
        if len(values) == 2:
            preservation_cpu.append(sum(map(float, values)))
    values = list(receipts.values())
    result = dict(
        retained_native_execution_records=len(values),
        native_cpu_seconds=sum(r.get('cpu_seconds') or 0 for r in values),
        native_cpu_unmeasured_records=sum(r.get('cpu_seconds') is None for r in values),
        native_wall_seconds=sum(r['wall_seconds'] for r in values),
        native_peak_rss_kib=max((r.get('peak_rss_kib') or 0 for r in values), default=0),
        native_output_bytes=sum(r.get('output_bytes', 0) for r in values),
        legacy_field_records=len(legacy),
        legacy_executed_operator_count=sum(r['native_invocations'] for r in legacy.values()),
        legacy_wall_seconds=sum(r['elapsed_seconds'] for r in legacy.values()),
        preservation_timed_jobs=len(preservation_cpu),
        preservation_job_cpu_seconds=sum(preservation_cpu),
        generated_group_bytes=sizes,
        registered_limits=dict(research_native_processes=10000, research_cpu_hours=8,
                               research_bytes=2 * 1024**3, preservation_cpu_hours=24,
                               preservation_bytes=8 * 1024**3),
        scope=('Unique retained native receipts by full receipt hash, including reproduction; '
               'legacy field operators are counted separately, not assumed to be processes. '
               'CPU totals exclude unretained exploratory invocations, host orchestration, '
               'research tests and final proof comparison. Preservation job CPU includes '
               'its source-bound full test suite. This is a measured lower bound, not a '
               'complete process-accounting claim. Group bytes exclude checkout, packs, '
               'restoration copies, root logs and this census.'),
    )
    assert sizes['research'] < result['registered_limits']['research_bytes']
    assert sizes['preservation'] < result['registered_limits']['preservation_bytes']
    write_json(root / 'resource-census.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    print(json.dumps(run(parser.parse_args().root), indent=2))
