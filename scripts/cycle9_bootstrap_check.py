"""Supplemental fresh bootstrap at the exact verified study commit."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def run(source, checkout, out):
    source=Path(source).resolve();checkout=Path(checkout).resolve();out=Path(out).resolve()
    verification=json.loads((out/'performance/C9-optimized.json').read_text());head=verification['source_head']
    assert len(verification['records'])==6,'Wait until the serial benchmark has finished'
    assert not checkout.exists(),'Use a new checkout path'
    evidence=out/'fresh-source-bootstrap';evidence.mkdir(exist_ok=True)
    env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}',TMPDIR='/dev/shm',C9_OUT=str(out))
    env.pop('C8_OUT',None)
    commands=[]
    def command(name,argv,cwd):
        started=time.time();log=evidence/(name+'.txt')
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(name=name,argv=argv,cwd=str(cwd),returncode=result.returncode,
            elapsed_seconds=time.time()-started,log=str(log.relative_to(out))))
        (evidence/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        assert result.returncode==0,(name,log)
    command('clone',['git','clone','--shared',str(source),str(checkout)],source)
    command('checkout',['git','checkout','--detach',head],checkout)
    status=subprocess.check_output(['git','status','--porcelain=v1'],cwd=checkout,text=True)
    assert not status.strip() and not (checkout/'.venv').exists() and not (checkout/'.runtime').exists()
    command('bootstrap',['bash','scripts/bootstrap.sh','--dependencies-only'],checkout)
    py=str(checkout/'.venv/bin/python')
    command('dataset',[py,'-m','training.cycle9_data','--out',str(evidence/'regenerated')],checkout)
    actual=json.loads((evidence/'regenerated/datasets/dataset.json').read_text())
    expected=json.loads((out/'datasets/dataset.json').read_text());assert actual==expected
    code='from pln_chess.pln import Runtime; from pln_chess.cycle6.inference import production_code_hash; import json; print(json.dumps(dict(runtime=Runtime().manifest,production_code_hash=production_code_hash())))'
    command('identity',[py,'-c',code],checkout)
    identity=json.loads((evidence/'identity.txt').read_text())
    assert identity['runtime']==verification['runtime'] and identity['production_code_hash']==verification['production_code_hash']
    assert not subprocess.check_output(['git','status','--porcelain=v1'],cwd=checkout,text=True).strip()
    result=dict(passed=True,source_head=head,initial_clean_checkout=True,fresh_venv=True,fresh_runtime=True,
        final_clean_checkout=True,exact_dataset_replay=True,dataset_hash=actual['hash'],**identity,
        dependency_lock_sha256=hashlib.sha256((checkout/'requirements-dev.lock').read_bytes()).hexdigest(),
        identity_source='performance/C9-optimized.json',
        scope='Fresh dependencies and deterministic dataset replay at the exact corrected study commit. Full tests, controls, evaluations and benchmarks are recorded in the main clean-study receipts.')
    assert result['dependency_lock_sha256']==json.loads((out/'bootstrap-context.json').read_text())['dependency_lock_sha256']
    (evidence/'verified.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--checkout',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();run(a.source,a.checkout,a.out)
