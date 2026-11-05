"""Cycle 3 production boundaries, adversaries, state uncertainty and proof parity."""
import builtins,copy,json
from dataclasses import replace
import pytest
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.api import explain_move,find_move,import_model
from pln_chess.domain import Position,Piece
from pln_chess.hypotheses import candidates
from pln_chess.evidence import Ledger
from pln_chess.pln import NativeError
from pln_chess.cycle3.descriptors import descriptors,relation
from pln_chess.cycle3.model import RelationalModel,observe_example,train
from pln_chess.cycle3.inference import infer_moves,Cycle3Options
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle3.counterfactual import compare
from pln_chess.cycle3.history import observe_transition
from pln_chess.spatial import color_flip,translate

FEN='8/6k1/8/8/8/2R5/2K5/8 w - - 0 1'

@pytest.fixture(scope='module')
def full(runtime):return RelationalModel.load(ROOT/'artifacts/cycle3/C3-full-model.json',runtime)

@pytest.fixture(scope='module')
def learned(runtime,tmp_path_factory):
    ledger=tmp_path_factory.mktemp('c3')/'evidence'
    for fen,label,group in [(FEN,True,'clear'),(FEN.replace('2R5','2RP4'),False,'block')]:
        observe_example(fen,'c3e3',label,'test',group,ledger,runtime)
    return train(Ledger(ledger),runtime=runtime)


@pytest.mark.parametrize('distance,blocker',[(3,1),(4,2),(5,3)])
def test_three_independent_blocker_transfers(learned,runtime,distance,blocker):
    # Different locations and opponent constellations; distances never trained.
    p=Position.from_fen('8/8/7k/8/8/8/R7/1K6 w - - 0 1')
    p=replace(p,pieces=p.pieces+(Piece('block','Pawn','White',(blocker,1)),Piece('extra','Knight','Black',(6,distance))))
    move=next(m for m in candidates(p) if m.start==(0,1) and m.end==(distance,1))
    c=explain_move(p,move,learned,runtime=runtime)['candidate']
    assert c['classification']=='contradicted'
    assert learned.hypotheses[c['chosen_hypothesis_id']]['tier']==4
    assert not any(r['tier']==6 for r in c['observations']['relations'])


@pytest.mark.parametrize('transform,notation',[(lambda p:translate(p,(1,0)),'d3f3'),(color_flip,'c6e6')])
def test_relative_conditions_invariant(learned,runtime,transform,notation):
    p=Position.from_fen(FEN);a=explain_move(p,'c3e3',learned,runtime=runtime)['candidate']
    b=explain_move(transform(p),notation,learned,runtime=runtime)['candidate']
    assert a['legal_move_truth_value']==b['legal_move_truth_value'] and a['matched_rule_ids']==b['matched_rule_ids']


def test_ontology_contains_no_coordinate_identifiers(full):
    banned={'position_id','candidate_id','attacker_id','king_id','square','fen','postmove_opponents'}
    def check(x):
        if isinstance(x,dict):
            assert not banned&x.keys()
            for v in x.values():check(v)
        elif isinstance(x,list):
            for v in x:check(v)
    for h in full.hypotheses.values():check(h['descriptor'])


@pytest.mark.parametrize('name', ['orthogonal-pin-Rook','orthogonal-pin-Bishop','orthogonal-pin-Queen','orthogonal-pin-Knight','orthogonal-pin-Pawn',
                                  'diagonal-pin-Rook','diagonal-pin-Bishop','diagonal-pin-Queen','diagonal-pin-Knight','diagonal-pin-Pawn',
                                  'double-check','check-block','checking-piece-capture','king-capture-protected','king-escape',
                                  'castle-transit','castle-origin','castle-final','ep-opening-ray'])
def test_adversarial_full_sets_have_no_false_safety_claim(full,runtime,name):
    import chess
    fixture=next(p for p in read_json(ROOT/'artifacts/cycle3/dataset.json')['positions'] if p['id']=='challenge-'+name)
    expected={m.uci() for m in chess.Board(fixture['fen']).legal_moves}
    result=infer_moves(fixture['fen'],full,runtime=runtime)
    assert not result['truncated']
    assert {c['move'] for c in result['candidates'] if c['classification']=='supported'}<=expected
    assert all(c['status']!='native-compositional' for c in result['candidates'])


def test_all_23_frozen_errors_resolved_without_oracle(full,runtime,monkeypatch):
    from evaluation.cycle3 import read_gzip
    baseline=read_gzip(ROOT/'artifacts/cycle3/baseline-B1-heldout-transfer.json.gz')
    errors=[r for r in baseline['rows'] if r['self_check'] and not r['label'] and r['classification']=='supported']
    assert len(errors)==23
    original=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('Oracle leak')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guarded)
    for row in errors:
        c=explain_move(row['fen'],row['move'],full,runtime=runtime)['candidate']
        assert c['classification'] in ('unknown','contradicted') and c['proof_trace']


