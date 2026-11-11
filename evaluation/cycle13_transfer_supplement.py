"""Ten explicitly selected correct held-out illustrations, separate from accuracy.

The original ordering and every fixed-cohort metric remain untouched. These
examples are selected after outcomes solely to inspect successful derivations.
"""
import argparse
from collections import Counter
from pathlib import Path
from pln_chess.common import digest,read_json,write_json
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from scripts.cycle13_clean_research import normalized
from scripts.cycle9_baseline import sha
import json


def build(out):
    out=Path(out);rows=read_gzip(out/'preferences/relational.json.xz')
    ledger={r['evidence_id']:r for r in (json.loads(line) for line in (out/'learning/relational/ledger.jsonl').read_text().splitlines())}
    eligible=[r for r in rows if r['split']!='train' and r['label'] in ('A','B') and
        r['result']['conditional_proof_complete'] and r['result']['status']==r['label']+'-preferred']
    eligible.sort(key=lambda r:(r['split']!='test',r['id']))
    selected=eligible[:10];assert len(selected)==10
    examples=[]
    for row in selected:
        preference=row['result'];training=[ledger[e] for e in preference['evidence_ids']]
        assert training and all(e['payload']['source_game']!=row['source_game'] and
            e['payload']['dependence_group']!=row['dependence_group'] and e['payload']['source_position']!=row['fen'] for e in training)
        assert digest(preference['proof_trace'])==preference['proof_id']
        feature=read_gzip(out/row['feature_artifact'])
        examples.append(dict(id=row['id'],split=row['split'],source=row['source_record'],training_evidence=training,
            packet=row['packet'],descriptor=preference['descriptor'],native_preference=preference,
            reference_label=row['label'],reference_evidence_id=row['reference_evidence_id'],
            endpoint_graphs={name:state['graph'] for name,state in feature['states'].items()},
            feature_artifact=row['feature_artifact'],independent_training_ancestry=True,
            correct_reference_direction=True,joint_strategic_proof=False,
            selection='Post-hoc correct answered held-out cases; test cases first, then calibration, ordered by ID. Illustrations only, not an accuracy estimate or ten independent test successes.'))
    assert len({r['source']['source_game'] for r in examples})==10
    return examples,dict(passed=True,demonstrations=len(examples),available_correct_heldout_cases=len(eligible),
        selected_partitions=dict(Counter(r['split'] for r in examples)),correct_reference_directions=10,
        posthoc_success_selection=True,accuracy_estimate=False,model_or_threshold_selection=False,
        model_version=read_json(out/'preferences/summary.json')['model_version'],
        initial_demonstrations_retained='transfer/demonstrations.json.xz',
        initial_summary=read_json(out/'transfer/summary.json'),
        full_test_metrics=read_json(out/'preferences/summary.json')['panels']['test'],
        selection='First ten correct answered held-out rows, ordered by test partition before calibration and then ID.',
        scope='Inspectable successful native conditional applications on supplied relative packets. Success selection cannot establish accuracy, complete strategy, or readiness for move selection.')


def run(out,compare=False):
    out=Path(out);examples,summary=build(out)
    semantic=digest(normalized(examples));pack(out/'verified-transfer/demonstrations.json.xz',examples)
    del examples
    if compare:
        replayed,replayed_summary=build(out/'clean-research/run')
        assert digest(normalized(replayed))==semantic and summary==replayed_summary
        pack(out/'clean-research/run/verified-transfer/demonstrations.json.xz',replayed)
        write_json(out/'clean-research/run/verified-transfer/summary.json',replayed_summary)
    summary.update(fresh_replay_verified=compare,semantic_sha256=semantic,
        artifact_sha256=sha(out/'verified-transfer/demonstrations.json.xz'),
        source_predictions_sha256=sha(out/'preferences/relational.json.xz'))
    write_json(out/'verified-transfer/summary.json',summary)
    print('POST-HOC CORRECT TRANSFER ILLUSTRATIONS',summary['selected_partitions'],'replay verified:',compare,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--compare',action='store_true')
    args=parser.parse_args();run(args.out,args.compare)
