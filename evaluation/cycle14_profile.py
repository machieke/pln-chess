"""Diagnostic C13 profiles before compact-response implementation, not benchmarks."""
import argparse
import cProfile
import io
import lzma
from pathlib import Path
import pstats
import resource
import time

from pln_chess.common import ROOT, canonical, digest, write_json
from evaluation.cycle13_performance import CountedRuntime, workloads


def models(runtime, temporal=False):
    from pln_chess.learning import Model
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle13.concepts import ForkModel
    from pln_chess.cycle13.model import PreferenceModel
    return dict(legal_model=Model.load(ROOT/'artifacts/cycle12/model/C12-default.json',runtime),
        field_model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime),
        concept_model=ConceptModel.load(ROOT/'artifacts/cycle12/model/C12-concept-trained.json',runtime),
        fork_model=ForkModel.load(ROOT/'artifacts/cycle13/model/C13-fork-role.json',runtime),
        preference_model=PreferenceModel.load(ROOT/('artifacts/cycle13/model/C13-preference-temporal.json'
            if temporal else 'artifacts/cycle13/model/C13-preference-relational.json'),runtime))


def run(out):
    from pln_chess.cycle13.api import compare_moves, PreferenceOptions, PreferenceSession
    from pln_chess.cycle13.temporal import analyze_continuations
    from pln_chess.cycle12.temporal import semantic_replay
    from pln_chess.cycle6.inference import production_code_hash
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    assert not (out/'profile.json').exists(), 'Preserve prior profile generations'
    rows=[]
    for name, workload in workloads(ROOT/'artifacts/cycle13').items():
        began=time.perf_counter();runtime=CountedRuntime(timeout=900)
        runtime_load=time.perf_counter()-began
        began=time.perf_counter();loaded=models(runtime,'ply' in name)
        model_load=time.perf_counter()-began
        began=time.perf_counter();runtime.execute('!(println! C14StartupProbe)')
        startup=time.perf_counter()-began
        session=PreferenceSession(runtime);options=PreferenceOptions(timeout_seconds=900)
        for temperature in ('cold','warm'):
            profiler=cProfile.Profile();began=time.perf_counter()
            launches,native_before=runtime.process_launches,runtime.elapsed
            profiler.enable()
            if workload['kind']=='pairs':
                result=[compare_moves(row['fen'],*row['moves'],**loaded,runtime=runtime,session=session,
                    options=options,history=row['history'],source='cycle14-profile/'+row['id']) for row in workload['pairs']]
            else:
                plan=workload['plan'];horizon=workload['horizon']
                branches={side:[line[:horizon]] for side,line in plan['branches'].items()}
                result=[analyze_continuations(plan['fen'],branches,**loaded,runtime=runtime,session=session,
                    options=options,history=plan['history'],horizons=(horizon,),
                    source='cycle14-profile/'+plan['id'],selection_provenance=plan['response_selection'])]
            profiler.disable();inference=time.perf_counter()-began
            stream=io.StringIO();stats=pstats.Stats(profiler,stream=stream).sort_stats('cumulative')
            stats.print_stats(60);(out/f'{name}-{temperature}.txt').write_text(stream.getvalue())
            phases=[dict(file=key[0],line=key[1],function=key[2],primitive_calls=value[0],calls=value[1],
                own_seconds=value[2],cumulative_seconds=value[3]) for key,value in stats.stats.items()
                if key[2] in ('prepare','build_state','infer_queries','build_graph','infer_preferences',
                    'execute','batch','deepcopy','compare_fields','compare_concepts','packet_for','enumerate_concepts')]
            began=time.perf_counter();raw=canonical(result).encode();serialization=time.perf_counter()-began
            began=time.perf_counter();compressed=lzma.compress(raw,preset=1);compression=time.perf_counter()-began
            row=dict(workload=name,temperature=temperature,runtime_load_seconds=runtime_load,
                model_load_seconds=model_load,empty_interpreter_launch_seconds=startup,
                profiled_inference_seconds=inference,native_execution_including_startup_seconds=runtime.elapsed-native_before,
                interpreter_launches=runtime.process_launches-launches,serialization_seconds=serialization,
                compression_seconds=compression,canonical_json_bytes=len(raw),xz_preset1_bytes=len(compressed),
                process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                semantic_sha256=digest(semantic_replay(result)),phases=phases,
                truncated=any(r['execution']['truncated'] for r in result))
            assert not row['truncated'];rows.append(row)
            write_json(out/'progress.json',rows)
            print('PROFILE',name,temperature,round(inference,2),flush=True)
            del raw,compressed,result
    for name in workloads(ROOT/'artifacts/cycle13'):
        assert len({r['semantic_sha256'] for r in rows if r['workload']==name})==1
    write_json(out/'profile.json',dict(passed=True,production_code_hash=production_code_hash(),runtime=runtime.manifest,
        model_versions={k:m.version for k,m in loaded.items()},rows=rows,
        scope='Instrumented diagnostic profile under concurrent baseline jobs; not a headline latency benchmark. '
            'Cumulative function times overlap. Empty interpreter launch includes library import. '
            'Peak memory is per-process cumulative, not per-workload working set. No child maxima are added.',
        browser_transfer_measured=False,archive_retrieval_measured=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14/profile-before')
    run(parser.parse_args().out)
