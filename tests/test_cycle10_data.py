"""External provenance, partition integrity and no model-dependent sampling."""
from collections import defaultdict
import io
from pathlib import Path
import chess
import pytest
from pln_chess.common import ROOT,read_json,digest
from scripts.cycle9_baseline import sha
from training.cycle10_data import partition,read_games,canonical
from training.cycle8_data import translation_key


def test_external_corpus_identity_and_game_level_partitions():
    path=ROOT/'artifacts/cycle10/datasets/dataset.json'
    if not path.exists():pytest.skip('Acquire the registered external corpus first')
    data=read_json(path);claimed=data.pop('hash');assert digest(data)==claimed
    assert data['registration_hash']==digest(read_json(ROOT/'configs/cycle10.json'))
    assert data['counts']['external-test']>=1000 and len(data['games'])>=100
    assert len({g['source_collection'] for g in data['games']})>=3
    groups=defaultdict(set);fixtures={f['id']:f for f in data['positions']}
    for game in data['games']:
        groups[game['opening_family']].add(game['split'])
        assert game['split']==partition(game['opening_family'])
        b=chess.Board(game['initial_fen']);sampled={fixtures[k]['ply']:fixtures[k] for k in game['sampled_fixtures']}
        for ply,notation in enumerate(game['moves'],1):
            move=chess.Move.from_uci(notation);assert move in b.legal_moves;b.push(move)
            if ply in sampled:
                assert b.fen(en_passant='fen')==sampled[ply]['fen']
                assert sampled[ply]['source_game']==game['id'] and sampled[ply]['split']==game['split']
        assert b.fen(en_passant='fen')==game['final_fen'] and game['complete']
        assert game['headers']['Result']!='*'
    assert all(len(s)==1 for s in groups.values())
    assert len({translation_key(f['fen']) for f in fixtures.values()})==len(fixtures)
    assert all(canonical(f['fen'])==f['canonical_hash'] for f in fixtures.values())


def test_source_bytes_and_explicit_reuse_terms_are_preserved():
    path=ROOT/'artifacts/cycle10/sources/manifest.json'
    if not path.exists():pytest.skip('Acquire public source files first')
    manifest=read_json(path);assert len(manifest['sources'])==3
    for source in manifest['sources']:
        folder=path.parent/source['source']['id']
        for download in source['downloads'].values():assert sha(folder/download['file'])==download['sha256']
        assert source['source']['license'] in ('CC0-1.0','CC-BY-SA-3.0','CC-BY-SA-4.0')
        assert source['downloads']['data']['acquired_utc'] and source['attribution']


def test_game_parser_never_counts_unfinished_or_invalid_records(tmp_path):
    path=tmp_path/'unfinished.pgn';path.write_text('[Event "Unfinished"]\n[Result "*"]\n\n1. e4 e5 *\n')
    games,audit=read_games(path,'test');assert not games and audit['excluded']['unfinished-record']==1
    path.write_text('[Event "Invalid"]\n[Result "1-0"]\n\n1. e4 e5 2. Qh8 1-0\n')
    games,audit=read_games(path,'test');assert not games and audit['excluded']['PGN-parse-error']==1


def test_symmetry_exclusion_retains_ep_and_rights_as_separate_metadata():
    a='7k/8/8/5pP1/8/8/8/K7 w - f6 0 2';b=a.replace(' f6 ',' - ')
    assert translation_key(a)==translation_key(b) # conservative geometry exclusion
    assert canonical(a)!=canonical(b) # epistemic difference is not erased in provenance
    assert translation_key(a)==translation_key(chess.Board(a).mirror().fen(en_passant='fen'))
