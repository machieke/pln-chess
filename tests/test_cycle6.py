"""Versioned mode/provenance/replay tests; previous cycle expectations stay intact."""
from dataclasses import asdict,replace
from pathlib import Path
import copy,json,os
import pytest
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from pln_chess.domain import Position
from pln_chess.api import explain_move,find_move,analyze_batch
from pln_chess.cycle6.model import ModeModel,POLICY
from pln_chess.cycle6.inference import Cycle6Options,Session,infer_moves,decision,default_mode
from pln_chess.cycle6.history import inspect

POS='7k/8/8/8/8/8/2R5/2K5 w - - 0 1'
BLOCK='7k/8/8/8/8/8/2RP4/2K5 w - - 0 1'
KNIGHT='2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1'
@pytest.fixture(scope='module')
def rt():return Runtime(timeout=120)
@pytest.fixture(scope='module')
def model(rt):return ModeModel.migrate(Model.load(ROOT/'artifacts/cycle5/model/C5-full.json',rt))

@pytest.mark.parametrize('mode,expected',[('operational','supported-legal'),('strict','unknown'),('experimental','unknown')])
def test_modes_preserve_raw_evidence(model,rt,mode,expected):
    c=explain_move(POS,'c2e2',model,runtime=rt,mode=mode)['candidate']
    assert c['classification']==expected and c['mode']==mode
    assert c['raw_stv']==c['legacy_projection']['truth_value'] and c['raw_stv']['strength']>.8
    assert c['positive_proof_complete'] is False and c['proof_status']!='native-composed'
    assert c['evidence_ids'] and c['dependence_groups'] and c['native_rule_ids']
    assert c['decision_node']['native'] is False

@pytest.mark.parametrize('mode',['operational','strict','experimental'])
def test_negative_and_unknown_distinct(model,rt,mode):
    c=explain_move(BLOCK,'c2h2',model,runtime=rt,mode=mode)['candidate']
    assert c['classification']=='supported-illegal' and c['proof_status']=='native-negative-chain'
    k=explain_move(KNIGHT,'f6h5',model,runtime=rt,mode=mode)['candidate']
    assert k['classification']=='unknown'

@pytest.mark.parametrize('mode',['operational','strict','experimental'])
def test_incomplete_never_unknown(model,rt,mode):
    r=explain_move(POS,'c2e2',model,Cycle6Options(mode=mode,max_native_invocations=0),rt)
    assert r['truncated'] and r['candidate']['classification']=='incomplete'

@pytest.mark.parametrize('mode',['operational','strict','experimental'])
def test_conflicting_channels_abstain(mode):
    positive={'classification':'supported','truth_value':{'strength':.99,'confidence':.9}}
    negative={'classification':'contradicted','truth_value':{'strength':.01,'confidence':.95}}
    result=decision(positive,negative,Cycle6Options(mode=mode))
    assert result[0]=='unknown' and 'opposing-global-channels' in result[1]

@pytest.mark.parametrize('mode',['operational','strict','experimental'])
def test_cache_full_proof_and_mode_isolation(model,rt,mode):
    p=Position.from_fen(POS);m=find_move(p,'c2e2');session=Session(rt);o=Cycle6Options(mode=mode)
    reference=infer_moves(p,model,o,rt,[m],optimized=False)
    cold=infer_moves(p,model,o,rt,[m],session);warm=infer_moves(p,model,o,rt,[m],session)
    assert reference['candidates']==cold['candidates']==warm['candidates']
    assert warm['native_invocations']==0 and warm['cache_hits']>0
    other=infer_moves(p,model,replace(o,mode='strict' if mode!='strict' else 'operational'),rt,[m],session)
    assert other['native_invocations']>0 and other['cache_scope']!=cold['cache_scope']
    limited=infer_moves(p,model,replace(o,max_native_invocations=0),rt,[m],session)
    assert limited['truncated'] and limited['candidates'][0]['classification']=='incomplete'

def test_model_lossless_migration(model,rt,tmp_path):
    p=tmp_path/'m.json';model.export(p);loaded=Model.load(p,rt)
    assert loaded.version==model.version
    assert loaded.source_model().version==Model.load(ROOT/'artifacts/cycle5/model/C5-full.json',rt).version
    d=read_json(p);d['policy']='fake';write_json(p,d)
    with pytest.raises(ValueError):Model.load(p,rt)

