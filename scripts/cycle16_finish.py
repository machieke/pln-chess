"""Finish local evidence only after complete preservation and evaluation pass."""
import argparse
import json
from pathlib import Path
import shutil
import time
from pln_chess.common import ROOT,read_json,write_json


def run(out):
    out=Path(out).resolve();last=None
    while not ((out/'preservation/cycle16-verification.json').exists() and (out/'evaluation/summary.json').exists()):
        commands=[read_json(p) for p in (out/'preservation/commands').glob('*.json')]
        failed=[c for c in commands if c['returncode']]
        if failed:raise RuntimeError('Preservation failed; retained receipts: '+str(failed))
        status=(len(commands),len(list((out/'evaluation/roots').glob('*.json'))))
        if status!=last:
            print('WAITING completed preservation jobs / evaluated roots:',status,flush=True);last=status
        time.sleep(20)
    preserved=read_json(out/'preservation/cycle16-verification.json')
    assert preserved['passed'] and preserved['legal_rows']==584112 and preserved['legal_shards']==206
    assert read_json(out/'reproduction/verified.json')['passed']
    print('Complete preservation and evaluation passed; starting separate benchmarks',flush=True)
    from evaluation.cycle16_performance import run as benchmark
    if not (out/'performance/summary.json').exists():benchmark(out/'performance',out/'learning/learned/model.json')
    from scripts.cycle16_audit import proof_audit,resources
    from scripts.cycle16_delivery import historical,pack
    proof_audit(out);resources(out);historical(out)
    copies=['evaluation/summary.json','performance/summary.json','performance/proof-integrity.json',
        'preservation/cycle16-verification.json','historical-final.json','resource-census.json',
        'supplement/proof-audit.json','supplement/bounded-controls.json','supplement/role-state-controls.json']
    for relative in copies:
        target=ROOT/'artifacts/cycle16'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/relative,target)
    restored=pack(out)
    print('CYCLE 16 EVIDENCE VERIFIED AND RESTORED',json.dumps(restored),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
