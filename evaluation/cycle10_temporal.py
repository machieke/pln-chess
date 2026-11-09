"""Temporal counterfactuals and exhaustive historical abstention interventions.

Synthetic predecessor reconstruction is explicitly a new controlled input, never
a recovery of an unobserved historical event in the original fixture.
"""
import argparse
from collections import Counter
from dataclasses import replace
from pathlib import Path
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def reference(fen,move):
    try:return chess.Move.from_uci(move) in chess.Board(fen).legal_moves
    except ValueError:return False


def run(out):
    from pln_chess.cycle10.temporal import replay,native_options,replay_game
    out=Path(out);rt=Runtime(timeout=180);model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    def transport(fen,moves,source,trust='unknown',expected=None):
        return replay(fen,moves,source=source,dependence_group=source,confidence=.99,initial_trust=trust,
            complete=False,model_version=model.version,runtime_version=rt.version,expected_fen=expected)
    def query(fen,move,history=None,suppressed=False):
        p=Position.from_fen(fen);m=find_move(p,move)
        if m is None:raise ValueError('Counterfactual move outside structural grammar')
        options=Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180,
                              suppress_families=('temporal',) if suppressed else ())
        if history:options=native_options(history,options)
        result=infer_moves(p,model,options,rt,[m]);assert not result['truncated']
        candidate=result['candidates'][0];assert not candidate['positive_proof_complete']
        return dict(candidate=candidate,expected_legal=reference(fen,move),native_invocations=result['native_invocations'],
                    model_version=model.version,runtime_version=rt.version)
    initial='6k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1'
    keep=['b2c4','g8f8','c4b2','f8g8'];king=['e1f1','g8f8','f1e1','f8g8'];rook=['h1h2','g8f8','h2h1','f8g8'];queenrook=['a1a2','g8f8','a2a1','f8g8']
    ep='7k/5p2/8/6P1/8/8/8/K7 b - - 0 1';epmoves=['f7f5']
    scenarios=[
        ('kingside-complete-versus-unknown',initial,keep,'e1g1','complete-unknown'),
        ('queenside-complete-versus-unknown',initial,keep,'e1c1','complete-unknown'),
        ('king-return-does-not-restore-right',initial,king,'e1g1','fresh-rights'),
        ('rook-return-does-not-restore-right',initial,rook,'e1g1','fresh-rights'),
        ('queen-rook-return-does-not-restore-right',initial,queenrook,'e1c1','fresh-rights'),
        ('en-passant-observed-versus-unknown',ep,epmoves,'g5f6','complete-unknown'),
        ('en-passant-stale-history',ep,epmoves+['a1b1','h8g8','b1a1','g8h8'],'g5f6','fresh-ep'),
        ('conflicting-reported-history',ep,epmoves,'g5f6','conflict'),
        ('conflicting-castling-claims',initial,keep,'e1g1','castle-conflict'),
        ('castling-through-attack','5rk1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1',[],'e1g1','complete-unknown'),
        ('queenside-through-attack','3r2k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1',[],'e1c1','complete-unknown'),
        ('castling-in-check','4r1k1/8/8/8/8/8/1N6/R3K2R w KQ - 0 1',[],'e1g1','complete-unknown'),
        ('en-passant-exposes-king','7k/5p2/8/r5PK/8/8/8/8 b - - 0 1',epmoves,'g5f6','complete-unknown'),
    ]
    demonstrations=[]
    for name,fen,moves,move,comparison in scenarios:
        # Validate the controlled sequence offline. The transport itself has no reference engine.
        b=chess.Board(fen)
        for notation in moves:
            m=chess.Move.from_uci(notation);assert m in b.legal_moves,(name,notation);b.push(m)
        history=transport(fen,moves,'synthetic-demonstration/'+name,'trusted-import',b.fen(en_passant='fen'))
        final=history['resulting_fen'];left=query(final,move,history);right_fen=final;right_history=None
        if comparison=='fresh-rights':
            right_fen=replace(Position.from_fen(final),rights='KQ').fen()
            right_history=transport(right_fen,[],'synthetic-demonstration/'+name+'/fresh-attestation','trusted-import')
        elif comparison=='fresh-ep':
            right_history=transport(ep,epmoves,'synthetic-demonstration/'+name+'/fresh-double-step','unknown')
            right_fen=right_history['resulting_fen']
        elif comparison=='conflict':
            right_history=transport(ep,[],'synthetic-demonstration/'+name+'/conflicting-source','unknown',final)
        elif comparison=='castle-conflict':
            right_history=transport(initial,king,'synthetic-demonstration/'+name+'/conflicting-source','trusted-import',final)
        right=query(right_fen,move,right_history)
        assert chess.Board(final).board_fen()==chess.Board(right_fen).board_fen(),name
        control=query(final,move,history,True)
        demonstrations.append(dict(id=name,initial_state=fen,event_history=moves,resulting_state=final,
            source='synthetic-controlled-temporal-experiment',left=dict(fen=final,history=history,**left),
            right=dict(fen=right_fen,history=right_history,**right),removed_temporal_channel=control,
            identical_geometry=True,comparison=comparison))
    # All four promotion choices and capture underpromotions, with and without event observations.
    for capture in (False,True):
        start='4r2k/3P4/8/8/8/8/1K6/8 w - - 0 1' if capture else '7k/3P4/8/8/8/8/1K6/8 w - - 0 1'
        for choice in 'qrbn':
            move='d7e8'+choice if capture else 'd7d8'+choice;history=transport(start,[],'synthetic-promotion/'+str(capture)+choice)
            a=query(start,move,history);b=query(start,move)
            demonstrations.append(dict(id='capture-'*capture+'promotion-'+choice,initial_state=start,event_history=[],resulting_state=start,
                source='synthetic-controlled-temporal-experiment',left=dict(fen=start,history=history,**a),right=dict(fen=start,history=None,**b),
                identical_geometry=True,comparison='promotion-does-not-invent-history'))
    pack(out/'temporal/counterfactuals.json.xz',demonstrations)
    failures=[];unhandled=[]
    cohorts=[('cycle9',split,sorted((out/'baseline/evaluation').glob('operational-'+split+'-*.json.xz'))) for split in ('adversarial','special-moves')]
    cohorts.append(('cycle10','synthetic-adversarial',sorted((out/'evaluation').glob('frozen-operational-synthetic-adversarial-*.json.xz'))))
    for cohort,split,paths in cohorts:
        for path in paths:
            report=read_gzip(path)
            for row in report['rows']:
                if not row['label'] or row['classification']!='unknown':continue
                before=query(row['fen'],row['move']);assert before['candidate']['classification']==row['classification']
                assert before['candidate']['raw_stv']==row['truth_value']
                p=Position.from_fen(row['fen']);move=find_move(p,row['move'])
                if move.effect not in ('castle','en-passant'):
                    unhandled.append(dict(cohort=cohort,split=split,row=row,reason='Not a historical-eligibility intervention; preserve the original abstention.'))
                    continue
                if move.effect=='en-passant':
                    b=chess.Board(row['fen']);end=chess.square(chess.square_file(b.ep_square),chess.square_rank(b.ep_square)+(-1 if b.turn else 1))
                    start=chess.square(chess.square_file(end),6 if b.turn else 1);piece=b.piece_at(end)
                    assert piece and piece.piece_type==chess.PAWN
                    b.remove_piece_at(end);b.set_piece_at(start,piece);b.turn=not b.turn;b.ep_square=None
                    b.fullmove_number=max(1,b.fullmove_number-(1 if b.turn==chess.BLACK else 0));b.halfmove_clock=0
                    notation=chess.square_name(start)+chess.square_name(end)
                    assert chess.Move.from_uci(notation) in b.legal_moves
                    history=transport(b.fen(en_passant='fen'),[notation],'synthetic-predecessor-intervention/'+row['fixture'])
                    # Historical FEN counters sometimes cannot describe a legal predecessor (e.g. fullmove 1 after Black).
                    # Counter values are retained in the original and changed only in this explicitly new intervention.
                    after_fen=history['resulting_fen']
                    assert chess.Board(after_fen).board_fen()==chess.Board(row['fen']).board_fen()
                else:
                    history=transport(row['fen'],[],'explicit-castling-attestation/'+row['fixture'],'trusted-import');after_fen=row['fen']
                after=query(after_fen,row['move'],history);removed=query(after_fen,row['move'],history,True)
                unknown=query(after_fen,row['move'])
                counter=replace(Position.from_fen(after_fen),rights='-' if move.effect=='castle' else p.rights,ep=None if move.effect=='en-passant' else p.ep)
                counter_history=transport(counter.fen(),[],'removed-eligibility/'+row['fixture'],'trusted-import')
                counter_result=query(counter.fen(),row['move'],counter_history)
                full=infer_moves(Position.from_fen(after_fen),model,native_options(history,Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180)),rt)
                expected={m.uci() for m in chess.Board(after_fen).legal_moves};predicted={c['move'] for c in full['candidates'] if c['classification']=='supported-legal'}
                assert not full['truncated']
                failures.append(dict(cohort=cohort,fixture=row['fixture'],split=split,original_fen=row['fen'],move=row['move'],
                    original_full_position_proof=[report['native_proof_dag'][i] for i in row['proof_refs']],
                    original_proof_id=row['proof_id'],before=before,intervention_history=history,intervention_fen=after_fen,
                    after=after,unknown_history=unknown,removed_temporal_channel=removed,removed_eligibility=counter_result,
                    complete_position=dict(expected=sorted(expected),predicted=sorted(predicted),exact=expected==predicted,result=full),
                    resolved_under_supplied_evidence=after['candidate']['classification']=='supported-legal',
                    provenance_limit='New declared metadata or synthetic predecessor is an intervention, not recovered factual history. Original FEN-only uncertainty remains valid.'))
    assert Counter(f['split'] for f in failures if f['cohort']=='cycle9')==dict(adversarial=16,**{'special-moves':9})
    pack(out/'temporal/historical-abstentions.json.xz',failures)
    pack(out/'temporal/other-abstentions.json.xz',unhandled)
    data=read_json(out/'datasets/dataset.json');game_replays=[]
    for game in data['games']:
        history=replay_game(game,len(game['moves']),model.version,rt.version)
        assert history['resulting_fen']==game['final_fen']
        game_replays.append(dict(game=game['id'],source_collection=game['source_collection'],event_count=len(history['events']),
            transport_id=history['id'],initial_trust=history['input']['initial_trust'],final_state=history['resulting_fen'],status=history['status']))
    write_json(out/'temporal/game-replay.json',dict(passed=True,games=game_replays,complete_games=len(game_replays),oracle_used_in_transport=False))
    # Store complete event lineage for a small inspectable cross-source replay sample.
    sample=[]
    for source in sorted({g['source_collection'] for g in data['games']}):
        game=next(g for g in data['games'] if g['source_collection']==source)
        sample.append(dict(game=game,replay=replay_game(game,len(game['moves']),model.version,rt.version)))
    pack(out/'temporal/external-replay-examples.json.xz',sample)
    errors=[]
    for case in demonstrations:
        for side in ('left','right'):
            result=case[side];classification=result['candidate']['classification']
            if (classification=='supported-legal' and not result['expected_legal']) or (classification=='supported-illegal' and result['expected_legal']):errors.append([case['id'],side,classification])
    write_json(out/'temporal/summary.json',dict(schema='temporal-transport-v10',demonstrations=len(demonstrations),counterfactual_errors=errors,
        historical_cases=sum(f['cohort']=='cycle9' for f in failures),additional_synthetic_cases=sum(f['cohort']=='cycle10' for f in failures),
        other_abstentions=len(unhandled),resolved_under_supplied_evidence=sum(f['resolved_under_supplied_evidence'] for f in failures),
        by_cohort={cohort:dict(cases=sum(f['cohort']==cohort for f in failures),resolved=sum(f['cohort']==cohort and f['resolved_under_supplied_evidence'] for f in failures)) for cohort in ('cycle9','cycle10')},
        full_position_exact_after_intervention=sum(f['complete_position']['exact'] for f in failures),
        temporal_removal_abstentions=sum(f['removed_temporal_channel']['candidate']['classification']=='unknown' for f in failures),
        eligibility_removal_supported=sum(f['removed_eligibility']['candidate']['classification']=='supported-legal' for f in failures),
        complete_game_replays=len(game_replays),new_operator_enabled=False,thresholds_changed=False,
        original_FEN_only_results_unchanged=True,
        caveat='Resolution is conditional on explicit added evidence; synthetic predecessor interventions are not independent observations of the original fixture history.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
