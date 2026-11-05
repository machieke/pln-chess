"""Rebuild the complete measured package locally. No network or external writes."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from pln_chess.common import ROOT,write_json,read_json,digest
from pln_chess.pln import Runtime
from pln_chess.pln.audit import runtime_audit
from pln_chess.api import train,explain_move,compare_transforms,observe_example
from pln_chess.evidence import Ledger
from pln_chess.learning import train as replay
from pln_chess.domain import Position
from training.factory import generate,reference_label
from evaluation.experiments import evaluate,fit_calibrator,score_calibration,ablations,benchmark,sample_efficiency
from evaluation.reporting import final_report


def main():
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
    print('Auditing native runtime...',flush=True)
    audit=runtime_audit(artifacts/'runtime-audit.json'); runtime=Runtime()
    write_json(artifacts/'runtime-manifest.json',runtime.manifest)
    data=generate(output=ROOT/'fixtures/dataset.json')
    write_json(artifacts/'dataset-manifest.json',{k:v for k,v in data.items() if k not in ('examples','positions')})
    print('Training via native revision...',flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        ledger=Path(tmp)/'evidence.jsonl'
        model=train([r for r in data['examples'] if r['split']=='train'],artifacts/'model.json',runtime=runtime,ledger_path=ledger)
        shutil.copyfile(ledger,artifacts/'evidence.jsonl')
    write_json(artifacts/'training-report.json',model.training_report)
    demonstrations=[]
    for fixture in data['positions']:
        if not fixture['focus_move']: continue
        trace=explain_move(fixture['fen'],fixture['focus_move'],model,runtime=runtime)
        source=next(r for r in data['examples'] if r['position_fixture']==fixture['id'] and r['move']==fixture['focus_move'])
        trace['evaluation_only_oracle']={'label':source['label'],'source':source['source']}
        write_json(artifacts/'proofs'/f'{fixture["id"]}.json',trace)
        demonstrations.append({'fixture':fixture['id'],'tv':trace['candidate']['legal_move_truth_value'],
                               'classification':trace['candidate']['classification'],'oracle_label':source['label'],'split':fixture['split']})
    # Replay, correlated conflict, and independent conflict are an actual native trace.
    focus=next(p for p in data['positions'] if p['id']=='transfer-source')
    with tempfile.TemporaryDirectory() as tmp:
        ledger=Path(tmp)/'revision.jsonl'; updates=[]
        for source,group,label in [('first','shared',True),('first','shared',True),('correlated','shared',False),('independent','new',False)]:
            receipt=observe_example(focus['fen'],focus['focus_move'],label,source,group,ledger,runtime)
            snapshot=replay(Ledger(ledger),runtime)
            key=next(k for k in snapshot.hypotheses if k.startswith('context:'))
            updates.append({'receipt':receipt,'hypothesis':snapshot.inspect_hypothesis(key),'training':snapshot.training_report})
        write_json(artifacts/'proofs/evidence-revision.json',{'updates':updates,'runtime_version':runtime.version})
    unknown=explain_move(Position.from_fen(focus['fen'],unknown_squares=((3,2),)),focus['focus_move'],model,runtime=runtime)
    write_json(artifacts/'proofs/incomplete-observation.json',unknown)
    invariance=compare_transforms(focus['fen'],(1,0),model,focus['focus_move'],runtime)
    write_json(artifacts/'invariance.json',invariance)
    reports={}
    for split in ('train','validation','heldout-transfer','controlled-transfer','adversarial'):
        print(f'Evaluating complete candidate sets: {split}...',flush=True)
        report=evaluate(data,model,split,runtime)
        write_json(artifacts/f'evaluation-{split}.json',report)
        reports[split]={'metrics':report['metrics'],'model_version':report['model_version']}
    import csv
    with (artifacts/'metrics.csv').open('w') as file:
        writer=csv.writer(file);writer.writerow(['split','precision','recall','f1','abstention_rate','exact_move_set_accuracy','false_legal_rate','incomplete_positions'])
        for split,report in reports.items():
            writer.writerow([split]+[report['metrics'][k] for k in ['precision','recall','f1','abstention_rate','exact_move_set_accuracy','false_legal_rate','incomplete_positions']])
    write_json(artifacts/'transfer-report.json',{'strict_recall_gap':reports['train']['metrics']['recall']-reports['heldout-transfer']['metrics']['recall'],
                                               'controlled_recall_gap':reports['train']['metrics']['recall']-reports['controlled-transfer']['metrics']['recall'],
                                               'invariance':invariance,'warning':'Strict structural novelty and controlled paired translation are distinct experiments.'})
    calibration=fit_calibrator(read_json(artifacts/'evaluation-validation.json'))
    write_json(artifacts/'calibration.json',score_calibration(read_json(artifacts/'evaluation-heldout-transfer.json'),calibration))
    print('Running ablations and runtime benchmarks...',flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        ablation=ablations(data,tmp,runtime)
        write_json(artifacts/'ablations.json',ablation)
        # Keep compact checkpoints and evidence for reproducibility of each ablation.
        dest=artifacts/'ablations';dest.mkdir(exist_ok=True)
        for path in Path(tmp).iterdir(): shutil.copyfile(path,dest/path.name)
    write_json(artifacts/'sample-efficiency.json',sample_efficiency(data,runtime))
    timings=benchmark(data,model,runtime)
    write_json(artifacts/'benchmark.json',timings)
    with (artifacts/'benchmark.csv').open('w') as file:
        writer=csv.DictWriter(file,fieldnames=list(timings['samples'][0]));writer.writeheader();writer.writerows(timings['samples'])
    write_json(artifacts/'run-summary.json',{'status':'native-partial','evaluations':reports,'invariance':invariance,
                                          'demonstrations':demonstrations,'model_version':model.version})
    print('Running validation suite...',flush=True)
    tests=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
    (artifacts/'pytest.txt').write_text(tests.stdout+tests.stderr)
    print(tests.stdout,flush=True)
    if tests.returncode: raise SystemExit(tests.returncode)
    final_report(ROOT/'docs/final-report.md');final_report(artifacts/'final-report.md')
    files=[str(p.relative_to(ROOT)) for parent in ('src','training','evaluation','scripts','tests','docs','configs','vendor') for p in sorted((ROOT/parent).rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    write_json(artifacts/'file-manifest.json',{'files':files,'root_files':['README.md','pyproject.toml','requirements-dev.lock','.gitignore'],'commits_created':False})
    from evaluation.reporting import finish_delivery
    finish_delivery(runtime)
    print('Complete package generated. Coverage: native-partial; see docs/final-report.md.',flush=True)

if __name__=='__main__': main()
