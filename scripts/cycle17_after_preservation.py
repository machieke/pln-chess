"""Run frozen-source benchmarks only after all preservation work has finished."""
import argparse
import os
from pathlib import Path
import subprocess
import time
from pln_chess.common import read_json, write_json
from scripts.cycle15_baseline import sha


def run(out, source, driver_pid):
    out = Path(out).resolve(); source = Path(source).resolve()
    gate = out/'preservation/cycle17-verification.json'
    while not gate.exists():
        status = Path('/proc')/str(driver_pid)/'stat'
        if not status.exists() or status.read_text().rsplit(')', 1)[1].split()[0]=='Z':
            raise RuntimeError('Preservation stopped without a completed verification receipt')
        time.sleep(10)
    assert read_json(gate)['passed']
    while not (out/'preservation-resource-observation.json').exists():
        time.sleep(2)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    assert head == read_json(gate)['source_head']
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True)
    env = {**os.environ, 'PLN_CHESS_ROOT': str(source), 'PYTHONPATH': str(source/'src')+':'+str(source)}
    argv = [str(source/'.venv/bin/python'), '-m', 'evaluation.cycle17_performance',
        '--learning', str(out/'learning'), '--out', str(out/'performance')]
    log = out/'benchmark-driver.log'; started = time.time()
    with log.open('w') as stream:
        process = subprocess.run(argv, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT)
    write_json(out/'benchmark-command.json', dict(source_head=head, argv=argv, returncode=process.returncode,
        started_unix=started, elapsed_seconds=time.time()-started, log=str(log), log_sha256=sha(log),
        scope='Benchmarks begin only after the completed preservation receipt and process-tree observer termination'))
    if process.returncode:
        raise RuntimeError(str(log))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); p.add_argument('--source', required=True)
    p.add_argument('--driver-pid', type=int, required=True); a = p.parse_args(); run(a.out, a.source, a.driver_pid)
