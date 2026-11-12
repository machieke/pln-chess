"""Use released first-partition slots for the final proof partition early."""
import os
from pathlib import Path
import subprocess
import time

from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def run():
    out=ROOT/'artifacts/cycle14';proof=out/'clean-research/proof-replay'
    began=time.monotonic()
    while True:
        early=proof/'early-shard1-released.json'
        one_done=(proof/'stream-complete-shard1-of-3.json').exists() or (
            early.exists() and read_json(early)['complete_shard'])
        if one_done and (proof/'stream-complete-shard0-of-3.json').exists():break
        if time.monotonic()-began>24*3600:raise TimeoutError('Early proof partition completion')
        time.sleep(5)
    fresh=Path('/data/pln-chess-cycle14-final')
    argv=[str(fresh/'.venv/bin/python'),'-u',str(ROOT/'scripts/cycle14_replay_stream.py'),
        '--source',str(out),'--out',str(proof),'--shard','2','--shards','3']
    started=time.time()
    with (out/'clean-research/proof-stream-2-early.log').open('w') as stdout, \
            (out/'clean-research/proof-stream-2-early.resources.log').open('w') as stderr:
        result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=fresh,
            env=dict(os.environ,PLN_CHESS_ROOT=str(fresh),PYTHONPATH=f'{fresh}/src:{fresh}',TMPDIR='/dev/shm'),
            stdout=stdout,stderr=stderr)
    write_json(out/'verification/early-final-proof-partition.json',dict(argv=argv,
        returncode=result.returncode,started_unix=started,elapsed_seconds=time.time()-started,
        driver_sha256=sha(__file__),workers=4,registered_owned_worker_ceiling=12,
        scheduling='Both first proof partitions and both feature generations complete before launch. At most three baseline comparison workers, one baseline control, four proof workers, and two scientific/UI workers run before current legal starts. After baseline closure, four current legal plus one control replace those baseline workers. A file lock prevents duplicate partition coordinators; later scheduling revalidates completed immutable receipts.'))
    assert result.returncode==0


if __name__=='__main__':run()
