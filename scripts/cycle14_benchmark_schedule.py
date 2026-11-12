"""Replace this idle waiter with the isolated registered benchmark process."""
import os
from pathlib import Path
import sys
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha


def run():
    out=ROOT/'artifacts/cycle14'
    required=('current/verified.json','clean-research/verified.json','interfaces/verified.json',
        'verification/commands/clean-research.json')
    began=time.monotonic()
    while True:
        ready=all((out/p).exists() for p in required)
        if ready:
            assert all(read_json(out/p).get('passed',read_json(out/p).get('returncode')==0) for p in required)
            # Receipt writers can still be exiting. Require every owned study
            # process to leave before replacing this waiter with the benchmark.
            active=[]
            for process in Path('/proc').glob('[0-9]*'):
                if int(process.name)==os.getpid():continue
                try:
                    cwd=(process/'cwd').resolve()
                    if cwd!=ROOT and not str(cwd).startswith('/data/pln-chess-cycle14-'):continue
                    argv=(process/'cmdline').read_bytes().decode().strip('\0').split('\0')
                except (FileNotFoundError,PermissionError,ProcessLookupError,UnicodeDecodeError):continue
                module=argv[argv.index('-m')+1] if '-m' in argv and argv.index('-m')+1<len(argv) else ''
                study=(module.startswith(('training.cycle14_','evaluation.cycle14_','scripts.cycle14_'))
                    or module in ('pytest','scripts.cycle13_clean_research','scripts.cycle12_legal_review',
                        'evaluation.cycle12_legal_controls','evaluation.cycle12_legal_recovery','pln_chess')
                    or any(Path(a).name=='cycle14_replay_stream.py' for a in argv)
                    or (argv and Path(argv[0]).name=='swipl'))
                if study:active.append(int(process.name))
            if not active:break
        if time.monotonic()-began>24*3600:raise TimeoutError('Isolated benchmark prerequisites')
        time.sleep(5)
    argv=[sys.executable,'-u','-m','evaluation.cycle14_performance','--out',str(out),'--repetitions','20']
    write_json(out/'verification/benchmark-launch.json',dict(argv=argv,started_unix=time.time(),
        prerequisites={p:sha(out/p) for p in required},scheduler_sha256=sha(__file__),
        benchmark_sha256=sha(ROOT/'evaluation/cycle14_performance.py'),owned_study_processes=[],
        scope='The waiter is replaced by exec; there is no concurrent outer study process or GNU-time wrapper. Benchmark workers record their own CPU and memory.'))
    print('C14 ISOLATED BENCHMARK START',flush=True)
    os.execve(sys.executable,argv,dict(os.environ,TMPDIR='/dev/shm'))


if __name__=='__main__':run()
