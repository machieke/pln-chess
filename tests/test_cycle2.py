"""Cycle 2 metamorphic, statistical, provenance, budget, and parity regressions."""
from dataclasses import replace
import builtins,json,subprocess
import pytest
from pln_chess.common import ROOT,read_json,digest,write_json
from pln_chess.domain import Position
from pln_chess.api import find_move,explain_move,import_model,export_model
from pln_chess.cycle2.descriptors import descriptors
from pln_chess.cycle2.model import train,observe_example,HierarchicalModel
from pln_chess.cycle2.inference import infer_moves
from pln_chess.cycle2.native import NativeSession
from pln_chess.evidence import Ledger
from pln_chess.inference import Options
from pln_chess.pln import NativeError,TV
from pln_chess.spatial import translate,color_flip

FEN='8/6k1/8/8/8/2R5/2K5/8 w - - 0 1'

@pytest.fixture(scope='module')
def learned(tmp_path_factory,runtime):
    ledger=tmp_path_factory.mktemp('c2')/'evidence.jsonl'
    for fen,move,label,group in [(FEN,'c3e3',True,'clear'),(FEN.replace('2R5','2RP4'),'c3e3',False,'occupied'),
                                 (FEN.replace('2R5','2R1N3'),'c3e3',False,'friend'),(FEN.replace('2R5','2R1n3'),'c3e3',True,'opponent')]:
        observe_example(fen,move,label,'test-supervision',group,ledger,runtime)
    return train(Ledger(ledger),runtime=runtime)


def desc(fen,move):
    p=Position.from_fen(fen) if isinstance(fen,str) else fen
    return descriptors(p,find_move(p,move))


def test_irrelevant_opponent_preserves_local_belief(learned,runtime):
    other=FEN.replace('8/6k1','n7/6k1')
    a=explain_move(FEN,'c3e3',learned,runtime=runtime)['candidate'];b=explain_move(other,'c3e3',learned,runtime=runtime)['candidate']
    assert a['observations']['context']!=b['observations']['context']
    assert a['movement_hypothesis_id']==b['movement_hypothesis_id']
    assert a['movement_truth_value']==b['movement_truth_value']
    assert a['chosen_hypothesis_id']==b['chosen_hypothesis_id']
    assert b['classification']=='supported'

@pytest.mark.parametrize('move', ['c3f3','c3g3','c3h3'])
def test_unseen_ray_length_and_late_occupancy(learned,runtime,move):
    fen=FEN.replace('2R5','2R1P3')
    result=explain_move(fen,move,learned,runtime=runtime)['candidate']
    assert result['classification']=='contradicted'
    assert learned.hypotheses[result['chosen_hypothesis_id']]['tier']==4
    assert desc(fen,move)['ray_motifs']['first_nonempty']['step']==2

@pytest.mark.parametrize('occupant,classification',[('N','contradicted'),('n','supported')])
def test_destination_contrast_transfers(learned,runtime,occupant,classification):
    result=explain_move(FEN.replace('2R5','2R3'+occupant+'1'),'c3g3',learned,runtime=runtime)['candidate']
    assert result['classification']==classification

@pytest.mark.parametrize('transform,move',[(lambda p:translate(p,(1,0)),'d3f3'),(color_flip,'c6e6')])
def test_relative_native_invariance(learned,runtime,transform,move):
    p=Position.from_fen(FEN);other=transform(p)
    a=explain_move(p,'c3e3',learned,runtime=runtime)['candidate'];b=explain_move(other,move,learned,runtime=runtime)['candidate']
    assert a['legal_move_truth_value']==b['legal_move_truth_value']
    assert a['matched_rule_ids']==b['matched_rule_ids']


def test_unknown_observation_is_not_false_certainty(learned,runtime):
    p=Position.from_fen(FEN,unknown_squares=((3,2),))
    c=explain_move(p,'c3e3',learned,runtime=runtime)['candidate']
    assert c['classification']=='unknown' and c['legal_move_truth_value']['confidence']==0 and not c['proof_trace']


def test_unknown_castle_history_abstains(runtime):
    p=Position.from_fen('4k3/8/8/8/8/8/8/4K2R w K - 0 1',rights_known=False)
    c=explain_move(p,'e1g1',HierarchicalModel(runtime.version),runtime=runtime)['candidate']
    assert c['classification']=='unknown' and not c['proof_trace']


def test_dependence_contradiction_replay_and_rollback(runtime,tmp_path):
    ledger=tmp_path/'events.jsonl'
    a=observe_example(FEN,'c3e3',True,'test','family',ledger,runtime)
    assert observe_example(FEN,'c3e3',True,'test','family',ledger,runtime)['status']=='duplicate'
    original=train(Ledger(ledger),runtime=runtime)
    observe_example(FEN,'c3e3',False,'correlated','family',ledger,runtime)
    repeated=train(Ledger(ledger),runtime=runtime)
    assert original.hypotheses==repeated.hypotheses and repeated.training_report['excluded_updates']
    observe_example(FEN,'c3e3',False,'independent','another',ledger,runtime)
    conflict=train(Ledger(ledger),runtime=runtime)
    key=next(r['id'] for r in desc(FEN,'c3e3')['relations'] if r['tier']==4)
    assert conflict.hypotheses[key]['positive']['strength']==pytest.approx(.5)
    assert conflict.hypotheses[key]['positive']['confidence']>original.hypotheses[key]['positive']['confidence']
    assert train(Ledger(ledger),runtime=runtime).version==conflict.version
    assert train(Ledger(ledger),options={'through_sequence':1},runtime=runtime).version==original.version


