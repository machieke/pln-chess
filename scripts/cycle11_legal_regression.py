"""Isolated experimental-checkpoint regression, distinct from default gates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time

from pln_chess.common import ROOT, digest, read_json, write_json
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle7.model import key
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def select(out):
    out = Path(out)
    curriculum = read_json(out / 'datasets/legal-curriculum.json')
    keys = {r['identifier'] for r in curriculum['examples'] if r['split'] == 'train'}
    effects = {r['descriptor']['effect'] for r in curriculum['examples'] if r['split'] == 'train'}
    c9 = read_json(ROOT / 'artifacts/cycle9/datasets/dataset.json')
    c10 = read_json(ROOT / 'artifacts/cycle10/datasets/dataset.json')
    fixtures, selected = [], []
    for fixture in c10['positions']:
        if fixture['split'] != 'external-test':
            continue
        position = Position.from_fen(fixture['fen'])
        matches = []
        for move in candidates(position):
            if move.effect not in effects:
                continue
            relation = next(r for r in descriptors(position, move)['relations'] if r['target'] == 'LocalAdmissibility')
            identifier = key(relation['descriptor'], 0)
            if identifier in keys:
                matches.append(dict(move=move.notation, hypothesis=identifier, descriptor=relation['descriptor']))
        if matches:
            fixtures.append(fixture)
            selected.append(dict(fixture=fixture['id'], matches=matches))
    payload = dict(schema=11, selected_without_model_predictions=True, training_keys=sorted(keys),
        selected_external=selected, external_population=1020, selected_external_positions=len(fixtures),
        cohorts={
            'c9-adversarial': {**c9, 'positions':[r for r in c9['positions'] if r['split'] == 'adversarial']},
            'c9-special': {**c9, 'positions':[r for r in c9['positions'] if r['split'] == 'special-moves']},
            'c10-synthetic': {**c10, 'positions':[r for r in c10['positions'] if r['split'] == 'synthetic-adversarial']},
            'c10-external-selected': {**c10, 'positions':fixtures}},
        scope='All dedicated adversarial/special fixtures plus every external-test position containing a candidate whose exact local descriptor occurs in the new curriculum. Excluded external positions are not claimed as freshly evaluated under the experimental checkpoint; the unchanged default is separately replayed on the complete acceptance populations.')
    payload['hash'] = digest(payload)
    write_json(out / 'datasets/legal-regression-panel.json', payload)
    print('Experimental regression panel', {k:len(v['positions']) for k,v in payload['cohorts'].items()}, flush=True)


def worker(out, cohort, offset, history):
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from evaluation.cycle8 import evaluate
    from evaluation.cycle10_temporal_eval import evaluate_temporal
    from scripts.cycle9_baseline import sha
    out = Path(out)
    panel = read_json(out / 'datasets/legal-regression-panel.json')
    data = panel['cohorts'][cohort]
    fixtures = data['positions'][offset:offset+10]
    assert fixtures
    runtime = Runtime(timeout=180)
    model = PromotionModel.load(out / 'model/C11-special-local.json', runtime)
    settings = Cycle8Options(mode='operational', timeout_seconds=180, max_native_invocations=100000)
    target = out / f'legal/regression/{cohort}-{"history" if history else "fen"}-{offset:04}.json.xz'
    evaluator = evaluate_temporal if history else evaluate
    report = evaluator({**data, 'positions':fixtures}, model, fixtures[0]['split'], runtime, settings, target)
    assert all(digest([report['native_proof_dag'][i] for i in row['proof_refs']]) == row['proof_id'] for row in report['rows'])
    write_json(target.with_suffix('.receipt.json'), dict(artifact=str(target.relative_to(out)), sha256=sha(target),
        panel_hash=panel['hash'], model_version=model.version, cohort=cohort, history=history,
        positions=len(report['positions']), rows=len(report['rows']), metrics=report['metrics'],
        proof_hash=digest([r['proof_id'] for r in report['rows']]), native_proofs_verified=True))


def run(out):
    out = Path(out).resolve()
    assert read_json(out / 'baseline/reproduction-receipt.json')['passed']
    panel = read_json(out / 'datasets/legal-regression-panel.json')
    jobs = []
    for cohort, data in panel['cohorts'].items():
        for history in ((False, True) if cohort == 'c10-external-selected' else (False,)):
            jobs.extend((cohort, offset, history) for offset in range(0, len(data['positions']), 10))
    def command(job):
        cohort, offset, history = job
        argv = [sys.executable, '-m', 'scripts.cycle11_legal_regression', '--out', str(out),
            '--worker', cohort, '--offset', str(offset)]
        if history:
            argv.append('--history')
        name = f'{cohort}-{"history" if history else "fen"}-{offset:04}'
        log = out / f'legal/regression/logs/{name}.txt'
        log.parent.mkdir(parents=True, exist_ok=True)
        started = time.time()
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=ROOT, env=dict(os.environ, TMPDIR='/dev/shm'), stdout=stream, stderr=subprocess.STDOUT)
        write_json(out / f'legal/regression/commands/{name}.json', dict(argv=argv, started_unix=started,
            elapsed_seconds=time.time()-started, returncode=result.returncode))
        if result.returncode:
            raise RuntimeError(str(log))
        print('Experimental regression', name, flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(command, jobs):
            pass
    from evaluation.cycle9_analysis import metrics
    summary = {}
    for cohort in panel['cohorts']:
        for mode in (('fen', 'history') if cohort == 'c10-external-selected' else ('fen',)):
            paths = sorted((out / 'legal/regression').glob(f'{cohort}-{mode}-*.json.xz'))
            reports = [read_gzip(path) for path in paths]
            rows = [row for report in reports for row in report['rows']]
            positions = [row for report in reports for row in report['positions']]
            summary[cohort+'/'+mode] = metrics(rows, positions)
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from scripts.cycle8_controls import negatives
    runtime = Runtime(timeout=180)
    model = PromotionModel.load(out / 'model/C11-special-local.json', runtime)
    controls = negatives(model, runtime, out / 'legal/regression')
    write_json(out / 'legal/regression/summary.json', dict(model_version=model.version,
        cohorts=summary, negative_controls=controls, selected_external_positions=panel['selected_external_positions'],
        external_population=panel['external_population'], selection_hash=panel['hash'],
        experimental_model_promoted=False, scope=panel['scope']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--select', action='store_true')
    parser.add_argument('--worker')
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    if args.select:
        select(args.out)
    elif args.worker:
        worker(args.out, args.worker, args.offset, args.history)
    else:
        run(args.out)
