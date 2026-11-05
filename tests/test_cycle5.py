"""Proof-gap, provenance, temporal and metamorphic contracts for Cycle 5."""
import copy,json,os,subprocess,sys
from dataclasses import replace
from pathlib import Path
import pytest
from pln_chess.common import ROOT,read_json,digest
from pln_chess.pln import Runtime,NativeError,TV
from pln_chess.learning import Model
from pln_chess.evidence import Ledger
from pln_chess.domain import Position,Move,Piece
from pln_chess.api import find_move,explain_move
from pln_chess.cycle5.ontology import descriptors
from pln_chess.cycle5.inference import infer_moves,Cycle5Options,Session,counterfactual
from pln_chess.cycle5.model import train
from pln_chess.cycle5.history import inspect,transform_evidence

OUT=Path(os.environ.get('C5_OUT',ROOT/'artifacts/cycle5'))
FEN='2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1'

@pytest.fixture(scope='module')
def model():return Model.load(OUT/'model/C5-full.json')

def candidate(model,runtime,fen=FEN,move='f6h5',options=None):
    return explain_move(fen,move,model,options,runtime)['candidate']

def test_knight_capture_gap_is_honest(model,runtime):
    c=candidate(model,runtime)
    assert c['classification']=='unknown' and c['legal_move_truth_value']=={'strength':.5,'confidence':0.}
    assert c['proof_plan']['native_conjunction']=='unsupported'
    assert any(p['family']=='geometry' and p['truth_value']['strength']>.8 for p in c['typed_premises'])
    assert any(p['family']=='destination' and p['truth_value']['strength']<.2 for p in c['typed_premises'])
    assert not c['proof_plan']['positive_proof_complete']

def test_model_round_trip_and_corruption(model,tmp_path,runtime):
    p=tmp_path/'m.json';model.export(p);assert Model.load(p,runtime).version==model.version
    x=read_json(p);x['hypotheses'][next(iter(x['hypotheses']))]['positive']['strength']=.123;p.write_text(json.dumps(x))
    with pytest.raises(ValueError,match='integrity'):Model.load(p,runtime)

def test_cross_version_imports(runtime):
    for f,s in [('artifacts/model.json',1),('artifacts/cycle2/B1-model.json',2),('artifacts/cycle3/C3-full-model.json',3),('artifacts/cycle4/model/C4-full.json',4)]:assert Model.load(ROOT/f,runtime).schema==s

@pytest.mark.parametrize('dx,dy',[(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1)])
def test_generated_translation_properties(dx,dy):
    from pln_chess.spatial import translate
    for kind in ('Rook','Bishop','Queen','Knight'):
        p=Position((Piece('white','King','White',(1,1)),Piece('black','King','Black',(6,6)),Piece('mover',kind,'White',(3,3))),'White')
        m=Move((3,3),(4,5) if kind=='Knight' else (4,4) if kind=='Bishop' else (3,5))
        q=translate(p,(dx,dy));n=Move((m.start[0]+dx,m.start[1]+dy),(m.end[0]+dx,m.end[1]+dy))
        assert descriptors(p,m)['typed_relations']==descriptors(q,n)['typed_relations']

def test_renaming_and_unrelated_piece():
    p=Position.from_fen(FEN);m=find_move(p,'f6h5');q=replace(p,pieces=tuple(replace(x,id='renamed-'+x.id) for x in p.pieces)+(Piece('remote','Pawn','Black',(0,5)),))
    assert descriptors(p,m)['typed_relations']==descriptors(q,m)['typed_relations']

def test_color_flip_premises():
    from pln_chess.spatial import color_flip
    p=Position.from_fen(FEN);m=find_move(p,'f6h5');q=color_flip(p);n=Move((5,2),(7,3))
    assert descriptors(p,m)['typed_relations']==descriptors(q,n)['typed_relations']

def test_no_absolute_rule_identity(model):
    for h in model.hypotheses.values():
        assert not {'fen','square','piece_id','source_game','attacker_id'}&set(h['descriptor'])

