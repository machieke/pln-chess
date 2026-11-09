"""Paired workload summaries and descriptive bootstrap timing comparisons."""
import argparse
from pathlib import Path
import random
import statistics
from pln_chess.common import ROOT,read_json,write_json


def compare(out):
    out=Path(out);before=read_json(out/'performance/C9-external.json');after=read_json(out/'performance/C10-current.json')
    assert before['model_version']==after['model_version'] and before['runtime']==after['runtime']
    assert before['dataset_hash']==after['dataset_hash'];records=[];rng=random.Random(100913)
    for left,right in zip(before['records'],after['records'],strict=True):
        assert left['fixture']==right['fixture']
        assert {s['candidate_digest'] for s in left['samples']}=={s['candidate_digest'] for s in right['samples']}
        assert all(not s['truncated'] and s['error'] is None for s in left['samples']+right['samples'])
        modes={}
        for mode in ('reference','cold','warm'):
            a=[s['wall_seconds'] for s in left['samples'] if s['mode']==mode];b=[s['wall_seconds'] for s in right['samples'] if s['mode']==mode]
            ratios=[]
            for _ in range(2000):
                # Runs are serial source blocks, so resample the two blocks independently.
                ratios.append(statistics.median(rng.choices(b,k=len(b)))/statistics.median(rng.choices(a,k=len(a))))
            ratios.sort();ci=[ratios[50],ratios[1949]]
            modes[mode]=dict(before=left['aggregates'][mode],after=right['aggregates'][mode],
                median_ratio=statistics.median(b)/statistics.median(a),ratio_interval95=ci,
                detectable_slowdown_at_this_sample=ci[0]>1,upper_bound_below_ten_percent=ci[1]<1.1,
                statistical_scope='Descriptive independent-block percentile bootstrap of nine repetitions; host drift and serial-block order are not randomized away.')
        records.append(dict(fixture=left['fixture']['id'],full_candidate_proof_parity=True,modes=modes))
    historical=read_json(out/'baseline/performance/C9-reproduced.json')
    old=read_json(ROOT/'artifacts/cycle9/performance/C9-optimized.json')
    reproduction=dict(reproduced=next(r['aggregates'] for r in historical['records'] if r['fixture']['id']=='full-214'),
                      originally_reported=next(r['aggregates'] for r in old['records'] if r['fixture']['id']=='full-214'))
    write_json(out/'performance/comparison.json',dict(passed_parity=True,model_version=before['model_version'],records=records,
        baseline_reproduction=reproduction,paired_workloads=len(records),new_samples=sum(len(r['samples']) for r in before['records']+after['records']),
        checkpoint_bytes=dict(before=before['checkpoint_bytes'],after=after['checkpoint_bytes']),
        checkpoint_load_seconds=dict(before=before['checkpoint_load_seconds'],after=after['checkpoint_load_seconds']),
        memory_scope=before['memory_scope'],quantile_limit=before['quantiles'],
        interpretation='No source changes to native arithmetic, observation construction, candidate generation or proof scheduling are permitted by this comparison. New interface/history code is measured separately. A nonsignificant difference is not proof of equal performance.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);compare(p.parse_args().out)