def test_no_default_promotion_without_complete_receipt(model,tmp_path,monkeypatch):
    monkeypatch.setenv('C6_OUT',str(tmp_path));assert default_mode(model)=='strict'
    receipt={'passed':True,'model_version':model.version,'runtime_version':model.runtime_version,'policy':POLICY}
    write_json(tmp_path/'acceptance.json',receipt);assert default_mode(model)=='strict'
    from pln_chess.cycle6.inference import REQUIRED_CHECKS,production_code_hash
    receipt.update(checks={k:True for k in REQUIRED_CHECKS},production_code_hash=production_code_hash(),registration_hash=digest(read_json(ROOT/'configs/cycle6.json')))
    write_json(tmp_path/'acceptance.json',{**receipt,'all_required_checks_executed':True});assert default_mode(model)=='operational'
    write_json(tmp_path/'acceptance.json',{**receipt,'all_required_checks_executed':True,'model_version':'wrong'});assert default_mode(model)=='strict'

def test_display_threshold_preserves_raw_tv(model,rt):
    a=explain_move(POS,'c2e2',model,Cycle6Options(mode='operational'),rt)['candidate']
    b=explain_move(POS,'c2e2',model,Cycle6Options(mode='operational',min_confidence=.999),rt)['candidate']
    assert a['raw_stv']==b['raw_stv'] and b['classification']=='unknown'

def test_batch_independent_modes(model,rt):
    r=analyze_batch([{'fen':POS,'move':'c2e2','mode':m} for m in ('operational','strict')],model,runtime=rt)
    assert [x['candidate']['classification'] for x in r['results']]==['supported-legal','unknown']

def test_explicit_mode_rejects_legacy_checkpoint(model,rt):
    with pytest.raises(ValueError):explain_move(POS,'c2e2',model.source_model(),runtime=rt,mode='strict')

@pytest.mark.parametrize('mode',['typo','legal','C4'])
def test_invalid_mode(mode):
    with pytest.raises(ValueError):Cycle6Options(mode=mode)

@pytest.mark.parametrize('alias,canonical',[('unknown','fen-only'),('trusted-fen','trusted-metadata'),('observed-events','event-backed')])
def test_history_aliases(alias,canonical):assert Cycle6Options(temporal_mode=alias).temporal_mode==canonical

@pytest.mark.parametrize('fen,notation,effect',[
 ('7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1','b7b5','ep'),
 ('6k1/8/8/8/8/8/8/4K2R w K - 0 1','h1h2','rights'),
 ('6k1/8/8/8/8/8/8/4K2R w K - 0 1','e1e2','rights'),
 ('6k1/8/8/8/8/8/8/4K2R w K - 0 1','e1g1','rights'),
 ('7k/P7/8/8/8/8/8/2K5 w - - 0 1','a7a8q','promotion'),
 ('4k2r/8/8/8/8/8/8/4K2R b Kk - 0 1','h8h1','capture'),
 ('7k/8/8/1pP5/8/8/8/2K5 w - b6 0 1','c5b6','capture')])
def test_versioned_replay_effects(fen,notation,effect):
    p=Position.from_fen(fen);q=p.successor(find_move(p,notation));e={'initial_fen':fen,'moves':[notation],'source':'unit-events','confidence':.99}
    receipt=inspect(q,'observed-events',e);assert receipt['status']=='structurally-consistent'
    event=receipt['events'][0];assert event['schema']=='events-v6.1' and event['historical_legality']=='unverified'
    assert event['effects']['removed_or_changed'] and event['effects']['added_or_changed']
    if effect=='rights':assert event['effects']['rights_before']!=event['effects']['rights_after']
    if effect=='ep':assert event['effects']['ep_after'] is not None
    assert inspect(p,'observed-events',e)['status']=='conflicting'
    assert inspect(q,'observed-events',{**e,'initial_fen':q.fen(),'moves':[]})['status']=='truncated'
    assert inspect(replace(q,rights='Q'),'observed-events',e)['status']=='conflicting'

def test_unknown_observation_is_not_illegal(model,rt):
    p=replace(Position.from_fen(POS),unknown_squares=((4,1),))
    c=explain_move(p,'c2e2',model,runtime=rt,mode='operational')['candidate']
    assert c['classification']=='unknown'

def test_piece_id_renaming(model,rt):
    p=Position.from_fen(POS);q=replace(p,pieces=tuple(replace(x,id='different-'+str(i)) for i,x in enumerate(reversed(p.pieces))))
    a=explain_move(p,'c2e2',model,runtime=rt,mode='operational')['candidate'];b=explain_move(q,'c2e2',model,runtime=rt,mode='operational')['candidate']
    assert a['raw_stv']==b['raw_stv'] and a['classification']==b['classification']
    assert a['observations']['local_context']==b['observations']['local_context']

