"""Read-only diagnosis of every recorded C7 promotion error."""
import argparse
from pathlib import Path
import chess
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle4.ontology import descriptors
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def run(out):
    out = Path(out)
    report = read_gzip(ROOT / 'artifacts/cycle7/evaluation/C7-learned-8-locked-cycle7-independent-games.json.xz')
    frozen = read_gzip(ROOT / 'artifacts/cycle7/evaluation/C7-frozen-cycle7-independent-games.json.xz')
    original = {(r['fixture'], r['move']): r for r in frozen['rows']}
    model = read_json(ROOT / 'artifacts/cycle7/model/C7-learned-8.json')
    ledger = read_gzip(ROOT / 'artifacts/cycle7/training/C7-learned-8-ledger.json.xz')
    evidence = {r['evidence_id']: r for r in ledger['records']}
    cases = []
    for row in report['rows']:
        false_legal = not row['label'] and row['classification'] == 'supported-legal'
        false_illegal = row['label'] and row['classification'] == 'supported-illegal'
        if not (false_legal or false_illegal):
            continue
        pos = Position.from_fen(row['fen']); move = find_move(pos, row['move']); obs = descriptors(pos, move)
        board = chess.Board(row['fen']); uci = chess.Move.from_uci(row['move'])
        h = model['hypotheses'][row['backoff']['rule_id']]
        sources = [evidence[e] for e in h['evidence_ids']]
        local = next(r for r in obs['relations'] if r['target'] == 'LocalAdmissibility')
        source_contexts = []
        for source in sources:
            p = source['payload']; target = next(t for t in p['targets'] if t['target'] == 'LocalAdmissibility')
            source_contexts.append({'evidence_id': source['evidence_id'], 'input': p['input'],
                 'dependence_group': p['dependence_group'], 'label': target['label'], 'descriptor': target['descriptor'],
                 'observation_tv': p['observation_tv'], 'source': p['source']})
        proof = [report['native_proof_dag'][i] for i in row['proof_refs']]
        assert digest(proof) == row['proof_id']
        assert move.promotion and row['backoff']['level_index'] == 2
        assert 'destination' not in h['descriptor'] and 'destination' in local['descriptor']
        case = {'id': row['fixture'] + ':' + row['move'], 'fen': row['fen'], 'move': row['move'],
            'promotion_target': move.promotion, 'color': pos.turn, 'mover_owner': pos.at(move.start).owner,
            'destination_owner': pos.at(move.end).owner if pos.at(move.end) else None,
            'capture': board.is_capture(uci), 'relative_geometry': obs['context']['geometry'],
            'destination_occupancy': obs['context']['destination'], 'destination_kind': obs['context']['destination_kind'],
            'king_exposure': {'self_check_tag': row['self_check'], 'in_check_before': board.is_check(),
                              'source': 'python-chess evaluation only; production receives no oracle result'},
            'history': {'castling_rights': pos.rights, 'en_passant': pos.ep, 'supplied_move_history': None,
                        'trust': 'FEN-only; no past-game legality proof'},
            'expected_legal': row['label'], 'actual_classification': row['classification'],
            'frozen_classification': original[(row['fixture'], row['move'])]['classification'],
            'truth_value': row['truth_value'], 'local_truth_value': row['local_truth_value'],
            'matched_rule_ids': row['rule_ids'], 'native_rule_ids': row['native_rule_ids'],
            'selected_hypothesis': h, 'evidence_ids': row['evidence_ids'], 'dependence_groups': row['dependence_groups'],
            'selected_evidence': source_contexts, 'native_proof': proof, 'proof_id': row['proof_id'],
            'policy_decision': report['policy_decisions'][row['decision_ref']],
            'original_descriptor': local['descriptor'], 'projected_descriptor': h['descriptor'],
            'first_incorrect_step': {'stage': 'C7 optional evidence selection, before native modus ponens',
                'selection': row['backoff'], 'lost_field': 'destination',
                'mechanism': 'Forward-empty positive evidence applied to an occupied forward destination' if false_legal else
                             'Diagonal-empty counterevidence applied to an opponent-occupied capture destination'},
            'root_causes': ['incorrect abstraction', 'missing destination context', 'incorrect rule applicability'],
            'not_established_as_cause': ['promotion-choice confusion', 'native TV arithmetic', 'missing history', 'king-safety composition'],
            'proof_status': row['proof_status'], 'runtime_version': row['runtime_version'], 'model_version': row['model_version']}
        cases.append(case)
    assert len(cases) == 8
    write_json(out / 'promotion-errors.json', {'source': 'Immutable delivered C7 learned-8 evaluation and training ledger',
        'cases': cases, 'false_legal': sum(not c['expected_legal'] for c in cases),
        'false_illegal': sum(c['expected_legal'] for c in cases),
        'scope': 'The shared mask is established separately for all eight records; two opposite evidence-pooling directions are retained.'})
    pack(out / 'proofs/promotion-errors.json.xz', cases)
    docs = ROOT / 'docs/cycle8'; docs.mkdir(parents=True, exist_ok=True)
    lines = ['# Promotion error forensics', '',
        'All eight C7 mistakes occur in `c7-french-709071-ply-56`: `' + cases[0]['fen'] + '`.', '',
        'Each case was checked independently against its recorded native graph and original training ledger. The first incorrect step is the optional level-2 evidence selection: it removes destination occupancy before applying a learned local conditional. Native inference faithfully propagates the selected, inapplicable conditional. This is not evidence of a faulty native truth-value operator.', '',
        '| Move | Reference | C7 learned | Frozen | Destination | First evidence mismatch |',
        '|---|---|---|---|---|---|']
    for c in cases:
        lines.append(f"| {c['move']} | {'legal' if c['expected_legal'] else 'illegal'} | {c['actual_classification']} | {c['frozen_classification']} | {c['destination_occupancy']} {c['destination_kind']} | {c['first_incorrect_step']['mechanism']} |")
    lines += ['', 'The four promotion choices have separate hypothesis IDs and evidence. Choice identity was retained, so these are not queen/rook/bishop/knight substitutions. The forward cases reuse positive empty-destination evidence; the diagonal cases reuse negative empty-destination evidence. Those two directions require distinct counterexamples even though the same projection removes the distinction.', '',
        'The position has no supplied history. Castling or en-passant provenance does not justify these decisions. The observed errors are not self-check errors. Destination piece identity and ownership must remain observable: in particular, the forward destination contains the opposing king. New training must distinguish local transition eligibility from post-move exposure instead of assigning every illegal label to movement.', '',
        'The [case inventory](../../artifacts/cycle8/promotion-errors.json) contains each FEN, move, target, orientation, occupancy, history, raw TV, selected hypothesis, original/projected descriptors, source evidence, dependence groups, policy node and full native graph. The [compressed copy](../../artifacts/cycle8/proofs/promotion-errors.json.xz) is lossless. Proposed fixes are evaluated separately; this forensic finding alone does not establish safe generalization.']
    (docs / 'promotion-error-analysis.md').write_text('\n'.join(lines) + '\n')
    return cases


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
