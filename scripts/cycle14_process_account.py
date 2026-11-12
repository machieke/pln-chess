"""Retain an identified job's cumulative kernel CPU counters before it exits."""
import argparse
import os
from pathlib import Path
import time

from pln_chess.common import write_json
from scripts.cycle9_baseline import sha


def run(pid,module,out):
    process=Path('/proc')/str(pid);out=Path(out)
    argv=[x.decode() for x in (process/'cmdline').read_bytes().split(b'\0') if x]
    assert '-m' in argv and argv[argv.index('-m')+1]==module
    hz=os.sysconf('SC_CLK_TCK');first=time.time();start_ticks=None;sample=None;count=0
    while True:
        try:fields=(process/'stat').read_text().rsplit(')',1)[1].split()
        except FileNotFoundError:break
        if start_ticks is None:start_ticks=fields[19]
        if fields[19]!=start_ticks:break
        sample=dict(sampled_unix=time.time(),parent_user_cpu_seconds=int(fields[11])/hz,
            parent_system_cpu_seconds=int(fields[12])/hz,reaped_child_user_cpu_seconds=int(fields[13])/hz,
            reaped_child_system_cpu_seconds=int(fields[14])/hz)
        count+=1
        if fields[0]=='Z':break
        time.sleep(1)
    assert sample
    write_json(out,dict(passed=True,pid=pid,argv=argv,kernel_start_ticks=start_ticks,
        clock_ticks_per_second=hz,sampling_started_unix=first,sampling_finished_unix=time.time(),samples=count,
        final_available_sample=sample,cpu_seconds_lower_bound=sum(v for k,v in sample.items() if k.endswith('_cpu_seconds')),
        driver_sha256=sha(__file__),exact_exit_counter_guaranteed=False,
        scope='Latest available cumulative /proc PID/stat CPU counters, including reaped descendants. PID start identity is checked. Active/unreaped descendants and work between the last sample and exit may be missing. This is a process-family lower bound, not a complete global cycle total.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pid',required=True,type=int)
    parser.add_argument('--module',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();run(args.pid,args.module,args.out)
