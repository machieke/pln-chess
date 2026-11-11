"""Fresh final tests and actual default CLI selection after all acceptance gates."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha


def run(out,checkout,commit):
    out=Path(out).resolve();checkout=Path(checkout).resolve();target=out/'final-checks'
    acceptance=read_json(out/'acceptance.json');assert acceptance['passed']
    code=production_code_hash();assert acceptance['production_code_hash']==code
    bootstrap(target/'bootstrap',checkout,commit)
    py=str(checkout/'.venv/bin/python');env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),
        PYTHONPATH=str(checkout/'src')+':'+str(checkout),C13_OUT=str(out),TMPDIR='/dev/shm')
    for cycle in range(6,13):env.pop(f'C{cycle}_OUT',None)
    started=time.time();log=target/'tests.txt'
    with log.open('w') as stream:
        subprocess.run([py,'-m','pytest','-q'],cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
    tests=int(re.search(r'(\d+) passed',log.read_text())[1]);assert tests>=588
    model=acceptance['default_model_version'];rows=[]
    # No checkpoint argument is supplied: exercise the actual CLI selector.
    for name,mode in (('automatic-default',None),('strict','strict'),('experimental','experimental')):
        argv=[str(checkout/'.venv/bin/pln-chess'),'inspect','--fen','7k/8/8/8/R6p/8/8/6K1 w - - 0 1',
            '--move','a4h4','--format','json',*(['--mode',mode] if mode else [])]
        result=json.loads(subprocess.check_output(argv,cwd=checkout,env=env,text=True))
        assert result['model_version']==model and result['mode']==(mode or 'operational')
        assert not result['truncated']
        if mode is None:assert result['candidate']['classification']=='supported-legal'
        write_json(target/(name+'.json'),result)
        rows.append(dict(name=name,argv=argv,mode=result['mode'],model_version=result['model_version'],
            classification=result['candidate']['classification']))
    # Also execute the user's working checkout without any cycle output override.
    local_env=dict(os.environ,TMPDIR='/dev/shm')
    for cycle in range(6,14):local_env.pop(f'C{cycle}_OUT',None)
    local_env.pop('PLN_CHESS_ROOT',None);local_env.pop('PYTHONPATH',None)
    argv=[str(ROOT/'.venv/bin/pln-chess'),'inspect','--fen','7k/8/8/8/R6p/8/8/6K1 w - - 0 1',
        '--move','a4h4','--format','json']
    result=json.loads(subprocess.check_output(argv,cwd=ROOT,env=local_env,text=True))
    assert result['model_version']==model and result['mode']=='operational' and result['candidate']['classification']=='supported-legal'
    write_json(target/'working-checkout-default.json',result)
    assert sha(out/'model/C13-default.json')==sha(ROOT/'artifacts/cycle12/model/C12-default.json')
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    assert production_code_hash()==code
    write_json(target/'verified.json',dict(passed=True,tests=tests,source_head=commit,checkout=str(checkout),
        source_clean=True,production_code_hash=code,acceptance_sha256=sha(out/'acceptance.json'),
        default_model_version=model,original_legal_checkpoint_byte_identical=True,
        fresh_checkout_cli=rows,working_checkout_automatic_default_verified=True,
        tests_sha256=sha(log),elapsed_seconds=time.time()-started,
        scope='Final full tests and operational/strict/experimental CLI defaults after source-bound acceptance. No experimental preference checkpoint is selected for legality.'))
    print('FINAL POST-ACCEPTANCE TESTS AND LEGAL DEFAULT VERIFIED',tests,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13')
    parser.add_argument('--checkout',required=True);parser.add_argument('--commit',required=True)
    args=parser.parse_args();run(args.out,args.checkout,args.commit)