def test_attack_chain_evidence_pools_are_disjoint(full):
    attack={e for h in full.hypotheses.values() if h['target']=='Attack' for e in h['evidence_ids']}
    a=set(full.hypotheses[relation(4,{'edge':'Attack-to-Exposure'},'Bridge')['id']]['evidence_ids'])
    b=set(full.hypotheses[relation(4,{'edge':'Exposure-to-NotLegal'},'Bridge')['id']]['evidence_ids'])
    assert a and b and attack and not (a&b or a&attack or b&attack)


def test_no_attack_hypothesis_does_not_infer_safety(learned,runtime):
    c=explain_move(FEN,'c3e3',learned,runtime=runtime)['candidate']
    assert any(a['origin']=='unlearned' for a in c['attack_beliefs'])
    assert all('Safe' not in t['conclusion'] for t in c['proof_trace'])
    assert c['status']=='native-partial'


@pytest.mark.parametrize('kind',['squares','ownership','duplicate','king'])
def test_incomplete_and_contradictory_state_abstains(learned,runtime,kind):
    p=Position.from_fen(FEN)
    if kind=='squares':p=replace(p,unknown_squares=((3,2),))
    if kind=='ownership':p=replace(p,pieces=p.pieces+(Piece('uncertain','Pawn','Unknown',(4,5)),))
    if kind=='duplicate':p=replace(p,pieces=p.pieces+(replace(p.pieces[0],id='duplicate'),))
    if kind=='king':p=replace(p,pieces=tuple(x for x in p.pieces if x.kind!='King' or x.owner!='White'))
    c=explain_move(p,'c3e3',learned,runtime=runtime)['candidate']
    assert c['classification']=='unknown' and not c['proof_trace']


def test_known_unknown_contradictory_ep_history(runtime,tmp_path):
    before='7k/3p4/8/2P5/8/8/8/K7 b - - 0 1'
    after='7k/8/8/2Pp4/8/8/8/K7 w - d6 0 2'
    p,receipt=observe_transition(after,before,'d7d5');assert receipt['id'] and p.history_known
    with pytest.raises(ValueError,match='Contradictory'):observe_transition(after,before,'d7d6')
    ledger=tmp_path/'ep';observe_example(p,'c5d6',True,'explicit predecessor','ep',ledger,runtime)
    model=train(Ledger(ledger),runtime=runtime)
    known=explain_move(p,'c5d6',model,runtime=runtime)['candidate']
    unknown=explain_move(after,'c5d6',model,runtime=runtime)['candidate']
    contradiction=explain_move(p,'c5d6',model,Cycle3Options(history_consistency='contradictory'),runtime)['candidate']
    assert known['classification']=='supported'
    assert unknown['classification']==contradiction['classification']=='unknown'


def test_four_promotions_are_scored_independently(full,runtime):
    fen='8/3P2k1/8/8/8/8/8/1K6 w - - 0 1'
    result=infer_moves(fen,full,runtime=runtime)
    items=[c for c in result['candidates'] if c['move'].startswith('d7d8')]
    assert {i['move'][-1] for i in items}==set('qrbn')
    assert all(i['proof_trace'] and i['chosen_hypothesis_id'] for i in items)


@pytest.mark.parametrize('budget',[Cycle3Options(max_native_invocations=0),Cycle3Options(max_proof_bytes=0),Cycle3Options(timeout_seconds=.000001)])
def test_budgets_are_explicitly_incomplete(learned,runtime,budget):
    r=explain_move(FEN,'c3e3',learned,budget,runtime)
    assert r['truncated'] and r['candidate']['classification']=='incomplete'


def test_native_timeout_keeps_no_false_conclusion(learned,runtime,monkeypatch):
    def fail(nodes):raise NativeError('timeout')
    monkeypatch.setattr(runtime,'batch',fail)
    r=explain_move(FEN,'c3e3',learned,runtime=runtime)
    assert r['truncated'] and r['candidate']['classification']=='incomplete'


