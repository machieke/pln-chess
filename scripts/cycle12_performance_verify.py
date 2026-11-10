"""Check benchmark completeness and independently replay its temporal proof hash."""
import argparse
from pathlib import Path

from evaluation.cycle7_io import pack
from evaluation.cycle12_performance import WORKLOADS
from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle11.fields.model import FieldModel
from pln_chess.cycle12.temporal import replay_fields, semantic_replay
from pln_chess.pln import Runtime
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out).resolve();summary=read_json(out/'performance/summary.json')
    assert summary['passed'] and summary['production_code_hash']==production_code_hash()
    temporal=[];checks=[]
    for name in WORKLOADS:
        for repetition in range(summary['repetitions']):
            path=out/f'performance/workers/{name}-{repetition}.json';worker=read_json(path)
            records={r['condition']:r for r in worker['measurements']}
            assert worker['exact_proof_evidence_graph_parity']
            for labels in [('full-cold','full-warm-existing-cache','dependency-parent-preparation'),
                           ('successor-full-cold','successor-dependency-reuse')]:
                for key in ('proof_hash','graph_hash'):
                    assert len({records[label][key] for label in labels})==1
                assert all(not records[label]['execution']['truncated'] for label in labels)
            concepts=records['eight-concept-conditional-queries']
            assert concepts['concepts']==8 and not concepts['execution']['truncated']
            for label in ('legal-accepted-full-fen','legal-candidate-full-fen'):
                assert records[label]['classifications']['incomplete']==0
            if name=='standard-opening':
                assert records['seven-state-temporal-replay']['states']==7
                temporal.append(records['seven-state-temporal-replay']['semantic_hash'])
            checks.append(dict(worker=str(path.relative_to(out)),sha256=sha(path),complete=True))
    assert len(checks)==42 and len(temporal)==7 and len(set(temporal))==1
    # Run only after all timed workers finish. This replay is deliberately outside
    # the measured conditions and verifies their retained complete-result hash.
    runtime=Runtime(timeout=600)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    supplied=next(r['input'] for r in read_json(out/'datasets/sequences.json')['sequences']
                  if r['input']['id']=='developing-attack')
    replay=replay_fields(supplied,field,runtime=runtime,options=FieldOptions(timeout_seconds=600))
    target=out/'performance/complete-temporal-reference.json.xz';pack(target,replay)
    expected=digest(semantic_replay(replay))
    temporal_checks=dict(complete_history=replay['complete_history'],complete_execution=not replay['execution']['truncated'],
        seven_states=len(replay['states'])==7,
        all_fields_complete=all(s['field'] and not s['field']['execution']['truncated'] for s in replay['states']),
        every_timed_hash_matches=all(value==expected for value in temporal))
    passed=all(temporal_checks.values())
    write_json(out/'performance/semantic-verification.json',dict(passed=passed,production_code_hash=production_code_hash(),
        driver_sha256=sha(__file__),workers=checks,complete_workers=len(checks),temporal_repetitions=len(temporal),
        temporal_states=len(replay['states']),temporal_checks=temporal_checks,
        temporal_semantic_hash=expected,reference_artifact=str(target.relative_to(out)),
        reference_sha256=sha(target),
        memory_scope_note='The legacy raw native_child_peak_rss_kib keys record getrusage(RUSAGE_CHILDREN).ru_maxrss across all terminated child commands. They may include inherited launch memory and do not isolate the native runtime working set. Raw values and timed worker files are preserved unchanged.',
        scope='Checks completeness of timed field, concept and legal results, then compares every timed temporal hash with an independent native replay. The reference and failed checks are retained. This extra replay is outside performance timings.'))
    assert passed,temporal_checks
    print('All 42 benchmark workers are complete; all 7 temporal hashes match the fresh complete native replay.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
