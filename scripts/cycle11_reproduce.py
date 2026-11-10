"""Fresh-checkout staged Cycle 11 reproduction with source-bound receipts."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha


def run(out, checkout, snapshot, work, plot_python='python3', browser=True):
    out, checkout, snapshot, work = (Path(path).resolve() for path in (out, checkout, snapshot, work))
    for path in (out, checkout, snapshot, work):
        if path.exists():
            raise ValueError('Use a new reproduction directory: '+str(path))
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True):
        raise ValueError('Reproduction starts from a committed, clean package')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out.mkdir(parents=True)
    bootstrap(out / 'bootstrap', checkout, head)
    py = str(checkout / '.venv/bin/python')
    env = dict(os.environ, PLN_CHESS_ROOT=str(checkout), PYTHONPATH=f'{checkout}/src:{checkout}', TMPDIR='/dev/shm', C11_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT'):
        env.pop(key, None)
    commands = []

    def command(name, args, interpreter=py):
        started = time.time()
        log = out / f'reproduction-logs/{name}.txt'
        log.parent.mkdir(parents=True, exist_ok=True)
        argv = [interpreter, *args]
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=checkout, env=env, stdout=stream, stderr=subprocess.STDOUT)
        receipt = dict(name=name, argv=argv, cwd=str(checkout), source_head=head, started_unix=started,
            elapsed_seconds=time.time()-started, returncode=result.returncode, log=str(log.relative_to(out)))
        commands.append(receipt)
        write_json(out / 'reproduction-commands.json', commands)
        if result.returncode:
            raise RuntimeError(name+': '+str(log))
        print('PASSED', name, flush=True)

    command('unchanged-baseline', ['-m','scripts.cycle11_baseline','--out',str(out/'baseline'),'--snapshot',str(snapshot)])
    for name, module in (
        ('field-dataset','training.cycle11_data'), ('legal-dataset','training.cycle11_legal_data'),
        ('worked-dataset','training.cycle11_examples'), ('temporal-dataset','training.cycle11_temporal_data'),
        ('data-audit','evaluation.cycle11_data_audit'), ('forensics','evaluation.cycle11_forensics')):
        command(name, ['-m', module, '--out', str(out)])
    command('legal-panel', ['-m','scripts.cycle11_legal_regression','--out',str(out),'--select'])
    shutil.copy2(checkout/'artifacts/cycle11/datasets/ATTRIBUTION.txt', out/'datasets/ATTRIBUTION.txt')
    for name, module in (
        ('field-learning','training.cycle11_fields'), ('legal-learning','training.cycle11_legal'),
        ('field-evaluation','evaluation.cycle11_fields'), ('relative-sharing','evaluation.cycle11_field_audit'),
        ('field-controls','evaluation.cycle11_field_controls'),
        ('temporal-controls','evaluation.cycle11_temporal'), ('legal-completion','evaluation.cycle11_legal'),
        ('experimental-regression','scripts.cycle11_legal_regression')):
        command(name, ['-m',module,'--out',str(out)])
    command('field-dependence',['-m','evaluation.cycle11_field_controls','--out',str(out),'--dependence'])
    command('current-gates',['-m','scripts.cycle11_regression','--out',str(out),'--source',str(checkout)])
    for action in ('boundary','acceptance'):
        command(action,['-m','evaluation.cycle11_delivery',action,'--out',str(out)])
    command('accepted-default-tests',['-m','pytest','-q'])
    command('performance',['-m','evaluation.cycle11_performance','--out',str(out)])
    if browser:
        command('browser',['-m','scripts.cycle11_ui_verify','--out',str(out),'--work',str(work)])
    else:
        # Headless scientific replay may deliberately omit the browser, but it
        # cannot claim complete delivery or manufacture a passing UI receipt.
        write_json(out/'browser-not-executed.json',dict(executed=False,reason='Explicit --skip-browser reproduction option'))
    comparisons = []
    for name in ('C11-field-trained.json','C11-field-empty.json','C11-special-local.json','C11-default.json'):
        expected, actual = checkout/'artifacts/cycle11/model'/name, out/'model'/name
        assert sha(expected) == sha(actual), name
        comparisons.append(dict(model=name, sha256=sha(actual), byte_identical=True))
    for name in ('field-queries.json.xz','legal-curriculum.json','worked-controls.json','temporal-controls.json','legal-regression-panel.json'):
        from evaluation.cycle3 import read_gzip
        load = read_gzip if name.endswith('.xz') else read_json
        assert load(out/'datasets'/name) == load(checkout/'artifacts/cycle11/datasets'/name), name
    for name in ('fields/transformations.json.xz','fields/learning-transfers.json.xz'):
        from evaluation.cycle3 import read_gzip
        assert read_gzip(out/name) == read_gzip(checkout/'artifacts/cycle11'/name), name
    # Native relation proofs are compared independently of timestamps and timings.
    expected_rows = read_gzip(checkout/'artifacts/cycle11/field-evaluation/rows.json.xz')
    actual_rows = read_gzip(out/'field-evaluation/rows.json.xz')
    assert expected_rows == actual_rows
    write_json(out/'reproduction-comparison.json',dict(passed=True, models=comparisons,
        field_relations=len(actual_rows), exact_field_native_proof_and_metric_rows=True,
        datasets_exact=True, transformations_and_transfer_proofs_exact=True,
        scope='Timing, process IDs, timestamps and browser-capture bytes are not required to match.'))
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    write_json(out/'delivery.json',dict(source_head=head, starting_head=read_json(checkout/'configs/cycle11.json')['starting_head'],
        clean_checkout=True, end_to_end_reproduction_executed=True, browser_executed=browser,
        complete_delivery=browser, model_proof_comparisons='reproduction-comparison.json',
        all_commands_passed=True, source_changes=False, pushed=False, deployed=False,
        scope='Executed fresh-checkout stages with original licensed source bytes. No Git push, deployment or upstream changes.'))
    if browser:
        command('research-acceptance',['-m','evaluation.cycle11_delivery','research','--out',str(out)])
        # Preserve the registered ontology specification in the standalone reports.
        (out/'reports').mkdir(exist_ok=True)
        shutil.copy2(checkout/'docs/cycle11/potential-field-ontology.md',out/'reports/potential-field-ontology.md')
        command('reports',['-m','evaluation.cycle11_reporting','--out',str(out),'--docs',str(out/'reports')])
    command('plots',[str(checkout/'evaluation/cycle11_plots.py'),'--out',str(out)],plot_python)
    command('manifest',['-m','evaluation.cycle11_delivery','manifest','--out',str(out),'--docs',str(out/'reports')])
    # The manifest command itself appends a final command receipt afterward.
    # Refresh hashes after the orchestration log is closed.
    from evaluation.cycle11_delivery import manifest
    manifest(out,out/'reports')
    print('CYCLE 11 REPRODUCTION COMPLETE', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--checkout',required=True)
    parser.add_argument('--baseline',required=True)
    parser.add_argument('--browser-work',required=True)
    parser.add_argument('--plot-python',default='python3')
    parser.add_argument('--skip-browser',action='store_true')
    args = parser.parse_args()
    run(args.out,args.checkout,args.baseline,args.browser_work,args.plot_python,not args.skip_browser)
