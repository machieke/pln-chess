"""Contract, semantic-boundary and causal tests for the factored constraint cycle."""
import copy,json,os,subprocess,sys
from dataclasses import replace
from pathlib import Path
import pytest
from pln_chess.common import ROOT,read_json,digest
from pln_chess.domain import Position,Move,Piece
from pln_chess.api import explain_move,find_move
from pln_chess.learning import Model
from pln_chess.evidence import Ledger
from pln_chess.cycle4.model import train,observe_example
from pln_chess.cycle4.ontology import descriptors,relation
from pln_chess.cycle4.inference import infer_moves,Cycle4Options
from pln_chess.cycle4.history import HistoryEvidence
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle3.counterfactual import compare
from pln_chess.pln import TV,NativeError

OUT=Path(os.environ.get('C4_OUT',ROOT/'artifacts/cycle4'))
FEN='7k/8/8/8/8/8/2R5/2K5 w - - 0 1'

@pytest.fixture(scope='module')
def model():return Model.load(OUT/'model/C4-full.json')

def item(model,runtime,fen=FEN,move='c2e2',options=None):
    return explain_move(fen,move,model,options,runtime)['candidate']

def row(label=True,group='g1',fen=FEN,move='c2e2',lineage=None):
    return {'fen':fen,'move':move,'label':label,'movement_label':label,'source':'test-explicit-label',
            'dependence_group':group,'transformation_lineage':lineage or []}

def test_schema_integrity(model,tmp_path,runtime):
    path=tmp_path/'m.json';model.export(path);assert Model.load(path,runtime).version==model.version
    d=read_json(path);d['grammar']='fake';path.write_text(json.dumps(d))
    with pytest.raises(ValueError):Model.load(path,runtime)

def test_previous_schemas_remain_loadable(runtime):
    for file,schema in [('artifacts/model.json',1),('artifacts/cycle2/B1-model.json',2),('artifacts/cycle3/C3-full-model.json',3)]:
        assert Model.load(ROOT/file,runtime).schema==schema

def test_key_excludes_bindings():
    p=Position.from_fen(FEN);m=find_move(p,'c2e2');o=descriptors(p,m)
    changed=replace(p,pieces=tuple(replace(x,id='another-'+x.id) for x in p.pieces))
    assert o['local_context']==descriptors(changed,m)['local_context']
    assert all('fen' not in r['descriptor'] and 'source_game' not in r['descriptor'] for r in o['relations'])

def test_remote_piece_does_not_change_local_key():
    p=Position.from_fen(FEN);m=find_move(p,'c2e2');q=replace(p,pieces=p.pieces+(Piece('remote','Knight','Black',(0,5)),))
    assert descriptors(p,m)['local_context']==descriptors(q,m)['local_context']
    assert len(descriptors(q,m)['attack_relations'])==len(descriptors(p,m)['attack_relations'])+1

def test_capture_kind_does_not_define_pooled_movement():
    p=Position.from_fen('7k/8/8/8/8/8/2R1n3/2K5 w - - 0 1');m=find_move(p,'c2e2')
    q=replace(p,pieces=tuple(replace(x,kind='Bishop') if x.square==(4,1) else x for x in p.pieces))
    assert descriptors(p,m)['local_context']==descriptors(q,m)['local_context']

@pytest.mark.parametrize('dx,dy',[(1,0),(-1,0),(0,1)])
def test_local_translation(dx,dy):
    p=Position.from_fen('8/6k1/8/8/8/2R5/2K5/8 w - - 0 1');m=find_move(p,'c3e3')
    from pln_chess.spatial import translate
    q=translate(p,(dx,dy));n=Move((m.start[0]+dx,m.start[1]+dy),(m.end[0]+dx,m.end[1]+dy))
    assert descriptors(p,m)['local_context']==descriptors(q,n)['local_context']

