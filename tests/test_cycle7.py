"""Scientific boundaries, conservative backoff, contracts and cache equivalence."""
from dataclasses import asdict, replace
import copy
import pytest
from pln_chess.common import ROOT, read_json, digest, write_json
from pln_chess.pln import Runtime, TV
from pln_chess.learning import Model
from pln_chess.api import find_move
from pln_chess.domain import Position
from pln_chess.cycle6.inference import infer_moves as before, Cycle6Options
from pln_chess.cycle7.model import BackoffModel, key, projection
from pln_chess.cycle7.inference import infer_moves, Cycle7Options, Session, default_mode, proof_category

POS='7k/8/8/8/8/8/2R5/2K5 w - - 0 1'
BLOCK='7k/8/8/8/8/8/2RP4/2K5 w - - 0 1'
KNIGHT='2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1'

@pytest.fixture(scope='module')
def rt():return Runtime(timeout=180)
@pytest.fixture(scope='module')
def model(rt):return BackoffModel.migrate(Model.load(ROOT/'artifacts/cycle6/model/C6-full.json',rt))

@pytest.mark.parametrize('mode',['operational','strict','experimental'])
@pytest.mark.parametrize('fen,move',[(POS,'c2e2'),(BLOCK,'c2h2'),(KNIGHT,'f6h5')])
def test_frozen_exact_proof_and_classification(model,rt,mode,fen,move):
    p=Position.from_fen(fen);m=find_move(p,move)
    a=before(p,model.source_model(),Cycle6Options(mode=mode),rt,[m])['candidates'][0]
    b=infer_moves(p,model,Cycle7Options(mode=mode),rt,[m])['candidates'][0]
    assert a['classification']==b['classification'] and a['raw_stv']==b['raw_stv']
    assert a['proof_trace']==b['proof_trace'] and b['legacy_proof_status']==a['proof_status']
    assert b['proof_status']!='native-compositional' and not b['positive_proof_complete']
    assert b['proof_status']==('negative-supported' if a['classification']=='supported-illegal' else 'learned-conditional' if a['classification']=='supported-legal' else 'unknown')

@pytest.mark.parametrize('mode',['operational','strict','experimental'])
def test_budget_and_cache_parity(model,rt,mode):
    p=Position.from_fen(POS);m=find_move(p,'c2e2');o=Cycle7Options(mode=mode);s=Session(rt)
    a=infer_moves(p,model,o,rt,[m],optimized=False)
    b=infer_moves(p,model,o,rt,[m],s);c=infer_moves(p,model,o,rt,[m],s)
    assert a['candidates']==b['candidates']==c['candidates'] and c['native_invocations']==0
    limited=infer_moves(p,model,replace(o,max_native_invocations=0),rt,[m],s)
    assert limited['truncated'] and limited['candidates'][0]['proof_status']=='incomplete'

def test_model_integrity_and_lossless_migration(model,rt,tmp_path):
    p=tmp_path/'m.json';model.export(p);loaded=BackoffModel.load(p,rt)
    assert loaded.version==model.version and loaded.source_model().version==model.source_model().version
    d=read_json(p);d['source']['policy']='fabricated';write_json(p,d)
    with pytest.raises(ValueError):BackoffModel.load(p,rt)

def test_projection_does_not_encode_squares():
    d={'piece':'Knight','motion':[1,2],'destination':'Opponent','ray_contents':['Friendly'],'effect':'ordinary','promotion':None}
    assert projection(d,0)==d
    assert projection(d,1)=={k:v for k,v in d.items() if k!='ray_contents'}
    assert projection(d,2)=={k:v for k,v in d.items() if k not in ('ray_contents','destination')}
    with pytest.raises(ValueError):projection(d,3)

def synthetic(model,rt,fen,move):
    from pln_chess.cycle4.ontology import descriptors
    changed=copy.deepcopy(model);p=Position.from_fen(fen);m=find_move(p,move)
    d=descriptors(p,m)['local_context'];k=key(d,1)
    tv=rt.batch([('r','(Truth_Revision (stv 0.5 0.05) (stv 1.0 0.9))')])['r'].json()
    negative=rt.batch([('n',f'(Truth_Negation {TV.from_json(tv).metta()})')])['n'].json()
    changed.hypotheses[k]={'id':k,'descriptor':projection(d,1),'level':1,'positive':tv,'negative':negative,
        'evidence_ids':['synthetic-positive'],'dependence_groups':['synthetic-positive'],'supporting_evidence':['synthetic-positive'],
        'contradicting_evidence':[],'new_training':True}
    return changed,p,m

def test_coarse_rule_never_overrides_existing_specific_evidence(model,rt):
    changed,p,m=synthetic(model,rt,BLOCK,'c2h2')
    c=infer_moves(p,changed,Cycle7Options(mode='operational'),rt,[m])['candidates'][0]
    assert c['classification']=='supported-illegal'

