"""Quiescent process benchmarks of dependency scheduling and native proofs."""
import argparse
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

WORKLOADS=('rook-obstruction','promotion','en-passant','en-passant-exposure','standard-opening','published-midgame')


def case_for(name):
    if name=='standard-opening':
        return dict(id=name,fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',move='e2e4',unknown_squares=[])
    if name=='published-midgame':
        data=read_json(ROOT/'artifacts/cycle10/datasets/dataset.json');games={g['id']:g for g in data['games']}
        fixture=next(p for p in data['positions'] if p['split']=='external-test' and p['ply']>=40
            and len(Position.from_fen(p['fen']).pieces)>=20 and p['ply']<len(games[p['source_game']]['moves']))
        return dict(id=name,fen=fixture['fen'],move=games[fixture['source_game']]['moves'][fixture['ply']],
            unknown_squares=[],fixture=fixture['id'],source_game=fixture['source_game'],
            selection='First registered external-test fixture with >=40 supplied plies, >=20 pieces and a supplied next move; no predictions used.')
    return next(r for r in read_json(ROOT/'artifacts/cycle11/datasets/worked-controls.json')['worked'] if r['id']==name)


def worker(out,name,repetition):
    from pln_chess.pln import Runtime
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, build_field
    from pln_chess.cycle12.incremental import IncrementalFieldSession, structural_successor
    from pln_chess.cycle12.graph import build_graph
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle12.inference import infer_concepts, ConceptSession
    from pln_chess.cycle12.temporal import replay_fields, semantic_replay
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import infer_moves as legal_infer, Cycle8Options
    out=Path(out);case=case_for(name);runtime=Runtime(timeout=600)
    field_model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    concept_model=ConceptModel.load(out/'model/C12-concept-trained.json',runtime)
    position=Position.from_fen(case['fen'],unknown_squares=case['unknown_squares'])
    successor=structural_successor(position,case['move'])
    options=FieldOptions(timeout_seconds=600);source='cycle12-performance-observation'
    session=IncrementalFieldSession(runtime);old_session=FieldSession(runtime);measurements=[]

    def measure(label,fn):
        tracemalloc.start();started=time.perf_counter();calls=runtime.invocations
        result=fn();elapsed=time.perf_counter()-started
        _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        measurements.append(dict(condition=label,wall_seconds=elapsed,python_peak_bytes=peak,
            native_invocations=runtime.invocations-calls))
        return result

    def full(p,cache):
        field=build_field(p,field_model,options=options,runtime=runtime,session=cache,source=source)
        return field,build_graph(field)

    def incremental(p):
        field=session.build(p,field_model,options=options,source=source)
        return field,build_graph(field)

    initial=measure('full-cold',lambda:full(position,old_session))
    warmed=measure('full-warm-existing-cache',lambda:full(position,old_session))
    assert initial[0]['relations']==warmed[0]['relations'] and initial[1]==warmed[1]
    # Prepare the exact same parent in the dependency scheduler outside the
    # successor measurement; report the preparation separately.
    prepared=measure('dependency-parent-preparation',lambda:incremental(position))
    assert prepared[0]['relations']==initial[0]['relations'] and prepared[1]==initial[1]
    after_full=measure('successor-full-cold',lambda:full(successor,FieldSession(runtime)))
    after_incremental=measure('successor-dependency-reuse',lambda:incremental(successor))
    assert after_full[0]['relations']==after_incremental[0]['relations']
    assert after_full[1]==after_incremental[1]
    for index,result in enumerate((initial,warmed,prepared,after_full,after_incremental)):
        field,graph=result;assert not field['execution']['truncated']
        measurements[index].update(relations=len(field['relations']),proof_hash=digest(field['relations']),
            graph_hash=digest(graph),graph_nodes=len(graph['nodes']),graph_edges=len(graph['edges']),
            execution=field['execution'],incremental=field.get('incremental'))
    data=read_json(out/'datasets/concepts.json')
    cases=[next(r['input'] for r in data['records'] if r['split']=='test' and r['input']['concept']==concept and r['variant']=='base')
           for concept in data['targets']]
    concepts=measure('eight-concept-conditional-queries',lambda:infer_concepts(cases,concept_model,field_model,
        options=options,runtime=runtime,session=ConceptSession(runtime)))
    measurements[-1].update(concepts=len(concepts['concepts']),proof_hash=digest(concepts['concepts']),execution=concepts['execution'])
    for label,path in [('legal-accepted-full-fen','artifacts/cycle10/model/C10-default.json'),
                       ('legal-candidate-full-fen','artifacts/cycle11/model/C11-special-local.json')]:
        legal_model=PromotionModel.load(ROOT/path,runtime)
        legal=measure(label,lambda:legal_infer(position,legal_model,Cycle8Options(mode='operational',timeout_seconds=600,max_native_invocations=100000),runtime))
        assert not legal['truncated']
        measurements[-1].update(candidates=len(legal['candidates']),model_version=legal_model.version,
            proof_hash=digest([c['proof_trace'] for c in legal['candidates']]),
            classifications={status:sum(c['classification']==status for c in legal['candidates']) for status in ('supported-legal','supported-illegal','unknown','incomplete')},
            temporal_scope='FEN-only benchmark. Complete supplied-history accuracy is separately tested in the full legal population review.')
    if name=='standard-opening':
        supplied=next(r['input'] for r in read_json(out/'datasets/sequences.json')['sequences'] if r['input']['id']=='developing-attack')
        temporal=measure('seven-state-temporal-replay',lambda:replay_fields(supplied,field_model,runtime=runtime,options=options))
        measurements[-1].update(states=len(temporal['states']),semantic_hash=digest(semantic_replay(temporal)))
    write_json(out/f'performance/workers/{name}-{repetition}.json',dict(workload=name,repetition=repetition,
        case=case,pieces=len(position.pieces),measurements=measurements,field_model_version=field_model.version,
        concept_model_version=concept_model.version,runtime_version=runtime.version,exact_proof_evidence_graph_parity=True,
        cold_cache_scope='Fresh inference/session caches within each new worker; operating-system and filesystem caches are not flushed.',
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        native_child_peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        timing_scope='Model/runtime construction excluded. Field observation, native inference, proof assembly, graph construction and its internal identity/validation hashing included. Additional parity digest calculations are outside the timed condition. Parent preparation is separately timed. No competing study workers.',
        memory_scope='Python tracemalloc peak per condition; Linux high-water RSS per fresh worker and maximum native child. Worker RSS includes retained comparison outputs for parity checks, not only one inference result. These are not total concurrent memory. Allocation tracking adds timing overhead.'))


def run(out):
    out=Path(out).resolve()
    assert read_json(out/'current/verified.json')['passed']
    assert read_json(out/'legal/regression-summary.json')['passed'] or read_json(out/'legal/promotion-decision.json')['promoted'] is False
    if subprocess.run(['pgrep','-x','swipl'],stdout=subprocess.DEVNULL).returncode==0:
        raise RuntimeError('Performance measurements require native-worker quiescence')
    repetitions=read_json(ROOT/'configs/cycle12.json')['benchmark_repetitions']
    for repetition in range(repetitions):
        for name in WORKLOADS:
            argv=[sys.executable,'-m','evaluation.cycle12_performance','--out',str(out),'--worker',name,'--repetition',str(repetition)]
            log=out/f'performance/logs/{name}-{repetition}.txt';log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
            with log.open('w') as stream:result=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT)
            write_json(out/f'performance/commands/{name}-{repetition}.json',dict(argv=argv,started_unix=started,
                elapsed_seconds=time.time()-started,returncode=result.returncode))
            if result.returncode:raise RuntimeError(str(log))
            print('DEPENDENCY BENCHMARK',name,repetition+1,'/',repetitions,flush=True)
    rows=[read_json(out/f'performance/workers/{name}-{i}.json') for name in WORKLOADS for i in range(repetitions)]
    summary={}
    for name in WORKLOADS:
        summary[name]={}
        subset=[r for r in rows if r['workload']==name]
        for condition in sorted({m['condition'] for r in subset for m in r['measurements']}):
            records=[m for r in subset for m in r['measurements'] if m['condition']==condition]
            seconds=sorted(m['wall_seconds'] for m in records)
            summary[name][condition]=dict(repetitions=len(records),median_seconds=statistics.median(seconds),
                minimum_seconds=seconds[0],maximum_seconds=seconds[-1],empirical_p95_seconds=seconds[-1],
                median_native_invocations=statistics.median(m['native_invocations'] for m in records),
                maximum_python_peak_bytes=max(m['python_peak_bytes'] for m in records))
    write_json(out/'performance/summary.json',dict(passed=True,repetitions=repetitions,workloads=summary,
        exact_proof_evidence_graph_parity=all(r['exact_proof_evidence_graph_parity'] for r in rows),
        max_process_peak_rss_kib=max(r['process_peak_rss_kib'] for r in rows),
        max_native_child_peak_rss_kib=max(r['native_child_peak_rss_kib'] for r in rows),
        limitations='Seven repetitions have weak tail resolution. Tracemalloc adds overhead; reported p95 is the empirical maximum. Legal accuracy is measured in separate complete replay cohorts. No strategic search or ranking is benchmarked.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--worker')
    parser.add_argument('--repetition',type=int,default=0);args=parser.parse_args()
    worker(args.out,args.worker,args.repetition) if args.worker else run(args.out)