@pytest.mark.parametrize('mode',['fen-only','trusted-metadata','event-backed'])
def test_temporal_modes_and_scope(mode):
    before='7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1';p=Position.from_fen(before);after=p.successor(find_move(p,'b7b5')).fen()
    e=None if mode=='fen-only' else {'source':'test-events','confidence':.8,'initial_fen':before,'moves':['b7b5']}
    r=inspect(after,mode,e)
    assert r==inspect(after,mode,e)
    assert r['ep_truth_value']['confidence']==(0 if mode=='fen-only' else .8)
    if mode=='event-backed':assert r['castle_truth_value']['confidence']==0 and len(r['events'])==1

def test_temporal_conflict_truncation_and_missing():
    fen='6k1/8/8/8/8/8/8/4K2R w K - 0 1'
    assert inspect(fen,'event-backed',{'source':'x','initial_fen':fen,'moves':[]})['status']=='truncated'
    assert inspect(fen,'event-backed',{'source':'x','initial_fen':fen,'moves':['e1f1']})['status']=='conflicting'
    with pytest.raises(ValueError):inspect(fen,'event-backed',{'source':'x'})
    with pytest.raises(ValueError):inspect(fen,'trusted-metadata',{})
    with pytest.raises(ValueError):transform_evidence({'source':'x'},'reflection')

@pytest.mark.parametrize('confidence',[float('nan'),float('inf'),-1,1,True])
def test_invalid_history_reliability(confidence):
    with pytest.raises(ValueError):inspect(FEN,'trusted-metadata',{'source':'x','confidence':confidence})

def test_fen_castle_regression(model,runtime):
    fen='3qk2r/1bp1ppbp/2p3Nn/p1n1P3/P5p1/1P1P4/1R2BPPP/2B1K2R w K - 6 25'
    c=candidate(model,runtime,fen,'e1g1');assert c['classification']=='unknown'
    assert c['temporal_evidence']['mode']=='fen-only'

def test_cache_full_proof_parity_and_history_isolation(model,runtime):
    p=Position.from_fen(FEN);moves=[find_move(p,'f6h5')];session=Session(runtime)
    a=infer_moves(p,model,runtime=runtime,selected_moves=moves,optimized=False)
    b=infer_moves(p,model,runtime=runtime,selected_moves=moves,session=session)
    c=infer_moves(p,model,runtime=runtime,selected_moves=moves,session=session)
    assert a['candidates']==b['candidates']==c['candidates'] and c['native_invocations']==0
    d=infer_moves(p,model,Cycle5Options(temporal_mode='trusted-metadata',temporal_evidence={'source':'new','confidence':.7}),runtime,moves,session)
    assert d['cache_scope']!=c['cache_scope'] and d['native_invocations']>0

def test_budget_and_runtime_failure_are_incomplete(model,runtime,monkeypatch):
    assert candidate(model,runtime,options=Cycle5Options(max_native_invocations=0))['classification']=='incomplete'
    def fail(*args,**kwargs):raise NativeError('Deliberate unavailable native dependency')
    monkeypatch.setattr(runtime,'batch',fail)
    assert candidate(model,runtime)['classification']=='incomplete'

def test_stricter_thresholds_never_reveal_positive(model,runtime):
    fen='k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1'
    for c in (.15,.25,.5,.75):
        item=candidate(model,runtime,fen,'e3f3',Cycle5Options(min_confidence=c))
        assert item['classification'] in ('contradicted','unknown')

def test_counterfactual_exposure_removal(model,runtime):
    r=counterfactual('k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1','e3f3',model,runtime=runtime)
    assert r['before']['candidates'][0]['classification']=='contradicted'
    assert r['without']['exposure']['candidates'][0]['classification']=='unknown'
    assert all(x['candidates'][0]['classification']!='supported' for x in r['without'].values())

