"""Registered explicit continuation selection and offline endpoint supervision.

This module never selects branches using a PLN prediction. The supplied engine
PV is one observed response, not exhaustive coverage or a production search.
"""
import argparse
from collections import Counter
from pathlib import Path
import time

import chess
import chess.engine

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha
from training.cycle13_labels import label, score_value, semantic_record


def source_board(plan):
    board = chess.Board(plan['history']['initial_fen'])
    for move in plan['history']['moves']:
        board.push_uci(move)
    assert board.fen(en_passant='fen') == plan['fen']
    return board


def select(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    source = read_json(out / 'datasets/source-pairs.json')
    labels = read_json(out / 'datasets/reference-labels.json')
    assert labels['source_hash'] == source['hash']
    indexed = {r['id']: r for r in labels['records']}
    eligible = []
    excluded = []
    for row in source['records']:
        candidates = indexed[row['id']]['evaluations'][-1]['candidates']
        by_move = {r['move']: r for r in candidates}
        if any(m not in by_move or len(by_move[m]['pv']) < 3 for m in row['moves']):
            excluded.append(dict(id=row['id'], reason='At least one supplied branch has fewer than three plies.'))
            continue
        branches = {channel: by_move[move]['pv'][:3] for channel, move in zip(('A', 'B'), row['moves'])}
        for channel, moves in branches.items():
            assert moves[0] == row['moves'][('A', 'B').index(channel)]
            board = source_board(row)
            for move in moves:
                assert chess.Move.from_uci(move) in board.legal_moves
                board.push_uci(move)
        eligible.append(dict(id=row['id'], fen=row['fen'], moves=row['moves'], history=row['history'],
            branches=branches, split=row['split'], source_game=row['source_game'],
            dependence_group=row['dependence_group'], source=row['source'],
            selection_rank=digest(['c13-explicit-temporal', row['id']]),
            response_source_evidence=indexed[row['id']]['evidence_id'],
            response_selection='First three plies of each explicit root PV at the registered 80,000-node offline search.',
            unexamined_responses='All responses outside these supplied lines remain unexamined; no exhaustive-response claim.',
            reference_legal_replay=True, independent_of_pln_predictions=True))
    selected = []
    for split, count in (('train', 36), ('calibration', 12), ('test', 12)):
        population = sorted((r for r in eligible if r['split'] == split), key=lambda r:r['selection_rank'])
        assert len(population) >= count, (split, len(population), count)
        selected.extend(population[:count])
    data = dict(schema='c13-explicit-temporal-plans-v1', source_hash=source['hash'],
        label_source_hash=labels['hash'], records=selected, excluded=excluded,
        selection_policy='Fixed hash order within the original source partitions; 36 train, 12 calibration, 12 test.',
        counts=dict(Counter(r['split'] for r in selected)), selected_using_reference_preference=False,
        maximum_supplied_branches_per_candidate=1, horizons=[2, 3])
    data['hash'] = digest(data)
    write_json(out / 'datasets/temporal-plans.json', data)
    return data


def run(out, binary=None):
    out = Path(out).resolve()
    data = select(out)
    reference = read_json(out / 'sources/stockfish-source.json')
    binary = Path(binary or ROOT / reference['binary_path']).resolve()
    binary_hash = sha(binary)
    assert binary_hash == reference['binary_sha256']
    config = read_json(ROOT / 'configs/cycle13.json')['reference_engine']
    engine = chess.engine.SimpleEngine.popen_uci(str(binary), timeout=120)
    records = []
    try:
        engine.configure({'Threads': config['threads'], 'Hash': config['hash_mib'], 'UCI_ShowWDL': True})
        for plan in data['records']:
            for horizon in (2, 3):
                identifier = plan['id'] + f'-ply{horizon}'
                path = out / 'temporal-labels' / (identifier + '.json')
                identity = dict(plan_hash=digest(plan), source_hash=data['hash'], reference_binary_sha256=binary_hash,
                    config=config, horizon=horizon, driver_sha256=sha(__file__))
                if path.exists():
                    record = read_json(path)
                    assert record['identity'] == identity, 'Use a new temporal label output directory'
                    records.append(semantic_record(record))
                    continue
                endpoints = {}
                root = source_board(plan)
                actor = root.turn
                for channel, moves in plan['branches'].items():
                    board = root.copy()
                    for move in moves[:horizon]:
                        board.push_uci(move)
                    endpoints[channel] = board
                evaluations = []
                for nodes in config['node_budgets']:
                    started = time.perf_counter()
                    candidates = []
                    for channel, board in endpoints.items():
                        engine.configure({'Clear Hash': None})
                        info = engine.analyse(board, chess.engine.Limit(nodes=nodes), game=object(), info=chess.engine.INFO_ALL)
                        pv = [m.uci() for m in info.get('pv', [])]
                        check = board.copy()
                        for move in pv:
                            check.push_uci(move)
                        candidates.append(dict(channel=channel, fen=board.fen(en_passant='fen'),
                            score=score_value(info['score'].pov(actor)), pv=pv,
                            depth=info.get('depth'), seldepth=info.get('seldepth'), nodes=info.get('nodes'),
                            engine_seconds=info.get('time'), lowerbound=bool(info.get('lowerbound')),
                            upperbound=bool(info.get('upperbound')),
                            wdl=list(info['wdl'].pov(actor)) if 'wdl' in info else None,
                            scope='Offline endpoint reference, original actor perspective; no production utility or native conclusion.'))
                    evaluations.append(dict(node_budget=nodes, candidates=candidates,
                        elapsed_seconds=time.perf_counter()-started))
                verdict, reason = label(evaluations, config)
                record = dict(id=identifier, identity=identity, plan_id=plan['id'], horizon=horizon,
                    label=verdict, reason=reason, evaluations=evaluations, split=plan['split'],
                    source_game=plan['source_game'], dependence_group=plan['dependence_group'],
                    temporal_context=dict(history=plan['history'], branches={k:v[:horizon] for k,v in plan['branches'].items()}),
                    original_actor='white' if actor else 'black', probability_of_correctness=None,
                    source='Separate fixed-node endpoint evaluations after the explicitly supplied branch.',
                    unexamined_responses=plan['unexamined_responses'], reference_selection_only=True)
                record['evidence_id'] = semantic_record(record)['evidence_id']
                write_json(path, record)
                records.append(semantic_record(record))
                print('TEMPORAL REFERENCE', identifier, verdict, flush=True)
    finally:
        engine.quit()
    payload = dict(schema='c13-offline-temporal-labels-v1', plan_hash=data['hash'], records=records,
        counts=dict(Counter(r['label'] for r in records)), horizons=dict(Counter(r['horizon'] for r in records)),
        no_production_reference_dependency=True,
        timing_scope='Raw files retain timing; semantic evidence excludes elapsed_seconds and engine_seconds only.')
    payload['hash'] = digest(payload)
    write_json(out / 'datasets/temporal-labels.json', payload)
    print('TEMPORAL REFERENCE COMPLETE', payload['counts'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    parser.add_argument('--binary')
    args = parser.parse_args()
    run(args.out, args.binary)
