"""Actual native revision distinguishes independent evidence from redelivery."""
import copy
import pytest
from pln_chess.common import ROOT,digest
from training.cycle13_learning import train
from tests.test_cycle13_preferences import packet


def row(identifier,label='A',group='ancestry-one'):
    return dict(id=identifier,fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',moves=['a1a2','a1b1'],
        label=label,packet=packet(),split='train',source='controlled-revision-test',source_game='controlled-game',
        dependence_group=group,transformation_lineage=[group],temporal_context=dict(horizon=1),
        model_versions={},reference_evidence_id='controlled-reference:'+identifier)


def fit(records,runtime,path):
    return train(records,runtime,path,dataset_hash=digest(records),baseline_root=ROOT/'artifacts/cycle13')


def channels(model):
    return next(iter(model.hypotheses.values()))['channels']


def test_native_revision_keeps_shared_ancestry_from_increasing_confidence(runtime,tmp_path):
    one=fit([row('one')],runtime,tmp_path/'one')
    repeated=fit([row('one'),row('two'),row('three')],runtime,tmp_path/'repeated')
    independent=fit([row('one'),row('two',group='two'),row('three',group='three')],runtime,tmp_path/'independent')
    assert channels(one)==channels(repeated)
    assert channels(independent)['first']['confidence']>channels(one)['first']['confidence']
    assert repeated.training_report['excluded_observations']['shared-ancestry']==1


def test_conflicting_dependent_labels_are_withheld(runtime,tmp_path):
    model=fit([row('one'),row('two','B')],runtime,tmp_path)
    assert not model.hypotheses
    assert model.training_report['excluded_observations']['contradictory-dependent-component']==1


def test_unknown_labels_are_retained_without_binary_negative_training(runtime,tmp_path):
    model=fit([row('one','unknown'),row('two','no-demonstrated-preference',group='two')],runtime,tmp_path)
    assert model.training_report['training_examples']==2
    assert model.training_report['excluded_observations']['unresolved-reference-label']==1
    assert channels(model)['no-demonstrated-preference']['strength']>channels(model)['first']['strength']
    assert len((tmp_path/'ledger.jsonl').read_text().splitlines())==2


def test_heldout_labels_cannot_update_checkpoint(runtime,tmp_path):
    heldout={**row('one'),'split':'test'}
    with pytest.raises(ValueError):
        fit([heldout],runtime,tmp_path)
    assert not (tmp_path/'checkpoint.json').exists()
