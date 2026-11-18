import copy
from types import SimpleNamespace
import pytest
from pln_chess.common import ROOT,digest,read_json
from research.cycle19.lifecycle import Journal,StaleEvidence
from research.cycle19.measurements import environment,measure
from research.cycle19.corpus import roots
from research.cycle19.learning import fit
from research.cycle15.knowledge import load_rules


def fake():
    class Reasoner:
        runtime=SimpleNamespace(version=read_json(ROOT/'configs/runtime-lock.json')['pln']['commit'])
        def execute_program(self,*args):raise AssertionError('Malformed/stale evidence must fail before native execution')
    return Reasoner()


def test_component_payload_integrity_before_revision(tmp_path):
    j=Journal();event=j.add('environment',environment(roots()[0]));m=measure(j,event)
    row=j.node(m['annotations']['Clear']);row['payload']['label']=False
    forged=j.add('annotation',row['payload'],row['parents'])
    with pytest.raises(ValueError,match='measured component'):fit(j,[forged],tmp_path/'bad','D-AB',reasoner=fake())


def test_prior_is_content_bound_and_templates_are_unchanged(tmp_path):
    j=Journal();prior=fit(j,[],tmp_path/'prior','P',reasoner=fake())
    assert prior['model']['admitted_components']=={}
    assert all(r['truth_value']==dict(strength=.5,confidence=0) for r in prior['model']['rules'].values())
    load_rules(prior['model'],path=ROOT/'knowledge/cycle16/finite_two.metta')
    corrupted=copy.deepcopy(prior['model']);corrupted['assumptions']['observation_confidence']=.9
    with pytest.raises(ValueError,match='integrity'):load_rules(corrupted,path=ROOT/'knowledge/cycle16/finite_two.metta')


def test_stale_fit_rejected_before_native(tmp_path):
    j=Journal();event=j.add('environment',environment(roots()[0]));m=measure(j,event)
    j.supersede(event,'environment',dict(corrected=True))
    with pytest.raises(StaleEvidence):fit(j,list(m['annotations'].values()),tmp_path/'stale','D-AB',reasoner=fake())
