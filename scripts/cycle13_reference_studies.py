"""Run registered reference supervision only after the complete baseline gate."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha


def run(out, wait_baseline=False):
    out = Path(out).resolve()
    gate = out / 'baseline/reproduction-receipt.json'
    while wait_baseline and not gate.exists():
        time.sleep(2)
    baseline = read_json(gate)
    assert baseline['passed'] and baseline['legal_shards'] == 206 and baseline['exact_native_proof_parity']
    target = out / 'reference-studies'
    target.mkdir(parents=True,exist_ok=True)
    for name,module,extra in (
        ('pair-labels','training.cycle13_labels',[]),
        ('label-audit','evaluation.cycle13_data_audit',['--require-labels']),
        ('temporal-labels','training.cycle13_temporal_sources',[])):
        argv = [sys.executable,'-u','-m',module,'--out',str(out),*extra]
        log = target / (name + '.txt')
        started = time.time()
        print('REGISTERED REFERENCE STUDY',name,flush=True)
        with log.open('w') as stream:
            result = subprocess.run(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT)
        write_json(target / (name + '.command.json'),dict(argv=argv,returncode=result.returncode,
            started_unix=started,elapsed_seconds=time.time()-started,baseline_receipt_sha256=sha(gate),
            driver_sha256=sha(__file__),log=str(log.relative_to(out))))
        if result.returncode:
            raise RuntimeError(str(log))
    write_json(target / 'verified.json',dict(passed=True,baseline_receipt_sha256=sha(gate),
        pair_labels_sha256=sha(out / 'datasets/reference-labels.json'),
        temporal_labels_sha256=sha(out / 'datasets/temporal-labels.json'),
        label_audit_sha256=sha(out / 'datasets/audit.json'),
        scope='Offline registered reference labels only; not evidence of native preference accuracy.'))
    print('REGISTERED REFERENCE STUDIES COMPLETE',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',default='artifacts/cycle13')
    parser.add_argument('--wait-baseline',action='store_true')
    args = parser.parse_args()
    run(args.out,args.wait_baseline)
