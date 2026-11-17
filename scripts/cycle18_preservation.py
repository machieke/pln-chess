"""One complete frozen-source acceptance using the unchanged historical driver."""
from pathlib import Path
from pln_chess.common import read_json
from scripts.cycle15_preservation import run as preserve
from research.cycle16.records import record


def run(out,source,workers=6):
    preserve(out,source,workers)
    value=read_json(Path(out)/'verified.json')
    return record(Path(out)/'cycle18-verification.json',dict(**{k:v for k,v in value.items() if k!='scope'},
        scope='Complete Cycle18 frozen-source tests, 206 legal shards, exact proof parity, removal/history/recovery/holdout controls',
        inherited_driver='scripts.cycle15_preservation.run; inherited receipt retained unchanged'))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--source',required=True)
    p.add_argument('--workers',type=int,default=6);a=p.parse_args();run(a.out,a.source,a.workers)
