"""Native revision, dependence and byte replay on controlled unit inputs."""
import copy
import pytest
from pln_chess.common import digest,write_json
from pln_chess.cycle14.ontology import project
from training.cycle14_learning import train
from test_cycle14_learning import packet


def examples():
    p=packet()
    return [dict(id='unit-'+str(i),fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',moves=['a1a2','a1b1'],
        packet=p,label=label,split='train',source='controlled-unit-input',source_game='game-'+str(i),
        dependence_group='game-'+str(i),transformation_lineage=['game-'+str(i)],temporal_context={'horizon':1},
        model_versions={},reference_evidence_id='unit-reference-'+str(i),label_generation='unit-g1')
        for i,label in enumerate(('A','A','unknown'))]


def test_native_fit_replay_and_dependent_copies_do_not_inflate(runtime,tmp_path):
    # This gate is a unit fixture; empirical runs require the real baseline receipt.
    write_json(tmp_path/'baseline/research/verified.json',dict(passed=True,scope='unit fixture'))
    rows=examples()
    def fit(data,name,**kwargs):return train(data,runtime,tmp_path/name,dataset_hash=digest(data),
        abstraction='role-change-v1',baseline_root=tmp_path,variant='C14-unit-native-fit',**kwargs)
    first=fit(rows,'first');again=fit(rows,'replayed')
    assert first.version==again.version
    assert (tmp_path/'first/checkpoint.json').read_bytes()==(tmp_path/'replayed/checkpoint.json').read_bytes()
    assert (tmp_path/'first/ledger.jsonl').read_bytes()==(tmp_path/'replayed/ledger.jsonl').read_bytes()
    repeated=rows+[dict(r,id=r['id']+'/repeated-budget') for r in rows]
    handled=fit(repeated,'handled');unsafe=fit(repeated,'unsafe',dependence=False)
    key=project(rows[0]['packet'],'role-change-v1')['rule_id']
    assert first.hypotheses[key]['channels']==handled.hypotheses[key]['channels']
    assert unsafe.hypotheses[key]['channels']['first']['confidence']>handled.hypotheses[key]['channels']['first']['confidence']
    assert first.training_report['excluded_observations']['unresolved-reference-label']==1
    conflicting=[rows[0],dict(rows[0],id='opposing-delivery',label='B')]
    conflict=fit(conflicting,'conflict')
    assert not conflict.hypotheses and conflict.training_report['excluded_observations']['contradictory-dependent-component']==1
    with pytest.raises(ValueError,match='Held-out'):
        fit([dict(rows[0],split='test')],'leak')
    # A changed generation must not mutate an existing model/ledger contract.
    before=(tmp_path/'first/ledger.jsonl').read_bytes()
    with pytest.raises(ValueError,match="Immutable generation"):fit([dict(rows[0],label='B')],'first')
    assert (tmp_path/'first/ledger.jsonl').read_bytes()==before
