"""Before/after native special-move experiments with explicit evidence controls."""
import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path

import chess

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves, Cycle8Options
from pln_chess.cycle10.temporal import replay, native_options
from pln_chess.pln import Runtime
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    runtime = Runtime(timeout=180)
    frozen = PromotionModel.load(ROOT / 'artifacts/cycle10/model/C10-default.json', runtime)
    candidate = PromotionModel.load(out / 'model/C11-special-local.json', runtime)
    options = Cycle8Options(mode='operational', timeout_seconds=180, max_native_invocations=100000)

    def configured(history, model, suppressed=()):
        setting = replace(options, suppress_families=tuple(suppressed))
        if history is None:
            return setting, None
        receipt = replay(**{**history, 'model_version': model.version, 'runtime_version': runtime.version})
        return native_options(receipt, setting), receipt

    def query(fen, notation, model, history=None, suppressed=(), mode=None):
        position = Position.from_fen(fen)
        move = find_move(position, notation)
        assert move is not None
        settings, receipt = configured(history, model, suppressed)
        if mode:
            settings = replace(settings, mode=mode)
        result = infer_moves(position, model, settings, runtime, [move])
        item = result['candidates'][0]
        return dict(candidate=item, native_proof_id=digest(item['proof_trace']), temporal_transport=receipt,
            model_version=model.version, runtime_version=runtime.version,
            reference_legal=chess.Move.from_uci(notation) in chess.Board(fen).legal_moves,
            execution={k: result[k] for k in ('native_invocations','scheduled_invocations','elapsed_seconds','truncated','error')})

    def full(fen, model, history):
        position = Position.from_fen(fen)
        settings, receipt = configured(history, model)
        result = infer_moves(position, model, settings, runtime)
        expected = {m.uci() for m in chess.Board(fen).legal_moves}
        predicted = {c['move'] for c in result['candidates'] if c['classification'] == 'supported-legal'}
        false_legal = sorted(predicted-expected)
        false_illegal = sorted(c['move'] for c in result['candidates'] if c['classification'] == 'supported-illegal' and c['move'] in expected)
        return dict(result=result, temporal_transport=receipt, expected=sorted(expected), predicted=sorted(predicted),
            exact=expected == predicted, false_legal=false_legal, false_illegal=false_illegal,
            unknown_legal=sorted(expected-predicted))

    ep_results = []
    for case in read_gzip(out / 'legal/en-passant-before.json.xz'):
        fen, notation = case['fixture']['fen'], case['candidate']
        history = case['supplied_prefix']['input']
        before = query(fen, notation, frozen, history)
        after = query(fen, notation, candidate, history)
        assert before['candidate']['raw_stv'] == case['frozen_supplied_history']['candidate']['raw_stv']
        controls = {family: query(fen, notation, candidate, history, (family,)) for family in ('geometry','destination','ray','boundary','exposure','temporal')}
        ep_results.append(dict(fixture=case['fixture'], move=notation, before=before, after=after,
            original_complete_game=case['complete_source_game'], original_cause=case['cause'],
            without_history=query(fen, notation, candidate), without_new_learning=query(fen, notation, frozen, history),
            evidence_removal=controls, full_after=full(fen, candidate, history),
            strict=query(fen, notation, candidate, history, mode='strict'),
            experimental=query(fen, notation, candidate, history, mode='experimental'),
            evidence_added=sorted(set(after['candidate']['evidence_ids'])-set(before['candidate']['evidence_ids'])),
            supported_after=after['candidate']['classification'] == 'supported-legal',
            caveat='Known prior-cycle development case, not an untouched test. The new checkpoint remains experimental.'))
    pack(out / 'legal/en-passant-after.json.xz', ep_results)
    holdouts = []
    for row in read_json(out / 'datasets/legal-curriculum.json')['examples']:
        if row['split'] != 'holdout':
            continue
        before = query(row['fen'], row['move'], frozen, row['history_input'])
        after = query(row['fen'], row['move'], candidate, row['history_input'])
        holdouts.append(dict(example=row, before=before, after=after,
            no_history=query(row['fen'], row['move'], candidate),
            removed_temporal=query(row['fen'], row['move'], candidate, row['history_input'], ('temporal',)),
            full_after=full(row['fen'], candidate, row['history_input'])))
    pack(out / 'legal/independent-holdouts.json.xz', holdouts)
    interventions = []
    for case in read_gzip(ROOT / 'artifacts/cycle10/temporal/historical-abstentions.json.xz'):
        history = case['intervention_history']['input']
        fen, notation = case['intervention_fen'], case['move']
        before = query(fen, notation, frozen, history)
        after = query(fen, notation, candidate, history)
        interventions.append(dict(cohort=case['cohort'], split=case['split'], fixture=case['fixture'],
            original_fen=case['original_fen'], intervention_fen=fen, move=notation,
            history_input=history, before=before, after=after,
            without_history=query(fen, notation, candidate),
            removed_temporal=query(fen, notation, candidate, history, ('temporal',)),
            full_after=full(fen, candidate, history),
            original_full_position_proof=case['original_full_position_proof'],
            provenance='Reused declared synthetic predecessor or imported-rights intervention; never claimed as recovered original history.'))
    pack(out / 'legal/historical-interventions.json.xz', interventions)

    def summarize(records, reference):
        before = Counter(r['before']['candidate']['classification'] for r in records)
        after = Counter(r['after']['candidate']['classification'] for r in records)
        errors = []
        for index, record in enumerate(records):
            expected = reference(record)
            classification = record['after']['candidate']['classification']
            if (classification == 'supported-legal' and not expected) or (classification == 'supported-illegal' and expected):
                errors.append(dict(index=index, expected=expected, classification=classification))
        return dict(cases=len(records), before=dict(before), after=dict(after), errors=errors,
            recovered_legal=sum(r['before']['candidate']['classification'] != 'supported-legal' and
                r['after']['candidate']['classification'] == 'supported-legal' and reference(r) for r in records),
            full_position_exact_after=sum(r['full_after']['exact'] for r in records),
            full_position_false_legal=sum(len(r['full_after']['false_legal']) for r in records),
            full_position_false_illegal=sum(len(r['full_after']['false_illegal']) for r in records),
            full_position_incomplete=sum(r['full_after']['result']['truncated'] for r in records))

    by_split = defaultdict(list)
    for record in interventions:
        by_split[record['cohort']+'/'+record['split']].append(record)
    summary = dict(schema=11, frozen_model=frozen.version, candidate_model=candidate.version,
        en_passant=summarize(ep_results, lambda r: True),
        independent_holdouts=summarize(holdouts, lambda r: r['example']['reference_legal']),
        historical_interventions={k:summarize(v, lambda r: r['after']['reference_legal']) for k,v in by_split.items()},
        en_passant_removal_controls={r['fixture']['id']:{k:v['candidate']['classification'] for k,v in r['evidence_removal'].items()} for r in ep_results},
        temporal_removal_supported=sum(r['removed_temporal']['candidate']['classification'] == 'supported-legal' for r in holdouts+interventions),
        strict_en_passant=[r['strict']['candidate']['classification'] for r in ep_results],
        experimental_en_passant=[r['experimental']['candidate']['classification'] for r in ep_results],
        accepted_default_changed=False, experimental_model_promoted=False,
        thresholds_changed=False, new_operator_enabled=False,
        limits='Finite controlled tests and known development cases. Full frozen/external regression outcomes are reported separately. History-free special moves still require evidence.')
    write_json(out / 'legal/summary.json', summary)
    print('Legal completion experiments complete', summary, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
