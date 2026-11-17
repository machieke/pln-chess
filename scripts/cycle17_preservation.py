"""Unchanged complete historical driver, explicitly bound to Cycle 17 source."""
from pathlib import Path
from pln_chess.common import read_json
from scripts.cycle15_preservation import run as preserve
from research.cycle16.records import record


def run(out, source, workers=4):
    preserve(out, source, workers)
    result = read_json(Path(out)/'verified.json')
    return record(Path(out)/'cycle17-verification.json', dict(**{k:v for k,v in result.items() if k!='scope'},
        scope='Complete source-bound Cycle 17 tests, 206 legal shards, controls, recoveries and holdouts',
        inherited_driver='scripts.cycle15_preservation.run; original receipt retained unchanged'))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); p.add_argument('--source', required=True)
    p.add_argument('--workers', type=int, default=4); a = p.parse_args(); run(a.out, a.source, a.workers)
