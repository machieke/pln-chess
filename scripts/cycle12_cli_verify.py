"""Publish usable payloads and execute both new command-line contracts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle7_io import pack


def run(out):
    out=Path(out).resolve();data=read_json(out/'datasets/concepts.json');sequences=read_json(out/'datasets/sequences.json')
    case=next(r['input'] for r in data['records'] if r['input']['concept']=='Pin' and r['split']=='test' and r['variant']=='base')
    sequence=next(r['input'] for r in sequences['sequences'] if r['input']['id']=='promotion-threat')
    payloads={'concept':dict(fen=case['fen'],cases=[case],family='attack',max_candidates=1),
        'sequence':dict(sequence=sequence,family='attack',max_candidates=4)}
    rows=[];code_hash=production_code_hash()
    for name,payload in payloads.items():
        path=out/'examples'/f'{name}-payload.json';write_json(path,payload)
        argv=[sys.executable,'-m','pln_chess','concept-inspect' if name=='concept' else 'field-evolution','--input',str(path)]
        started=time.time()
        raw=subprocess.check_output(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm',C12_OUT=str(out)),text=True)
        result=json.loads(raw);assert not result['execution']['truncated']
        if name=='concept':assert result['concepts'][0]['classification']=='supported'
        else:assert len(result['states'])==5 and result['complete_history']
        pack(out/'cli-smoke'/f'{name}.json.xz',result)
        rows.append(dict(name=name,argv=argv,elapsed_seconds=time.time()-started,passed=True))
    assert code_hash==production_code_hash()
    write_json(out/'cli-smoke/verified.json',dict(passed=True,production_code_hash=code_hash,commands=rows))
    print('Both Cycle 12 CLI payloads verified',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