def test_replay_idempotency_retraction_and_conflict(model,tmp_path,runtime):
    rows=read_json(OUT/'datasets/dataset.json')['factorial_evidence'][:4];ledger=Ledger(tmp_path/'evidence.jsonl')
    a=train(rows,model.base_model(),runtime,ledger.path);b=train(rows,model.base_model(),runtime,ledger.path)
    assert a.version==b.version and len(ledger.records())==4
    assert all(len(h['evidence_ids'])==1 for h in a.hypotheses.values())
    rolled=train(ledger,model.base_model(),runtime,through_sequence=1)
    assert rolled.hypotheses==a.hypotheses
    removed=train(ledger,model.base_model(),runtime,retract_groups=[rows[0]['dependence_group']]);assert not removed.hypotheses
    payload=copy.deepcopy(rows[0]);payload['source']='new-independent';payload['dependence_group']='new-independent';payload['targets'][0]['label']=False
    ledger.append(payload,'fixed-id');bad=copy.deepcopy(payload);bad['source']='different'
    with pytest.raises(ValueError,match='Idempotency'):ledger.append(bad,'fixed-id')
    conflict=train(ledger,model.base_model(),runtime)
    assert any(h['supporting_evidence'] and h['contradicting_evidence'] for h in conflict.hypotheses.values())

def test_leakage_audit_detects_transformed_ancestry():
    from training.cycle5 import audit_leakage
    d=read_json(OUT/'datasets/dataset.json');train=d['factorial_train'];test=copy.deepcopy(d['factorial_test'])
    assert d['leakage_audit']['factorial_passed']
    test[0]['transformation_lineage']=[train[0]['dependence_group']]
    assert not audit_leakage(train,test,[])['factorial_passed']

def test_native_composition_probe():
    from evaluation.cycle5_native import audit
    r=audit();assert 'independent-geometry-destination ())' in r['raw']
    assert any('0.8402599999999999' in x['output'] for x in r['records'] if x['id']=='curried-supplied-rule')

def test_production_no_oracle_import(model,tmp_path):
    path=tmp_path/'m.json';model.export(path)
    code='''import sys
class Block:
 def find_spec(self,name,*args):
  if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('Oracle import '+name)
sys.meta_path.insert(0,Block())
from pln_chess.api import explain_move
result=explain_move(sys.argv[2],'f6h5',sys.argv[1])
assert result['candidate']['classification']=='unknown'
'''
    r=subprocess.run([sys.executable,'-c',code,str(path),FEN],capture_output=True,text=True)
    assert r.returncode==0,r.stderr

def test_event_backed_ep_enables_scoped_observation(model,runtime):
    before='7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1';p=Position.from_fen(before);after=p.successor(find_move(p,'b7b5')).fen()
    a=candidate(model,runtime,after,'c5b6')
    b=candidate(model,runtime,after,'c5b6',Cycle5Options(temporal_mode='event-backed',temporal_evidence={'source':'event','confidence':.99,'initial_fen':before,'moves':['b7b5']}))
    assert not a['observations']['complete'] and b['observations']['complete']
    assert b['classification']!='supported' and b['temporal_evidence']['castle_truth_value']['confidence']==0

def test_inspector_c5_contract(model,runtime,monkeypatch,tmp_path):
    from pln_chess.cli import web
    # Fixture root preserves the actual model dispatch without requiring a
    # generated model in the source checkout during a clean experiment run.
    root=tmp_path/'root';model.export(root/'artifacts/cycle5/model/C5-full.json');model.base_model().export(root/'artifacts/cycle4/model/C4-full.json')
    monkeypatch.setattr(web,'ROOT',root)
    r=web.inspector_infer({'model':'C5-full','fen':FEN,'move':'f6h5','compare':True})
    assert set(r['comparisons'])=={'C4-full','C5-full'}
    assert r['comparisons']['C5-full']['candidate']['proof_plan']['native_conjunction']=='unsupported'
    r=web.inspector_infer({'model':'C5-full','fen':FEN,'move':'f6h5','max_invocations':0})
    assert r['candidate']['classification']=='incomplete'
    r=web.inspector_infer({'model':'default','fen':FEN,'move':'f6h5','max_invocations':0},root/'artifacts/cycle5/model/C5-full.json')
    assert r['candidate']['classification']=='incomplete'
    with pytest.raises(ValueError):web.inspector_infer({'model':'C5-full','fen':'malformed','move':'f6h5'})

def test_batch_temporal_mode(model,runtime):
    from pln_chess.api import analyze_batch
    r=analyze_batch([{'fen':FEN,'move':'f6h5','temporal_mode':'trusted-metadata','temporal_evidence':{'source':'x','confidence':.7}}],model,runtime=runtime)
    assert r['results'][0]['temporal_evidence']['mode']=='trusted-metadata'
