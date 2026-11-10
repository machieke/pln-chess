"""Registered offline relation labels and structural holdouts for Cycle 11.

The reference library occurs only on the training/evaluation side. No model is
loaded or queried while sampling. Whole-position transformations are audited.
"""
import argparse
from collections import Counter, defaultdict
import itertools
from pathlib import Path
import random

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.spatial import ray_cells
from evaluation.cycle7_io import pack
from training.cycle10_data import translation_key

KINDS = {'Pawn': chess.PAWN, 'Knight': chess.KNIGHT, 'Bishop': chess.BISHOP,
         'Rook': chess.ROOK, 'Queen': chess.QUEEN, 'King': chess.KING}
DESTINATIONS = ('empty', 'friend-pawn', 'foe-pawn', 'friend-knight', 'foe-knight', 'friend-king', 'foe-king')


def labels(board, origin, target):
    """Distinct reference tasks; attack maps include pinned/friendly coverage."""
    piece = board.piece_at(origin)
    assert piece is not None and origin != target
    destination = board.piece_at(target)
    bare = chess.Board(None)
    bare.set_piece_at(origin, piece)
    geometric = target in bare.attacks(origin)
    attack = target in board.attacks(origin)
    defense = attack if destination and destination.color == piece.color else None
    exposure = attack if destination and destination.piece_type == chess.KING and destination.color != piece.color else None
    pseudo = board.copy(stack=False)
    pseudo.turn = piece.color
    promotion = chess.QUEEN if piece.piece_type == chess.PAWN and chess.square_rank(target) in (0, 7) else None
    move = chess.Move(origin, target, promotion=promotion)
    special = ((piece.piece_type == chess.KING and chess.square_rank(origin) == chess.square_rank(target)
                and abs(chess.square_file(target)-chess.square_file(origin)) == 2)
               or (piece.piece_type == chess.PAWN and target == board.ep_square
                   and abs(chess.square_file(target)-chess.square_file(origin)) == 1))
    mobility = None if special else (pseudo.is_pseudo_legal(move) and not (destination and destination.piece_type == chess.KING))
    return dict(geometry=geometric, attack=attack, defense=defense, mobility=mobility, **{'king-exposure': exposure})


def offsets(kind, split):
    if kind in ('Rook', 'Bishop', 'Queen'):
        distances = (1, 2, 4) if split == 'train' else (3, 5, 6, 7)
        result = [(dx*n, dy*n) for dx, dy in itertools.product((-1, 0, 1), repeat=2)
                  if (dx, dy) != (0, 0) for n in distances]
        result += [(sx*a, sy*b) for a, b in ((1, 2), (2, 1), (2, 3), (3, 2)) for sx, sy in itertools.product((-1, 1), repeat=2)]
        return result
    return [(dx, dy) for dx, dy in itertools.product(range(-2, 3), repeat=2) if (dx, dy) != (0, 0)]


def controlled_board(kind, offset, destination, obstruction, rng):
    owner = rng.choice((chess.WHITE, chess.BLACK))
    dx, dy = offset[0], offset[1] if owner else -offset[1]
    origins = [(x, y) for x, y in itertools.product(range(8), repeat=2)
               if 0 <= x+dx < 8 and 0 <= y+dy < 8 and (kind != 'Pawn' or y not in (0, 7))]
    if not origins:
        return None
    x, y = rng.choice(origins)
    source, target = chess.square(x, y), chess.square(x+dx, y+dy)
    ray = [chess.square(a, b) for a, b in ray_cells((x, y), (x+dx, y+dy))]
    if obstruction != 'empty' and not ray:
        return None
    board = chess.Board(None)
    board.set_piece_at(source, chess.Piece(KINDS[kind], owner))
    if destination != 'empty':
        side, target_kind = destination.split('-')
        color = owner if side == 'friend' else not owner
        piece_type = {'pawn': chess.PAWN, 'knight': chess.KNIGHT, 'king': chess.KING}[target_kind]
        if kind == 'King' and piece_type == chess.KING and color == owner:
            return None
        if piece_type == chess.PAWN and chess.square_rank(target) in (0, 7):
            return None
        board.set_piece_at(target, chess.Piece(piece_type, color))
    protected = {source, target, *ray}
    if obstruction != 'empty':
        sq = rng.choice(ray)
        board.set_piece_at(sq, chess.Piece(chess.KNIGHT, owner if obstruction == 'friend' else not owner))
    choices = [sq for sq in chess.SQUARES if sq not in protected]
    rng.shuffle(choices)
    for color in (chess.WHITE, chess.BLACK):
        if board.king(color) is None:
            board.set_piece_at(choices.pop(), chess.Piece(chess.KING, color))
    # Distinct distant contexts are generated directly, not transformed copies.
    for _ in range(3):
        board.set_piece_at(choices.pop(), chess.Piece(rng.choice((chess.KNIGHT, chess.BISHOP, chess.ROOK)), rng.choice((chess.WHITE, chess.BLACK))))
    attacked = [color for color in (chess.WHITE, chess.BLACK)
                if board.is_attacked_by(not color, board.king(color))]
    board.turn = attacked[0] if len(attacked) == 1 else owner
    board.fullmove_number = 20
    return board, source, target


