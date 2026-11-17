"""Reuse the exact established 206-shard source-bound preservation driver."""
from pathlib import Path
from pln_chess.common import read_json
from scripts.cycle15_preservation import run as full_preservation
from research.cycle16.records import record


def run(out,source,workers=4):
    out=Path(out)
    full_preservation(out,source,workers)
    result=read_json(out/'verified.json')
    record(out/'cycle16-verification.json',dict(**{k:v for k,v in result.items() if k!='scope'},
        scope='Cycle 16 frozen source: complete existing 206-shard legal replay, controls and full tests',
        inherited_driver='scripts.cycle15_preservation.run; historical verified receipt left unchanged'))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True)
    p.add_argument('--workers',type=int,default=4);a=p.parse_args();run(a.out,a.source,a.workers)
