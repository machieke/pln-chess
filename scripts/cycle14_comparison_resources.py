"""Observe the four existing comparison workers without changing their work."""
import argparse
import os
from pathlib import Path
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha


def snapshot(pid):
    directory=Path('/proc')/str(pid)
    fields=(directory/'stat').read_text().rpartition(') ')[2].split()
    status=(directory/'status').read_text().splitlines()
    return dict(pid=pid,parent_pid=int(fields[1]),start_ticks=int(fields[19]),
        cpu_seconds=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK'),
        peak_rss_kib=int(next(line.split()[1] for line in status if line.startswith('VmHWM:'))),
        argv=(directory/'cmdline').read_bytes().decode().strip('\0').split('\0'))


def run(parent,pids):
    out=ROOT/'artifacts/cycle14/current/comparison-process-resources.json'
    assert not out.exists(),'Preserve the prior measurement generation'
    commands=list((out.parent/'commands').glob('legal-*.json'))
    assert len(commands)==206 and all(read_json(p)['returncode']==0 for p in commands)
    assert len(set(pids))==4
    records={pid:snapshot(pid) for pid in pids}
    assert all(r['parent_pid']==parent and r['argv'][-2:]==['-m','scripts.cycle14_schedule'] for r in records.values())
    started=time.time();driver=sha(__file__);active=set(pids)
    while active:
        for pid in list(active):
            try:row=snapshot(pid)
            except (FileNotFoundError,ProcessLookupError,StopIteration):
                active.remove(pid);continue
            if row['start_ticks']!=records[pid]['start_ticks']:
                active.remove(pid);continue
            assert row['cpu_seconds']>=records[pid]['cpu_seconds']
            row['peak_rss_kib']=max(row['peak_rss_kib'],records[pid]['peak_rss_kib'])
            records[pid]=row
        if active:time.sleep(5)
    write_json(out,dict(passed=True,parent_pid=parent,workers=list(records.values()),
        started_unix=started,completed_unix=time.time(),observer_driver_sha256=driver,
        regression_driver_sha256=sha(ROOT/'scripts/cycle14_regression.py'),
        cpu_seconds_lower_bound=sum(r['cpu_seconds'] for r in records.values()),
        scope='Cumulative per-process CPU for the four post-replay aggregate comparison workers, sampled every five seconds. Includes CPU before observer launch; the final unsampled tail may be missing. No native replay child or parent CPU is included, so this does not overlap per-command GNU-time receipts. Individual RSS high-water marks are separate, not summed into simultaneous memory.'))
    print('C14 CURRENT COMPARISON RESOURCE COUNTERS CLOSED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--parent',type=int,required=True)
    parser.add_argument('--pids',type=int,nargs=4,required=True);args=parser.parse_args()
    run(args.parent,args.pids)
