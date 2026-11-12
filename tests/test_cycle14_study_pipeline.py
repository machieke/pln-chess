"""Exercise the fit/freeze/test barrier on disclosed unit observations."""
import copy
from pathlib import Path

from pln_chess.common import digest,write_json,read_json
from pln_chess.cycle13.ontology import seal as base_seal
from pln_chess.cycle14.ontology import seal
from test_cycle14_native_learning import examples
from evaluation import cycle14_preferences as study
from evaluation import cycle14_studies as controls


def test_registered_fit_freeze_and_matched_endpoint_workflow(tmp_path,monkeypatch):
    rows=[]
    for split,n in (('train',4),('development',2),('calibration',2),('test',2),('source-holdout',2)):
        for i in range(n):
            base=copy.deepcopy(examples()[0]);base.update(id=f'unit-{split}-{i}',split=split,
                source_game=f'{split}-game-{i}',dependence_group=f'{split}-game-{i}',transformation_lineage=[f'{split}-game-{i}'],
                source={'collection':'unit-collection'},label='A' if i%2==0 else 'B')
            for h in (1,2,3):
                packet=copy.deepcopy(base['packet']);packet['base']['horizon']=h
                packet['base']['profiles']['A']['fields']['attack'].update(supported=1,contradicted=0)
                packet['base']=base_seal(packet['base']);packet=seal(packet)
                rows.append(dict(base,id=base['id']+(f'-ply{h}' if h>1 else ''),packet=packet,temporal_context={'horizon':h}))
    def records(out,temporal=False,labels='revised'):
        return copy.deepcopy([r for r in rows if temporal or r['temporal_context']['horizon']==1])
    monkeypatch.setattr(study,'training_records',records);monkeypatch.setattr(controls,'training_records',records)
    write_json(tmp_path/'baseline/research/verified.json',{'passed':True,'scope':'unit fixture'})
    write_json(tmp_path/'datasets/partitions.json',{'scope':'unit partition'})
    write_json(tmp_path/'datasets/reversal-registration.json',{'scope':'unit registration'})
    study.fit(tmp_path);registry=read_json(tmp_path/'model/registry.json')
    assert registry['test_predictions_run'] is False
    assert not (tmp_path/'evaluation').exists()
    study.freeze(tmp_path);study.evaluate(tmp_path)
    assert read_json(tmp_path/'evaluation-freeze.json')['final_predictions_observed'] is False
    controls.factorial(tmp_path)
    summary=read_json(tmp_path/'ablations/summary.json')
    assert summary['passed'] and len(summary['temporal'])==4
    for panel in summary['temporal']:
        assert all(c['N_all']==2 for c in panel['counts'].values())
    controls.dependence(tmp_path)
    assert read_json(tmp_path/'dependence/summary.json')['rollback_checkpoint_byte_identical']
