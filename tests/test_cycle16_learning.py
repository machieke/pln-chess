import copy
import pytest
from pln_chess.common import digest
from training.cycle16_paths import evidence,fit
from research.cycle16.corpus import roots,groups
from research.cycle16.experiments import knowledge


def test_grouping_and_admission():
    registered=roots();audit=groups(registered)
    assert audit['source_episode_counts']==dict(train=12,development=6,test=24)
    assert audit['unique_source_games']==42
    assert not audit['wholly_unseen_test_geometry']
    rows=evidence()
    assert all(r['occupancy']=='EE' and r['label'] is True for r in rows if r['admitted'])
    assert all(r['label'] is None for r in rows if not r['admitted'])


def test_native_fit_replay_and_real_refit(tmp_path):
    rows=[r for r in evidence() if r['rule']=='clear-two' and r['admitted']][:2]
    model,_=fit(rows,tmp_path/'fit')
    replay,ledger=fit(rows+rows,tmp_path/'replay')
    reduced,_=fit(rows,tmp_path/'reduced',exclude_ancestry=(rows[0]['ancestry'],))
    assert model['rules']==replay['rules']
    assert sum(r['action']=='duplicate-ancestry-rejected' for r in ledger)==2
    assert reduced['rules']['clear-two']['truth_value']['confidence']<model['rules']['clear-two']['truth_value']['confidence']
    rule=next(r for r in knowledge('L',model) if r.stamps[0]=='rule_clear-two')
    assert len(rule.stamps)==3 and rule.ancestry==tuple(r['ancestry'] for r in rows)


@pytest.mark.parametrize('field,value',[('split','test'),('label',False),('ancestry','forged'),('state_identity','forged')])
def test_training_rejects_unregistered_evidence(tmp_path,field,value):
    row=copy.deepcopy(next(r for r in evidence() if r['admitted']));row[field]=value
    with pytest.raises(ValueError,match='frozen training evidence'):fit([row],tmp_path)
