"""Re-execute the retained real Cycle 16 failure and its surrounding controls."""
from pathlib import Path
from pln_chess.common import ROOT, read_json
from research.cycle15.native_reasoner import NativeReasoner, Sentence, Budgets
from research.cycle16.experiments import fixture, GENEROUS
from research.cycle16.evidence_audit import minimal, dependencies
from research.cycle16.records import compact, record
from scripts.cycle15_baseline import sha
from .study import infer
from .provenance import witness


def run(out):
    out = Path(out)
    old = read_json(ROOT/'artifacts/cycle16/supplement/shared-training-witness.json')
    source = Path(old['source']['path'])
    assert sha(source) == old['source']['sha256']
    original = read_json(source)
    fresh = NativeReasoner().infer([Sentence(**f) for f in original['facts']],
        [Sentence(**r) for r in original['rules']], original['query'], contrary=original['contrary_query'],
        budgets=Budgets(**original['budgets']), marginals=original['marginals'], mode=original['api'])
    assert all(fresh[k] == original[k] for k in ('classification', 'answer', 'contrary'))
    result = dict(stages={'Attack': fresh}, query_domain_valid=True)
    diagnostic = witness(result, out)
    assert diagnostic['diagnostic']['overlap'] == old['diagnostic']['overlap']
    assert len(diagnostic['diagnostic']['overlap']) == 11
    state, a, t = fixture(tag='c17_baseline')
    arms = {}
    for name, checkpoint in [('supplied', None), ('learned-clearance', ROOT/'artifacts/cycle16/learning/learned/model.json'),
                              ('shared-chain', ROOT/'artifacts/cycle16/learning/shared-chain/model.json')]:
        arms[name] = compact(infer(state, a, t, checkpoint=checkpoint, budgets=GENEROUS), out)
    for occupancy in ('OE', 'EU'):
        state, a, t = fixture(occupancy, tag='c17_baseline_'+occupancy)
        arms[occupancy] = compact(infer(state, a, t), out)
    recursive = minimal(out/'recursive')
    dependence = dependencies(out/'dependencies')
    return record(out/'summary.json', dict(passed=True, real_case=compact(fresh, out), witness=diagnostic,
        original_source=old['source'], exact_baseline_channels=True, eleven_stamp_intersection=True,
        arms=arms, recursive=recursive, dependence=dependence,
        scope='Fresh native execution of historical regression cases, not untouched evaluation'))
