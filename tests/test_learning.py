from dataclasses import replace
import pytest
from pln_chess.api import observe_example,train,explain_move,compare_transforms
from pln_chess.evidence import Ledger
from pln_chess.learning import Model
from pln_chess.domain import Position
from pln_chess.inference import Options
from pln_chess.common import read_json,write_json

FEN='8/6k1/8/8/8/2R5/2K5/8 w - - 0 1'

def test_idempotency_correlation_conflict_and_replay(runtime,tmp_path):
    path=tmp_path/'ledger.jsonl'
    a=observe_example(FEN,'c3e3',True,'test','group',path,runtime)
    b=observe_example(FEN,'c3e3',True,'test','group',path,runtime)
    assert a['status']=='appended' and b['status']=='duplicate'
    first=train(Ledger(path),runtime=runtime)
    observe_example(FEN,'c3e3',True,'repeat','group',path,runtime)
    repeated=train(Ledger(path),runtime=runtime)
    assert first.hypotheses==repeated.hypotheses
    observe_example(FEN,'c3e3',False,'independent','different-group',path,runtime)
    conflict=train(Ledger(path),runtime=runtime)
    key=next(k for k in conflict.hypotheses if k.startswith('context:'))
    assert conflict.hypotheses[key]['positive']['strength']==pytest.approx(.5)
    assert conflict.hypotheses[key]['positive']['confidence']>first.hypotheses[key]['positive']['confidence']
    assert train(Ledger(path),runtime=runtime).version==conflict.version
    restored=train(Ledger(path),options={'through_sequence':1},runtime=runtime)
    assert restored.version==first.version
    output=tmp_path/'model.json'; conflict.export(output)
    assert Model.load(output,runtime).version==conflict.version
    data=read_json(output); data['hypotheses'][key]['positive']['strength']=.8; write_json(output,data)
    with pytest.raises(ValueError): Model.load(output,runtime)

def test_native_transfer_and_budget(runtime,tmp_path):
    path=tmp_path/'ledger.jsonl'
    observe_example(FEN,'c3e3',True,'test','group',path,runtime)
    model=train(Ledger(path),runtime=runtime)
    proof=explain_move(FEN,'c3e3',model,runtime=runtime)
    assert proof['candidate']['classification']=='supported'
    assert compare_transforms(FEN,(1,0),model,'c3e3',runtime)['passed']
    empty=explain_move(FEN,'c3e3',model,Options(max_native_invocations=0),runtime)
    assert empty['truncated'] and empty['candidate']['classification']=='incomplete'
    unknown=explain_move(Position.from_fen(FEN,unknown_squares=((3,2),)),'c3e3',model,runtime=runtime)
    assert unknown['candidate']['classification']=='unknown'

def test_illegal_context_does_not_discredit_geometry(runtime,tmp_path):
    path=tmp_path/'ledger.jsonl'
    observe_example(FEN,'c3e3',True,'positive','clear',path,runtime)
    observe_example(FEN.replace('2R5','2RP4'),'c3e3',False,'blocked','blocked',path,runtime)
    model=train(Ledger(path),runtime=runtime)
    clear=explain_move(FEN,'c3e3',model,runtime=runtime)['candidate']
    blocked=explain_move(FEN.replace('2R5','2RP4'),'c3e3',model,runtime=runtime)['candidate']
    assert clear['classification']=='supported'
    assert blocked['classification']=='contradicted'
    assert clear['movement_truth_value']==blocked['movement_truth_value']


def test_pawn_color_orientation_native_transfer(runtime,tmp_path):
    fen='7k/8/8/8/8/8/2P5/K7 w - - 0 1'
    path=tmp_path/'pawn.jsonl'
    observe_example(fen,'c2c4',True,'orientation','pawn-family',path,runtime)
    model=train(Ledger(path),runtime=runtime)
    report=compare_transforms(fen,'color-flip',model,'c2c4',runtime)
    assert report['passed'] and report['tested']==1
    assert report['checks'][0]['translated_move']=='c7c5'


def test_changed_context_is_not_a_passing_invariance(runtime):
    fen='8/6k1/8/8/8/8/2P5/2K5 w - - 0 1'
    report=compare_transforms(fen,(0,1),move='c2c3',runtime=runtime)
    assert report['tested']==0 and not report['passed']
