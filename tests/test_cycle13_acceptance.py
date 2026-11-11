"""Operational recognition cannot be granted by experimental success alone."""
import copy
import hashlib
import shutil
from types import SimpleNamespace

import pytest
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle13.acceptance import CHECKS,accepted_model,default_checkpoint
from pln_chess.cycle13.model import PreferenceModel
from pln_chess.cycle13.concepts import ForkModel


@pytest.fixture
def verified(runtime,tmp_path,monkeypatch):
    monkeypatch.setenv('C13_OUT',str(tmp_path))
    config=read_json(ROOT/'configs/cycle13.json')
    gates={}
    for name in CHECKS:
        path=tmp_path/'gates'/f'{name}.json';write_json(path,dict(passed=True,name=name))
        gates[name]=dict(path=str(path.relative_to(tmp_path)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    receipt=dict(passed=True,all_required_checks_executed=True,checks={name:True for name in CHECKS},gate_receipts=gates,
        accepted_model_versions=[config['accepted_legal_model_version']],
        accepted_legacy_model_versions=read_json(ROOT/'artifacts/cycle12/acceptance.json')['accepted_legacy_model_versions'],
        default_model_version=config['accepted_legal_model_version'],preference_model_is_default=False,
        new_legal_learning_promoted=False,runtime_version=runtime.version,production_code_hash=production_code_hash(),
        registration_hash=digest(config),legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in range(6,13)})
    write_json(tmp_path/'acceptance.json',receipt)
    model=SimpleNamespace(schema=8,version=config['accepted_legal_model_version'],runtime_version=runtime.version)
    assert accepted_model(model)
    return tmp_path,receipt,model


def test_every_operational_gate_required(verified):
    out,receipt,model=verified
    for name in CHECKS:
        changed=copy.deepcopy(receipt);changed['checks'][name]=False
        write_json(out/'acceptance.json',changed)
        assert not accepted_model(model),name


def test_gate_receipts_bind_bytes_and_stay_inside_output(verified):
    out,receipt,model=verified;name=CHECKS[0]
    target=out/receipt['gate_receipts'][name]['path'];original=target.read_bytes()
    target.write_bytes(original+b'\n');assert not accepted_model(model)
    target.unlink();assert not accepted_model(model)
    target.write_bytes(original)
    for path in ('../outside.json',str(target.resolve()),''):
        changed=copy.deepcopy(receipt);changed['gate_receipts'][name]['path']=path
        write_json(out/'acceptance.json',changed);assert not accepted_model(model)
    changed=copy.deepcopy(receipt);changed['gate_receipts'].pop(name)
    write_json(out/'acceptance.json',changed);assert not accepted_model(model)


def test_source_identity_and_experimental_models_fail_closed(verified,runtime):
    out,receipt,model=verified
    for delta in (dict(production_code_hash='other'),dict(registration_hash='other'),dict(runtime_version='other'),
        dict(legacy_registrations={}),dict(preference_model_is_default=True),dict(new_legal_learning_promoted=True),
        dict(all_required_checks_executed=False),dict(default_model_version='other')):
        write_json(out/'acceptance.json',{**receipt,**delta});assert not accepted_model(model)
    for experimental in (PreferenceModel(runtime.version),ForkModel(runtime.version),
        SimpleNamespace(schema=8,version='injected-experimental',runtime_version=runtime.version)):
        write_json(out/'acceptance.json',{**receipt,'accepted_model_versions':[experimental.version]})
        assert not accepted_model(experimental)


def test_recognized_default_is_original_legal_checkpoint(verified,monkeypatch):
    out,receipt,model=verified
    for i in range(6,13):monkeypatch.delenv(f'C{i}_OUT',raising=False)
    path=out/'model/C13-default.json';path.parent.mkdir()
    shutil.copy2(ROOT/'artifacts/cycle12/model/C12-default.json',path)
    assert default_checkpoint('explicit-fallback')==path
    monkeypatch.setenv('C12_OUT',str(out/'missing-prior-override'))
    assert default_checkpoint('explicit-fallback')=='explicit-fallback'
