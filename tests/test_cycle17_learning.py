import copy
import pytest
from pln_chess.common import ROOT, read_json
from research.cycle17.corpus import roots
from training.cycle17_shared_evidence import evidence, memberships, fit
from research.cycle16.experiments import knowledge


def test_registered_groups_have_real_disjoint_roots():
    items = roots(); historical = read_json(ROOT/'artifacts/cycle16/corpus-registration.json')['roots']
    assert len({r['game_identity'] for r in items}) == 54
    assert not {r['game_identity'] for r in items} & {r['game_identity'] for r in historical}
    assert [sum(r['split']==s for r in items) for s in ('A', 'B', 'development', 'test')] == [12, 12, 6, 24]
    groups = memberships()
    assert [len(set(groups[a][0]) & set(groups[a][1])) for a in ('D-AB', 'overlap-1', 'overlap-6', 'S-AA')] == [0, 1, 6, 12]
    rows = evidence()
    assert all(r['label'] is True and r['source_kind']=='natural position' for r in rows if r['admitted'])
    assert all(r['label'] is None for r in rows if not r['admitted'])


@pytest.mark.parametrize('field,value', [('split', 'test'), ('label', False), ('ancestry', 'renamed'), ('state_identity', 'changed')])
def test_forged_training_is_rejected(tmp_path, field, value):
    row = copy.deepcopy(next(r for r in evidence() if r['admitted']))
    row[field] = value
    with pytest.raises(ValueError, match='exact frozen'):
        fit([row], tmp_path, 'D-AB')


def test_native_revision_replay_and_group_refit(tmp_path):
    rows = [r for r in evidence() if r['admitted']][:4]
    full = fit(rows, tmp_path/'full', 'S-AA')
    replay = fit(rows+rows, tmp_path/'replay', 'S-AA')
    removed = fit(rows, tmp_path/'removed', 'remove-A-refit')
    assert full['rules'] == replay['rules']
    assert all(r['truth_value']['confidence'] == 0 for r in removed['rules'].values())
    native = knowledge('L', full)
    assert all(r.stamps[0].startswith('rule_') for r in native)
    assert all(len(r.stamps) == 1+len(r.ancestry) for r in native)