def test_color_orientation(model,runtime):
    result=compare(FEN,'c2e2',model,'color-flip',runtime=runtime)
    a=result['before']['candidate'];b=result['after']['candidate']
    assert a['classification']==b['classification'] and a['legal_move_truth_value']==b['legal_move_truth_value']

@pytest.mark.parametrize('square',['d2','f2','g2'])
def test_any_intermediate_cell_transfers(model,runtime,square):
    r=compare(FEN,'c2h2',model,'add-blocker',square,runtime=runtime)
    assert r['before']['candidate']['classification']=='supported'
    assert r['after']['candidate']['classification']=='contradicted'
    c=r['after']['candidate'];assert any(a['target']=='Obstruction' for a in c['matched_hypotheses'])
    assert any(t['operator']=='Truth_ModusPonens' and t['conclusion']=='Not LegalMove' for t in c['proof_trace'])

def test_knight_jump_preserved(model,runtime):
    r=compare('7k/8/8/8/8/8/2N5/2K5 w - - 0 1','c2e3',model,'add-blocker','d2',runtime=runtime)
    assert r['before']['candidate']['classification']==r['after']['candidate']['classification']=='supported'

@pytest.mark.parametrize('fen,move',[
 ('k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1','e3f3'),
 ('k7/8/7b/8/8/4N3/8/2K5 w - - 0 1','e3f5'),
 ('k3r3/8/8/8/1b6/8/3R4/4K3 w - - 0 1','d2e2'),
 ('k4r2/8/8/8/8/8/8/4K2R w K - 0 1','e1g1'),
 ('k3r3/8/8/8/8/8/4n3/4K3 w - - 0 1','e1e2'),
])
def test_exposure_resolves_negative(model,runtime,fen,move):
    c=item(model,runtime,fen,move)
    assert c['classification']=='contradicted'
    assert c['status']=='native-constraint-chain'
    assert any(t['conclusion']=='WouldExposeOwnKing' for t in c['proof_trace'])

def test_three_independent_pools(model,runtime):
    c=item(model,runtime,'k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1','e3f3')
    nodes={t['id']:t for t in c['proof_trace']}
    found=False
    for t in c['proof_trace']:
        if t['operator']!='Truth_ModusPonens' or t['conclusion'] not in ('WouldExposeOwnKing','Not LegalMove'):continue
        parent=next((p['node'] for p in t['premises'] if 'node' in p),None)
        key=next((p['conditional'] for p in t['premises'] if 'conditional' in p),None)
        if parent and key:
            assert not set(nodes[parent]['dependence_groups'])&set(model.hypotheses[key]['dependence_groups'])
            if t['conclusion']=='Not LegalMove' and nodes[parent]['conclusion']=='WouldExposeOwnKing':found=True
    assert found

def test_shared_bridge_pool_abstains(model,runtime):
    m=copy.deepcopy(model)
    groups=sorted({g for h in m.hypotheses.values() if h['target']=='Attack' for g in h['dependence_groups']})
    m.hypotheses[relation('Bridge',{'edge':'Attack-to-Exposure'})['id']]['dependence_groups']=groups
    c=item(m,runtime,'k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1','e3f3')
    assert c['classification']=='unknown'
    assert any(a.get('chain_gap')=='Correlated premise pools' for a in c['attack_beliefs'])

def test_no_threat_is_not_a_safety_fact(model,runtime):
    c=item(model,runtime);assert c['classification']=='supported'
    assert 'global safety is unproved' in ' '.join(c['gaps'])
    assert not any(t['conclusion'] in ('KingSafe','NoAttack') for t in c['proof_trace'])

def test_disputed_attack_does_not_disappear(model,runtime):
    m=copy.deepcopy(model)
    for h in m.hypotheses.values():
        if h['target']=='Attack':
            h['positive']=h['negative']={'strength':.5,'confidence':.9}
            h['supporting_evidence']=['support'];h['contradicting_evidence']=['counter']
    c=item(m,runtime);assert c['classification']=='unknown' and c['conflicting_evidence']