def generate(out):
    out = Path(out)
    config = read_json(ROOT / 'configs/cycle11.json')
    seen = set()
    records, rejected = [], Counter()

    def record(board, origin, target, split, group, source, ancestry=(), metadata=None):
        fen = board.fen(en_passant='fen')
        payload = dict(fen=fen, piece_square=chess.square_name(origin), target_square=chess.square_name(target),
            split=split, source=source, dependence_group=group, transformation_lineage=list(ancestry),
            labels=labels(board, origin, target), observation_confidence=config['training_observation_confidence'],
            reference_board_valid=board.is_valid(), reference_board_status=int(board.status()),
            metadata=metadata or {})
        payload['id'] = 'c11query:' + digest(payload)[:24]
        records.append(payload)

    for split, groups, base in (('train', 4, 0), ('calibration', 2, 1000), ('test', 2, 2000)):
        for group_index in range(groups):
            seed = config['seed'] + base + group_index
            rng = random.Random(seed)
            group = f'c11-controlled-{split}-{seed}'
            for kind in KINDS:
                for displacement, destination, obstruction in itertools.product(offsets(kind, split), DESTINATIONS, ('empty', 'friend', 'foe')):
                    for attempt in range(16):
                        generated = controlled_board(kind, displacement, destination, obstruction, rng)
                        if generated is None:
                            rejected['outside_structural_domain'] += 1
                            break
                        board, origin, target = generated
                        canonical = translation_key(board.fen(en_passant='fen'))
                        if canonical in seen:
                            rejected['whole_board_symmetry_duplicate'] += 1
                            continue
                        seen.add(canonical)
                        record(board, origin, target, split, group, 'synthetic-relative-context/'+group,
                            metadata=dict(kind=kind, owner_relative_displacement=list(displacement),
                                requested_destination=destination, requested_obstruction=obstruction,
                                generator_seed=seed, generator_family='controlled-relative-context',
                                canonical_hash=canonical,
                                validity_scope='Static relational query; invalid full-game states are explicitly marked and excluded from legal-play claims.'))
                        break
                    else:
                        raise RuntimeError('Could not produce a distinct controlled query')
    controlled_count = len(records)
    corpus = read_json(ROOT / 'artifacts/cycle10/datasets/dataset.json')
    external_selection = []
    for source in sorted({g['source_collection'] for g in corpus['games']}):
        for split, old_split, n in (('train', 'external-adaptation', 4), ('calibration', 'external-calibration', 2), ('test', 'external-test', 4)):
            games = sorted([g for g in corpus['games'] if g['split'] == old_split and g['source_collection'] == source], key=lambda g: digest(g['id']))[:n]
            for game in games:
                fixtures = sorted([f for f in corpus['positions'] if f.get('source_game') == game['id']], key=lambda f: digest(f['id']))[:2]
                for fixture in fixtures:
                    board = chess.Board(fixture['fen'])
                    assert board.is_valid()
                    external_selection.append(dict(split=split, fixture=fixture['id'], source_game=game['id'], source=source))
                    for origin, piece in sorted(board.piece_map().items()):
                        targets = set(sorted([sq for sq in chess.SQUARES if sq != origin], key=lambda sq: digest([fixture['id'], origin, sq]))[:8])
                        targets.update(sq for sq, other in board.piece_map().items() if sq != origin and (other.color == piece.color or other.piece_type == chess.KING))
                        for target in sorted(targets):
                            if split == 'train' and piece.piece_type in (chess.ROOK, chess.BISHOP, chess.QUEEN):
                                distance = chess.square_distance(origin, target)
                                if distance not in (1, 2, 4):
                                    rejected['external_train_long_range_withheld'] += 1
                                    continue
                            record(board, origin, target, split, game['id'], 'published-game/'+source+'/'+game['id'],
                                ancestry=['opening/'+fixture['opening_family']],
                                metadata=dict(generator_family='external-game-panel', fixture=fixture['id'], source_collection=source,
                                    opening_family=fixture['opening_family'], ply=fixture['ply'], original_dataset_hash=corpus['hash']))
    groups = {split: {r['dependence_group'] for r in records if r['split'] == split} for split in ('train', 'calibration', 'test')}
    assert all(not groups[a] & groups[b] for a, b in itertools.combinations(groups, 2))
    external_games = {split: {r['source_game'] for r in external_selection if r['split'] == split} for split in groups}
    payload = dict(schema='field-query-dataset-v11', registration_hash=digest(config), queries=records,
        external_selection=external_selection, original_external_dataset_hash=corpus['hash'],
        oracle=dict(name='python-chess', version=chess.__version__, scope='Offline relation labels; no inference or ranking by any model.'),
        semantics=dict(geometry='Empty-board piece attack geometry', attack='Occupancy-aware attack map including pins and friendly occupied endpoints',
            defense='Attack-map protection of a friendly occupied endpoint; not legal recapture',
            mobility='Ordinary pseudo-legal transition, with a queen promotion witness where needed; king captures excluded; special historical transitions omitted',
            **{'king-exposure': 'One opposing source attacks this king under current occupancy; no global safety complement'}),
        generation=dict(controlled_queries=controlled_count, external_queries=len(records)-controlled_count, rejected=dict(rejected),
            generator_groups={k: sorted(v) for k, v in groups.items()}, external_games={k: sorted(v) for k, v in external_games.items()},
            transformed_copies_counted_as_independent=False, model_used_for_selection=False,
            contextual_validity='Static synthetic relations include explicitly marked non-game states; external panels are valid published states.'))
    payload['hash'] = digest(payload)
    pack(out / 'datasets/field-queries.json.xz', payload)
    counts = {}
    for split in groups:
        selected = [r for r in records if r['split'] == split]
        counts[split] = dict(queries=len(selected), groups=len(groups[split]),
            reference_valid=sum(r['reference_board_valid'] for r in selected),
            by_family={family: dict(Counter('positive' if r['labels'][family] else 'negative' for r in selected if r['labels'][family] is not None))
                       for family in ('geometry', 'attack', 'defense', 'mobility', 'king-exposure')})
    write_json(out / 'datasets/field-query-manifest.json', dict(schema=11, dataset_hash=payload['hash'], counts=counts,
        generation=payload['generation'], semantics=payload['semantics'], external_selection=external_selection,
        leakage=dict(source_group_overlap=False, controlled_whole_board_symmetry_duplicates_removed=True,
            external_partition='Inherited disjoint Cycle 10 game and opening partitions',
            relative_submotifs='Expected sharing of reusable local observations; a separate inference-time descriptor audit quantifies exact and pooled overlap.'),
        limits=['Synthetic queries are controlled structural contexts, not a random sample of chess games.',
                'Generator groups are declared evidence units; independent random seeds do not certify statistical independence.',
                'Relative geometry categories and distance pooling are supplied inductive biases.',
                'External sample is a small deterministic panel of the existing archive windows.']))
    print('Field dataset', payload['hash'], counts, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    generate(parser.parse_args().out)
