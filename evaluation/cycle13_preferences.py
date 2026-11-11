"""Registered native preference studies on a fixed label-independent feature set."""
import argparse
import copy
from collections import Counter
from pathlib import Path

from pln_chess.common import digest, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle11.fields.inference import FieldOptions
from evaluation.cycle7_io import pack
from evaluation.cycle3 import read_gzip
from evaluation.cycle13_metrics import metrics, calibration, bootstrap
from training.cycle13_features import training_records
from training.cycle13_learning import train


ABSTRACTIONS = ('relational', 'attack-only', 'defense-only', 'mobility-only', 'exposure-only',
                'without-concepts', 'weaker-relative', 'full')


def panels(rows):
    groups = {split:[r for r in rows if r['split'] == split] for split in ('train','calibration','test')}
    test = groups['test']
    groups.update({
        'test-independent-games':[r for r in test if r['source_record']['source']['cohort'] == 'independent-games'],
        'test-external-tactical':[r for r in test if r['source_record']['source']['cohort'] == 'external-tactical'],
        'test-quiet':[r for r in test if r['source_record']['offline_reference']['quiet_pair']],
        'test-ambiguous':[r for r in test if r['label'] == 'no-demonstrated-preference'],
        'test-unknown-reference':[r for r in test if r['label'] == 'unknown'],
        'test-promotion':[r for r in test if any(r['source_record']['offline_reference']['promotions'])]})
    return groups


