"""Registered interventions; explicit low-level audits are never fallbacks."""
import copy
from dataclasses import replace
from pathlib import Path
from pln_chess.common import read_json
from research.cycle15.native_reasoner import NativeReasoner, Sentence, Budgets
from research.cycle16.experiments import fixture, observations, knowledge, SMALL, MEDIUM, GENEROUS
from research.cycle16.corpus import OCCUPANCIES
from research.cycle16.records import compact, record
from .study import infer
from .provenance import witness, audit


def run(out, learning):
    out = Path(out); learning = Path(learning)
    model = read_json(learning/'D-AB/model.json'); shared = read_json(learning/'S-AA/model.json')
    state, a, t = fixture(tag='c17_control'); rows = {}
    def keep(name, result):
        audit(result); rows[name] = compact(result, out)
        return result
    keep('baseline', infer(state, a, t, checkpoint=model))
    for rule in ('clear-two', 'rook-attack'):
        keep('remove-'+rule, infer(state, a, t, checkpoint=model, remove=(rule,)))
        blocked, ba, bt = fixture('OE', tag='remove_negative_'+rule)
        keep('negative-survives-remove-'+rule, infer(blocked, ba, bt, checkpoint=model, remove=(rule,)))
    for index in (0, 1):
        def omit(facts, index=index):
            empty = [f for f in facts if f.term.startswith('(Empty ')]
            return [f for f in facts if f != empty[index]]
        keep('remove-empty-'+str(index), infer(state, a, t, checkpoint=model, facts_transform=omit))
    for arm in ('prior-clearance', 'prior-terminal', 'remove-A-refit', 'leave-one-A'):
        keep(arm, infer(state, a, t, checkpoint=read_json(learning/arm/'model.json')))
    keep('duplicate-inference', infer(state, a, t, checkpoint=model, facts_transform=lambda f: f+f))
    keep('replayed-training', infer(state, a, t, checkpoint=read_json(learning/'replay-D-AB/model.json')))
    keep('wrong-state', infer(state, a, t, checkpoint=model, facts_transform=lambda facts: [
        replace(f, term=f.term.replace(state['id'], 'unrelated_state')) if f.term.startswith('(Empty ') else f for f in facts]))
    keep('wrong-role', infer(state, a, t, checkpoint=model, facts_transform=lambda facts: [
        replace(f, term=f.term.replace(t, 'unrelated_target')) if f.term.startswith('(RayPath ') else f for f in facts]))
    renamed = copy.deepcopy(state)
    renamed['id'] += '_renamed'; renamed['root'] += '_renamed'
    for p in renamed['pieces']:
        p['id'] += '_renamed'
    keep('renaming', infer(renamed, a+'_renamed', t+'_renamed', checkpoint=model))
    translated = copy.deepcopy(state); translated['id'] += '_translated'
    for p in translated['pieces']:
        p['cell'][1] += 2
    keep('translation', infer(translated, a, t, checkpoint=model))
    for occupancy in OCCUPANCIES:
        occupied, oa, ot = fixture(occupancy, tag='occupancy_'+occupancy)
        keep('occupancy-'+occupancy, infer(occupied, oa, ot, checkpoint=model))
    for kind in ('bishop', 'queen'):
        secondary, sa, st = fixture(kind=kind, tag='secondary_'+kind)
        keep('supplied-terminal-'+kind, infer(secondary, sa, st, checkpoint=read_json(learning/'learned-clearance/model.json')))
    def conflict(facts):
        empty = next(f for f in facts if f.term.startswith('(Empty '))
        occupied = Sentence(empty.term.replace('(Empty ', '(Occupied '), stamps=('obs_c17_contradiction',), origin='audit-input')
        return facts+[occupied]
    keep('low-level-conflict', infer(state, a, t, checkpoint=model, facts_transform=conflict))
    invalid = copy.deepcopy(state); invalid['pieces'] = invalid['pieces'][:1]
    keep('missing-query-entity', infer(invalid, a, t, checkpoint=model))
    budget_rows = {}
    for arm, checkpoint in [('S-AA', shared), ('D-AB', model), ('R', None)]:
        budget_rows[arm] = {}
        for name, budget in [('small', SMALL), ('medium', MEDIUM), ('generous', GENEROUS)]:
            native = infer(state, a, t, checkpoint=checkpoint, arm='R' if arm=='R' else 'F', budgets=budget)
            budget_rows[arm][name] = dict(result=compact(native, out), witness=witness(native, out))
    # Direct adapter audits preserve the exact input facts, rules and raw channels.
    facts, _ = observations(state, a, t); rules = knowledge('L', model)
    query = f'(Attack {a} {t} {state["id"]})'; reasoner = NativeReasoner(); low = {}
    for name, rs, fs, budget, mode in [
        ('query-api', rules, facts, GENEROUS, 'query'),
        ('retention-pressure', rules, facts, Budgets(64, 8, 8, 15), 'derive'),
        ('actual-timeout', rules, facts, Budgets(64, 128, 256, .001), 'derive'),
        ('low-confidence-supplied-diagnostic', [replace(r, confidence=.05) if r.stamps[0]=='rule_clear-two' else r for r in knowledge('F')], facts, GENEROUS, 'derive'),
        ('reversed-input', rules[::-1], facts[::-1], MEDIUM, 'derive')]:
        native = reasoner.infer(fs, rs, query, budgets=budget, mode=mode)
        low[name] = compact(native, out)
    return record(out/'summary.json', dict(interventions=rows, budgets=budget_rows, low_level=low,
        scope='Low-level conflict/low-confidence diagnostics are isolated from primary models'))
