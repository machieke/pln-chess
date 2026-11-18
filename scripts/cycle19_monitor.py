"""Observe preservation CPU/memory without modifying or scheduling its jobs."""
from pathlib import Path
from scripts.cycle17_monitor import run as observe
from pln_chess.common import read_json,write_json


def run(pid,out):
    out=Path(out);raw=out.with_name('preservation-observer-raw.json')
    observe(pid,raw)
    data=read_json(raw)
    data['scope']='Read-only /proc sampling from Cycle19 preservation start. Process-tree CPU and per-process RSS are observed lower bounds. Comparison phase begins at 209 completed command receipts. These overlap timed command counters and must not be added to them.'
    write_json(out,data)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--out',required=True)
    a=p.parse_args();run(a.pid,a.out)
