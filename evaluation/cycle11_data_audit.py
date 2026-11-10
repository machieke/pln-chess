"""Model-blind split, ancestry, geometry and historical-overlap audits."""
import argparse
from collections import defaultdict
import itertools
from pathlib import Path

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position, parse_square
from evaluation.cycle3 import read_gzip
from training.cycle10_overlap import all_symmetry_key
from scripts.cycle9_baseline import sha


def run(out):
    out = Path(out)
    data = read_gzip(out / 'datasets/field-queries.json.xz')
    expected = data.pop('hash')
    assert digest(data) == expected
    keys, groups, ancestry, raw = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(set)
    board_keys = {}
    seen_ids = set()
    for row in data['queries']:
        assert row['id'] not in seen_ids
        seen_ids.add(row['id'])
        fen, split = row['fen'], row['split']
        if fen not in board_keys:
            board_keys[fen] = all_symmetry_key(fen)
        keys[split].add(board_keys[fen])
        groups[split].add(row['dependence_group'])
        ancestry[split].update([row['dependence_group'], *row['transformation_lineage']])
        position = Position.from_fen(fen)
        origin, target = parse_square(row['piece_square']), parse_square(row['target_square'])
        piece = position.at(origin)
        dx, dy = target[0]-origin[0], (target[1]-origin[1])*(1 if piece.owner == 'White' else -1)
        raw[split].add((piece.kind, abs(dx), dy))
    comparisons = []
    for a, b in itertools.combinations(('train', 'calibration', 'test'), 2):
        comparisons.append(dict(left=a, right=b, whole_board_overlap=sorted(keys[a]&keys[b]),
            source_group_overlap=sorted(groups[a]&groups[b]), ancestry_overlap=sorted(ancestry[a]&ancestry[b]),
            shared_raw_relative_configurations=len(raw[a]&raw[b])))
    assert all(not any(c[k] for k in ('whole_board_overlap', 'source_group_overlap', 'ancestry_overlap')) for c in comparisons)
    controls = read_json(out / 'datasets/worked-controls.json')
    transfers = []
    for case in controls['transfers']:
        position = Position.from_fen(case['fen'])
        source, target = parse_square(case['source']), parse_square(case['target'])
        piece = position.at(source)
        raw_key = (piece.kind, abs(target[0]-source[0]), (target[1]-source[1])*(1 if piece.owner == 'White' else -1))
        transfers.append(dict(id=case['id'], raw_relative_configuration=list(raw_key),
            present_in_training=raw_key in raw['train'], whole_position_in_training=all_symmetry_key(case['fen']) in keys['train']))
    assert all(not t['present_in_training'] and not t['whole_position_in_training'] for t in transfers)
    legal = read_json(out / 'datasets/legal-curriculum.json')
    legal_keys = {split: {all_symmetry_key(r['fen']) for r in legal['examples'] if r['split'] == split}
                  for split in ('train', 'holdout')}
    assert not legal_keys['train'] & legal_keys['holdout']
    historical = defaultdict(set)
    paths = [ROOT / 'fixtures/dataset.json']
    for cycle in range(2, 11):
        paths.extend(p for p in (ROOT / f'artifacts/cycle{cycle}/dataset.json', ROOT / f'artifacts/cycle{cycle}/datasets/dataset.json') if p.exists())
    for path in paths:
        original = read_json(path)
        for fen in {r['fen'] for r in original.get('positions', [])+original.get('examples', []) if r.get('fen')}:
            historical[all_symmetry_key(fen)].add(str(path.relative_to(ROOT)))
    controlled_keys = {split: {board_keys[r['fen']] for r in data['queries'] if r['split'] == split
                              and r['metadata']['generator_family'] == 'controlled-relative-context'} for split in keys}
    controlled_historical = {split: sorted(controlled_keys[split] & historical.keys()) for split in controlled_keys}
    legal_training_historical = sorted(legal_keys['train'] & historical.keys())
    assert not legal_training_historical and not any(controlled_historical.values())
    receipt = dict(passed=True, field_dataset_hash=expected, legal_dataset_hash=legal['hash'],
        worked_controls_hash=controls['hash'], field_queries=len(data['queries']), unique_full_fens=len(board_keys),
        comparisons=comparisons, dedicated_transfers=transfers,
        controlled_historical_overlaps=controlled_historical, legal_training_historical_overlaps=legal_training_historical,
        legal_train_holdout_overlap=[], historical_dataset_hashes={str(p.relative_to(ROOT)): sha(p) for p in paths},
        method='All eight planar symmetries, owner swaps and translation-normalized piece configurations; conservative even where a transform is not a chess symmetry.',
        intentional_reuse='External field panels reuse registered Cycle 10 adaptation/calibration/test games in their original partitions. Those are new relation tasks on a previously observed corpus, not newly acquired games.',
        relative_transfer='Dedicated long-range configurations are absent as raw displacements in all field training. Shared pooled conditionals will be measured after ontology implementation; their pooling is a supplied assumption.')
    write_json(out / 'datasets/audit.json', receipt)
    print('Split and transfer audit passed', len(data['queries']), 'queries;', len(transfers), 'unseen configurations', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
