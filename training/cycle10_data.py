"""Independent PGN corpus and separately labelled synthetic stress pairs.

All reference chess queries in this module are offline dataset operations.
Selection never observes a model prediction or calibrated score.
"""
import argparse
from collections import Counter, defaultdict
import io
from pathlib import Path
import random
import subprocess

import chess
import chess.pgn
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from training.cycle8_data import translation_key
from training.cycle9_data import PAIRS
from scripts.cycle9_baseline import sha


def canonical(fen):
    b=chess.Board(fen)
    return digest(' '.join(b.fen(en_passant='fen').split()[:4]))


def partition(opening):
    number=int(digest(['cycle10-opening-family',opening]),16)%5
    return 'external-adaptation' if number==0 else 'external-calibration' if number==1 else 'external-test'


def read_games(path, source, limit=1000):
    process=None
    if path.suffix=='.zst':
        process=subprocess.Popen(['zstd','-dc',str(path)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        stream=io.TextIOWrapper(process.stdout,encoding='utf-8-sig',errors='strict')
    else:stream=path.open(encoding='utf-8-sig')
    games=[];excluded=Counter();ordinal=0
    try:
        while len(games)<limit:
            game=chess.pgn.read_game(stream)
            if game is None:break
            ordinal+=1
            if game.errors:excluded['PGN-parse-error']+=1;continue
            if game.headers.get('Variant','Standard') not in ('Standard','Chess'):excluded['nonstandard-variant']+=1;continue
            if game.headers.get('Result','*')=='*':excluded['unfinished-record']+=1;continue
            b=game.board();initial=b.fen(en_passant='fen');moves=[];valid=b.is_valid()
            for move in game.mainline_moves():
                if move not in b.legal_moves:valid=False;break
                moves.append(move.uci());b.push(move)
                if not b.is_valid():valid=False;break
            if not valid:excluded['invalid-game-transition']+=1;continue
            if len(moves)<30:excluded['less-than-30-plies']+=1;continue
            content=digest([initial,moves]);opening=game.headers.get('ECO')
            if not opening or opening=='?':opening='moves/'+'/'.join(moves[:4])
            else:opening=opening[:3]
            games.append(dict(id='c10-game-'+content[:24],content_hash=content,source_collection=source,
                original_game_identifier=game.headers.get('Site') or f'{source}/record/{ordinal}',archive_ordinal=ordinal,
                headers=dict(game.headers),initial_fen=initial,moves=moves,final_fen=b.fen(en_passant='fen'),complete=True,
                completion_scope='Complete published PGN record with declared result; resignation/adjudication need not be a rules-terminal position.',
                opening_family=opening,split=partition(opening),legal_replay_verified=True))
    finally:
        stream.close()
        if process:
            process.terminate();process.wait()
    return games,dict(records_read=ordinal,valid_complete_records=len(games),excluded=dict(excluded),scan_limit=limit)


def context(board,ply):
    pieces=board.piece_map();legal=list(board.legal_moves);counts=Counter(p.piece_type for p in pieces.values())
    nonpawn={p.piece_type for p in pieces.values() if p.piece_type not in (chess.PAWN,chess.KING)}
    phase='opening' if ply<=24 else 'endgame' if len(pieces)<=10 else 'early-middlegame' if ply<=50 else 'middlegame'
    endgame='pawn' if not nonpawn else 'rook' if nonpawn<={chess.ROOK} else 'minor' if nonpawn<={chess.BISHOP,chess.KNIGHT} else 'mixed'
    attacked=sum(bool(board.attackers(not p.color,s)) for s,p in pieces.items())
    multi=sum(len(board.attackers(not p.color,s))>=2 for s,p in pieces.items())
    pins=sum(board.is_pinned(p.color,s) for s,p in pieces.items())
    kingmoves=sum(board.piece_at(m.from_square).piece_type==chess.KING for m in legal)
    discoveries=0
    for move in legal:
        if not board.gives_check(move):continue
        after=board.copy(stack=False);after.push(move)
        if any(s!=move.to_square for s in after.checkers()):discoveries+=1
    return dict(phase=phase,material_count=len(pieces),endgame_type=endgame if phase=='endgame' else None,
        legal_move_count=len(legal),attacked_pieces=attacked,multiple_attacked_pieces=multi,pinned_pieces=pins,
        discovered_check_opportunities=discoveries,king_legal_moves=kingmoves,restricted_king_mobility=kingmoves<=1,
        in_check=board.is_check(),double_check=len(board.checkers())>=2,
        castling_opportunities=sum(board.is_castling(m) for m in legal),ep_opportunities=sum(board.is_en_passant(m) for m in legal),
        promotion_opportunities=sum(bool(m.promotion) for m in legal),
        promotion_race=any(p.piece_type==chess.PAWN and chess.square_rank(s) in (1,6) for s,p in pieces.items()),
        tactical_density=(attacked+pins+discoveries)/max(1,len(pieces)))


def generate(out):
    out=Path(out);cfg=read_json(ROOT/'configs/cycle10.json');manifest=read_json(out/'sources/manifest.json')
    historical=set();historic_files={};historical_exact=set();historical_canonical=set()
    paths=[ROOT/'fixtures/dataset.json']
    for cycle in range(2,10):
        paths += [p for p in (ROOT/f'artifacts/cycle{cycle}/dataset.json',ROOT/f'artifacts/cycle{cycle}/datasets/dataset.json') if p.exists()]
    for path in paths:
        d=read_json(path);historic_files[str(path.relative_to(ROOT))]=sha(path)
        for row in d.get('positions',[])+d.get('examples',[]):
            if not row.get('fen'):continue
            historical.add(translation_key(row['fen']));historical_exact.add(row['fen']);historical_canonical.add(canonical(row['fen']))
    pools=[];source_audits={};duplicates=[];seen_games={}
    for source in manifest['sources']:
        spec=source['source'];path=out/'sources'/spec['id']/spec['filename']
        assert sha(path)==source['downloads']['data']['sha256']
        games,audit=read_games(path,spec['id']);source_audits[spec['id']]=audit
        for game in games:
            if game['content_hash'] in seen_games:
                duplicates.append(dict(game=game['id'],source=spec['id'],previous_source=seen_games[game['content_hash']]))
            else:seen_games[game['content_hash']]=spec['id'];pools.append(game)
        print('parsed',spec['id'],audit,flush=True)
    used={};positions=[];chosen_games=[];excluded=Counter();selected_counts=Counter();relative_family_counts=defaultdict(Counter)
    def add(board,split,family,group,source_game=None,**extra):
        fen=board.fen(en_passant='fen');key=translation_key(fen)
        if key in historical:excluded['historical-whole-position-equivalent']+=1;return None
        if key in used:excluded['repeated-whole-position-equivalent']+=1;return None
        p=Position.from_fen(fen);moves=list(candidates(p));expected={m.uci() for m in board.legal_moves}
        missing=sorted(expected-{m.notation for m in moves})
        item=dict(id=f'c10-position-{len(positions):05}',fen=fen,split=split,family=family,structural_family=family,
            source_game=source_game,dependence_group=group,translation_key=key,exact_fen_hash=digest(fen),canonical_hash=canonical(fen),
            candidate_count=len(moves),candidate_generation_missing=missing,unknown_squares=[],
            promotion_candidates=sum(bool(m.promotion) for m in moves),**extra)
        positions.append(item);used[key]=item['id'];return item
    for game in sorted(pools,key=lambda g:g['content_hash']):
        source=game['source_collection'];split=game['split'];target=cfg['games_per_source'][split]
        if selected_counts[source,split]>=target:continue
        b=chess.Board(game['initial_fen']);available=[]
        for ply,notation in enumerate(game['moves'],1):
            b.push_uci(notation)
            if ply<8 or b.is_game_over():continue
            # Special opportunities are an offline structural stratum, never a prediction filter.
            special=b.has_legal_en_passant() or any(b.is_castling(m) or m.promotion for m in b.legal_moves)
            available.append((ply,b.fen(en_passant='fen'),special))
        n=cfg['positions_per_game'][split]
        if len(available)<n:excluded['too-few-sampling-points']+=1;continue
        special=[i for i,(_,_,yes) in enumerate(available) if yes][:2]
        targets=special+[round(q*(len(available)-1)/(n-len(special)-1)) for q in range(n-len(special))]
        selected=[];attempted=set()
        for target_index in targets:
            for index in sorted(range(len(available)),key=lambda i:(abs(i-target_index),i)):
                if index in attempted:continue
                attempted.add(index);ply,fen,_=available[index];board=chess.Board(fen)
                extra=context(board,ply)
                fixture=add(board,split,'opening/'+game['opening_family'],game['id'],source_game=game['id'],
                    source_collection=source,ply=ply,opening_family=game['opening_family'],history_completeness='complete-published-game-prefix',
                    original_game_identifier=game['original_game_identifier'],**extra)
                if fixture:selected.append(fixture['id']);break
        if len(selected)!=n:
            # Keep all selected observations and report the registered sampling shortfall honestly.
            excluded['game-position-quota-shortfall']+=1
        if selected:
            game={**game,'sampled_fixtures':selected};chosen_games.append(game);selected_counts[source,split]+=1
            for identifier in selected:relative_family_counts[split][game['opening_family']]+=1
    for source in source_audits:
        for split,n in cfg['games_per_source'].items():
            if selected_counts[source,split]!=n:raise ValueError(f'Source quota unmet: {source} {split} {selected_counts[source,split]}/{n}')
    pairs=[];rng=random.Random(cfg['seed'])
    for family,fen,focus,square,symbol,label_a,label_b in PAIRS:
        for repeat in range(cfg['adversarial_pairs_per_family']):
            for attempt in range(20000):
                a=chess.Board(fen);b=a.copy();b.set_piece_at(chess.parse_square(square),chess.Piece.from_symbol(symbol) if symbol else None)
                for j in range(2+repeat%4):
                    occupied=set(a.piece_map())|set(b.piece_map())|{chess.parse_square(focus[:2]),chess.parse_square(focus[2:4]),chess.parse_square(square)}
                    choices=[s for s in chess.SQUARES if s not in occupied and chess.square_rank(s) in (1,2,5,6)]
                    s=rng.choice(choices);piece=chess.Piece(chess.KNIGHT if j%2 else chess.PAWN,bool(j%2));a.set_piece_at(s,piece);b.set_piece_at(s,piece)
                move=chess.Move.from_uci(focus)
                if not all(x.is_valid() and not x.is_game_over() for x in (a,b)):continue
                if (move in a.legal_moves,move in b.legal_moves)!=(label_a,label_b):continue
                keys=[translation_key(x.fen()) for x in (a,b)]
                if keys[0]==keys[1] or any(k in historical or k in used for k in keys):continue
                group=f'c10-stress-{family}-{repeat}'
                items=[add(x,'synthetic-adversarial',family,group,focus_move=focus,pair_side=side,
                           source_collection='synthetic-controlled-edit',history_completeness='unknown') for x,side in ((a,'a'),(b,'b'))]
                assert all(items)
                pairs.append(dict(id=group,fixtures=[x['id'] for x in items],focus_move=focus,edit=dict(square=square,piece=symbol),expected_labels=[label_a,label_b]))
                break
            else:raise RuntimeError('Cannot create stress pair '+family)
    family_sets={split:set(counts) for split,counts in relative_family_counts.items()}
    cross=[(a,b,sorted(family_sets[a]&family_sets[b])) for a in family_sets for b in family_sets if a<b]
    assert all(not overlap for _,_,overlap in cross)
    audit=dict(historical_datasets=historic_files,historical_geometry_keys=len(historical),historical_exact_fens=len(historical_exact),
        historical_canonical_keys=len(historical_canonical),excluded=dict(excluded),duplicate_games=duplicates,source_scan=source_audits,
        selected_game_counts={source:{split:selected_counts[source,split] for split in cfg['games_per_source']} for source in source_audits},
        exact_fen_unique=len({p['fen'] for p in positions})==len(positions),canonical_unique=len({p['canonical_hash'] for p in positions})==len(positions),
        geometry_unique=len(used)==len(positions),historical_geometry_overlap=0,cross_split_opening_overlap=cross,
        opening_families={k:sorted(v) for k,v in family_sets.items()},
        scope='Game identities and full-position equivalence excluded; recurring local motifs are expected transfer, not independent evidence. Opening families partitioned globally. Human identities and engine-opening reuse may remain correlated.')
    result=dict(schema=10,registration_hash=digest(cfg),source_manifest_hash=digest(manifest),positions=positions,games=chosen_games,
        examples=[],counterfactual_pairs=pairs,counts=dict(Counter(p['split'] for p in positions)),
        game_counts=dict(Counter(g['split'] for g in chosen_games)),overlap_audit=audit,
        license='CC-BY-SA-4.0',attribution='../sources/ATTRIBUTION.txt',
        oracle=dict(version=chess.__version__,scope='Offline validity, structural stratification and reference labels only. No inference labels supplied.'))
    result['hash']=digest(result);write_json(out/'datasets/dataset.json',result);write_json(out/'datasets/overlap-audit.json',audit)
    write_json(out/'datasets/manifest.json',dict(hash=result['hash'],registration_hash=result['registration_hash'],counts=result['counts'],game_counts=result['game_counts'],
        source_counts=dict(Counter(p['source_collection'] for p in positions)),complete_games=len(chosen_games),positions=len(positions),
        diversity={field:dict(Counter(str(p.get(field)) for p in positions if p['source_game'])) for field in ('phase','endgame_type','opening_family','material_count','castling_opportunities','ep_opportunities','promotion_opportunities','pinned_pieces','multiple_attacked_pieces','discovered_check_opportunities','restricted_king_mobility')},
        candidate_generator_missing=[dict(id=p['id'],missing=p['candidate_generation_missing']) for p in positions if p['candidate_generation_missing']]))
    print(result['counts'],result['hash'],flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);generate(p.parse_args().out)