def test_batch_production_diagnostics(model,runtime):
    from pln_chess.api import analyze_batch
    r=analyze_batch([{'fen':FEN,'move':'c2e2'}],model,runtime=runtime)
    assert len(r['results'])==1 and r['unresolved']==[]
    with pytest.raises(ValueError):analyze_batch([{}]*65,model,runtime=runtime)

def test_inspector_factored_ui_contract():
    from pln_chess.cli.web import HTML,inspector_infer
    assert 'C4-full' in HTML and 'Factored premises and origin' in HTML and 'Export diagnostic JSON' in HTML
    result=inspector_infer({'model':'default','fen':FEN,'move':'c2e2'},OUT/'model/C4-full.json')
    assert result['candidate']['factored_premises']

@pytest.mark.parametrize('fen,move',[
 ('6k1/8/8/3Pp3/8/8/8/K7 w - e6 0 1','d5e6'),
 ('k7/8/8/8/8/8/8/4K2R w K - 0 1','e1g1')])
def test_fen_temporal_flags_are_not_full_history(model,runtime,fen,move):
    assert item(model,runtime,fen,move)['classification']=='unknown'

def test_history_evidence_scopes_and_contradiction():
    p=Position.from_fen('6k1/4p3/8/3P4/8/8/8/K7 b - - 0 1');m=find_move(p,'e7e5');after=p.successor(m)
    h=HistoryEvidence(p.fen(),('e7e5',),'observed-board')
    pos,receipt=h.apply(after.fen());assert pos.history_known and receipt['ep_predecessor_observed']
    with pytest.raises(ValueError):h.apply(FEN)
    weak=replace(h,confidence=.2);assert not weak.apply(after.fen())[0].history_known

def test_ordinary_predecessor_does_not_attest_castling():
    p=Position.from_fen('k7/8/8/8/8/8/7p/4K2R b K - 0 1');after=p.successor(find_move(p,'h2h1q'))
    h=HistoryEvidence(p.fen(),('h2h1q',),'observation')
    assert not h.apply(after.fen())[0].history_known

@pytest.mark.parametrize('promotion',list('qrbn'))
def test_promotion_structural_replacement(promotion):
    p=Position.from_fen('8/3P2k1/8/8/8/8/8/1K6 w - - 0 1');m=find_move(p,'d7d8'+promotion)
    assert p.successor(m).at((3,7)).kind=={'q':'Queen','r':'Rook','b':'Bishop','n':'Knight'}[promotion]

def test_replay_duplicate_rollback_retraction(tmp_path,runtime):
    ledger=tmp_path/'e.jsonl';a=train([row()],runtime=runtime,ledger_path=ledger)
    b=train([row()],runtime=runtime,ledger_path=ledger);assert a.version==b.version
    c=train([row(False,'g2')],runtime=runtime,ledger_path=ledger)
    assert c.version!=a.version
    rolled=train(Ledger(ledger),options={'through_sequence':1},runtime=runtime)
    assert rolled.version==a.version
    retracted=train(Ledger(ledger),options={'retract_groups':['g2']},runtime=runtime)
    assert retracted.hypotheses==a.hypotheses
    h=next(h for h in c.hypotheses.values() if h['target']=='LocalAdmissibility')
    assert h['positive']['strength']==pytest.approx(.5)
    assert h['supporting_evidence'] and h['contradicting_evidence']

def test_transformed_ancestor_not_independent(tmp_path,runtime):
    a=train([row(),row(group='translated',lineage=['g1'])],runtime=runtime,ledger_path=tmp_path/'a.jsonl')
    b=train([row()],runtime=runtime,ledger_path=tmp_path/'b.jsonl')
    assert a.hypotheses==b.hypotheses

def test_same_game_dependence(tmp_path,runtime):
    a=train([row(),row(False)],runtime=runtime,ledger_path=tmp_path/'a.jsonl')
    assert a.training_report['excluded_update_count']>0
    b=train([row(),row(False)],options={'dependence_aware':False},runtime=runtime,ledger_path=tmp_path/'b.jsonl')
    assert a.hypotheses!=b.hypotheses

