"""Two supplied conditionals fitted by native revision with genuine ancestry."""
import argparse
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from pln_chess.pln import TV
from research.cycle15.knowledge import templates
from research.cycle15.native_reasoner import NativeReasoner, parse, save_result
from research.cycle16.corpus import variant, reference, OCCUPANCIES
from research.cycle16.records import record
from research.cycle17.corpus import roots

PATH = ROOT/'knowledge/cycle16/finite_two.metta'
PAIR = ('clear-two', 'rook-attack')


def memberships():
    groups = {g: [r['source_ancestry'] for r in roots() if r['split'] == g] for g in ('A', 'B')}
    a, b = groups['A'], groups['B']
    return {'S-AA': (a, a), 'S-BB': (b, b), 'D-AB': (a, b), 'D-BA': (b, a),
        'overlap-1': (a, a[:1]+b[:11]), 'overlap-6': (a, a[:6]+b[:6]),
        'learned-clearance': (a, []), 'prior': ([], []), 'prior-clearance': ([], b),
        'prior-terminal': (a, []), 'remove-A-refit': ([], b), 'leave-one-A': (a[1:], b)}


def evidence():
    rows = []
    for root in roots():
        if root['split'] not in ('A', 'B'):
            continue
        for occupancy in OCCUPANCIES:
            state = root['state'] if occupancy == 'EE' else variant(root, occupancy)
            ref = reference(state, root['attacker'], root['target'])
            for rule in PAIR:
                rows.append(dict(root=root['id'], ancestry=root['source_ancestry'], split=root['split'], rule=rule,
                    occupancy=occupancy, state_identity=digest(state),
                    observation_identity=digest([state, root['attacker'], root['target']]),
                    admitted=occupancy == 'EE', label=ref['label'] if occupancy == 'EE' else None,
                    reference=ref, source_kind='natural position' if occupancy == 'EE' else 'dependent synthetic exclusion control',
                    antecedent='Two-cell ray and two observed empty cells' if rule == 'clear-two' else 'Rook kind and evaluation-verified clear path',
                    reason='antecedent satisfied' if occupancy == 'EE' else 'unknown antecedent' if 'U' in occupancy else 'blocked antecedent'))
    return rows


def fit(rows, out, arm, *, reasoner=None):
    out = Path(out)
    if (out/'model.json').exists():
        raise ValueError('Checkpoint generation already exists')
    targets = memberships()[arm]
    structures = templates(PATH)
    names = ('clear-two',) if arm == 'learned-clearance' else PAIR
    rules = {name: dict(truth_value=TV(.5, 0).json(), ancestry=[], evidence=[], declaration=structures[name],
        rule_identity='rule_'+name, origin='Supplied structure; Cycle 17 native parameter revision') for name in names}
    allowed = {digest(r) for r in evidence()}
    seen = set(); ledger = []; reasoner = reasoner or NativeReasoner()
    for row in rows:
        if digest(row) not in allowed:
            raise ValueError('Only exact frozen training records are admitted')
        if row['rule'] not in rules:
            continue
        item = dict(row)
        key = row['rule'], row['ancestry']
        if not row['admitted']:
            item['action'] = 'unadmitted'
        elif row['ancestry'] not in targets[PAIR.index(row['rule'])]:
            item['action'] = 'outside-registered-arm'
        elif key in seen:
            item['action'] = 'duplicate-ancestry-rejected'
        else:
            seen.add(key)
            current = rules[row['rule']]; before = TV(**current['truth_value'])
            expression = f'(|- (LearnedBelief {before.metta()}) (LearnedBelief {TV(float(row["label"]), .5).metta()}))'
            program = f'!(import! &self "{reasoner.runtime.library}")\n!(println! (C17REVISION {expression}))\n'
            receipt = reasoner.execute_program(program, 15)
            proof = save_result(receipt, out/'raw')
            if receipt['incomplete']:
                raise RuntimeError(f'Native revision incomplete: {proof}')
            values = [parse(line) for line in receipt['stdout'].splitlines() if line.startswith('(C17REVISION ')]
            if len(values) != 1:
                raise RuntimeError('Ambiguous native revision')
            tv = values[0][1][1]; after = TV(float(tv[1]), float(tv[2]))
            item.update(action='native-revision', before=before.json(), after=after.json(), expression=expression, proof=proof)
            current['truth_value'] = after.json(); current['ancestry'].append(row['ancestry']); current['evidence'].append(digest(row))
        ledger.append(item)
    model = dict(schema='cycle17-learned-pair-v1', arm=arm, runtime_version=reasoner.runtime.version,
        structure_hash=digest(structures), corpus_hash=digest(roots()), rules=rules,
        ledger_hash=digest(ledger), logical_structure_origin='Supplied; no structure discovery',
        observation_trust='Supplied confidence .5; not learned or calibrated')
    model['version'] = digest(model)
    record(out/'model.json', model); record(out/'ledger.json', ledger)
    return model


def run(out):
    out = Path(out); rows = evidence(); record(out/'evidence.json', rows)
    models = {arm: fit(rows, out/arm, arm) for arm in memberships()}
    replay = fit(rows+rows, out/'replay-D-AB', 'D-AB')
    assert replay['rules'] == models['D-AB']['rules']
    comparison = {}
    for arm, model in models.items():
        support = {name: set(rule['ancestry']) for name, rule in model['rules'].items()}
        comparison[arm] = dict(parameters={n: r['truth_value'] for n, r in model['rules'].items()},
            admitted_counts={n: len(s) for n, s in support.items()},
            unique_sources=len(set().union(*support.values())),
            overlap=sorted(support.get('clear-two', set()) & support.get('rook-attack', set())), version=model['version'])
    return record(out/'summary.json', dict(arms=comparison, duplicate_replay_equal=True,
        all_admitted_positive=all(r['label'] is True for r in rows if r['admitted']),
        roots=24, source='Natural EE positions; blocked/unknown transformations excluded', memberships=memberships()))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); run(p.parse_args().out)
