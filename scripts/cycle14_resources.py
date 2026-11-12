"""Account measured work without inventing missing global process counters."""
import argparse
from collections import defaultdict
from pathlib import Path
import re
import subprocess
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha


def baseline_node_census(out):
    import chess
    reported={};unreported=[]
    for kind,filename in [('immediate','reference-labels.json'),('temporal','temporal-labels.json')]:
        total=0
        for row in read_json(out/'baseline/research/run/datasets'/filename)['records']:
            for analysis in row['evaluations']:
                values=[]
                for candidate in analysis['candidates']:
                    nodes=candidate['nodes']
                    if nodes is None:
                        terminal=chess.Board(candidate['fen']).is_game_over()
                        assert terminal and candidate['depth']==0
                        unreported.append(dict(kind=kind,id=row['id'],channel=candidate['channel'],
                            node_budget=analysis['node_budget'],terminal=True,reported_nodes=None,
                            reason='Terminal endpoint returned a depth-zero score without a node counter; no numeric value is imputed.'))
                    else:values.append(nodes)
                # MultiPV candidate records share cumulative search work;
                # temporal candidates are separate endpoint searches.
                total+=max(values,default=0) if kind=='immediate' else sum(values)
        reported[kind]=total
    return reported,unreported


def run(out):
    out=Path(out).resolve();budgets=read_json(ROOT/'configs/cycle14.json')['budgets']
    required=('features/immediate-g2/index.json','features/temporal-g1/index.json',
        'clean-research/selected/verified.json','clean-research/verified.json',
        'current/verified.json','performance/summary.json')
    assert all((out/path).exists() for path in required)
    primary={kind:read_json(out/f'labels/{kind}-g1/index.json')['actual_reported_nodes'] for kind in ('immediate','temporal')}
    primary['additional-responses']=read_json(out/'labels/responses-g1/index.json')['actual_additional_reported_nodes']
    baseline,unreported_reference_nodes=baseline_node_census(out)
    audit=sum(a['actual_reported_nodes'] for p in (out/'reference-audit/raw').glob('*.json')
        for a in read_json(p)['analyses'])
    verification=sum(r['actual_reported_nodes'] for r in read_json(out/'clean-research/selected/verified.json')['reference_analyses'])
    total_nodes=sum(primary.values())+sum(baseline.values())+audit+verification
    timing_paths=sorted(set(out.glob('*.resources.log'))|set(out.glob('clean-research/*resources.log*'))|
        set(out.glob('pipeline/logs/*.txt'))|set(out.glob('clean-research/logs/*.txt'))|
        set(out.glob('clean-research/reference-bootstrap/one-worker-build.txt'))|
        set(out.glob('*unit*.txt')))
    measured=[]
    for path in timing_paths:
        text=path.read_text(errors='replace')
        users=re.findall(r'User time \(seconds\): ([0-9.]+)',text)
        systems=re.findall(r'System time \(seconds\): ([0-9.]+)',text)
        if not users or len(users)!=len(systems):continue
        # Outer orchestration timing includes the per-stage timings below; do
        # not add the same child CPU twice. Preserve it as a separate receipt.
        outer=path.name in ('reproduce.resources.log','clean-research.resources.log')
        measured.append(dict(path=str(path.relative_to(out)),sha256=sha(path),
            cpu_seconds=sum(map(float,users))+sum(map(float,systems)),
            included_in_nonoverlapping_sum=not outer,
            terminated='Command terminated by signal' in text,
            scope='GNU time user plus system CPU, including reaped descendants of this command.'))
    tests=read_json(out/'current/tests-resources.json')
    test_cpu=tests['child_user_cpu_seconds']+tests['child_system_cpu_seconds']
    benchmark_cpu=sum(sum(read_json(p)['worker_cpu_seconds'].values()) for p in (out/'performance/receipts').glob('*.json'))
    measured_cpu=sum(r['cpu_seconds'] for r in measured if r['included_in_nonoverlapping_sum'])+test_cpu+benchmark_cpu
    perf=read_json(out/'performance/summary.json')
    interpreter=dict(benchmark_requests=sum(r['interpreter_process_launches'] for r in perf['rows']),
        completed_streamed_archive_replays=sum(read_json(p)['interpreter_launches']
            for p in (out/'clean-research/proof-replay/stream-resources').glob('*.json')),
        final_archive_join=read_json(out/'clean-research/proof-replay/verified.json')['interpreter_launches_this_invocation'])
    retained=defaultdict(int);file_counts=defaultdict(int)
    for path in out.rglob('*'):
        if path.is_file():
            group=path.relative_to(out).parts[0];retained[group]+=path.stat().st_size;file_counts[group]+=1
    checkouts=[Path('/data/pln-chess-cycle14-baseline'),Path('/data/pln-chess-cycle14-final'),
        Path('/data/pln-chess-cycle14-feature-source'),Path('/data/pln-chess-cycle14-feature-source-g2')]
    usage=subprocess.check_output(['du','-sb',*[str(p) for p in checkouts if p.exists()]],text=True)
    temporary=[dict(bytes=int(line.split('\t',1)[0]),path=line.split('\t',1)[1]) for line in usage.splitlines()]
    assert sum(retained.values())<=budgets['new_artifact_bytes']
    assert sum(r['bytes'] for r in temporary)<=budgets['temporary_checkouts_bytes']
    assert total_nodes<=budgets['reference_search_nodes']
    write_json(out/'resources.json',dict(schema='c14-resource-accounting-v1',created_unix=time.time(),
        registered_budgets=budgets,reference_reported_nodes=dict(primary=primary,baseline_regeneration=baseline,
            raw_adapter_audit=audit,selected_clean_verification=verification,total=total_nodes,
            unreported_terminal_analyses=unreported_reference_nodes,
            scope='Sum of available engine-reported analysis nodes; terminal analyses lacking a node counter are listed separately, not imputed as zero. Reused response labels are counted once and MultiPV cumulative nodes once per search. Compiler PGO/engine self-test work is outside reference supervision.'),
        measured_cpu_seconds_lower_bound=measured_cpu,measured_cpu_hours_lower_bound=measured_cpu/3600,
        cpu_receipts=measured,current_test_cpu_seconds=test_cpu,benchmark_worker_cpu_seconds=benchmark_cpu,
        total_cycle_cpu_seconds=None,total_cycle_interpreter_launches=None,
        measured_interpreter_launches=interpreter,
        interpreter_scope='Exact launch counters in benchmark requests and completed native archive replay. Logical operator invocations in other receipts are not mislabeled as process launches. Interrupted in-memory work may lack a completed per-archive counter.',
        retained_artifact_bytes=sum(retained.values()),retained_files=sum(file_counts.values()),
        retained_by_top_level=dict(retained),files_by_top_level=dict(file_counts),temporary_checkout_usage=temporary,
        temporary_checkout_scope='du apparent bytes in one invocation; shared hardlinks counted once by du. Runtime and selected-source symlinks are not followed.',
        generated_bytes_total=None,measured_benchmark_output_bytes=dict(
            canonical_interactive=sum(r['canonical_interactive_bytes'] for r in perf['rows']),
            canonical_full=sum(r['canonical_full_bytes'] for r in perf['rows']),
            compressed_audit=sum(r['compressed_audit_bytes'] for r in perf['rows'])),
        limitations=['No continuous process accounting was installed at cycle start; early baseline/audit/debug CPU and interpreter totals cannot be reconstructed exactly.',
            'The first feature attempt and interrupted proof-stream attempts retain evidence and partial resource logs; missing counters are not imputed as zero.',
            'Retained bytes are a snapshot. Total transient generated bytes, deleted scratch programs and SQLite write amplification were not globally instrumented.',
            'Worker counts were explicitly scheduled; a complete historical peak-concurrency census was not recorded. Short auxiliary checks may have overlapped earlier jobs.',
            'Measured CPU and interpreter totals are lower bounds, so those global budget-compliance claims remain unverified. Available reported reference nodes and retained storage are checked against their ceilings.',
            'Baseline terminal endpoint analyses without a node counter are explicitly listed; the complete cycle reference-node total is therefore not claimed exactly measured.'],
        budget_checks=dict(reported_reference_nodes=True,complete_reference_node_total_verified=not unreported_reference_nodes,
            retained_artifacts=True,temporary_checkouts=True,
            complete_cpu_total_verified=False,complete_interpreter_total_verified=False,complete_historical_concurrency_peak_verified=False)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    run(parser.parse_args().out)
