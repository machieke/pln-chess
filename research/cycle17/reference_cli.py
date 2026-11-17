"""The sole executable importer of the isolated reference laboratory."""
import argparse
import json
import time
from fractions import Fraction
from pathlib import Path
from .reference_models import run


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); args = p.parse_args()
    start = time.perf_counter(); result = run(); result['wall_seconds'] = time.perf_counter()-start
    result['native_processes'] = 0
    path = Path(args.out); path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError('Choose a new reference generation')
    path.write_text(json.dumps(result, indent=2, sort_keys=True,
        default=lambda x: str(x) if isinstance(x, Fraction) else None)+'\n')


if __name__ == '__main__':
    main()
