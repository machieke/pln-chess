"""Small checked-in-fixture reproduction without historical bulk archives."""
import argparse
from pathlib import Path
from pln_chess.common import ROOT, read_json
from research.cycle16.experiments import fixture, MEDIUM
from research.cycle16.records import compact, record
from .study import infer
from .provenance import witness, roles, audit


def minimal(out, learning=None):
    out = Path(out); learning = Path(learning or ROOT/'artifacts/cycle17/learning')
    state, a, t = fixture(tag='c17_minimal')
    results = {}
    for arm in ('S-AA', 'S-BB', 'D-AB', 'D-BA', 'overlap-1', 'overlap-6', 'learned-clearance', 'prior'):
        model = read_json(learning/arm/'model.json')
        native = infer(state, a, t, checkpoint=model, budgets=MEDIUM)
        results[arm] = dict(result=compact(native, out), witness=witness(native, out),
            provenance=roles(native, model), proof_audit=audit(native))
    return record(out/'summary.json', dict(fixture=state, attacker=a, target=t, arms=results,
        scope='Two learned conditionals where named; other rule structures and trust remain supplied'))


def main():
    p = argparse.ArgumentParser(); p.add_argument('command', choices=('minimal', 'baseline'))
    p.add_argument('--out', required=True); p.add_argument('--learning'); args = p.parse_args()
    if args.command == 'minimal':
        minimal(args.out, args.learning)
    else:
        from .baseline import run
        run(args.out)


if __name__ == '__main__':
    main()
