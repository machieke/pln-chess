"""Explicit offline PGN preparation preserves uncertainty and provenance."""
import pytest
from training.cycle10_import import import_pgn


def test_partial_pgn_import_preserves_supplied_events_without_fabricating_completion(tmp_path):
    path=tmp_path/'partial.pgn';path.write_text('[Event "Partial record"]\n[Result "*"]\n\n1. e4 e5 2. Nf3 *\n')
    result=import_pgn(path,'local-study');game=result['games'][0]
    assert game['moves']==['e2e4','e7e5','g1f3'] and game['complete'] is False
    assert result['complete_games']==0 and result['source']=='local-study'
    assert game['source_collection']=='local-study' and 'offline' in result['oracle_scope']
    assert import_pgn(path,'local-study')['games'][0]['id']==game['id']
    assert import_pgn(path,'other-source')['games'][0]['id']!=game['id']


def test_import_does_not_accept_ambiguous_or_malformed_pgn_as_history(tmp_path):
    path=tmp_path/'invalid.pgn';path.write_text('[Result "1-0"]\n\n1. e4 e5 2. Qh8 1-0\n')
    with pytest.raises(ValueError,match='Malformed PGN'):import_pgn(path,'source')
    with pytest.raises(ValueError,match='source'):import_pgn(path,'')
    with pytest.raises(ValueError,match='limit'):import_pgn(path,'source',True)