@pytest.mark.parametrize('mode',['strict','experimental'])
def test_backoff_cannot_enable_strict_positives(model,rt,mode):
    changed,p,m=synthetic(model,rt,KNIGHT,'f6h5')
    c=infer_moves(p,changed,Cycle7Options(mode=mode),rt,[m])['candidates'][0]
    assert c['classification']=='unknown' and c['backoff']['level']=='none'

def test_backoff_has_explicit_lineage_and_is_not_compositional(model,rt):
    changed,p,m=synthetic(model,rt,KNIGHT,'f6h5')
    c=infer_moves(p,changed,Cycle7Options(mode='operational'),rt,[m])['candidates'][0]
    assert c['backoff']['level']=='ray-contents-masked' and c['backoff']['host_projection']
    assert c['backoff']['lineage']==['synthetic-positive'] and not c['positive_proof_complete']
    assert c['proof_status'] in ('learned-conditional','unknown','negative-supported')
    no=infer_moves(p,changed,Cycle7Options(mode='operational',backoff=False),rt,[m])['candidates'][0]
    assert no['classification']=='unknown' and no['backoff']['level']=='none'

def test_no_oracle_import_in_production(model,rt,monkeypatch):
    import builtins
    original=builtins.__import__
    def blocked(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError(name)
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',blocked)
    p=Position.from_fen(POS)
    assert infer_moves(p,model,Cycle7Options(mode='operational'),rt,[find_move(p,'c2e2')])['candidates'][0]['classification']=='supported-legal'

def test_default_fails_closed_without_receipt(model,tmp_path,monkeypatch):
    monkeypatch.setenv('C7_OUT',str(tmp_path));assert default_mode(model)=='strict'
    write_json(tmp_path/'acceptance.json',{'passed':True,'accepted_model_versions':[model.version]})
    assert default_mode(model)=='strict'

def test_native_joint_introduction_missing_and_choice_not_conjunction(rt):
    raw=rt.execute('!(println! (JOINT (collapse (|- (A (stv 0.9 0.8)) (B (stv 0.9 0.8))))))')
    assert '(JOINT ())' in raw
    value=rt.batch([('pick','(let ($tv $e) (BestConfidenceCandidate (((stv 0.9 0.7) (A)) ((stv 0.1 0.8) (B)))) $tv)')])['pick']
    assert value==TV(.1,.8)

def test_native_typed_inheritance_signature(rt):
    correct='(collapse (|- ((Evaluation (Predicate Eligible) (List (Concept B))) (stv 0.9 0.8)) ((Inheritance (Concept A) (Concept B)) (stv 0.95 0.8))))'
    wrong='(collapse (|- ((Evaluation Eligible B) (stv 0.9 0.8)) ((Inheritance A B) (stv 0.95 0.8))))'
    raw=rt.execute(f'!(println! (TYPED {correct}))\n!(println! (UNTYPED {wrong}))')
    # The rule is source-present, but neither exact probe executes in the pinned runtime.
    assert '(TYPED ())' in raw and '(UNTYPED ())' in raw

def test_native_duplicate_stamp_and_zero_confidence(rt):
    raw=rt.execute('!(println! (DUP (collapse (if (StampDisjoint (shared) (shared)) (Truth_Revision (stv 1.0 0.8) (stv 1.0 0.8)) (empty)))))')
    assert '(DUP ())' in raw
    assert rt.batch([('zero','(Truth_ModusPonens (stv 1.0 0.0) (stv 1.0 0.8))')])['zero'].confidence==0

def test_disjoint_deterministic_game_families():
    from training.cycle7 import generate
    d=generate();assert digest(d)==digest(generate())
    a={p['family'] for p in d['positions'] if p['split']=='train'};b={p['family'] for p in d['positions'] if p['split']!='train'}
    assert not a&b and len([p for p in d['positions'] if p['split']=='independent-games'])==32
    assert not d['leakage']['position_symmetry_overlap']

@pytest.fixture(scope='module')
def operator_inventory():
    from evaluation.cycle7_native import Recorder,inventory
    return inventory(Recorder())

@pytest.mark.parametrize('operator',['mp','deduction','induction','abduction','revision','negation','inversion','equivalence','similarity','evaluation','symmetric-mp','choice'])
def test_operator_native_signature_and_source(operator_inventory,operator):
    row=next(r for r in operator_inventory['operators'] if r['id']==operator)
    assert len(row['stvs'])==1 and row['source'] and row['domain']
    assert '(stv ' in row['stdout'] and row['runtime_executable']
    TV.from_json(row['stvs'][0])
    assert all(d['definition'] in (ROOT/d['source']).read_text() for d in row['source'])

@pytest.mark.parametrize('case',['revision-zero','revision-one','choice-zero','inheritance-predicate'])
def test_native_undefined_and_unmatched_cases_are_not_fabricated(operator_inventory,case):
    row=next(r for r in operator_inventory['signature_and_edge_cases'] if r['id']==case)
    assert row['runtime_result_kind']=='empty' and row['stvs']==[]

def test_transform_preserves_backoff_selection_and_tv(model,rt):
    from pln_chess.spatial import color_flip
    from dataclasses import replace
    changed,p,m=synthetic(model,rt,KNIGHT,'f6h5')
    q=color_flip(p);mm=replace(m,start=(m.start[0],7-m.start[1]),end=(m.end[0],7-m.end[1]))
    a=infer_moves(p,changed,Cycle7Options(mode='operational'),rt,[m])['candidates'][0]
    b=infer_moves(q,changed,Cycle7Options(mode='operational'),rt,[mm])['candidates'][0]
    assert a['backoff']==b['backoff'] and a['raw_stv']==b['raw_stv'] and a['classification']==b['classification']

def test_frozen_supported_candidates_survive_even_adversarial_backoff(model,rt):
    changed,p,m=synthetic(model,rt,BLOCK,'c2h2')
    a=before(p,model.source_model(),Cycle6Options(mode='operational'),rt,[m])['candidates'][0]
    b=infer_moves(p,changed,Cycle7Options(mode='operational'),rt,[m])['candidates'][0]
    assert b['proof_trace']==a['proof_trace'] and b['classification']==a['classification']=='supported-illegal'

def test_public_api_and_batch_schema7(model,rt,tmp_path):
    from pln_chess.api import explain_move,analyze_batch
    from pln_chess.inference import infer_moves as public
    path=tmp_path/'model.json';model.export(path)
    loaded=Model.load(path,rt);assert loaded.version==model.version
    a=explain_move(POS,'c2e2',loaded,runtime=rt,mode='operational')
    assert a['schema']==7 and a['candidate']['proof_status']=='learned-conditional'
    r=analyze_batch([{'fen':POS,'move':'c2e2','mode':mode,'temporal_mode':'fen-only'} for mode in ('operational','strict','experimental')],loaded,runtime=rt)
    assert [x['candidate']['classification'] for x in r['results']]==['supported-legal','unknown','unknown']
    p=Position.from_fen(POS)
    strict=public(p,loaded,Cycle7Options(backoff=False),rt,[find_move(p,'c2e2')],mode='strict')
    assert strict['candidate']['classification']=='unknown' if 'candidate' in strict else strict['candidates'][0]['classification']=='unknown'

def test_inspector_comparison_contains_real_evidence(model):
    from pln_chess.cli.web import inspector_infer,HTML
    data=inspector_infer({'fen':POS,'move':'c2e2','mode':'operational','compare':True},model)
    assert data['native_proof_equal'] and set(data['comparisons'])=={'C6-operational','C7-operational'}
    for result in data['comparisons'].values():
        c=result['candidate'];assert c['evidence_ids'] and c['typed_premises'] and c['dependence_groups']
    assert 'C7-default' in HTML and 'comparisonExport' in HTML

def test_cli_cycle_comparison(model,tmp_path,capsys):
    from pln_chess.cli import main
    path=tmp_path/'m.json';model.export(path)
    assert main(['compare-cycles','--fen',POS,'--move','c2e2','--checkpoint',str(path)])==0
    import json
    value=json.loads(capsys.readouterr().out)
    assert value['schema']=='cycle-comparison-v7' and value['native_proof_equal']

def test_dependence_ablation_retains_real_provenance(model,rt):
    from evaluation.cycle6_research import conflicting_model
    from pln_chess.cycle5.ontology import relation
    from pln_chess.cycle4.ontology import relation as old_relation
    from pln_chess.cycle5.inference import infer_moves as premise_infer,Cycle5Options
    changed=conflicting_model(model.source_model(),rt).source_model()
    k=relation('ray',{'piece':'Rook','effect':'ordinary','occupancy':'Empty'},'RayObstruction')['id']
    bridge=changed.base['hypotheses'][old_relation('Bridge',{'edge':'Obstruction-to-NotLegal'})['id']]
    changed.hypotheses[k]['dependence_groups']+=bridge['dependence_groups']
    p=Position.from_fen(POS);m=find_move(p,'c2e2')
    safe=premise_infer(p,changed,Cycle5Options(),rt,[m])['candidates'][0]
    unsafe=premise_infer(p,changed,Cycle5Options(dependence_aware=False),rt,[m])['candidates'][0]
    assert safe['classification']=='unknown' and unsafe['classification']=='contradicted'
    assert any(x.get('bridge_overlap') for x in unsafe['typed_premises'])
def test_paired_bootstrap_mixed_game_ids_and_zero():
    from evaluation.cycle7_analysis import paired
    positions=[{'fixture':f'fixture-{i}','family':'control','source_game':game,
                'expected':['a2a3'],'predicted':['a2a3'],'exact':True}
               for i,game in enumerate((0,0,'0',None))]
    report={'dataset_hash':'same-locked-data','positions':positions,
            'rows':[{'fixture':p['fixture'],'move':'a2a3','label':True} for p in positions]}
    result=paired(report,report)
    assert result['cluster_count']==3
    assert result['recall_delta_95_percentile_interval']==[0.,0.]
    assert result['exact_set_delta_95_percentile_interval']==[0.,0.]
