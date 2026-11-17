"""Equal *field* counts with different connected attack targets."""
import argparse
from collections import Counter
from pathlib import Path
from pln_chess.common import ROOT,write_json
from pln_chess.domain import Position,Piece
from pln_chess.cycle11.fields.inference import build_field
from pln_chess.cycle11.fields.model import FieldModel
from research.cycle15.native_reasoner import NativeReasoner,save_result
from research.cycle15.queries import infer_state
from research.cycle15.observations import successor
from evaluation.cycle15_corpus import reference
from evaluation.cycle15_consequences import compact


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);reasoner=NativeReasoner()
    model=FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',reasoner.runtime)
    before=dict(id='field_before',root='equal_field_root',actor='white',history='observed',unknown=[],pieces=[
        dict(id='specified_attacker',kind='rook',owner='black',cell=[0,0]),
        dict(id='other_attacker',kind='rook',owner='black',cell=[7,0]),
        dict(id='specified_target',kind='knight',owner='white',cell=[0,2]),
        dict(id='other_target',kind='knight',owner='white',cell=[7,2]),
        dict(id='blocker',kind='pawn',owner='white',cell=[0,1])])
    after=successor(before,dict(id='supplied_swap',piece='blocker',destination=[7,1]))
    query=dict(attacker='specified_attacker',target='specified_target',predicate='Attack')
    panel=[]
    for state in (before,after):
        position=Position(tuple(Piece(p['id'],p['kind'].title(),p['owner'].title(),tuple(p['cell'])) for p in state['pieces']),'White')
        field=build_field(position,model,runtime=reasoner.runtime,families=('attack',))
        counts=dict(Counter(r['classification'] for r in field['relations']))
        panel.append(dict(state=state,reference=reference(state,query),full_attack_field_counts=counts,
            query_count=len(field['relations']),field_evidence=save_result(field,out/'raw'),
            connected_result=compact(infer_state(state,query,reasoner=reasoner),out)))
    assert panel[0]['full_attack_field_counts']==panel[1]['full_attack_field_counts']
    assert panel[0]['reference']['label'] is False and panel[1]['reference']['label'] is True
    assert [r['connected_result']['classification'] for r in panel]==['supported-negative','supported-positive']
    write_json(out/'field-information-loss.json',dict(passed=True,panel=panel,
        scope='All source pieces to all distinct board cells, attack family only; mirrored structural fixture pair, not independent samples'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
