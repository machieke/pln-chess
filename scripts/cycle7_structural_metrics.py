"""Postprocess stored results by structural motifs; never rerun or alter inference."""
import argparse
import hashlib
import json
import lzma
from collections import defaultdict
from pathlib import Path


def board(fen):
    cells = {}
    for y, rank in enumerate(fen.split()[0].split('/')):
        x = 0
        for char in rank:
            if char.isdigit():
                x += int(char)
            else:
                cells[(x, 7-y)] = char
                x += 1
    return cells


def motifs(row, cells):
    result = set(row['tags'])
    if not row['destination_exists']:
        return result | {'boundary'}
    move = row['move']
    start = (ord(move[0])-97, int(move[1])-1)
    end = (ord(move[2])-97, int(move[3])-1)
    occupant = cells.get(end)
    white = row['fen'].split()[1] == 'w'
    if occupant is None:
        result.add('empty-destination')
    elif occupant.isupper() == white:
        result.add('friendly-destination')
    else:
        result.add('opponent-destination')
        if occupant.lower() == 'k':
            result.add('opponent-king-destination')
    if 'en-passant' in result or (occupant and occupant.isupper() != white):
        result.add('capture-structure')
    if result & {'castling', 'en-passant', 'history'}:
        result.add('history-sensitive')
    dx, dy = end[0]-start[0], end[1]-start[1]
    if row['piece'] in ('Rook', 'Bishop', 'Queen') and (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
        steps = max(abs(dx), abs(dy))
        sx, sy = (dx > 0)-(dx < 0), (dy > 0)-(dy < 0)
        blocked = any((start[0]+n*sx, start[1]+n*sy) in cells for n in range(1, steps))
        result.add('ray-obstructed' if blocked else 'ray-clear')
    return result


def metrics(rows):
    tp = sum(r['label'] and r['classification'] == 'supported-legal' for r in rows)
    fp = sum(not r['label'] and r['classification'] == 'supported-legal' for r in rows)
    tn = sum(not r['label'] and r['classification'] == 'supported-illegal' for r in rows)
    fi = sum(r['label'] and r['classification'] == 'supported-illegal' for r in rows)
    legal = sum(r['label'] for r in rows)
    unknown = sum(r['classification'] == 'unknown' for r in rows)
    incomplete = sum(r['classification'] == 'incomplete' for r in rows)
    return {'candidates': len(rows), 'legal_candidates': legal, 'true_positive': tp,
            'false_positive': fp, 'true_negative': tn, 'false_illegal': fi,
            'unknown': unknown, 'incomplete': incomplete,
            'precision': tp/(tp+fp) if tp+fp else None,
            'recall': tp/legal if legal else None,
            'f1': 2*tp/(tp+fp+legal) if tp+fp+legal else None,
            'abstention_rate': (unknown+incomplete)/len(rows) if rows else 0,
            'self_check_false_legal': sum(r['self_check'] and not r['label'] and r['classification'] == 'supported-legal' for r in rows)}


def aggregate(path):
    with lzma.open(path, 'rt') as stream:
        report = json.load(stream)
    groups = defaultdict(list)
    boards = {}
    for row in report['rows']:
        if row['fen'] not in boards:
            boards[row['fen']] = board(row['fen'])
        for name in motifs(row, boards[row['fen']]):
            groups[name].append(row)
    result = {'all': metrics(report['rows']), 'motifs': {k: metrics(v) for k, v in sorted(groups.items())}}
    for key in ('candidates', 'true_positive', 'false_positive', 'true_negative', 'false_illegal', 'unknown', 'incomplete', 'precision', 'recall', 'f1', 'self_check_false_legal'):
        assert result['all'][key] == report['metrics'][key], (path, key)
    result.update(dataset_hash=report['dataset_hash'], model_version=report['model_version'],
                  artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--arm', help='Optional single-arm verification; omit for the complete report.')
    args = parser.parse_args()
    results = {}
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    scope = 'Overlapping structural categories derived from recorded evaluation tags and board occupancy. Opening-family metrics remain separate. No inference, training, or oracle queries are performed.'
    pattern = f'{args.arm}-summary.json' if args.arm else '*-summary.json'
    for summary in sorted((args.out/'evaluation').glob(pattern)):
        arm = summary.name.removesuffix('-summary.json')
        entries = json.loads(summary.read_text())
        cache = args.out/f'structural-check-{arm}.json'
        prior = json.loads(cache.read_text()) if cache.exists() else {}
        cached = prior.get('results', {}).get(arm, {})
        reuse = prior.get('passed') is True and prior.get('source_script_sha256') == source_hash and cached.keys() == entries.keys()
        if reuse:
            reuse = all(cached[k]['artifact_sha256'] == hashlib.sha256((args.out/v['artifact']).read_bytes()).hexdigest() for k, v in entries.items())
        if reuse:
            results[arm] = cached
        else:
            results[arm] = {split: aggregate(args.out/entry['artifact']) for split, entry in entries.items()}
        cache.write_text(json.dumps({'passed': True, 'source_script_sha256': source_hash, 'scope': scope,
                                    'results': {arm: results[arm]}}, indent=2, sort_keys=True)+'\n')
        print(arm, len(results[arm]), 'hash-verified reuse' if reuse else 'structural reports verified', flush=True)
    assert results
    destination = args.out/('structural-metrics.json' if not args.arm else f'structural-check-{args.arm}.json')
    destination.write_text(json.dumps({'passed': True, 'source_script_sha256': source_hash,
        'scope': scope,
        'results': results}, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