def test_native_independent_premises_and_removal(rt):
    for expr in ['(collapse (|- (A (stv 0.9 0.8)) (B (stv 0.9 0.8))))','(collapse (|- (A (stv 0.9 0.8))))','(collapse (|- (B (stv 0.9 0.8))))']:
        assert '(C6TEST ())' in rt.execute(f'!(println! (C6TEST {expr}))')

def test_inspector_mode_contract(model,rt):
    from pln_chess.cli.web import inspector_infer,HTML
    for mode,expected in [('operational','supported-legal'),('strict','unknown')]:
        c=inspector_infer({'fen':POS,'move':'c2e2','mode':mode},model)['candidate'];assert c['classification']==expected
    assert 'id="mode"' in HTML and 'mode_comparison' in HTML

def test_cli_mode_surface(capsys):
    from pln_chess.cli import main
    for cmd in ('infer','inspect','evaluate','benchmark'):
        with pytest.raises(SystemExit) as e:main([cmd,'--help'])
        assert e.value.code==0 and '--mode' in capsys.readouterr().out

def test_factorial_curriculum_withholds_combinations(model,rt,tmp_path):
    from training.cycle6 import generate
    from evaluation.cycle6_research import curriculum
    d=generate();curriculum(d,model,rt,tmp_path)
    report=read_json(tmp_path/'factorial-curriculum.json');assert report['abstract_combination_overlap']==[]
    assert all(len(set(x['family'] for x in p['targets']))<=2 for p in report['evidence'])
    assert any(t['move']=='f6h5' and t['family']=='mandatory-C5-knight' for t in d['factorial_tasks'])

def test_opposing_native_channels_keep_both_proofs(model,rt):
    from evaluation.cycle6_research import conflicting_model
    changed=conflicting_model(model,rt)
    c=explain_move(POS,'c2e2',changed,Cycle6Options(mode='operational'),rt)['candidate']
    assert c['evidence_channels']['C4']['classification']=='supported'
    assert c['evidence_channels']['C5']['classification']=='contradicted'
    assert c['classification']=='unknown' and 'opposing-global-channels' in c['decision_policy']
    assert c['evidence_channels']['positive_nodes'] and c['evidence_channels']['negative_nodes']

def test_lossless_evaluation_proof_export(model,rt):
    from evaluation.cycle6 import evaluate
    data={'hash':'unit','positions':[{'id':'unit','family':'unit','split':'test','fen':'7k/8/8/8/8/8/8/2K5 w - - 0 1'}]}
    report=evaluate(data,model,'test',rt)
    for row in report['rows']:
        trace=[report['native_proof_dag'][ref] for ref in row['proof_refs']]
        assert digest(trace)==row['proof_id']
        assert report['policy_decisions'][row['decision_ref']]['native'] is False

def test_overlapping_negative_bridge_cannot_reveal_positive(model,rt):
    from evaluation.cycle6_research import conflicting_model
    from pln_chess.cycle5.ontology import relation
    from pln_chess.cycle4.ontology import relation as old_relation
    changed=conflicting_model(model,rt);key=relation('ray',{'piece':'Rook','effect':'ordinary','occupancy':'Empty'},'RayObstruction')['id']
    bridge=changed.source_model().base_model().hypotheses[old_relation('Bridge',{'edge':'Obstruction-to-NotLegal'})['id']]
    changed.source['hypotheses'][key]['dependence_groups']+=bridge['dependence_groups']
    c=explain_move(POS,'c2e2',changed,runtime=rt,mode='operational')['candidate']
    assert c['classification']=='unknown' and c['evidence_channels']['dependency_conflicts']
    assert c['evidence_channels']['C4']['classification']=='supported'
    assert c['evidence_channels']['C5']['classification']=='unknown'

def test_cycle6_inference_without_oracle_imports(model,rt,monkeypatch):
    import builtins
    original=builtins.__import__
    def restricted(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('Oracle import in production')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',restricted)
    assert explain_move(POS,'c2e2',model,runtime=rt,mode='operational')['candidate']['classification']=='supported-legal'

def test_native_failure_remains_incomplete(model,rt,monkeypatch):
    from pln_chess.pln import NativeError
    def fail(*args,**kwargs):raise NativeError('injected native interpreter failure')
    monkeypatch.setattr(rt,'batch',fail)
    r=explain_move(POS,'c2e2',model,runtime=rt,mode='operational')
    assert r['truncated'] and r['candidate']['classification']=='incomplete'
    assert 'injected native interpreter failure' in str(r)
