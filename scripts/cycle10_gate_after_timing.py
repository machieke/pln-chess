"""Start implementation tests only after the original-source timing arm finishes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from pln_chess.common import ROOT,read_json,write_json


def run(out,source):
    out=Path(out).resolve();source=Path(source).resolve();deadline=time.time()+43200
    while True:
        receipt=out/'commands/benchmark-C9-external.json'
        bootstraps=[p for p in out.glob('*bootstrap*/verified.json') if read_json(p)['checkout']==str(source)]
        if receipt.exists() and bootstraps:
            try:
                result=read_json(receipt)
                if result['returncode']!=0:raise RuntimeError('Original-source benchmark failed; inspect its log')
                assert read_json(bootstraps[0])['passed'];break
            except json.JSONDecodeError:pass
        if time.time()>deadline:raise RuntimeError('Timed out waiting for completed original timing and fresh bootstrap')
        time.sleep(5)
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm',C10_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT'):env.pop(key,None)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip();py=str(source/'.venv/bin/python')
    log=out/'development/native-tests.txt';log.parent.mkdir(exist_ok=True);start=time.time()
    argv=[py,'-m','pytest','-q','tests/test_cycle10_native.py']
    with log.open('w') as stream:r=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
    write_json(out/'development/native-tests-command.json',dict(argv=argv,cwd=str(source),source_head=head,
        returncode=r.returncode,elapsed_seconds=time.time()-start,log=str(log.relative_to(out))))
    if r.returncode:raise RuntimeError(f'Native transport test failed: {log}')
    print('native transport pilot passed',flush=True)
    code='''import sys
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle10.temporal import replay_game
from pln_chess.cycle8.model import PromotionModel
from pln_chess.pln import Runtime
out=Path(sys.argv[1]);rt=Runtime();model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt);games=[]
for game in read_json(out/'datasets/dataset.json')['games']:
    receipt=replay_game(game,len(game['moves']),model.version,rt.version)
    assert receipt['resulting_fen']==game['final_fen'] and not receipt['conflicts'],game['id']
    games.append(dict(game=game['id'],events=len(receipt['events']),receipt_id=receipt['id']))
write_json(out/'development/full-game-replay.json',dict(passed=True,games=games,complete_games=len(games),oracle_used=False))
'''
    subprocess.run([py,'-c',code,str(out)],cwd=source,env=env,check=True)
    print('all complete published game replays passed',flush=True)
    subprocess.run([py,'-m','scripts.cycle10_regression','--out',str(out),'--source',str(source)],cwd=source,env=env,check=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True)
    a=p.parse_args();run(a.out,a.source)
