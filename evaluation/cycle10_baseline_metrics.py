"""Aggregate fresh Cycle 9 receipts and compare reported cohort measurements."""
import argparse
from collections import defaultdict
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json


def run(out):
    out=Path(out);groups=defaultdict(list)
    for path in (out/'baseline/evaluation').glob('operational-*.receipt.json'):
        name=path.name.removeprefix('operational-').rsplit('-',1)[0];groups[name].append(read_json(path))
    original=read_json(ROOT/'artifacts/cycle9/analysis/evaluation-summary.json');results={}
    for name,receipts in sorted(groups.items()):
        tp=sum(r['metrics']['true_positive'] for r in receipts);fp=sum(r['metrics']['false_positive'] for r in receipts)
        fn=sum(r['metrics']['false_negative_including_abstention'] for r in receipts);n=sum(r['positions'] for r in receipts)
        exact=sum(round(r['metrics']['exact_move_set_accuracy']*r['positions']) for r in receipts)
        metrics=dict(precision=tp/(tp+fp) if tp+fp else 0,recall=tp/(tp+fn) if tp+fn else 0,
            f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,positions=n,exact_positions=exact,
            exact_move_set_accuracy=exact/n if n else 0,false_positive=fp,
            false_illegal=sum(r['metrics']['false_illegal'] for r in receipts),
            self_check_false_legal=sum(r['metrics']['self_check_false_legal'] for r in receipts),
            incomplete=sum(r['metrics']['incomplete'] for r in receipts))
        previous=original['operational/'+name]['complete']
        assert all(abs(metrics[k]-previous[k])<1e-12 for k in metrics),(name,metrics,previous)
        results[name]=dict(reproduced=metrics,reported={k:previous[k] for k in metrics},equal=True)
    assert set(results)=={'development','calibration','independent-games','adversarial','special-moves'}
    write_json(out/'baseline/cohort-metrics.json',dict(passed=True,cohorts=results,
        scope='Fresh native inference metrics. Full row/proof comparison and fresh timings are separate baseline receipts.'))
    print({k:v['reproduced'] for k,v in results.items()})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
