"""Native partial evidence, conservative selection and provenance boundaries."""
from dataclasses import replace
import copy
import random
import pytest
from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position, Move
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import infer_moves as prior_infer, Cycle7Options
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.ontology import observe, key, project
from pln_chess.cycle8.inference import infer_moves, Cycle8Options, Session, default_mode

ROOK='7k/8/8/8/8/8/2R5/2K5 w - - 0 1'
BLOCK='7k/8/8/8/8/8/2RP4/2K5 w - - 0 1'
PROMOTION='r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29'


@pytest.fixture(scope='module')
def rt():return Runtime(timeout=180)


@pytest.fixture(scope='module')
def frozen(rt):
    return PromotionModel.wrap(BackoffModel.load(ROOT/'artifacts/cycle7/model/C7-frozen.json',rt),'C8-frozen')


@pytest.fixture(scope='module')
def trained(frozen,rt):
    import chess
    from training.cycle8_data import construct
    from training.cycle4 import enrich4
    from training.cycle8 import train
    rows=[];rng=random.Random(8181)
    for scenario in ('diagonal-opponent-knight','forward-opponent-king'):
        for index in range(4):
            board,start,end=construct(scenario,rng)
            for choice in ('q','r','b','n'):
                move=chess.square_name(start)+chess.square_name(end)+choice
                rows.append(enrich4({'fen':board.fen(),'move':move,'label':chess.Move.from_uci(move) in board.legal_moves,
                    'source':'unit-test-supervision','dependence_group':f'unit-{scenario}-{index}',
                    'transformation_lineage':[],'confidence':.5,'split':'train','family':scenario,
                    'position_fixture':f'unit-{scenario}-{index}'}))
    data={'examples':rows};data['hash']=digest(data)
    return train(data,frozen.source_model(),rt),data


@pytest.mark.parametrize('mode',['operational','strict','experimental'])
@pytest.mark.parametrize('fen,move',[(ROOK,'c2e2'),(BLOCK,'c2h2'),(PROMOTION,'f7e8n')])
def test_frozen_preserves_every_native_node(frozen,rt,mode,fen,move):
    p=Position.from_fen(fen);m=find_move(p,move)
    old=prior_infer(p,frozen.source_model(),Cycle7Options(mode=mode),rt,[m])['candidates'][0]
    new=infer_moves(p,frozen,Cycle8Options(mode=mode),rt,[m])['candidates'][0]
    assert (old['classification'],old['raw_stv'],old['proof_trace'])==(new['classification'],new['raw_stv'],new['proof_trace'])
    assert not new['positive_proof_complete'] and new['proof_status']!='native-compositional'


def test_relative_transition_is_color_reflection_and_translation_invariant():
    from pln_chess.spatial import translate,color_flip
    p=Position.from_fen('5k2/3P4/8/8/8/8/1K6/8 w - - 0 1');m=find_move(p,'d7d8n')
    translated=translate(p,(1,0));tm=replace(m,start=(4,6),end=(4,7))
    flipped=color_flip(p);fm=replace(m,start=(3,1),end=(3,0))
    assert observe(p,m)['descriptor']==observe(translated,tm)['descriptor']==observe(flipped,fm)['descriptor']
    d=observe(p,m)['descriptor'];assert d['end_boundary_distance']==0 and d['resulting_piece']=='Knight'
    assert 'White' not in str(d) and 'd7' not in str(d)


@pytest.mark.parametrize('choice',['q','r','b','n'])
def test_promotion_choice_and_destination_are_not_erased(trained,rt,choice):
    model,_=trained;p=Position.from_fen(PROMOTION)
    good=find_move(p,'f7e8'+choice);bad=find_move(p,'f7f8'+choice)
    a=observe(p,good);b=observe(p,bad)
    assert a['descriptor']['destination_occupancy']=='Opponent'
    assert b['descriptor']['destination_kind']=='King'
    assert key(a['descriptor'])!=key(b['descriptor'])
    result=infer_moves(p,model,Cycle8Options(mode='operational'),rt,[good,bad])['candidates']
    assert [c['classification'] for c in result]==['supported-legal','supported-illegal']
    assert all(c['promotion_selection'] and c['evidence_ids'] for c in result)
    assert all(not c['positive_proof_complete'] for c in result)


@pytest.mark.parametrize('mode',['strict','experimental'])
def test_new_training_cannot_claim_strict_positive_composition(trained,rt,mode):
    model,_=trained;p=Position.from_fen(PROMOTION);move=find_move(p,'f7e8n')
    c=infer_moves(p,model,Cycle8Options(mode=mode),rt,[move])['candidates'][0]
    assert c['classification']=='unknown' and c['promotion_selection'] is None
    assert c['mode_comparison']['operational']['evaluated'] is False