def test_schema_integrity_and_runtime_mismatch(learned,runtime,tmp_path):
    path=tmp_path/'model.json';export_model(learned,path)
    assert import_model(path).version==learned.version
    data=read_json(path);data['variant']='tampered';write_json(path,data)
    with pytest.raises(ValueError,match='integrity'):HierarchicalModel.load(path,runtime)
    mismatch=replace(learned,runtime_version='other')
    with pytest.raises(ValueError,match='runtime'):infer_moves(FEN,mismatch,runtime=runtime)


def test_native_budget_and_timeout(learned,runtime,monkeypatch):
    r=explain_move(FEN,'c3e3',learned,Options(max_native_invocations=0),runtime)
    assert r['truncated'] and r['candidate']['classification']=='incomplete'
    def fail(nodes):raise NativeError('Native inference timed out')
    monkeypatch.setattr(runtime,'batch',fail)
    r=explain_move(FEN,'c3e3',learned,runtime=runtime)
    assert r['truncated'] and r['candidate']['classification']=='incomplete'


def test_optimized_reference_proof_parity(learned,runtime):
    p=Position.from_fen(FEN);selected=[find_move(p,'c3e3'),find_move(p,'c3f3')]
    ref=infer_moves(p,learned,runtime=runtime,selected_moves=selected,optimized=False)
    session=NativeSession(runtime);cold=infer_moves(p,learned,runtime=runtime,selected_moves=selected,session=session)
    warm=infer_moves(p,learned,runtime=runtime,selected_moves=selected,session=session)
    assert ref['candidates']==cold['candidates']==warm['candidates']
    assert cold['native_invocations']<ref['native_invocations'] and warm['native_invocations']==0


def test_cached_dependency_identity_and_evidence_not_fused(runtime):
    nodes=[('a','(Truth_Revision (stv 0.5 0.05) (stv 1.0 0.5))'),('b','(Truth_Revision (stv 0.5 0.05) (stv 1.0 0.5))'),
           ('c','(Truth_Negation (a))'),('d','(Truth_Negation (b))')]
    session=NativeSession(runtime);values=session.batch(nodes)
    assert values==runtime.batch(nodes) and session.calls==2
    assert session.batch(nodes)==values and session.calls==2


def test_production_inference_without_oracle(learned,runtime,monkeypatch):
    original=builtins.__import__
    def guard(name,*args,**kwargs):
        if name.split('.')[0] in ('chess','training','evaluation'):raise AssertionError('oracle leakage')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guard)
    assert explain_move(FEN,'c3e3',learned,runtime=runtime)['candidate']['classification']=='supported'


def test_negative_label_does_not_discredit_general_motion(runtime,tmp_path):
    ledger=tmp_path/'events';observe_example(FEN,'c3e3',False,'unknown reason','g',ledger,runtime)
    assert all(t['target']!='MovementPatternSupported' for t in Ledger(ledger).records()[0]['payload']['targets'])


def test_bulk_evidence_idempotency_matches_single(runtime,tmp_path):
    p=observe_example(FEN,'c3e3',True,'test','g',tmp_path/'single',runtime,_payload_only=True)
    a=Ledger(tmp_path/'bulk');assert a.append_many([p,p])[1]['status']=='duplicate'
    b=Ledger(tmp_path/'single');b.append(p)
    assert a.records()[0]['evidence_id']==b.records()[0]['evidence_id']
    assert a.append_many([p])[0]['status']=='duplicate'


def test_induction_counts_and_executable_result(runtime,tmp_path):
    ledger=tmp_path/'induction'
    for i,move in enumerate(['c3e3','c3e3','c3f3','c3f3','c3c4','c3c5']):
        observe_example(FEN,move,i!=5,'population',f'g{i}',ledger,runtime)
    model=train(Ledger(ledger),options={'induction':True},runtime=runtime)
    assert model.induction
    for key,ind in model.induction.items():
        counts=ind['counts'];assert counts['B']<=counts['A']<=counts['N'] and counts['BC']<=counts['C']
        s=' '.join(f'(stv {v!r} 0.5)' for v in ind['premises'])
        # Compare exact stored expression with its measured native confidence input.
        weight=runtime.batch([('c',f'(stv 1.0 (Truth_w2c {float(counts["B"])}))')])['c']
        s=' '.join(f'(stv {v!r} {weight.confidence!r})' for v in ind['premises'])
        assert runtime.batch([('i','(Truth_Induction '+s+')')])['i'].json()==ind['truth_value']
    c=explain_move(FEN,'c3e3',model,runtime=runtime)['candidate']
    assert any(h['origin']=='native-induction' for h in c['matched_hypotheses'])


