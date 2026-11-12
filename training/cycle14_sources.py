"""Score-blind, immutable expanded source and ancestry registration."""
import argparse
from collections import Counter, defaultdict
import copy
import csv
from pathlib import Path
import re
from urllib.parse import urlparse

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha
from training.cycle10_data import read_games
from training.cycle13_sources import make_record, THEMES


def normalized_url(url):
    """Only a game-specific URL is an ancestry identity, never a publisher Site."""
    parsed=urlparse(url or '')
    if parsed.hostname not in ('lichess.org','www.lichess.org'):return ''
    path=parsed.path.rstrip('/').removesuffix('/black').removesuffix('/white')
    if path.startswith('/game/'):path=path.removeprefix('/game')
    if not re.fullmatch(r'/[A-Za-z0-9]{8}',path):return ''
    return 'https://lichess.org'+path


def immutable(path, value):
    path=Path(path)
    if path.exists():
        assert read_json(path)==value, 'Preserve the frozen generation: '+str(path)
    else:
        write_json(path,value)


def components(records):
    parent=list(range(len(records)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    known={}
    for i,row in enumerate(records):
        for token in row['ancestry_tokens']:
            if token in known:
                a,b=find(i),find(known[token]);parent[max(a,b)]=min(a,b)
            else:known[token]=i
    result=defaultdict(list)
    for i,row in enumerate(records):result[find(i)].append(row)
    return list(result.values())


def run(out):
    out=Path(out);cfg=read_json(ROOT/'configs/cycle14.json');seed=cfg['seed']
    old=copy.deepcopy(read_json(ROOT/'artifacts/cycle13/datasets/source-pairs.json')['records'])
    old_concepts=read_json(ROOT/'artifacts/cycle13/datasets/external-concepts.json')['records']
    old_games=read_json(ROOT/'artifacts/cycle10/datasets/dataset.json')['games']
    old_contents={g['content_hash'] for g in old_games}
    old_urls={normalized_url(r['source'].get('game_url',r['source_game'])) for r in old}
    old_urls.update(normalized_url(r['source_game']) for r in old_concepts)
    old_motifs={r['raw_structural_family'] for r in old};old_pairs={r['canonical_pair'] for r in old}
    historical_content={g['id']:g['content_hash'] for g in old_games}
    for row in old:
        row['historical_split']=row['split']
        if row['split']!='train':row['split']='historical-'+row['split']
        content=historical_content.get(row['source'].get('original_record'))
        row['ancestry_tokens']=['game:'+row['source_game'],row['raw_structural_family'],row['canonical_pair']]
        url=normalized_url(row['source'].get('game_url'))
        if url:row['ancestry_tokens'].append('url:'+url)
        if content:row['ancestry_tokens'].append('content:'+content)
        row['generation']='historical-c13'
    used_urls=set(old_urls);used_contents=set(old_contents);used_games={r['source_game'] for r in old}
    fresh=[];exclusions=[];scans={};counts=Counter()
    manifests=read_json(ROOT/'artifacts/cycle10/sources/manifest.json')['sources']

    def add(row,collection,content=None):
        if row is None:return False
        url=normalized_url(row['source'].get('game_url'))
        reason=None
        if content and content in used_contents:reason='reused-game-content'
        elif row['source_game'] in used_games or (url and url in used_urls):reason='reused-source-game'
        elif row['raw_structural_family'] in old_motifs or row['canonical_pair'] in old_pairs:reason='historical-relative-geometry'
        if reason:
            exclusions.append(dict(id=row['id'],collection=collection,reason=reason));return False
        row['ancestry_tokens']=['game:'+row['source_game'],row['raw_structural_family'],row['canonical_pair']]
        if url:row['ancestry_tokens'].append('url:'+url);used_urls.add(url)
        if content:row['ancestry_tokens'].append('content:'+content);used_contents.add(content)
        row['generation']='new-c14';fresh.append(row);used_games.add(row['source_game']);counts[collection]+=1
        return True

    provenance=[]
    for source in manifests:
        spec=source['source'];collection=spec['id'];path=ROOT/'artifacts/cycle10/sources'/collection/spec['filename']
        assert sha(path)==source['downloads']['data']['sha256']
        games,audit=read_games(path,collection,limit=1000);scans[collection]=audit
        quota=cfg['new_collection_targets'][collection]
        for game in sorted(games,key=lambda g:digest([seed,collection,g['content_hash']])):
            if counts[collection]>=quota:break
            if game['content_hash'] in used_contents:
                exclusions.append(dict(id=game['id'],collection=collection,reason='historical-game-content'));continue
            if not game['moves']:continue
            board=chess.Board(game['initial_fen']);index=min(max(12,len(game['moves'])//2),60,len(game['moves'])-1)
            for move in game['moves'][:index]:board.push_uci(move)
            if not board.is_valid() or board.is_game_over():
                exclusions.append(dict(id=game['id'],collection=collection,reason='invalid-or-terminal-sampling-position'));continue
            source_row=dict(collection=collection,game_id='game-content:'+game['content_hash'],
                content_hash=game['content_hash'],game_url=game['original_game_identifier'],
                source_dataset=str(path.relative_to(ROOT)),source_dataset_sha256=sha(path),ply=index,
                cohort='independent-games',opening_family=game['opening_family'],
                license=spec['license'],attribution=source['attribution'],headers=game['headers'])
            history=dict(initial_fen=game['initial_fen'],moves=game['moves'][:index],source=game['original_game_identifier'] or collection)
            row=make_record(board,chess.Move.from_uci(game['moves'][index]),'c14-'+game['id'],source_row,['published-game'],history)
            add(row,collection,game['content_hash'])
        provenance.append(dict(collection=collection,path=str(path.relative_to(ROOT)),sha256=sha(path),
            license=spec['license'],attribution=source['attribution'],publisher=spec['publisher'],
            source_receipt_sha256=sha(ROOT/'artifacts/cycle10/sources'/collection/'receipt.json'),
            quota=quota,selected=counts[collection],shortfall=max(0,quota-counts[collection])))
        print('C14 SOURCE',collection,counts[collection],flush=True)

    path=ROOT/'artifacts/cycle13/sources/lichess-puzzle-prefix.csv';pool=list(csv.DictReader(path.open()))
    puzzle_hash=sha(path);collection='lichess-puzzles-frozen-prefix'
    # The source fallback is registered before labels and cannot consult a result.
    quota=cfg['new_root_pairs']-len(fresh);selected=set();theme_counts=Counter()
    queues={theme:iter(sorted((r for r in pool if theme in r['Themes'].split()),
        key=lambda r:digest([seed,theme,r['PuzzleId']]))) for theme in THEMES}
    while counts[collection]<quota and queues:
        for theme in list(queues):
            if counts[collection]>=quota:break
            for puzzle in queues[theme]:
                if puzzle['PuzzleId'] in selected:continue
                selected.add(puzzle['PuzzleId']);line=puzzle['Moves'].split()
                if len(line)<2:continue
                board=chess.Board(puzzle['FEN'])
                if not board.is_valid():continue
                board.push_uci(line[0]);primary=chess.Move.from_uci(line[1])
                if primary not in board.legal_moves:continue
                source_row=dict(collection=collection,game_id=normalized_url(puzzle['GameUrl']),
                    game_url=puzzle['GameUrl'],puzzle_id=puzzle['PuzzleId'],rating=int(puzzle['Rating']),
                    puzzle_url='https://lichess.org/training/'+puzzle['PuzzleId'],source_sha256=puzzle_hash,
                    supplied_solution=line[1:],cohort='external-tactical',selection_theme=theme,
                    original_fen=puzzle['FEN'],preceding_move=line[0],license='CC0-1.0',attribution='Lichess puzzle database')
                if not source_row['game_id']:
                    raise ValueError('Unrecognized puzzle game identity; do not merge unknown URLs')
                row=make_record(board,primary,'c14-puzzle-'+puzzle['PuzzleId'],source_row,puzzle['Themes'].split(),
                    dict(initial_fen=puzzle['FEN'],moves=line[:1],source=puzzle['GameUrl']))
                if add(row,collection):theme_counts[theme]+=1;break
            else:del queues[theme]
    provenance.append(dict(collection=collection,path=str(path.relative_to(ROOT)),sha256=puzzle_hash,
        license='CC0-1.0',publisher='Lichess',attribution='Lichess puzzle database',
        quota=cfg['new_collection_targets'][collection],quota_with_registered_fallback=quota,
        selected=counts[collection],source_receipt_sha256=sha(ROOT/'artifacts/cycle13/sources/lichess-puzzle-source.json')))
    groups=components(fresh)
    ordered=sorted(groups,key=lambda group:digest([seed,sorted(r['id'] for r in group)]))
    assigned=Counter();targets=cfg['new_partitions'];heldout=cfg['source_holdout_collection']
    for group in ordered:
        choices=['source-holdout'] if any(r['source']['collection']==heldout for r in group) else ['test','development','calibration','train']
        split=next((s for s in choices if assigned[s]+len(group)<=targets[s]),None)
        if split is None:split='diagnostic-ancestry-overflow'
        identifier='c14-ancestry:'+digest(sorted(token for r in group for token in r['ancestry_tokens']))
        for row in group:
            row.update(split=split,dependence_group=identifier,transformation_lineage=[identifier],
                partition_source='Connected source content, normalized URL, unordered pair and relative geometry; score-blind seeded component ordering')
        assigned[split]+=len(group)
    all_records=old+fresh
    across=components(all_records)
    assert all(len({r['split'] for r in group})==1 for group in across), 'Cross-partition ancestry contamination'
    assert len({r['source_game'] for r in fresh})==len(fresh)
    audit=dict(records=len(all_records),historical=len(old),new_pairs=len(fresh),new_ancestry_groups=len(groups),
        all_ancestry_groups=len(across),largest_component=max(map(len,across)),new_splits=dict(assigned),
        all_splits=dict(Counter(r['split'] for r in all_records)),new_collection_counts=dict(counts),
        quiet_new=sum(r['offline_reference']['quiet_pair'] for r in fresh),
        promotion_new=sum(any(r['offline_reference']['promotions']) for r in fresh),
        source_game_overlap=0,cross_partition_ancestry_overlap=0,historical_geometry_overlap=0,
        theme_counts=dict(theme_counts),source_scans=scans,exclusions=exclusions,
        quota_shortfalls={s:max(0,n-assigned[s]) for s,n in targets.items()},
        new_pair_shortfall=max(0,cfg['new_root_pairs']-len(fresh)),
        predictions_used=False,reference_scores_used=False,
        limitations=['Publisher overlap: rated, broadcast and puzzle data are distributed by Lichess.',
            'Raw geometry ancestry does not prove independence of every semantic motif or player/opening.'])
    payload=dict(schema='c14-source-pairs-v1',registration_sha256=sha(ROOT/'configs/cycle14.json'),
        records=all_records,audit=audit,source_provenance=provenance,
        license='Source-specific CC0 / CC-BY-SA-3.0 / CC-BY-SA-4.0; derived combined corpus CC-BY-SA-4.0')
    payload['hash']=digest(payload);immutable(out/'datasets/source-pairs.json',payload)
    partitions=dict(schema='c14-partitions-v1',source_hash=payload['hash'],
        records=[{k:r[k] for k in ('id','split','source_game','dependence_group','ancestry_tokens','generation')} for r in all_records],
        registered_targets=targets,audit=audit,labels_present=False,models_fitted=False)
    partitions['hash']=digest(partitions);immutable(out/'datasets/partitions.json',partitions)
    immutable(out/'datasets/overlap-audit.json',audit)
    immutable(out/'sources/provenance.json',dict(sources=provenance,reused_immutable_sources=True,
        new_network_acquisition=False,original_licenses_and_attribution_preserved=True))
    print('C14 PARTITIONS FROZEN',len(all_records),dict(assigned),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    run(parser.parse_args().out)
