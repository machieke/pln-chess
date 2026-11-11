"""Offline, score-blind move-pair selection from pinned external sources.

Chess is used here solely to reconstruct published positions and select legal
reference examples. This module is never imported by production inference.
"""
import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path

import chess

from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from scripts.cycle9_baseline import sha

THEMES = ('fork','pin','discoveredAttack','deflection','clearance','defensiveMove',
          'quietMove','exposedKing','promotion','attraction','interference','trappedPiece')


def geometry_key(board, moves, local=True):
    """Partition ancestry only; never a learned model key.

    Translation, file reflection and owner reversal share a canonical role
    geometry. Distant pieces are omitted only for the stricter local motif key.
    Both candidate orderings are included. Pawns retain forward orientation.
    """
    variants=[]
    for pair in (moves, list(reversed(moves))):
        anchor=pair[0].from_square;ax,ay=chess.square_file(anchor),chess.square_rank(anchor)
        orientation=1 if board.turn else -1
        endpoints=[m.from_square for m in pair]+[m.to_square for m in pair]
        def nearby(square):
            x,y=chess.square_file(square),chess.square_rank(square)
            for endpoint in endpoints:
                dx,dy=x-chess.square_file(endpoint),y-chess.square_rank(endpoint)
                if max(abs(dx),abs(dy))<=2 or dx==0 or dy==0 or abs(dx)==abs(dy):return True
            return False
        for flip in (1,-1):
            def relative(square):
                return [(chess.square_file(square)-ax)*flip,(chess.square_rank(square)-ay)*orientation]
            pieces=sorted([[piece.piece_type,piece.color==board.turn,relative(square)]
                for square,piece in board.piece_map().items() if not local or nearby(square)])
            roots=[[relative(m.from_square),relative(m.to_square),m.promotion] for m in pair]
            variants.append(canonical([pieces,roots]))
    return digest(min(variants))


def make_record(board, primary, identifier, provenance, themes, history=None):
    assert board.is_valid() and primary in board.legal_moves
    alternatives=[m for m in board.legal_moves if m!=primary]
    if not alternatives:return None
    alternate=min(alternatives,key=lambda m:digest([131313,identifier,m.uci()]))
    pair=[primary,alternate]
    if int(digest(['display-order',identifier])[:8],16)%2:pair.reverse()
    after=[]
    for move in pair:
        successor=board.copy();successor.push(move);after.append(successor)
    mover=board.piece_at(primary.from_square)
    return dict(id=identifier,fen=board.fen(en_passant='fen'),moves=[m.uci() for m in pair],
        source=provenance,source_game=provenance['game_id'],themes=list(themes),history=history,
        source_primary_move=primary.uci(),selection='Published move and hash-selected legal alternative; A/B order fixed by independent hash before preference evaluation.',
        raw_structural_family='relative-motif:'+geometry_key(board,pair),
        canonical_pair='relative-pair:'+geometry_key(board,pair,False),
        offline_reference=dict(valid_board=True,legal_candidates=True,
            captures=[board.is_capture(m) for m in pair],checks=[board.gives_check(m) for m in pair],
            promotions=[bool(m.promotion) for m in pair],
            quiet_pair=all(not board.is_capture(m) and not board.gives_check(m) and not m.promotion for m in pair),
            pieces=len(board.piece_map()),mover_kind=chess.piece_name(mover.piece_type)),
        unknown_squares=[])