@pytest.mark.parametrize('kwargs',[{'label':1},{'movement_label':'true'},{'auxiliary_labels':{'x':1}},{'component_labels':{'x':1}},{'constraint_bridge_targets':['wrong']}])
def test_invalid_training_labels_rejected(tmp_path,runtime,kwargs):
    args={'position':FEN,'move':'c2e2','label':True,'source':'test','dependence_group':'g','ledger_path':tmp_path/'e.jsonl','runtime':runtime,**kwargs}
    with pytest.raises(ValueError):observe_example(**args)

def test_cache_full_proof_parity_and_invalidation(model,runtime):
    p=Position.from_fen(FEN);moves=[find_move(p,'c2e2'),find_move(p,'c2h2')];s=NativeSession(runtime)
    reference=infer_moves(p,model,runtime=runtime,selected_moves=moves,optimized=False)
    cold=infer_moves(p,model,runtime=runtime,selected_moves=moves,session=s)
    warm=infer_moves(p,model,runtime=runtime,selected_moves=moves,session=s)
    assert reference['candidates']==cold['candidates']==warm['candidates'] and warm['native_invocations']==0
    changed=infer_moves(p,model,Cycle4Options(min_confidence=.4),runtime,moves,s)
    assert changed['cache_scope']!=warm['cache_scope'] and changed['native_invocations']>0

@pytest.mark.parametrize('kwargs',[{'max_native_invocations':0},{'max_proof_bytes':1},{'timeout_seconds':.00001}])
def test_budget_is_incomplete(model,runtime,kwargs):
    result=infer_moves(FEN,model,Cycle4Options(**kwargs),runtime)
    assert result['truncated'] and any(c['classification']=='incomplete' for c in result['candidates'])

def test_cache_bounded(model,runtime):
    s=NativeSession(runtime,max_entries=3);infer_moves(FEN,model,runtime=runtime,session=s)
    assert len(s.cache)<=3

def test_unknown_ownership_or_cells_never_complete(model,runtime):
    p=replace(Position.from_fen(FEN),unknown_squares=((3,1),))
    assert all(c['classification']=='unknown' for c in infer_moves(p,model,runtime=runtime)['candidates'])

def test_production_no_reference_import(model):
    code='''import sys,importlib.abc
class Block(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname=='chess' or fullname.startswith('chess.') or fullname.startswith('training') or fullname.startswith('evaluation'):raise RuntimeError('oracle import '+fullname)
sys.meta_path.insert(0,Block())
from pln_chess.api import explain_move
r=explain_move(sys.argv[1],'c2e2',sys.argv[2])
assert r['candidate']['classification']=='supported'
'''
    subprocess.run([sys.executable,'-c',code,FEN,str(OUT/'model/C4-full.json')],check=True,capture_output=True,text=True)

def test_native_composition_negative_controls():
    from evaluation.cycle4_native import audit
    r=audit();assert 'conjunction' in r['decision']

def test_dataset_isolation_and_fixed_registration():
    d=read_json(OUT/'datasets/dataset.json');assert d['registration_hash']==digest(read_json(ROOT/'configs/cycle4.json'))
    assert len([g for g in d['games'] if g['split']=='independent-games'])==12
    assert d['leakage_audit']['train_test_board_symmetry_overlap']==[]
    assert all(r['split']=='train' for r in d['examples'])

def test_bootstrap_accepts_legacy_integer_game_zero():
    from evaluation.cycle4 import bootstrap
    positions=[{'fixture':'a','source_game':0,'exact':True,'elapsed':0},
               {'fixture':'b','source_game':0,'exact':True,'elapsed':0},
               {'fixture':'c','source_game':None,'exact':True,'elapsed':0}]
    rows=[{'fixture':p['fixture'],'label':True,'classification':'supported'} for p in positions]
    assert bootstrap(rows,positions,draws=5)['independent_clusters']==2
