"""Exercise the real automatic legal default after all acceptance gates pass."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

from pln_chess.common import ROOT, read_json
from scripts.cycle9_baseline import sha
from training.cycle14_labels import atomic_json


def run(out, source=None):
    out=Path(out).resolve();source=Path(source or ROOT).resolve()
    accepted=read_json(out/'acceptance.json');assert accepted['passed']
    py=str(source/'.venv/bin/python')
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',C14_OUT=str(out),TMPDIR='/dev/shm')
    for cycle in range(6,14):env.pop(f'C{cycle}_OUT',None)
    target=out/'post-acceptance';records=[]
    probe='''import json
from pln_chess.common import ROOT
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.cycle14.acceptance import accepted_model,default_checkpoint
from pln_chess.cycle8.inference import default_mode
from pln_chess.cycle6.inference import production_code_hash
p=default_checkpoint(ROOT/'artifacts/cycle5/C5-full-model.json');m=Model.load(p,Runtime())
print(json.dumps(dict(path=str(p),model_version=m.version,accepted=accepted_model(m),mode=default_mode(m),production_code_hash=production_code_hash())))'''
    identity=json.loads(subprocess.check_output([py,'-c',probe],cwd=source,env=env,text=True))
    assert identity['path']==str(out/'model/C14-default.json')
    assert identity['accepted'] and identity['mode']=='operational'
    assert identity['model_version']==accepted['default_model_version']
    assert identity['production_code_hash']==accepted['production_code_hash']
    for mode in ('automatic','strict','experimental'):
        argv=[py,'-m','pln_chess','inspect','--fen','7k/8/8/8/R6p/8/8/6K1 w - - 0 1',
            '--move','a4h4','--format','json']
        if mode!='automatic':argv+=['--mode',mode]
        began=time.monotonic();result=subprocess.run(argv,cwd=source,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        assert result.returncode==0,result.stderr
        value=json.loads(result.stdout);candidate=value['candidate']
        assert candidate['classification']==('supported-legal' if mode=='automatic' else 'unknown')
        atomic_json(target/(mode+'.json'),value)
        records.append(dict(mode=mode,argv=argv,returncode=0,elapsed_seconds=time.monotonic()-began,
            classification=candidate['classification'],artifact_sha256=sha(target/(mode+'.json'))))
    assert sha(out/'model/C14-default.json')==sha(ROOT/'artifacts/cycle12/model/C12-default.json')
    atomic_json(target/'verified.json',dict(passed=True,identity=identity,commands=records,
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        probe_driver_sha256=sha(__file__),production_code_hash=identity['production_code_hash'],
        automatic_default_is_unchanged_accepted_legal_model=True,strict_and_experimental_abstention_preserved=True,
        acceptance_sha256=sha(out/'acceptance.json'),preferences_promoted=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');parser.add_argument('--source')
    args=parser.parse_args();run(args.out,args.source)
