"""Isolated five-repetition comparison workloads with full native-proof parity."""
import argparse
from dataclasses import asdict
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time

from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle12.temporal import semantic_replay
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


class CountedRuntime(Runtime):
    """Count interpreter launches without changing native execution semantics."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process_launches = 0

    def execute(self, *args, **kwargs):
        self.process_launches += 1
        return super().execute(*args, **kwargs)


def workloads(out):
    pairs = read_json(out / 'datasets/source-pairs.json')['records']
    ordered = sorted(pairs, key=lambda r:digest(['cycle13-performance', r['id']]))
    quiet = next(r for r in ordered if r['offline_reference']['quiet_pair'])
    promotion = next(r for r in ordered if any(r['offline_reference']['promotions']))
    tactical = next(r for r in ordered if r['source']['cohort'] == 'external-tactical')
    temporal = read_json(out / 'datasets/temporal-plans.json')
    plans = temporal.get('records', temporal.get('plans'))
    plan = min(plans, key=lambda r:digest(['cycle13-performance', r['id']]))
    return dict(single=dict(kind='pairs', pairs=[quiet]),
        multiple=dict(kind='pairs', pairs=[quiet, promotion, tactical]),
        **{'two-ply':dict(kind='temporal', plan=plan, horizon=2),
           'three-ply':dict(kind='temporal', plan=plan, horizon=3)})


def worker(out, name, arm, repetition):
    from pln_chess.learning import Model
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle13.concepts import ForkModel
    from pln_chess.cycle13.model import PreferenceModel
    from pln_chess.cycle13.api import compare_moves, PreferenceOptions, PreferenceSession
    from pln_chess.cycle13.temporal import analyze_continuations
    from pln_chess.cycle6.inference import production_code_hash
    out = Path(out)
    runtime = CountedRuntime(timeout=900)
    models = dict(legal_model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json', runtime),
        field_model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json', runtime),
        concept_model=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json', runtime),
        fork_model=ForkModel.load(out/'model/C13-fork-role.json', runtime),
        preference_model=PreferenceModel.load(out/('model/C13-preference-temporal.json' if 'ply' in name else 'model/C13-preference-relational.json'), runtime))
    session = PreferenceSession(runtime)
    options = PreferenceOptions(timeout_seconds=900, incremental=(arm == 'incremental'))
    workload = workloads(out)[name]
    rows = []
    for temperature in ('cold', 'warm'):
        started = time.perf_counter()
        before_calls, before_processes = runtime.invocations, runtime.process_launches
        if workload['kind'] == 'pairs':
            results = [compare_moves(row['fen'], *row['moves'], **models, runtime=runtime,
                options=options, session=session, history=row['history'],
                source='cycle13-performance/'+row['id']) for row in workload['pairs']]
        else:
            plan = workload['plan']
            horizon = workload['horizon']
            branches = {side:[branch[:horizon]] for side,branch in plan['branches'].items()}
            results = [analyze_continuations(plan['fen'], branches, **models, runtime=runtime,
                options=options, session=session, history=plan['history'], horizons=(horizon,),
                source='cycle13-performance/'+plan['id'], selection_provenance=plan['response_selection'])]
        elapsed = time.perf_counter()-started
        semantic = digest(semantic_replay(results))
        target = out/'performance/raw'/f'{name}-{arm}-{repetition}-{temperature}.json.xz'
        pack(target, results)
        executions = [result['execution'] for result in results]
        rows.append(dict(workload=name, arm=arm, repetition=repetition, temperature=temperature,
            elapsed_seconds=elapsed, native_invocations=runtime.invocations-before_calls,
            interpreter_process_launches=runtime.process_launches-before_processes,
            peak_process_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            grounded_atoms=sum(e.get('grounded_atoms', 0) for e in executions),
            cache_hits=sum(e.get('cache_hits', 0) for e in executions),
            proof_bytes=sum(e.get('proof_bytes', 0) for e in executions),
            logical_native_nodes=sum(e.get('logical_native_nodes', 0) for e in executions),
            truncated=any(e['truncated'] for e in executions),
            errors=[e.get('error') for e in executions if e.get('error')],
            semantic_sha256=semantic, artifact=str(target.relative_to(out)), artifact_sha256=sha(target),
            execution=executions))
    assert rows[0]['semantic_sha256'] == rows[1]['semantic_sha256'], 'Cold/warm semantic or proof mismatch'
    assert not any(row['truncated'] or row['errors'] for row in rows)
    receipt = dict(passed=True, workload=name, arm=arm, repetition=repetition, rows=rows,
        production_code_hash=production_code_hash(), runtime=runtime.manifest,
        model_versions={key:model.version for key,model in models.items()}, options=asdict(options),
        memory_scope='Fresh worker per workload/arm/repetition; warm RSS includes retained cold output and caches. Child maximum RSS is not an aggregate working-set estimate.',
        cache_intervention='Both arms retain pure native math memoization. Full clears dependency-bound relation records before every state; incremental retains them. Query domains are reconstructed in both arms.')
    write_json(out/'performance/receipts'/f'{name}-{arm}-{repetition}.json', receipt)


def run(out):
    out = Path(out).resolve()
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    population = workloads(out)
    write_json(out/'performance/workloads.json', dict(workloads=population,
        selection='Hash-selected from registered sources without consulting predictions or preference labels.',
        repetitions=5, inference_oracle=False))
    all_rows = []
    for name in population:
        for repetition in range(5):
            order = ('full', 'incremental') if repetition % 2 == 0 else ('incremental', 'full')
            for arm in order:
                target = out/'performance/receipts'/f'{name}-{arm}-{repetition}.json'
                # Every run is executed afresh; benchmark receipts are never resumed as timings.
                if target.exists():
                    raise ValueError('Preserve the previous benchmark generation before running again')
                log = out/'performance/logs'/f'{name}-{arm}-{repetition}.txt'
                log.parent.mkdir(parents=True, exist_ok=True)
                with log.open('w') as stream:
                    subprocess.run([sys.executable, '-m', 'evaluation.cycle13_performance', '--out', str(out), '--worker',
                        name, '--arm', arm, '--repetition', str(repetition)], cwd=ROOT,
                        env=dict(os.environ, TMPDIR='/dev/shm'), stdout=stream, stderr=subprocess.STDOUT, check=True)
                all_rows.extend(read_json(target)['rows'])
                print('BENCHMARK', name, arm, repetition, flush=True)
    parity = {}
    summaries = []
    for name in population:
        selected = [row for row in all_rows if row['workload'] == name]
        hashes = {row['semantic_sha256'] for row in selected}
        assert len(hashes) == 1, name
        parity[name] = dict(exact=True, compared_runs=len(selected), semantic_sha256=next(iter(hashes)))
        for arm in ('full', 'incremental'):
            for temperature in ('cold', 'warm'):
                rows = [row for row in selected if row['arm'] == arm and row['temperature'] == temperature]
                summaries.append(dict(workload=name, arm=arm, temperature=temperature, repetitions=len(rows),
                    medians={key:statistics.median(row[key] for row in rows) for key in
                        ('elapsed_seconds','native_invocations','interpreter_process_launches','grounded_atoms',
                         'cache_hits','proof_bytes','logical_native_nodes','peak_process_rss_kib','peak_child_rss_kib')},
                    runtime_min=min(row['elapsed_seconds'] for row in rows), runtime_max=max(row['elapsed_seconds'] for row in rows),
                    truncation_rate=sum(row['truncated'] for row in rows)/len(rows),
                    timeout_count=sum('timeout' in str(row['errors']).lower() for row in rows)))
    write_json(out/'performance/summary.json', dict(passed=True, rows=all_rows, summaries=summaries,
        parity=parity, workload_count=len(population), isolated_processes=40, measured_requests=len(all_rows),
        repetitions=5, parallel_native_workloads=False, inference_includes_serialization=False,
        sampling_scope='Four fixed registered workloads; repeated timings are not independent chess examples.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    parser.add_argument('--worker', choices=('single','multiple','two-ply','three-ply'))
    parser.add_argument('--arm', choices=('full','incremental'))
    parser.add_argument('--repetition', type=int)
    args = parser.parse_args()
    if args.worker:
        worker(args.out, args.worker, args.arm, args.repetition)
    else:
        run(args.out)