def test_cache_parity_and_invalidation(learned,runtime):
    p=Position.from_fen(FEN);moves=[find_move(p,'c3e3'),find_move(p,'c3f3')];session=NativeSession(runtime)
    a=infer_moves(p,learned,runtime=runtime,selected_moves=moves,optimized=False)
    b=infer_moves(p,learned,runtime=runtime,selected_moves=moves,session=session)
    c=infer_moves(p,learned,runtime=runtime,selected_moves=moves,session=session)
    assert a['candidates']==b['candidates']==c['candidates'] and c['native_invocations']==0
    for other in [replace(learned,variant='no-arbitration'),replace(learned,ledger_digest='new-evidence'),replace(learned,ledger_digest='rollback')]:
        previous=session.invalidations
        d=infer_moves(p,other,runtime=runtime,selected_moves=moves,session=session)
        assert session.invalidations>previous and d['native_invocations']>0
    assert len(session.cache)<=session.max_entries


def test_runtime_manifest_and_cache_bound(runtime):
    session=NativeSession(runtime,max_entries=1);nodes=[('a','(Truth_Negation (stv 0.1 0.5))'),('b','(Truth_Negation (stv 0.2 0.5))')]
    a=session.batch(nodes);assert len(session.cache)==1
    original=copy.deepcopy(runtime.manifest)
    try:
        runtime.manifest['test-scope']='changed';calls=session.calls
        assert session.batch(nodes)==a and session.calls>calls
    finally:runtime.manifest=original


def test_schema_migration_requires_replay(full,tmp_path,runtime):
    path=tmp_path/'model';full.export(path);assert import_model(path).version==full.version
    d=read_json(path);d['schema']=2;write_json(path,d)
    with pytest.raises(ValueError):import_model(path)
    assert import_model(ROOT/'artifacts/cycle2/B1-model.json').schema==2


def test_ledger_conflict_replay_rollback_corruption(runtime,tmp_path):
    ledger=tmp_path/'events';observe_example(FEN,'c3e3',True,'test','g1',ledger,runtime,idempotency_key='first')
    original=train(Ledger(ledger),runtime=runtime)
    with pytest.raises(ValueError,match='Idempotency'):observe_example(FEN,'c3e3',False,'test','g1',ledger,runtime,idempotency_key='first')
    observe_example(FEN,'c3e3',False,'test','g2',ledger,runtime)
    conflict=train(Ledger(ledger),runtime=runtime)
    assert any(h['positive']['strength']==pytest.approx(.5) for h in conflict.hypotheses.values() if h['target']=='LegalMove')
    assert train(Ledger(ledger),options={'through_sequence':1},runtime=runtime).version==original.version
    assert train(Ledger(ledger),runtime=runtime).version==conflict.version
    d=json.loads(ledger.read_text().splitlines()[0]);d['payload']['label']=False;ledger.write_text(json.dumps(d)+'\n')
    with pytest.raises(ValueError,match='hash'):Ledger(ledger).records()


@pytest.mark.parametrize('confidence',[0,.001])
def test_low_confidence_observation_never_decisive(runtime,tmp_path,confidence):
    ledger=tmp_path/'weak';observe_example(FEN,'c3e3',True,'weak','g',ledger,runtime,observation_confidence=confidence)
    m=train(Ledger(ledger),runtime=runtime)
    assert explain_move(FEN,'c3e3',m,runtime=runtime)['candidate']['classification']=='unknown'


def test_counterfactual_uses_real_native_results(learned,runtime):
    r=compare(FEN,'c3e3',learned,'add-blocker','d3',runtime=runtime)
    assert r['before']['candidate']['classification']=='supported'
    assert r['after']['candidate']['classification']=='contradicted' and r['rules_added']


def test_inspector_cycle3_contract(full,runtime):
    from pln_chess.cli.web import inspector_infer
    a=inspector_infer({'fen':FEN,'move':'c3e3'},full)
    b=explain_move(FEN,'c3e3',full,runtime=runtime)
    assert a['candidate']==b['candidate']
    assert a['candidate']['condition_beliefs']


def test_comparison_keeps_server_checkpoint_selected(full):
    from pln_chess.cli.web import inspector_infer
    result=inspector_infer({'fen':FEN,'move':'c3e3','compare':True},full)
    assert result['comparisons']['default']['model_version']==full.version
    assert result['comparisons']['default']['candidate']['condition_beliefs']


def test_native_composition_boundary():
    from evaluation.cycle3_native import audit
    r=audit();assert r['records'] and 'independent-premises ())' in r['raw']


def test_dataset_hash_families_and_candidate_completeness():
    import chess
    d=read_json(ROOT/'artifacts/cycle3/dataset.json');assert digest({k:v for k,v in d.items() if k!='hash'})==d['hash']
    assert not d['overlap_audit']['train_test_fen_overlap'] and not d['overlap_audit']['family_overlap']
    for p in d['positions']:
        b=chess.Board(p['fen']);assert b.is_valid()
        assert {m.uci() for m in b.legal_moves}<={m.notation for m in candidates(Position.from_fen(p['fen']))}
