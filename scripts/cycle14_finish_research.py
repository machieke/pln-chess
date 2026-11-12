"""Join completed scientific inputs, then run independent delivery verifiers."""
from pathlib import Path
import os
import subprocess
import sys
import time

from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def run():
    out=ROOT/'artifacts/cycle14'
    source=read_json(out/'verification/research-audit-source.json')
    fresh=Path(source['checkout']);commit=source['commit']
    def wait(predicate,description):
        began=time.monotonic()
        while not predicate():
            if time.monotonic()-began>24*3600:raise TimeoutError(description)
            time.sleep(5)
    def pipeline_done():
        path=out/'pipeline/commands/bounded-responses.json'
        return path.exists() and read_json(path)['returncode']==0
    def command(name,module,args):
        target=out/'verification/commands'/f'{name}.json';log=out/'verification/logs'/f'{name}.txt'
        argv=[sys.executable,'-u','-m',module,*args]
        identity=dict(argv=argv,driver_sha256=sha(ROOT/(module.replace('.','/')+'.py')))
        if target.exists():
            previous=read_json(target);assert previous['identity']==identity
            if previous['returncode']==0:return
            attempt=1
            while log.with_suffix(f'.attempt-{attempt}.txt').exists():attempt+=1
            if log.exists():log.rename(log.with_suffix(f'.attempt-{attempt}.txt'))
            target.rename(target.with_suffix(f'.attempt-{attempt}.json'))
        started=time.time();log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w') as stream:
            result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=ROOT,
                env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT)
        write_json(target,dict(identity=identity,returncode=result.returncode,elapsed_seconds=time.time()-started,
            log_sha256=sha(log),started_unix=started))
        if result.returncode:raise RuntimeError(str(log))
        print('C14 DELIVERY VERIFICATION',name,'PASSED',flush=True)
    wait(pipeline_done,'Registered scientific pipeline exceeded the stage budget')
    command('dataset-integrity','evaluation.cycle14_integrity',['--out',str(out)])
    command('native-boundary','evaluation.cycle14_delivery',['boundary','--out',str(out)])
    wait(lambda:all((out/'clean-research/proof-replay'/f'stream-complete-shard{i}-of-3.json').exists()
        for i in range(3)),'Complete native proof shards exceeded the stage budget')
    wait(lambda:(out/'clean-research/bootstrap-audit/verified.json').exists()
        and (out/'clean-research/selected/verified.json').exists(),
        'Sparse research bootstrap and selected observation replay')
    command('clean-research','scripts.cycle14_reproduce',['--out',str(out),'--checkout',str(fresh),'--commit',commit])


if __name__=='__main__':run()
