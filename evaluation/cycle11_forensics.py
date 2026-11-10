"""Read-only predevelopment census and reconstruction of known legal gaps."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.api import find_move, explain_move
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle7.model import key
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle10.temporal import replay_game
from pln_chess.pln import Runtime
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


def run(out):
    out = Path(out)
    runtime = Runtime(timeout=180)
    model = PromotionModel.load(ROOT / 'artifacts/cycle10/model/C10-default.json', runtime)
    data = read_json(ROOT / 'artifacts/cycle10/datasets/dataset.json')
    games = {g['id']: g for g in data['games']}
    paths = []
    for split in ('adversarial', 'special-moves'):
        paths.extend(('cycle9/' + split, p) for p in sorted((ROOT / 'artifacts/cycle9/evaluation').glob(f'operational-{split}-*.json.xz')))
    for split in ('synthetic-adversarial', 'external-test'):
        paths.extend(('cycle10/fen-only/' + split, p) for p in sorted((ROOT / 'artifacts/cycle10/evaluation').glob(f'frozen-operational-{split}-*.json.xz')))
    paths.extend(('cycle10/supplied-history/external-test', p) for p in sorted((ROOT / 'artifacts/cycle10/evaluation').glob('temporal-operational-external-test-*.json.xz')))
    inventory, proofs, proof_index, summaries, source_hashes = [], [], {}, defaultdict(Counter), {}
    for cohort, path in paths:
        report = read_gzip(path)
        relative = str(path.relative_to(ROOT))
        source_hashes[relative] = sha(path)
        summaries[cohort]['positions'] += len(report['positions'])
        summaries[cohort]['exact_positions'] += sum(p['exact'] for p in report['positions'])
        summaries[cohort]['candidates'] += len(report['rows'])
        for row_index, row in enumerate(report['rows']):
            summaries[cohort]['legal_candidates'] += row['label']
            summaries[cohort]['supported_legal'] += row['classification'] == 'supported-legal'
            if row['classification'] not in ('unknown', 'incomplete'):
                continue
            trace = [report['native_proof_dag'][i] for i in row['proof_refs']]
            assert digest(trace) == row['proof_id']
            refs = []
            for node in trace:
                identifier = digest(node)
                if identifier not in proof_index:
                    proof_index[identifier] = len(proofs)
                    proofs.append(node)
                refs.append(proof_index[identifier])
            inventory.append(dict(cohort=cohort, source_artifact=relative, source_row=row_index,
                row={**row, 'proof_refs': refs},
                interpretation='Unresolved legal candidate' if row['label'] else 'Unresolved negative candidate; not a false-legal classification'))
            summaries[cohort]['unresolved_legal' if row['label'] else 'unresolved_negative'] += 1
            summaries[cohort]['incomplete'] += row['classification'] == 'incomplete'
    pack(out / 'legal/unresolved-baseline.json.xz', dict(schema=11, inventory=inventory,
        native_proof_dag=proofs, source_hashes=source_hashes,
        scope='Complete unknown/incomplete census, including negative candidates, in all registered adversarial, special-move and external final cohorts. Original full-position native proofs retained.'))
    write_json(out / 'legal/unresolved-baseline-summary.json', dict(cohorts={k: dict(v) for k, v in summaries.items()},
        cases=len(inventory), native_nodes=len(proofs), source_hashes=source_hashes,
        schema='cycle11-unresolved-census-v1'))
    ledger = read_gzip(ROOT / 'artifacts/cycle7/training/C7-learned-8-ledger.json.xz')
    cases = []
    for identifier, notation in (('c10-position-00861', 'd5e6'), ('c10-position-01151', 'd5c6')):
        fixture = next(f for f in data['positions'] if f['id'] == identifier)
        game = games[fixture['source_game']]
        history = replay_game(game, fixture['ply'], model.version, runtime.version)
        complete = replay_game(game, len(game['moves']), model.version, runtime.version)
        assert history['resulting_fen'] == fixture['fen'] and complete['resulting_fen'] == game['final_fen']
        position = Position.from_fen(fixture['fen'])
        candidate = find_move(position, notation)
        obs = descriptors(position, candidate)
        local = next(r for r in obs['relations'] if r['target'] == 'LocalAdmissibility')
        learned = model.source_model().hypotheses.get(key(local['descriptor'], 0))
        evidence_ids = set(learned['evidence_ids']) if learned else set()
        inherited = [r for r in ledger['records'] if r['evidence_id'] in evidence_ids]
        with_history = explain_move(position, notation, model, runtime=runtime, temporal_evidence=history, mode='operational')
        fen_only = explain_move(position, notation, model, runtime=runtime, mode='operational')
        archived = next(r for r in inventory if r['cohort'] == 'cycle10/supplied-history/external-test'
                        and r['row']['fixture'] == identifier and r['row']['move'] == notation)
        assert with_history['candidate']['classification'] == archived['row']['classification'] == 'unknown'
        assert with_history['candidate']['raw_stv'] == archived['row']['truth_value']
        before = chess.Board(game['initial_fen'])
        for move in game['moves'][:fixture['ply']-1]:
            before.push_uci(move)
        last = chess.Move.from_uci(game['moves'][fixture['ply']-1])
        assert before.piece_type_at(last.from_square) == chess.PAWN
        assert abs(chess.square_rank(last.to_square)-chess.square_rank(last.from_square)) == 2
        before.push(last)
        assert before.fen(en_passant='fen') == fixture['fen']
        assert chess.Move.from_uci(notation) in before.legal_moves
        cases.append(dict(fixture=fixture, complete_source_game=game, complete_replay=complete,
            supplied_prefix=history, previous_double_pawn_move=last.uci(), candidate=notation,
            relative_observations=obs, original_exact_local_conditional=learned,
            inherited_training_records=inherited, frozen_fen_only=fen_only, frozen_supplied_history=with_history,
            original_full_position_proof=[proofs[i] for i in archived['row']['proof_refs']],
            original_full_position_proof_id=archived['row']['proof_id'],
            cause='Weak existing local conditional with zero-confidence inherited observation' if learned else 'Missing signed relative en-passant local conditional',
            temporal_eligibility_recognized=with_history['candidate']['temporal_evidence']['ep_truth_value'],
            oracle_scope='Offline reconstruction and labels only; production receives supplied events and observations.'))
    pack(out / 'legal/en-passant-before.json.xz', cases)
    write_json(out / 'legal/en-passant-before-summary.json', dict(cases=[dict(fixture=c['fixture']['id'], move=c['candidate'],
        cause=c['cause'], source_game=c['fixture']['source_game'], prefix_events=len(c['supplied_prefix']['events']),
        complete_game_events=len(c['complete_replay']['events']), local_conditional=c['original_exact_local_conditional'],
        inherited_observation_tvs=[r['payload']['observation_tv'] for r in c['inherited_training_records']],
        temporal_eligibility=c['temporal_eligibility_recognized'],
        local_truth_value=c['frozen_supplied_history']['candidate']['local_admissibility_truth_value']) for c in cases],
        checkpoint=model.version, accepted_checkpoint_modified=False))
    print('Predevelopment census and en-passant reconstruction complete', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
