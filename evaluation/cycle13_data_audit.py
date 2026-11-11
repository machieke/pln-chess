"""Source, partition, label and external-concept integrity checks."""
import argparse
from collections import defaultdict
from pathlib import Path

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha


def normalized_game(row):
    return row['source'].get('game_url',row['source_game']).split('#')[0].rstrip('/').removesuffix('/black')


def run(out,require_labels=False):
    out=Path(out);source=read_json(out/'sources/lichess-puzzle-source.json')
    assert sha(out/'sources/lichess-puzzle-prefix.csv')==source['sha256']
    data=read_json(out/'datasets/source-pairs.json');expected=data.pop('hash');assert digest(data)==expected
    assert data['registration_hash']==digest(read_json(ROOT/'configs/cycle13.json'))
    rows=data['records'];assert len({r['id'] for r in rows})==len(rows)
    assert len({r['source_game'] for r in rows})>=100
    partitions={}
    for field in ('source_game','raw_structural_family','canonical_pair','dependence_group'):
        values=defaultdict(set)
        for row in rows:values[row[field]].add(row['split'])
        assert all(len(splits)==1 for splits in values.values()),field
        partitions[field]=dict(groups=len(values),cross_partition_groups=0)
    for row in rows:
        board=chess.Board(row['history']['initial_fen'])
        for move in row['history']['moves']:board.push_uci(move)
        assert board.fen(en_passant='fen')==row['fen']
        assert len(row['moves'])==len(set(row['moves']))==2
        assert all(chess.Move.from_uci(m) in board.legal_moves for m in row['moves'])
    concepts=read_json(out/'datasets/external-concepts.json');value=concepts.pop('hash');assert digest(concepts)==value
    games={normalized_game(r) for r in rows};external={r['source_game'] for r in concepts['records']}
    assert not games&external and len(external)==len(concepts['records'])
    concept_groups={r['dependence_group'] for r in concepts['records']}
    assert all(c['dependence_group'] in concept_groups and c['independent_example'] is False for c in concepts['controls'])
    labels=None;label_path=out/'datasets/reference-labels.json'
    if require_labels or label_path.exists():
        from training.cycle13_labels import label,semantic_record
        labels=read_json(label_path);label_hash=labels.pop('hash');assert digest(labels)==label_hash
        assert labels['source_hash']==expected
        indexed={r['id']:r for r in rows}
        assert len(labels['records'])==len(indexed)
        assert {r['id'] for r in labels['records']}==set(indexed)
        for record in labels['records']:
            row=indexed[record['id']]
            raw=read_json(out/'labels'/f"{row['id']}.json")
            assert record==semantic_record(raw)
            assert record['identity']['row_hash']==digest(row)
            assert record['identity']['reference_binary_sha256']==read_json(out/'sources/stockfish-source.json')['binary_sha256']
            assert record['label']==label(record['evaluations'],record['identity']['config'])[0]
            assert record['split']==row['split'] and record['dependence_group']==row['dependence_group']
    receipt=dict(passed=True,source_pairs=len(rows),source_hash=expected,partition_audit=partitions,
        external_concept_cases=len(concepts['records']),external_concept_controls=len(concepts['controls']),
        external_concept_games_disjoint=True,source_history_and_candidate_legal_replay_verified=True,
        labels_verified=len(labels['records']) if labels else 0,teacher_labels_required=require_labels,
        raw_labels_are_not_production_inference=True,driver_sha256=sha(__file__),
        scope='Offline reference integrity and conservative ancestry partition checks; no strategic correctness or native preference claim.')
    write_json(out/'datasets'/('audit.json' if require_labels else 'source-audit.json'),receipt)
    print(receipt,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--require-labels',action='store_true')
    args=parser.parse_args();run(args.out,args.require_labels)
