"""Identity preservation, immutable-state caching and diagnostic isolation."""
from dataclasses import dataclass,asdict,replace
import copy
import hashlib
import pytest
from pln_chess.common import ROOT,read_json,write_json,digest,digest_dataclass
from pln_chess.domain import Position,Piece,Move
from pln_chess.hypotheses import candidates
from pln_chess.pln import TV
from pln_chess.cycle9.acceptance import accepted_model,CHECKS
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle9.diagnostics import calibrated_diagnostic,report


def test_domain_cache_preserves_locked_identity_for_every_c9_fixture():
    path=ROOT/'artifacts/cycle9/performance/domain-golden.json'
    if not path.exists():pytest.skip('Pre-edit golden receipt is required for delivery')
    rows=[]
    for f in read_json(ROOT/'artifacts/cycle9/datasets/dataset.json')['positions']:
        p=Position.from_fen(f['fen'])
        rows.append(dict(fen=p.fen(),id=p.id,pieces=[(i.id,i.symbol,i.square) for i in p.pieces],
            moves=[(m.id,m.notation) for m in candidates(p)],
            occupied=[p.at((x,y)).id if p.at((x,y)) else None for y in range(8) for x in range(8)]))
    old=read_json(path);assert len(rows)==old['positions'] and digest(rows)==old['identity_digest']


def test_frozen_state_detaches_mutable_inputs_and_replace_drops_caches():
    square=[1,1];unknown=[[2,2]];pieces=[Piece('r','Rook','White',square)]
    p=Position(pieces,'White',unknown_squares=unknown);m=Move(square,[1,3]);before=(p.id,p.fen(),m.id,m.notation)
    p.at((1,1));square[0]=7;unknown[0][0]=7;pieces.clear()
    assert (p.id,p.fen(),m.id,m.notation)==before and p.at((1,1)).id=='r'
    q=replace(p,turn='Black');assert q.id!=p.id and q.fen()!=p.fen()
    q=replace(p,unknown_squares=());assert q.id!=p.id and q.fen()==p.fen()
    assert copy.deepcopy(p).id==p.id
    duplicate=Position((Piece('first','Rook','White',(1,1)),Piece('second','Bishop','White',(1,1))),'White')
    assert duplicate.at((1,1)).id=='first'


def test_model_digest_preserves_deep_encoding_and_never_caches_mutable_evidence():
    @dataclass
    class Inner:
        records:list
    @dataclass
    class Outer:
        nested:dict
        inner:Inner
    value=Outer({'belief':{'strength':.975,'confidence':.495}},Inner([1,2,{'x':True}]))
    original=digest_dataclass(value);assert original==digest(asdict(value))
    value.nested['belief']['strength']=.125
    assert digest_dataclass(value)==digest(asdict(value))!=original
    with pytest.raises(ValueError):digest_dataclass(Inner([float('nan')]))


def test_tv_export_is_a_fresh_dictionary_with_identical_native_numbers():
    tv=TV(.123,.456);a=tv.json();assert a==asdict(tv);a['strength']=1
    assert tv.json()==asdict(tv)


def test_consolidation_acceptance_is_source_bound_and_cannot_promote_new_learning(tmp_path,monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv('C9_OUT',str(tmp_path));model=SimpleNamespace(version='known',runtime_version='pinned')
    assert not accepted_model(model)
    receipt=dict(passed=True,all_required_checks_executed=True,checks={k:True for k in CHECKS},new_learning_promoted=False,
        accepted_model_versions=['known'],runtime_version='pinned',production_code_hash=production_code_hash(),
        registration_hash=digest(read_json(ROOT/'configs/cycle9.json')),
        legacy_registrations={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8)})
    write_json(tmp_path/'acceptance.json',receipt);assert accepted_model(model)
    for change in ({'new_learning_promoted':True},{'production_code_hash':'different'},{'checks':{**receipt['checks'],'negative_controls':False}}):
        write_json(tmp_path/'acceptance.json',{**receipt,**change});assert not accepted_model(model)


def test_empirical_diagnostics_are_integrity_checked_and_never_change_native_result(tmp_path,monkeypatch):
    monkeypatch.setenv('C9_OUT',str(tmp_path))
    candidate=dict(model_version='m',mode='operational',classification='supported-legal',raw_stv=dict(strength=.95,confidence=.4),
        observations=dict(context=dict(destination_exists=True)))
    before=copy.deepcopy(candidate)
    mapping=[dict(n=8,legal=7,probability=.8) for _ in range(10)]
    data=dict(model_version='m',mappings={'in-board':mapping,'complete':mapping},fit_games=20,fit_positions=100,fit_split='calibration',dataset_hash='d')
    path=tmp_path/'calibration/results.json';write_json(path,data)
    write_json(tmp_path/'acceptance.json',dict(passed=True,calibration_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    result=calibrated_diagnostic(candidate)
    assert result['estimated_legal_frequency']==.8 and result['native'] is False and result['changes_classification'] is False
    assert candidate==before
    assert not calibrated_diagnostic({**candidate,'mode':'strict'})['available']
    assert not calibrated_diagnostic({**candidate,'model_version':'other'})['available']
    assert not calibrated_diagnostic({**candidate,'classification':'incomplete'})['available']
    write_json(path,{**data,'dataset_hash':'tampered'});assert not calibrated_diagnostic(candidate)['available']
    with pytest.raises(ValueError):report('../outside')