def partition(records):
    parent=list(range(len(records)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    seen={}
    for i,row in enumerate(records):
        for field in ('source_game','raw_structural_family','canonical_pair'):
            key=(field,row[field])
            if key in seen:union(i,seen[key])
            else:seen[key]=i
    components=defaultdict(list)
    for i,row in enumerate(records):components[find(i)].append(row)
    for rows in components.values():
        group='c13-ancestry:'+digest(sorted(r['id'] for r in rows))
        value=int(digest([131313,group])[:8],16)%10
        split='train' if value<6 else 'calibration' if value<8 else 'test'
        for row in rows:
            row.update(split=split,dependence_group=group,transformation_lineage=[group],
                partition_source='Connected source game / canonical unordered pair / local relative motif; fixed hash partition before teacher labels.')
    return components


def run(out):
    out=Path(out);source=out/'sources';games=read_json(ROOT/'artifacts/cycle10/datasets/dataset.json')
    records=[];used_games=set();skipped=[]
    for game in sorted(games['games'],key=lambda g:g['id']):
        board=chess.Board(game['initial_fen']);index=min(max(12,len(game['moves'])//2),60,len(game['moves'])-1)
        for move in game['moves'][:index]:board.push_uci(move)
        provenance=dict(collection=game['source_collection'],game_id=game['original_game_identifier'],
            original_record=game['id'],source_dataset='artifacts/cycle10/datasets/dataset.json',
            source_dataset_sha256=sha(ROOT/'artifacts/cycle10/datasets/dataset.json'),ply=index,
            cohort='independent-games',opening_family=game['opening_family'])
        history=dict(initial_fen=game['initial_fen'],moves=game['moves'][:index],source=game['original_game_identifier'])
        row=make_record(board,chess.Move.from_uci(game['moves'][index]),'c13-'+game['id'],provenance,['published-game'],history)
        if row is None:skipped.append(dict(id=game['id'],reason='No alternative legal root'));continue
        records.append(row);used_games.add(provenance['game_id'].split('#')[0].rstrip('/').removesuffix('/black'))
    pool=list(csv.DictReader((source/'lichess-puzzle-prefix.csv').open()))
    selected_puzzles=set();theme_counts=Counter()
    for theme in THEMES:
        eligible=sorted((r for r in pool if theme in r['Themes'].split()),key=lambda r:digest([131313,theme,r['PuzzleId']]))
        for puzzle in eligible:
            if theme_counts[theme]>=16:break
            url=puzzle['GameUrl'];game_id=url.split('#')[0].rstrip('/').removesuffix('/black')
            if game_id in used_games or puzzle['PuzzleId'] in selected_puzzles:continue
            moves=puzzle['Moves'].split()
            if len(moves)<2:continue
            board=chess.Board(puzzle['FEN'])
            if not board.is_valid():continue
            board.push_uci(moves[0])
            provenance=dict(collection='lichess-puzzles-frozen-prefix',game_id=game_id,puzzle_id=puzzle['PuzzleId'],
                puzzle_url='https://lichess.org/training/'+puzzle['PuzzleId'],game_url=url,
                source_sha256=sha(source/'lichess-puzzle-prefix.csv'),rating=int(puzzle['Rating']),
                supplied_solution=moves[1:],cohort='external-tactical',selection_theme=theme,
                original_fen=puzzle['FEN'],preceding_move=moves[0])
            row=make_record(board,chess.Move.from_uci(moves[1]),'c13-puzzle-'+puzzle['PuzzleId'],provenance,puzzle['Themes'].split(),
                dict(initial_fen=puzzle['FEN'],moves=[moves[0]],source=url))
            if row is None:continue
            records.append(row);used_games.add(game_id);selected_puzzles.add(puzzle['PuzzleId']);theme_counts[theme]+=1
    components=partition(records)
    audit=dict(passed=True,records=len(records),independent_source_games=len({r['source_game'] for r in records}),
        independent_ancestry_components=len(components),raw_structural_families=len({r['raw_structural_family'] for r in records}),
        maximum_component_size=max(map(len,components.values())),
        splits=dict(Counter(r['split'] for r in records)),cohorts=dict(Counter(r['source']['cohort'] for r in records)),
        selection_theme_counts=dict(theme_counts),quiet_pairs=sum(r['offline_reference']['quiet_pair'] for r in records),
        promotion_pairs=sum(any(r['offline_reference']['promotions']) for r in records),skipped=skipped,
        native_inference_used_for_selection=False,preference_labels_used_for_selection=False,
        learned_hypotheses_contain_partition_keys=False)
    assert audit['independent_ancestry_components']>=100 and audit['independent_source_games']>=100
    for field in ('source_game','raw_structural_family','canonical_pair','dependence_group'):
        groups=defaultdict(set)
        for row in records:groups[row[field]].add(row['split'])
        assert all(len(v)==1 for v in groups.values()),field
    payload=dict(schema='c13-preference-source-pairs-v1',records=records,selection_audit=audit,
        registration_hash=digest(read_json(ROOT/'configs/cycle13.json')),
        scope='Score-blind offline source selection. No preference label or native strategic conclusion has been assigned.')
    payload['hash']=digest(payload)
    destination=out/'datasets/source-pairs.json'
    if destination.exists():assert read_json(destination)==payload,'Append-only source selection cannot be overwritten'
    else:write_json(destination,payload)
    write_json(out/'datasets/source-selection-audit.json',audit)
    print(audit,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
