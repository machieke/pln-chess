"""Isolated-process field benchmarks with exact incremental proof comparisons."""
import argparse
import json
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from evaluation.cycle7_io import pack

WORKLOADS = ('rook-obstruction', 'knight-relocation', 'promotion', 'en-passant', 'en-passant-exposure', 'published-midgame')
COSTS = ('native_invocations', 'scheduled_invocations', 'cache_hits', 'relation_cache_hits',
         'relation_cache_invalidations', 'grounded_atoms', 'proof_bytes', 'elapsed_seconds', 'truncated')


def semantic(field):
    return [{k:r[k] for k in ('relation_id', 'family', 'source_entity', 'target_square', 'raw_stv',
        'classification', 'rule_id', 'evidence_ids', 'proof_id')} for r in field['relations']]


def worker(out, name, repetition):
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, build_field
    out = Path(out)
    runtime = Runtime(timeout=600)
    model = FieldModel.load(out / 'model/C11-field-trained.json', runtime)
    options = FieldOptions(timeout_seconds=600, max_native_invocations=100000)
    if name == 'published-midgame':
        data = read_json(ROOT / 'artifacts/cycle10/datasets/dataset.json')
        games = {g['id']:g for g in data['games']}
        fixture = next(p for p in data['positions'] if p['split'] == 'external-test' and p['ply'] >= 40
            and len(Position.from_fen(p['fen']).pieces) >= 20 and p['ply'] < len(games[p['source_game']]['moves']))
        case = dict(id=name, fen=fixture['fen'], move=games[fixture['source_game']]['moves'][fixture['ply']],
            unknown_squares=[], fixture=fixture['id'], source_game=fixture['source_game'],
            selection='First registered external-test fixture with at least 40 supplied plies, at least 20 pieces and a supplied next move; no model predictions used.')
    else:
        case = next(row for row in read_json(out / 'datasets/worked-controls.json')['worked'] if row['id'] == name)
    position = Position.from_fen(case['fen'], unknown_squares=case['unknown_squares'])
    successor = position.successor(find_move(position, case['move']))
    session = FieldSession(runtime)
    measurements = []

    def measure(label, current, cache, families=None):
        tracemalloc.start()
        started = time.perf_counter()
        extra = dict(families=families) if families else {}
        result = build_field(current, model, options=options, runtime=runtime, session=cache,
            source='cycle11-performance-observation', **extra)
        elapsed = time.perf_counter()-started
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert not result['execution']['truncated']
        measurements.append(dict(condition=label, wall_seconds=elapsed,
            python_allocations_peak_bytes=peak, relations=len(result['relations']),
            static_proof_hash=digest(semantic(result)), **{key:result['execution'][key] for key in COSTS}))
        return result

    cold = measure('full-cold', position, session)
    warm = measure('full-warm', position, session)
    full_after = measure('successor-full-cold', successor, FieldSession(runtime))
    incremental = measure('successor-incremental', successor, session)
    assert semantic(cold) == semantic(warm)
    assert semantic(full_after) == semantic(incremental)
    assert incremental['execution']['relation_cache_hits'] > 0
    assert incremental['execution']['relation_cache_invalidations'] > 0
    for family in ('attack', 'defense', 'mobility', 'king-exposure'):
        measure('family-'+family, position, FieldSession(runtime), families=[family])
    # Multi-candidate work uses a shared parent field and separate hypothetical
    # snapshots. Each alternative is verified against an independent full run.
    from pln_chess.hypotheses import candidates
    alternatives = [m for m in candidates(position) if position.successor(m) is not None][:3]
    multi = []
    for index, move in enumerate(alternatives):
        other = position.successor(move)
        full = measure('multi-full-'+str(index), other, FieldSession(runtime))
        cached = measure('multi-incremental-'+str(index), other, session)
        assert semantic(full) == semantic(cached)
        multi.append(dict(move=move.notation, exact_native_proof_parity=True))
    result = dict(workload=name, repetition=repetition, source_case=case, measurements=measurements,
        model_version=model.version, runtime_version=runtime.version,
        exact_incremental_and_warm_proof_parity=True, multi_candidate_parity=multi,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        largest_native_child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        memory_scope='Linux per-worker process high-water RSS and maximum child high-water RSS, not summed concurrent memory. Per-condition tracemalloc measures Python allocations only.',
        timing_scope='Model/runtime construction excluded. Full observation, grounding, native inference, proof assembly and serialization-size accounting included; no concurrent study inference workers.')
    write_json(out / f'performance/workers/{name}-{repetition}.json', result)


