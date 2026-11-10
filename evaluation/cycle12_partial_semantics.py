"""Overload consequences and trapping diagnostics with explicit limits."""
import argparse
import copy
from dataclasses import replace
from pathlib import Path
import chess
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position, parse_square
from pln_chess.pln import Runtime
from pln_chess.api import infer_moves
from pln_chess.hypotheses import candidates
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import Cycle8Options
from evaluation.cycle7_io import pack


def run(out):
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, build_field
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle12.inference import infer_concepts
    from pln_chess.cycle12.ontology import structural_successor
    from pln_chess.cycle12.graph import compare_fields, build_graph
    out=Path(out);assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    runtime=Runtime(timeout=600);options=FieldOptions(timeout_seconds=600)
    field=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime)
    model=ConceptModel.load(out/'model/C12-concept-trained.json',runtime)
    rows=read_json(out/'datasets/concepts.json')['records']
    case=next(r['input'] for r in rows if r['split']=='test' and r['input']['concept']=='OverloadedDefender' and r['reference']['label'])
    initial=Position.from_fen(case['fen']);roles=case['roles'];defender=initial.at(parse_square(roles['defender']))
    before=build_field(initial,field,runtime=runtime,options=options,source='overload-counterfactual')
    branches=[]
    for ward,enemy,remaining in [('ward_a','enemy_a','ward_b'),('ward_b','enemy_b','ward_a')]:
        # Turn override is an explicit intervention, not a claim that these are legal continuations.
        threat=initial.at(parse_square(roles[enemy]));state=replace(initial,turn=threat.owner)
        capture=roles[enemy]+roles[ward];captured=structural_successor(state,capture)
        reply=roles['defender']+roles[ward];response=structural_successor(replace(captured,turn=defender.owner),reply)
        after_capture=build_field(captured,field,runtime=runtime,options=options,source='overload-counterfactual')
        after_reply=build_field(response,field,runtime=runtime,options=options,source='overload-counterfactual')
        remaining_entity=initial.at(parse_square(roles[remaining]));after_defense=next(r for r in after_reply['relations']
            if r['family']=='defense' and r['source_entity']==defender.id and r['target_entity']==remaining_entity.id)
        branches.append(dict(attacked_ward=ward,remaining_ward=remaining,capture=capture,response=reply,
            after_capture=after_capture,after_response=after_reply,remaining_defense=after_defense,
            capture_changes=compare_fields(before,after_capture),response_changes=compare_fields(after_capture,after_reply),
            graph=build_graph(after_reply,before=before,move=reply),legality_asserted=False,
            scope='One explicitly supplied response to one local capture. This does not quantify over all legal responses or prove strategic overload.'))
    concept=infer_concepts([case],model,field,runtime=runtime,options=options)['concepts'][0]
    pack(out/'concepts/overload-consequences.json.xz',dict(input=case,concept=concept,before=before,branches=branches,
        strategically_overloaded=None,all_responses_excluded=False))
    # A valid board permits a separately labelled legal-exit reference. Never
    # replace a missing learned exit with the offline answer in production.
    fen='N6k/2P5/1P6/8/8/8/8/7K w - - 0 1';board=chess.Board(fen);assert board.is_valid()
    trapped=[];legal_model=PromotionModel.load(ROOT/'artifacts/cycle10/model/C10-default.json',runtime)
    for name in ('no-ordinary-exit','escape-opened','unknown-exit-cell'):
        current=board.copy()
        if name=='escape-opened':current.remove_piece_at(chess.B6)
        inp=dict(concept='TrappedPiece',fen=current.fen(en_passant='fen'),roles=dict(subject='a8'),
            source='valid-trapping-diagnostic',unknown_squares=['b6'] if name=='unknown-exit-cell' else [])
        position=Position.from_fen(inp['fen'],unknown_squares=[parse_square(s) for s in inp['unknown_squares']])
        result=infer_concepts([inp],model,field,runtime=runtime,options=options)['concepts'][0]
        selected=[move for move in candidates(position) if move.start==parse_square('a8')]
        legal=infer_moves(position,legal_model,Cycle8Options(mode='operational',timeout_seconds=600),runtime,selected)
        legal['execution']={'elapsed_seconds':legal.pop('elapsed_seconds')}
        reference=[m.uci() for m in current.legal_moves if m.from_square==chess.A8]
        trapped.append(dict(id=name,input=inp,concept=result,legal_candidates=legal,
            reference_legal_exits=reference if not inp['unknown_squares'] else None,
            reference_scope='Offline legal-exit reference applies only to this valid fully observed board.',
            supported_legal_exits=[r['move'] for r in legal['candidates'] if r['classification']=='supported-legal'],
            unknown_legal_exits=[r['move'] for r in legal['candidates'] if r['classification'] in ('unknown','incomplete')],
            unfavorable_exits=None,strategically_trapped=None))
    pack(out/'concepts/trapping-diagnostics.json.xz',trapped)
    write_json(out/'concepts/partial-semantics-summary.json',dict(overload_branches=len(branches),
        remaining_defense=[b['remaining_defense']['classification'] for b in branches],all_responses_excluded=False,
        trapping=[dict(id=r['id'],conditional=r['concept']['classification'],supported_legal_exits=r['supported_legal_exits'],
            unknown_legal_exits=r['unknown_legal_exits'],reference_legal_exits=r['reference_legal_exits']) for r in trapped],
        complete_overload_theorems=0,complete_strategic_trapping_theorems=0))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
