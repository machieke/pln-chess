"""Execute new research stages in a fresh environment and compare frozen evidence.

The separately executed unchanged-source baseline and current legality replay
are reused by receipt, not represented as a second end-to-end baseline run.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time
from pln_chess.common import read_json, write_json
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip


def run(out,source):
    out,source=Path(out).resolve(),Path(source).resolve()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    baseline=out/'baseline/reproduction-receipt.json'
    assert read_json(baseline)['passed']
    target=out/'clean-research'
    if target.exists():raise ValueError('Research replay requires a new output directory')
    (target/'baseline').mkdir(parents=True)
    shutil.copy2(baseline,target/'baseline/reproduction-receipt.json')
    (target/'datasets').mkdir()
    shutil.copy2(out/'datasets/ATTRIBUTION.txt',target/'datasets/ATTRIBUTION.txt')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm',C11_OUT=str(target))
    for name in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT'):env.pop(name,None)
    commands=[]
    stages=(('field-data','training.cycle11_data'),('legal-data','training.cycle11_legal_data'),
        ('worked-data','training.cycle11_examples'),('temporal-data','training.cycle11_temporal_data'),
        ('dataset-audit','evaluation.cycle11_data_audit'),('field-learning','training.cycle11_fields'),
        ('legal-learning','training.cycle11_legal'),('field-evaluation','evaluation.cycle11_fields'),
        ('field-audit','evaluation.cycle11_field_audit'),('field-controls','evaluation.cycle11_field_controls'),
        ('temporal-controls','evaluation.cycle11_temporal'))
    for name,module in stages:
        argv=[str(source/'.venv/bin/python'),'-m',module,'--out',str(target)]
        log=target/'logs'/f'{name}.txt'
        log.parent.mkdir(exist_ok=True)
        started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(stage=name,argv=argv,source_head=head,returncode=result.returncode,elapsed_seconds=time.time()-started,log=str(log.relative_to(target))))
        write_json(target/'commands.json',commands)
        if result.returncode:raise RuntimeError(str(log))
        print('FRESH REPLAY',name,flush=True)
    comparisons=[]
    for name in ('C11-field-trained.json','C11-field-empty.json','C11-special-local.json'):
        assert sha(target/'model'/name)==sha(out/'model'/name),name
        comparisons.append(dict(path='model/'+name,sha256=sha(target/'model'/name),byte_identical=True))
    for name in ('datasets/field-queries.json.xz','datasets/legal-curriculum.json','datasets/worked-controls.json',
        'datasets/temporal-controls.json','field-evaluation/rows.json.xz','fields/transformations.json.xz',
        'fields/learning-transfers.json.xz','field-learning/main/native-training.json.xz','legal/training.json.xz',
        'temporal/summary.json'):
        load=read_gzip if name.endswith('.xz') else read_json
        assert load(target/name)==load(out/name),name
        comparisons.append(dict(path=name,content_identical=True))
    # Full successor fields carry timings; compare each native relation and the
    # typed differences independently of those measurements.
    original=read_gzip(out/'fields/worked-examples.json.xz')
    reproduced=read_gzip(target/'fields/worked-examples.json.xz')
    assert len(original)==len(reproduced)==15
    for a,b in zip(original,reproduced):
        assert a['case']==b['case']
        for side in ('before','after'):assert a['comparison'][side]['relations']==b['comparison'][side]['relations']
        assert a['comparison']['differences']==b['comparison']['differences']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    write_json(target/'verified.json',dict(passed=True,source_head=head,checkout=str(source),initial_clean=True,final_clean=True,
        comparisons=comparisons,worked_native_relation_and_difference_parity=15,
        baseline_reused_by_receipt=dict(path=str(baseline),sha256=sha(baseline)),
        end_to_end_second_baseline_run=False,all_listed_research_stages_executed=True,
        scope='Fresh venv/runtime/source execution of new data generation, native learning, held-out field inference and controls. Full unchanged-source baseline and current legality replay have separate receipts; this is not a second full end-to-end run.'))
    print('FRESH RESEARCH REPRODUCTION PASSED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--source',required=True)
    args=parser.parse_args()
    run(args.out,args.source)
