import chess
import chess.engine
import asyncio
import pytest

from training.cycle14_reference import parse_info, direction, classify_tier, board_from_history


@pytest.mark.parametrize('turn,actor,expected,bound',[(True,True,120,'lower'),(False,False,120,'lower'),
    (True,False,-120,'upper'),(False,True,-120,'upper')])
def test_perspective_reverses_numeric_value_and_bound(turn,actor,expected,bound):
    info=parse_info('info depth 8 score cp 120 lowerbound nodes 20000 pv e2e4 e7e5',side_to_move=turn,actor=actor)
    assert info['score']==dict(kind='cp',value=expected,mate_outcome=None,bound=bound)


def test_newer_unflagged_record_cannot_inherit_an_old_bound():
    old='info depth 7 multipv 1 score cp 40 lowerbound pv e2e4'
    new='info depth 8 multipv 1 score cp 65 pv e2e4 e7e5'
    async def aggregate_records():
        aggregate=chess.engine.AnalysisResult()
        aggregate.post(chess.engine._parse_uci_info(old[5:],chess.Board(),chess.engine.INFO_ALL))
        aggregate.post(chess.engine._parse_uci_info(new[5:],chess.Board(),chess.engine.INFO_ALL))
        return aggregate.multipv
    assert asyncio.run(aggregate_records())[0]['lowerbound'] is True
    assert parse_info(new,side_to_move=True,actor=True)['score']['bound']=='unflagged'


@pytest.mark.parametrize('raw,actor,outcome,value',[(0,True,'loss',0),(0,False,'win',0),
    (3,True,'win',3),(3,False,'loss',-3),(-4,True,'loss',-4),(-4,False,'win',4)])
def test_mates_preserve_outcome_at_zero_without_centipawn_conversion(raw,actor,outcome,value):
    score=parse_info(f'info depth 9 score mate {raw} pv e2e4',side_to_move=True,actor=actor)['score']
    assert score==dict(kind='mate',value=value,mate_outcome=outcome,bound='unflagged')
    assert 'cp' not in score


def score(value,bound='unflagged',kind='cp',outcome=None):
    return dict(kind=kind,value=value,bound=bound,mate_outcome=outcome)


def test_interval_separation_and_mate_order_remain_operational():
    assert direction(score(180,'lower'),score(90,'upper'))=='A'
    assert direction(score(180,'upper'),score(90,'lower')) is None
    assert direction(score(2,kind='mate',outcome='win'),score(4,kind='mate',outcome='win'))=='A'
    assert direction(score(-4,kind='mate',outcome='loss'),score(-2,kind='mate',outcome='loss'))=='A'
    assert direction(score(2,'lower','mate','win'),score(100)) is None


def evaluation(a,b,**extra):
    return dict(candidates={'A':dict(score=a),'B':dict(score=b)},termination='completed',history_verified=True,**extra)


def test_budget_disagreement_missing_interrupted_and_nondirectional_are_distinct():
    a=evaluation(score(200),score(0));b=evaluation(score(0),score(200))
    assert classify_tier([a,a])==('A','stable-operational-direction')
    assert classify_tier([a,b])==('unknown','budget-disagreement')
    assert classify_tier([dict(a,candidates={'A':a['candidates']['A']}),a])[1]=='missing-candidate-analysis'
    assert classify_tier([dict(a,termination='interrupted'),a])[1]=='interrupted-search'
    near=evaluation(score(10),score(0))
    assert classify_tier([near,near])[0]=='no-demonstrated-preference'
    intermediate=evaluation(score(40),score(0))
    assert classify_tier([intermediate,intermediate])==('unknown','insufficient-margin')


def test_multipv_order_does_not_identify_the_candidate():
    a=parse_info('info depth 8 multipv 2 score cp 100 pv e2e4',side_to_move=True,actor=True)
    b=parse_info('info depth 8 multipv 1 score cp 20 pv d2d4',side_to_move=True,actor=True)
    assert {r['candidate']:r['score']['value'] for r in (b,a)}=={'e2e4':100,'d2d4':20}


def test_even_and_odd_history_prefixes_preserve_explicit_actor():
    for moves in (['e2e4'],['e2e4','e7e5']):
        board=board_from_history(dict(initial_fen=chess.STARTING_FEN,moves=moves))
        info=parse_info('info depth 6 score cp 40 upperbound pv g1f3',side_to_move=board.turn,actor=True)
        assert info['score']['bound']==('lower' if len(moves)%2 else 'upper')
    with pytest.raises(ValueError,match='reconstruct'):
        board_from_history(dict(initial_fen=chess.STARTING_FEN,moves=['e2e4']),chess.STARTING_FEN)
    with pytest.raises(ValueError,match='Illegal'):
        board_from_history(dict(initial_fen=chess.STARTING_FEN,moves=['e2e5']))