def test_essential_evidence_retraction_removes_new_conclusion(trained,rt):
    from training.cycle8 import train
    model,data=trained;p=Position.from_fen(PROMOTION);move=find_move(p,'f7e8n')
    original=infer_moves(p,model,Cycle8Options(mode='operational'),rt,[move])['candidates'][0]
    groups=model.hypotheses[original['promotion_selection']['rule_id']]['dependence_groups']
    removed=train(data,model.source_model(),rt,retract_groups=groups)
    result=infer_moves(p,removed,Cycle8Options(mode='operational'),rt,[move])['candidates'][0]
    assert original['classification']=='supported-legal' and result['classification']=='unknown'
    assert not set(groups)&set(result['dependence_groups'])


def test_cold_warm_reference_proofs_are_identical(trained,rt):
    model,_=trained;p=Position.from_fen(PROMOTION);moves=[find_move(p,'f7e8n'),find_move(p,'f7f8n')]
    options=Cycle8Options(mode='operational');session=Session(rt)
    reference=infer_moves(p,model,options,rt,moves,optimized=False)
    cold=infer_moves(p,model,options,rt,moves,session)
    warm=infer_moves(p,model,options,rt,moves,session)
    assert reference['candidates']==cold['candidates']==warm['candidates']
    assert warm['native_invocations']==0 and cold['native_invocations']>0
    limited=infer_moves(p,model,replace(options,max_native_invocations=0),rt,moves,session)
    assert limited['truncated'] and all(c['classification']=='incomplete' for c in limited['candidates'])


def test_missing_destination_stays_unknown(trained,rt):
    model,_=trained;p=Position.from_fen(PROMOTION,unknown_squares=((4,7),));move=find_move(p,'f7e8n')
    c=infer_moves(p,model,Cycle8Options(mode='operational'),rt,[move])['candidates'][0]
    assert c['classification']=='unknown' and c['promotion_selection'] is None
    assert not c['promotion_transition']['complete']


def test_model_replay_and_tamper_detection(trained,rt,tmp_path):
    model,_=trained;path=tmp_path/'m.json';model.export(path)
    assert PromotionModel.load(path,rt).version==model.version
    value=read_json(path);value['hypotheses'][next(iter(value['hypotheses']))]['positive']['strength']=.123
    write_json(path,value)
    with pytest.raises(ValueError,match='integrity'):PromotionModel.load(path,rt)


def test_c8_defaults_require_complete_bound_receipt(frozen,tmp_path,monkeypatch):
    monkeypatch.setenv('C8_OUT',str(tmp_path));assert default_mode(frozen)=='strict'
    write_json(tmp_path/'acceptance.json',{'passed':True,'accepted_model_versions':[frozen.version]})
    assert default_mode(frozen)=='strict'


def test_production_never_imports_reference_or_proposed_math(trained,rt,monkeypatch):
    import builtins
    model,_=trained;original=builtins.__import__
    def blocked(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError(name)
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',blocked)
    p=Position.from_fen(PROMOTION)
    assert infer_moves(p,model,Cycle8Options(mode='operational'),rt,[find_move(p,'f7e8n')])['candidates'][0]['classification']=='supported-legal'


def test_inspector_uses_shared_comparison_and_exports_proofs(trained,rt,tmp_path,monkeypatch):
    from pln_chess.cycle8.api import compare_generations
    from pln_chess.cli.web import inspector_infer
    model,_=trained;monkeypatch.setenv('C8_OUT',str(tmp_path))
    model.export(tmp_path/'model/C8-promotion-relative.json')
    payload={'fen':PROMOTION,'move':'f7e8n','model':'C8-experimental','mode':'operational','compare':True}
    result=inspector_infer(payload)
    direct=compare_generations(PROMOTION,'f7e8n',model,runtime=rt)
    assert set(result['comparisons'])=={'C7-operational','C7-learned-experimental','C8-experimental'}
    assert result['differences']==direct['differences']
    assert result['comparisons']['C8-experimental']['candidate']==direct['comparisons']['C8-experimental']['candidate']
    assert result['selected_key']=='C8-experimental'
    assert result['promotion_transition']['descriptor']['resulting_piece']=='Knight'
    assert not result['comparisons']['C8-experimental']['candidate']['proof_complete']
    ordinary=inspector_infer({**payload,'compare':False})
    assert ordinary['candidate']['classification']=='supported-legal'


def test_cli_benchmark_preserves_explicit_mode(frozen,tmp_path,monkeypatch,capsys):
    from pln_chess.cli import main
    import evaluation.cycle8_benchmark as benchmark
    path=tmp_path/'frozen.json';frozen.export(path);seen={}
    def capture(*args,**kwargs):
        seen.update(kwargs);return []
    monkeypatch.setattr(benchmark,'run',capture)
    assert main(['benchmark','--checkpoint',str(path),'--mode','strict'])==0
    assert seen['mode']=='strict'
