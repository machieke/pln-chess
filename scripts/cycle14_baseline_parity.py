"""Resumable full baseline proof comparison after native shards finish."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import subprocess

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha
from scripts.cycle12_baseline import compare_reports
from scripts.cycle14_baseline import START


def compare(task):
    out,source,job=task;out,source=Path(out),Path(source)
    actual=out/'legal/evaluation'/(job['id']+'.json.xz')
    reference=source/job['reference']
    path=out/'comparison-receipts'/(job['id']+'.json')
    identity=dict(actual_sha256=sha(actual),reference_sha256=sha(reference),
        comparator_sha256=sha(ROOT/'scripts/cycle12_baseline.py'))
    if path.exists():
        receipt=read_json(path)
        assert receipt['identity']==identity and receipt['passed']
        return receipt['comparison']
    result=compare_reports(actual,reference)
    assert result['exact_native_proof_parity']
    write_json(path,dict(passed=True,identity=identity,comparison=result,
        orchestration_sha256=sha(__file__)))
    print('C14 BASELINE FULL PARITY',job['id'],flush=True)
    return result


def run(out,source,workers):
    out,source=Path(out).resolve(),Path(source).resolve()
    assert 1<=workers<=read_json(ROOT/'configs/cycle14.json')['budgets']['legal_workers']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==START
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    assert sha(ROOT/'scripts/cycle12_baseline.py')==sha(source/'scripts/cycle12_baseline.py')
    jobs=read_json(out/'legal/panel.json')['jobs'];assert len(jobs)==206
    receipts=[read_json(out/'legal/evaluation'/(job['id']+'.receipt.json')) for job in jobs]
    assert all(r['passed'] and not r['changes'] and r['native_proofs_verified'] for r in receipts)
    assert sum(r['rows'] for r in receipts)==584112
    with ProcessPoolExecutor(max_workers=workers) as pool:
        comparisons=list(pool.map(compare,[(str(out),str(source),job) for job in jobs]))
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    write_json(out/'legal-proof-parity.json',dict(passed=True,shards=206,rows=584112,
        comparisons=comparisons,exact_native_proof_parity=True,
        source_head=START,source_clean=True,comparison_workers=workers,
        orchestration_sha256=sha(__file__),comparator_sha256=sha(ROOT/'scripts/cycle12_baseline.py'),
        scope='Every independently executed native shard is compared in full with its frozen Cycle 13 reference. Per-shard receipts are bound to exact artifact bytes and permit resumption.'))
    print('C14 BASELINE COMPLETE FULL PROOF PARITY',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14/baseline')
    parser.add_argument('--source',required=True);parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args();run(args.out,args.source,args.workers)
