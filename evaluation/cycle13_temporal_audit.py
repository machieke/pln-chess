"""Independent validation of explicit branches and endpoint supervision."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha
from training.cycle13_labels import label, semantic_record
from training.cycle13_temporal_sources import source_board


def checked(path):
    data=read_json(path)
    expected=data.pop('hash')
    assert digest(data)==expected,path
    data['hash']=expected
    return data


def run(out):
    out=Path(out)
    plans=checked(out/'datasets/temporal-plans.json')
    labels=checked(out/'datasets/temporal-labels.json')
    original=checked(out/'datasets/source-pairs.json')
    original_labels=checked(out/'datasets/reference-labels.json')
    source={r['id']:r for r in original['records']}
    source_labels={r['id']:r for r in original_labels['records']}
    assert plans['source_hash']==original['hash']
    assert plans['label_source_hash']==original_labels['hash']
    assert labels['plan_hash']==plans['hash']
    indexed={r['id']:r for r in plans['records']}
    assert len(indexed)==len(plans['records'])==60
    assert len({r['source_game'] for r in indexed.values()})==60
    endpoints={}
    for plan in indexed.values():
        parent=source[plan['id']]
        assert plan['response_source_evidence']==source_labels[plan['id']]['evidence_id']
        for field in ('fen','moves','history','split','source_game','dependence_group'):
            assert plan[field]==parent[field],(plan['id'],field)
        root=source_board(plan)
        for channel,moves in plan['branches'].items():
            assert len(moves)==3 and moves[0]==parent['moves'][('A','B').index(channel)]
            board=root.copy()
            for index,notation in enumerate(moves,1):
                move=chess.Move.from_uci(notation)
                assert move in board.legal_moves,(plan['id'],channel,index)
                board.push(move)
                endpoints[plan['id'],channel,index]=board.fen(en_passant='fen')
    seen=set()
    for record in labels['records']:
        plan=indexed[record['plan_id']]
        assert record['horizon'] in (2,3)
        assert record['id']==plan['id']+'-ply'+str(record['horizon'])
        assert record['id'] not in seen
        seen.add(record['id'])
        raw=read_json(out/'temporal-labels'/(record['id']+'.json'))
        assert record==semantic_record(raw)
        assert record['identity']['plan_hash']==digest(plan)
        assert record['identity']['label_policy_sha256']==sha(ROOT/'training/cycle13_labels.py')
        assert record['identity']['reference_binary_sha256']==read_json(out/'sources/stockfish-source.json')['binary_sha256']
        assert record['label']==label(record['evaluations'],record['identity']['config'])[0]
        assert record['original_actor']==('white' if source_board(plan).turn else 'black')
        for field in ('source_game','dependence_group','split'):
            assert record[field]==plan[field]
        for evaluation in record['evaluations']:
            assert [r['channel'] for r in evaluation['candidates']]==['A','B']
            for candidate in evaluation['candidates']:
                assert candidate['fen']==endpoints[plan['id'],candidate['channel'],record['horizon']]
                if candidate['score']['mate'] is not None:
                    assert candidate['score']['mate_outcome'] in ('win','loss')
    assert len(seen)==120
    groups=defaultdict(set)
    for r in labels['records']:
        groups[r['dependence_group']].add(r['split'])
    assert all(len(v)==1 for v in groups.values())
    receipt=dict(passed=True,plans=len(indexed),endpoint_comparisons=len(seen),source_games=60,
        dependent_horizons_per_game=2,partition_overlap=0,
        counts=dict(Counter(r['split'] for r in labels['records'])),
        explicit_branch_legal_replay=True,original_actor_score_perspective=True,
        terminal_mate_outcomes_preserved=True,normalized_label_identity_verified=True,
        plan_hash=plans['hash'],label_hash=labels['hash'],driver_sha256=sha(__file__),
        source_history_scope='Recorded source history plus explicit hypothetical continuations; other replies remain unexamined.',
        scope='Offline reference and selection integrity only; no production legality or native strategic conclusion.')
    write_json(out/'datasets/temporal-audit.json',receipt)
    print('TEMPORAL SOURCE AUDIT',receipt,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='artifacts/cycle13')
    run(parser.parse_args().out)
