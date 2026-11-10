"""Fresh-environment concept/field reproduction, with exact semantic comparisons."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import read_json, write_json, digest
from pln_chess.cycle12.temporal import semantic_replay
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip


def run(out,source):
    out,source=Path(out).resolve(),Path(source).resolve()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    baseline=out/'baseline/reproduction-receipt.json';assert read_json(baseline)['passed']
    target=out/'clean-research';(target/'baseline').mkdir(parents=True,exist_ok=True)
    shutil.copy2(baseline,target/'baseline/reproduction-receipt.json')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm',C12_OUT=str(target))
    for name in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT','C11_OUT'):env.pop(name,None)
    commands=[]
    stages=(('concept-data','training.cycle12_data'),('concept-controls','training.cycle12_controls'),
        ('sequences','training.cycle12_sequences'),('dataset-audit','evaluation.cycle12_data_audit'),
        ('concept-learning','training.cycle12_learning'),('concept-evaluation','evaluation.cycle12_concepts'),
        ('dependence','evaluation.cycle12_dependence'),('partial-semantics','evaluation.cycle12_partial_semantics'),
        ('evolution','evaluation.cycle12_evolution'))
    for name,module in stages:
        argv=[str(source/'.venv/bin/python'),'-m',module,'--out',str(target)]
        log=target/'logs'/f'{name}.txt';log.parent.mkdir(exist_ok=True)
        receipt=target/'commands'/f'{name}.json'
        if receipt.exists() and read_json(receipt).get('source_head')==head and read_json(receipt).get('returncode')==0:
            commands.append(read_json(receipt));continue
        started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        record=dict(stage=name,argv=argv,source_head=head,returncode=result.returncode,elapsed_seconds=time.time()-started,log=str(log.relative_to(target)))
        commands.append(record);write_json(receipt,record);write_json(target/'commands.json',commands)
        if result.returncode:raise RuntimeError(str(log))
        print('FRESH CYCLE12 REPLAY',name,flush=True)
    comparisons=[]
    for name in ('C12-concept-trained.json','C12-concept-empty.json'):
        assert sha(target/'model'/name)==sha(out/'model'/name),name
        comparisons.append(dict(path='model/'+name,sha256=sha(target/'model'/name),byte_identical=True))
    paths=['datasets/concepts.json','datasets/concept-controls.json','datasets/sequences.json','datasets/audit.json',
        'learning/main/native-training.json.xz','learning/main/ledger.json.xz','learning/dependence.json',
        'concepts/rows.json.xz','concepts/summary.json','concepts/transformations.json.xz','concepts/counterfactuals.json.xz',
        'concepts/transfers.json.xz','concepts/controls-summary.json','concepts/overload-consequences.json.xz',
        'concepts/trapping-diagnostics.json.xz','concepts/partial-semantics-summary.json',
        'interactions/summary.json','interactions/transformations.json.xz','temporal/summary.json','incremental/parity.json']
    paths.extend(str(p.relative_to(out)) for p in sorted((out/'interactions').glob('*.json.xz')) if str(p.relative_to(out)) not in paths)
    paths.extend(str(p.relative_to(out)) for p in sorted((out/'temporal').rglob('*.json.xz')))
    for name in paths:
        load=read_gzip if name.endswith('.xz') else read_json
        a,b=load(out/name),load(target/name)
        assert digest(semantic_replay(a))==digest(semantic_replay(b)),name
        comparisons.append(dict(path=name,semantic_identical=True,semantic_sha256=digest(semantic_replay(a))))
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    write_json(target/'verified.json',dict(passed=True,source_head=head,checkout=str(source),initial_clean=True,final_clean=True,
        comparisons=comparisons,baseline_reused_by_receipt=dict(path=str(baseline),sha256=sha(baseline)),
        end_to_end_second_baseline_run=False,all_listed_research_stages_executed=True,
        scope='Fresh locked environment reruns Cycle 12 data generation, native learning, limited-target evaluation, counterfactuals, dependence, fields and supplied sequences. The full baseline and legal population gates have separate executed receipts. Timing and cache counters are excluded from semantic equality.'))
    print('FRESH CYCLE12 RESEARCH REPRODUCTION PASSED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--source',required=True)
    args=parser.parse_args();run(args.out,args.source)
