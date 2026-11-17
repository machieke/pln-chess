import pytest
from evaluation.cycle15_corpus import registration,episode,reference
from training.cycle15_consequences import evidence,fit
from research.cycle15.queries import infer_state


def test_root_partitions_and_dependent_translations():
    roots=registration()
    assert {split:sum(r['split']==split for r in roots) for split in ('train','development','test')}=={'train':24,'development':12,'test':48}
    assert len({r['source_ancestry'] for r in roots})==84
    for r in roots:
        e=episode(r);translated=episode(r,translated=True,renamed=True)
        assert reference(e['after'],e['query'])==reference(translated['after'],translated['query'])
        assert e['state']['root']==translated['state']['root']


def test_test_evidence_cannot_update(tmp_path):
    root=next(r for r in registration() if r['split']=='test')
    with pytest.raises(ValueError):evidence([root])
    with pytest.raises(ValueError):fit([dict(split='test')],tmp_path)


def test_native_revision_replay_and_ancestry_removal(tmp_path):
    roots=[r for r in registration() if r['split']=='train'][:2]
    rows=evidence(roots)
    model,ledger=fit(rows+rows,tmp_path/'fit')
    clean,_=fit(rows,tmp_path/'clean')
    assert model['rules']==clean['rules']
    assert any(r['action']=='duplicate-ancestry-rejected' for r in ledger)
    excluded,_=fit(rows,tmp_path/'excluded',exclude_ancestry=(roots[0]['source_ancestry'],))
    assert excluded['rules']['obstruction']['truth_value']['confidence']<clean['rules']['obstruction']['truth_value']['confidence']