def run(out):
    out = Path(out)
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    assert read_json(out / 'datasets/audit.json')['passed']
    from pln_chess.cycle13.inference import infer_preferences, PreferenceNativeSession
    from pln_chess.cycle13.ontology import project, reverse_packet
    records = training_records(out)
    train_rows = [r for r in records if r['split'] == 'train']
    dataset_hash = digest(records)
    training_hash = digest(train_rows)
    runtime = Runtime(timeout=600)
    options = FieldOptions(timeout_seconds=600)

    def evaluate(model, population=records):
        session = PreferenceNativeSession(runtime)
        result = []
        for start in range(0, len(population), 64):
            batch = population[start:start+64]
            inferred = infer_preferences([r['packet'] for r in batch], model,
                runtime=runtime, options=options, session=session)
            assert not inferred['execution']['truncated']
            for row, comparison in zip(batch, inferred['comparisons']):
                assert digest(comparison['proof_trace']) == comparison['proof_id']
                assert not comparison['joint_proof_complete']
                result.append({**row, 'result':comparison})
        return result

    models = {}
    outcomes = {}
    summaries = {}
    for abstraction in ABSTRACTIONS:
        model = train(train_rows, runtime, out / 'learning' / abstraction,
            dataset_hash=training_hash, abstraction=abstraction, baseline_root=out)
        models[abstraction] = model
        rows = evaluate(model)
        outcomes[abstraction] = rows
        groups = panels(rows)
        summaries[abstraction] = dict(model_version=model.version, training_report=model.training_report,
            panels={name:metrics(population) for name,population in groups.items()},
            test_uncertainty=bootstrap(groups['test']))
        pack(out / 'preferences' / (abstraction + '.json.xz'), rows)
        print('PREFERENCE STUDY', abstraction, summaries[abstraction]['panels']['test'], flush=True)
    main = models['relational']
    main.export(out / 'model/C13-preference-relational.json')
    models['full'].export(out / 'model/C13-preference-full.json')
    groups = panels(outcomes['relational'])
    write_json(out / 'preferences/calibration.json', dict(model_version=main.version,
        panels={name:calibration(population) for name,population in groups.items()},
        calibrator_fitted=False, confidence_is_probability=False, inference_changed=False))
    write_json(out / 'preferences/summary.json', dict(passed=True, dataset_hash=dataset_hash, training_dataset_hash=training_hash,
        source_pairs=len(records), independent_groups=len({r['dependence_group'] for r in records}),
        model_version=main.version, panels=summaries['relational']['panels'],
        bootstrap={name:bootstrap(population) for name,population in groups.items() if name != 'train'},
        hypotheses=main.training_report['hypotheses'], native_training=main.training_report,
        cohorts=Counter(r['source_record']['source']['cohort'] for r in records),
        heldout_threshold_tuning=False, strategic_strength_claimed=False))
    write_json(out / 'ablations/immediate.json', dict(variants=summaries,
        reference_variant='relational', fixed_population=True, selected_by_heldout_performance=False,
        no_concept_comparison='The primary relational model and without-concepts arm use the same four field families; the full arm adds limited concept consequences.',
        causal_claim=False, temporal_ablation_report='ablations/temporal.json'))

    symmetry = []
    for row in records:
        normal = evaluate(main, [row])[0]['result']
        reversed_row = {**row, 'packet':reverse_packet(row['packet'])}
        swapped = evaluate(main, [reversed_row])[0]['result']
        expected = {'A-preferred':'B-preferred', 'B-preferred':'A-preferred',
                    'indeterminate':'indeterminate', 'incomplete':'incomplete'}[normal['status']]
        passed = (normal['rule_id'] == swapped['rule_id'] and swapped['status'] == expected
            and normal['channels']['A']['raw_stv'] == swapped['channels']['B']['raw_stv']
            and normal['channels']['B']['raw_stv'] == swapped['channels']['A']['raw_stv']
            and normal['evidence_ids'] == swapped['evidence_ids'])
        assert passed, row['id']
        symmetry.append(dict(id=row['id'], passed=passed, original=normal, reversed=swapped))
    pack(out / 'preferences/reversal.json.xz', symmetry)

    removals = []
    for row in groups['test']:
        reduced = copy.deepcopy(main)
        reduced.hypotheses.pop(row['result']['rule_id'], None)
        reduced.variant = 'C13-query-conditional-removed'
        result = evaluate(reduced, [row])[0]['result']
        assert result['status'] == 'indeterminate' and not result['conditional_proof_complete']
        removals.append(dict(id=row['id'], before=row['result'], after=result,
            removed_rule_id=row['result']['rule_id'], already_absent=not row['result']['conditional_proof_complete']))
    pack(out / 'preferences/removals.json.xz', removals)

    ledger = [__import__('json').loads(line) for line in (out / 'learning/relational/ledger.jsonl').read_text().splitlines()]
    ledger = {row['evidence_id']:row for row in ledger}
    eligible = [r for r in [*groups['test'], *groups['calibration']] if r['result']['conditional_proof_complete']]
    eligible.sort(key=lambda r:(r['split'] != 'test', r['result']['status'] not in ('A-preferred','B-preferred'), r['id']))
    transfers = []
    for row in eligible[:10]:
        result = row['result']
        training = [ledger[e] for e in result['evidence_ids'] if e in ledger]
        assert training
        assert all(e['payload']['dependence_group'] != row['dependence_group'] for e in training)
        feature = read_gzip(out / row['feature_artifact'])
        transfers.append(dict(id=row['id'], split=row['split'], source=row['source_record'],
            training_evidence=training, heldout_packet=project(row['packet'], 'relational'),
            native_preference=result, reference_label=row['label'], feature_artifact=row['feature_artifact'],
            endpoint_graphs={name:state['graph'] for name,state in feature['states'].items()},
            correct_direction=result['status'] == {'A':'A-preferred','B':'B-preferred'}.get(row['label']),
            selection_scope='Post-hoc inspectable illustrations, ordered by test partition and answered status. Full fixed-cohort metrics are reported separately.',
            independent_training_ancestry=True, exact_context_memorization=False))
    pack(out / 'transfer/demonstrations.json.xz', transfers)
    write_json(out / 'transfer/summary.json', dict(demonstrations=len(transfers), target=10,
        target_met=len(transfers) >= 10, correct_direction=sum(r['correct_direction'] for r in transfers),
        all_test_transfer=metrics([r for r in groups['test'] if r['result']['conditional_proof_complete']]),
        unselected_test_metrics=metrics(groups['test']), illustrative_selection_disclosed=True,
        rule_keys_are_relative=True, no_competitive_strength_claim=True))
    write_json(out / 'preferences/controls-summary.json', dict(reversal_cases=len(symmetry),
        reversal_passes=sum(r['passed'] for r in symmetry), removals=len(removals),
        removal_abstentions=len(removals), complete_joint_strategic_proofs=0))

    volume = []
    ordered = sorted(train_rows, key=lambda r:digest(['evidence-volume',r['dependence_group']]))
    for size in (25, 50, 100, len(ordered)):
        selected = ordered[:size]
        if size == len(ordered):
            model = main
        else:
            model = train(selected, runtime, out / 'learning' / ('volume-' + str(size)),
                dataset_hash=digest(selected), baseline_root=out, variant='C13-volume-' + str(size))
        result = evaluate(model, [r for r in records if r['split'] == 'test'])
        pack(out / 'preferences' / ('volume-' + str(size) + '.json.xz'), result)
        volume.append(dict(training_pairs=len(selected), training_groups=len({r['dependence_group'] for r in selected}),
            metrics=metrics(result), calibration=calibration(result), model_version=model.version))
    write_json(out / 'preferences/evidence-volume.json', dict(studies=volume, fixed_test_population=True,
        selection_before_predictions=True, no_model_selected_using_test=True))

    shift = {}
    for cohort in ('independent-games','external-tactical'):
        selected = [r for r in train_rows if r['source_record']['source']['cohort'] == cohort]
        model = train(selected, runtime, out / 'learning' / ('source-only-' + cohort),
            dataset_hash=digest(selected), baseline_root=out, variant='C13-source-only-' + cohort)
        result = evaluate(model, [r for r in records if r['split'] == 'test'])
        pack(out / 'preferences' / ('source-only-' + cohort + '.json.xz'), result)
        shift[cohort] = dict(training_pairs=len(selected), model_version=model.version,
            test_sources={target:dict(metrics=metrics(population), calibration=calibration(population), uncertainty=bootstrap(population))
                for target in ('independent-games','external-tactical')
                for population in [[r for r in result if r['source_record']['source']['cohort'] == target]]})
    write_json(out / 'preferences/distribution-shift.json', dict(studies=shift,
        source_holdout_in_training=True, fixed_test_partition=True,
        scope='Source-only training evaluated both within source and on the other held-out source family. The mixed-source primary test strata alone are not an unseen-source experiment.',
        limitations='Two curated source pools; this does not quantify arbitrary deployment shift.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='artifacts/cycle13')
    run(parser.parse_args().out)