def test_native_extended_audit(tmp_path):
    from evaluation.cycle2_native import audit
    result=audit(tmp_path/'probes.json')
    assert next(r for r in result['records'] if r['id']=='conjunction-introduction')['status']=='unsupported'
    assert next(r for r in result['records'] if r['id']=='measured-induction')['output']['confidence']>0


def test_cycle2_split_disjointness_and_hash():
    from training.cycle2 import generate
    d=generate();body={k:v for k,v in d.items() if k!='hash'}
    assert digest(body)==d['hash']
    assert all(not o['families'] and not o['games'] and not o['fens'] for o in d['overlap_audit'])
    assert len([p for p in d['positions'] if p['split']=='heldout-transfer'])==40
    assert all(not p['lineage'] for p in d['positions'] if p['split']=='heldout-transfer')


def test_public_representation_selector(learned,runtime):
    from pln_chess.api import infer_moves as public
    with pytest.raises(ValueError,match='representation'):public(FEN,learned,runtime=runtime,representation='full')
    assert public(FEN,learned,runtime=runtime,representation='hierarchical')['schema']==2


def test_inspector_uses_same_inference_contract(learned,runtime):
    from pln_chess.cli.web import inspector_infer
    a=inspector_infer({'fen':FEN,'move':'c3e3'},learned)
    b=explain_move(FEN,'c3e3',learned,runtime=runtime)
    assert a['candidate']==b['candidate'] and a['model_version']==b['model_version']
    with pytest.raises(ValueError,match='selector'):inspector_infer({'fen':FEN,'model':'../../file'},learned)


def test_all_reported_legal_moves_are_in_candidate_grammar():
    import chess
    from training.cycle2 import generate
    from pln_chess.hypotheses import candidates
    for row in generate()['positions']:
        bounded={m.notation for m in candidates(Position.from_fen(row['fen']))}
        assert {m.uci() for m in chess.Board(row['fen']).legal_moves}<=bounded,row['id']


def test_runtime_missing_source_and_hash_mismatch(runtime,tmp_path):
    from pln_chess.pln import Runtime
    missing=Runtime();missing.runner=tmp_path/'not-installed'
    with pytest.raises(NativeError,match='unavailable'):missing.verify()
    corrupt=Runtime();corrupt.library=tmp_path/'bad.metta';corrupt.library.write_text('modified')
    with pytest.raises(NativeError,match='hash'):corrupt.verify()


def test_obstruction_ablation_removes_all_movement_path_keys():
    a=desc(FEN,'c3e3');p=Position.from_fen(FEN.replace('2R5','2RP4'))
    b=descriptors(p,find_move(p,'c3e3'),'no-obstruction')
    c=descriptors(Position.from_fen(FEN),find_move(Position.from_fen(FEN),'c3e3'),'no-obstruction')
    assert b['relations']==c['relations']
    assert not any(r['tier'] in (2,6) for r in b['relations'])


def test_negative_auxiliary_label_does_not_assign_missing_cause(runtime,tmp_path):
    record=observe_example(FEN,'c3e3',False,'ambiguous','group',tmp_path/'e',runtime,movement_label=False,_payload_only=True)
    assert all(t['target']=='LegalMove' for t in record['targets'])


def test_missing_king_abstains(runtime,learned):
    # The structural parser permits incomplete scenes; inferred legality must not
    # turn a missing king into a zero-attacker safety claim.
    p=Position.from_fen('8/6k1/8/8/8/2R5/8/8 w - - 0 1')
    result=explain_move(p,'c3e3',learned,runtime=runtime)['candidate']
    assert result['classification']=='unknown'


def test_slider_training_mask_holds_out_ray_lengths():
    from training.cycle2 import generate
    from pln_chess.spatial import geometry
    d=generate();withheld=0
    for row in d['examples']:
        if row['split']!='train':continue
        p=Position.from_fen(row['fen']);m=find_move(p,row['move'])
        if p.at(m.start).kind in ('Rook','Bishop','Queen'):
            length=geometry(m.start,m.end)['distance']
            assert row['training_eligible']==(length<=2)
            withheld+=not row['training_eligible']
    assert withheld>500


def test_exact_counterevidence_cannot_be_ignored(runtime,tmp_path):
    ledger=tmp_path/'context-conflict'
    for i in range(8):observe_example(FEN,'c3e3',True,'positive',f'g{i}',ledger,runtime)
    other=FEN.replace('8/6k1','n7/6k1')
    observe_example(other,'c3e3',False,'specific counterexample','specific',ledger,runtime)
    model=train(Ledger(ledger),runtime=runtime)
    result=explain_move(other,'c3e3',model,runtime=runtime)['candidate']
    assert result['legal_move_truth_value']['strength']>.8
    assert result['classification']=='unknown'
    assert any(model.hypotheses[key]['tier']==6 for key in result['conflicting_hypotheses'])
