"""Run frozen Cycle 12 research alongside its independently required legal replay."""
import argparse
import os
from pathlib import Path
import subprocess
import time

from pln_chess.common import read_json, write_json
from scripts.cycle9_baseline import sha


def run(out,source):
    out,source=Path(out).resolve(),Path(source).resolve()
    manifest=read_json(out/'manifest.json');head=manifest['starting_head']
    assert read_json(out/'commands/tests.json')['returncode']==0
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==head
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    target=out/'research';gate=source/'artifacts/cycle12/acceptance.json'
    assert read_json(gate)['passed']
    write_json(target/'baseline/reproduction-receipt.json',dict(passed=True,
        scope='Previously accepted Cycle 12 gate plus fresh starting-source tests. Complete new legal replay remains independently required.',
        accepted_gate_sha256=sha(gate),fresh_tests_sha256=sha(out/'commands/tests.json')))
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm')
    for i in range(6,14):env.pop(f'C{i}_OUT',None)
    env['C12_OUT']=str(target)
    stages=(('concept-data','training.cycle12_data'),('concept-controls','training.cycle12_controls'),
        ('sequences','training.cycle12_sequences'),('dataset-audit','evaluation.cycle12_data_audit'),
        ('concept-learning','training.cycle12_learning'),('concept-evaluation','evaluation.cycle12_concepts'),
        ('dependence','evaluation.cycle12_dependence'),('partial-semantics','evaluation.cycle12_partial_semantics'),
        ('evolution','evaluation.cycle12_evolution'))
    for name,module in stages:
        name='research-'+name;argv=[str(source/'.venv/bin/python'),'-m',module,'--out',str(target)]
        receipt=out/'commands'/f'{name}.json'
        if receipt.exists():
            old=read_json(receipt)
            if old['source_head']==head and old['argv']==argv and old['returncode']==0:continue
        log=out/'logs'/f'{name}.txt';started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(receipt,dict(argv=argv,cwd=str(source),source_head=head,identity=manifest['identity'],
            started_unix=started,elapsed_seconds=time.time()-started,returncode=result.returncode,
            log=str(log.relative_to(out)),driver_sha256=sha(__file__),environment_overrides=dict(C12_OUT=str(target))))
        if result.returncode:raise RuntimeError(str(log))
        print('BASELINE RESEARCH',name,flush=True)
    write_json(out/'research-execution.json',dict(passed=True,source_head=head,
        scope='Executed baseline research stages; the main baseline join separately verifies all semantic comparisons and legal results.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--source',required=True)
    args=parser.parse_args();run(args.out,args.source)
