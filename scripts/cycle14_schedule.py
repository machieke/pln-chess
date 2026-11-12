"""Schedule independent verification within the registered 12-worker ceiling."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha


def wait_for(predicate, description):
    started=time.monotonic()
    while not predicate():
        if time.monotonic()-started>24*3600:
            raise TimeoutError(description+' exceeded the registered stage budget')
        time.sleep(5)


def run():
    out=ROOT/'artifacts/cycle14';fresh=Path('/data/pln-chess-cycle14-final')
    def success(name):
        path=out/'current/commands'/(name+'.json')
        return path.exists() and read_json(path)['returncode']==0
    def controls_done():
        return all(success(name) for name in ('tests','negative-and-history-controls','recoveries-and-holdouts'))
    env=dict(os.environ,PLN_CHESS_ROOT=str(fresh),PYTHONPATH=f'{fresh}/src:{fresh}',TMPDIR='/dev/shm')
    def current():
        wait_for(lambda:(out/'baseline/legal-reproduction.json').exists() and success('tests'),'Baseline and current tests')
        from scripts.cycle14_baseline_receipt import run as join
        from scripts.cycle14_regression import run as regression
        join(out)
        regression(out,fresh,workers=4)
    def proof(shard):
        wait_for(controls_done,'Current negative/history/recovery controls')
        if shard==2:
            wait_for(lambda:any((out/'features'/generation/'index.json').exists()
                for generation in ('immediate-g2','temporal-g1')),'One completed feature generation')
        with (out/f'clean-research/proof-stream-{shard}.log').open('w') as stdout, \
                (out/f'clean-research/proof-stream-{shard}.resources.log').open('w') as stderr:
            subprocess.run(['/usr/bin/time','-v',str(fresh/'.venv/bin/python'),'-u',
                str(ROOT/'scripts/cycle14_replay_stream.py'),'--source',str(out),
                '--out',str(out/'clean-research/proof-replay'),'--shard',str(shard),'--shards','3'],
                env=env,cwd=fresh,stdout=stdout,stderr=stderr,check=True)
    write_json(out/'verification/schedule.json',dict(driver_sha256=sha(__file__),
        fresh_source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=fresh,text=True).strip(),
        current_legal_workers=4,proof_shards=3,registered_maximum_workers=12,
        stages=[dict(condition='Baseline and full current tests complete',workers='4 legal + 1 controls + 4 immediate + 2 temporal + 1 proof = 12'),
            dict(condition='Current controls complete',workers='4 legal + 4 immediate + 2 temporal + 2 proof = 12'),
            dict(condition='At least one feature generation complete',workers='4 legal + at most 4 remaining features + 3 proof = at most 11')],
        scope='Deterministic scheduling change only. No scientific inputs, model outcomes, native semantics or archive membership change.'))
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(current),pool.submit(proof,1),pool.submit(proof,2)]
        for future in futures:future.result()


if __name__=='__main__':run()