def run(out):
    out = Path(out).resolve()
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    assert read_json(out / 'current/verified.json')['passed']
    active = subprocess.run(['pgrep', '-x', 'swipl'], capture_output=True, text=True)
    if active.returncode == 0:
        raise RuntimeError('Timed inference requires native-worker quiescence: '+active.stdout.strip())
    repetitions = read_json(ROOT / 'configs/cycle11.json')['benchmark_repetitions']
    env = dict(os.environ, TMPDIR='/dev/shm')
    for repetition in range(repetitions):
        for name in WORKLOADS:
            argv = [sys.executable, '-m', 'evaluation.cycle11_performance', '--out', str(out),
                    '--worker', name, '--repetition', str(repetition)]
            log = out / f'performance/logs/{name}-{repetition}.txt'
            log.parent.mkdir(parents=True, exist_ok=True)
            started = time.time()
            with log.open('w') as stream:
                result = subprocess.run(argv, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
            write_json(out / f'performance/commands/{name}-{repetition}.json', dict(argv=argv,
                started_unix=started, elapsed_seconds=time.time()-started, returncode=result.returncode))
            if result.returncode:
                raise RuntimeError(str(log))
            print('Benchmark', name, repetition+1, '/', repetitions, flush=True)
    rows = [read_json(out / f'performance/workers/{name}-{i}.json') for name in WORKLOADS for i in range(repetitions)]
    summary = {}
    for name in WORKLOADS:
        subset = [r for r in rows if r['workload'] == name]
        summary[name] = {}
        for condition in sorted({m['condition'] for r in subset for m in r['measurements']}):
            records = [m for r in subset for m in r['measurements'] if m['condition'] == condition]
            values = sorted(m['wall_seconds'] for m in records)
            summary[name][condition] = dict(repetitions=len(records), median_seconds=statistics.median(values),
                minimum_seconds=values[0], maximum_seconds=values[-1],
                empirical_p95_seconds=values[min(len(values)-1, int(.95*len(values)))],
                median_native_invocations=statistics.median(m['native_invocations'] for m in records),
                median_relation_cache_hits=statistics.median(m['relation_cache_hits'] for m in records),
                median_relation_cache_invalidations=statistics.median(m['relation_cache_invalidations'] for m in records),
                median_grounded_atoms=statistics.median(m['grounded_atoms'] for m in records),
                median_proof_bytes=statistics.median(m['proof_bytes'] for m in records),
                maximum_python_allocations_peak_bytes=max(m['python_allocations_peak_bytes'] for m in records))
    write_json(out / 'performance/summary.json', dict(passed=True, workloads=summary,
        repetitions=repetitions, native_proof_parity=True,
        all_exact_incremental_reuse=all(r['exact_incremental_and_warm_proof_parity'] for r in rows),
        max_process_peak_rss_kib=max(r['process_peak_rss_kib'] for r in rows),
        max_native_child_peak_rss_kib=max(r['largest_native_child_peak_rss_kib'] for r in rows),
        limitations='Nine repetitions give weak tail resolution. RSS is per fresh workload worker; Python allocation tracking adds overhead. Warm runtime computations are cached pure native expressions; no strategic search or move ranking is benchmarked.'))
    pack(out / 'performance/measurements.json.xz', rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--worker')
    parser.add_argument('--repetition', type=int, default=0)
    args = parser.parse_args()
    worker(args.out, args.worker, args.repetition) if args.worker else run(args.out)
