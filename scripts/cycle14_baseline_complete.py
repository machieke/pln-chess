"""Complete baseline controls after retaining the missing-prerequisite attempt."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import time

from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle9_baseline import sha
from scripts.cycle14_baseline import START


def run(out, source):
    out, source = Path(out).resolve(), Path(source).resolve()
    began = time.monotonic()
    jobs=read_json(out/'legal/panel.json')['jobs']
    while not all((out/'legal/evaluation'/(job['id']+'.receipt.json')).exists() for job in jobs):
        if time.monotonic()-began > 24*3600:
            raise TimeoutError('Baseline legal proof comparison')
        time.sleep(5)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip() == START
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    manifest = read_json(out/'manifest.json')
    tests = read_json(out/'tests.json')
    assert len(jobs)==206
    assert all(read_json(out/'legal/evaluation'/(job['id']+'.receipt.json'))['passed'] for job in jobs)
    assert tests['passed'] and tests['tests'] == 588 and tests['exact_once']
    # The unchanged historical control runner requires evidence that its legal
    # predecessor was verified. Copy the genuine retained predecessor receipt;
    # this is a prerequisite only, never evidence of this cycle's fresh controls.
    prior = source/'artifacts/cycle13/baseline/reproduction-receipt.json'
    previous = read_json(prior)
    assert previous['passed'] and previous['identity']['accepted_model'] == manifest['accepted_legal_version']
    prerequisite = out/'baseline/reproduction-receipt.json'
    prerequisite.parent.mkdir(parents=True,exist_ok=True)
    if prerequisite.exists():
        assert sha(prerequisite) == sha(prior)
    else:
        shutil.copy2(prior,prerequisite)
    env = {k:v for k,v in os.environ.items() if not (k.startswith('C') and k.endswith('_OUT'))}
    env.update(PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm')
    py = str(source/'.venv/bin/python')
    probe = 'import json;from pln_chess.pln import Runtime;from pln_chess.cycle6.inference import production_code_hash;print(json.dumps(dict(runtime=Runtime().manifest,production_code_hash=production_code_hash())))'
    import json
    identity = json.loads(subprocess.check_output([py,'-c',probe],cwd=source,env=env,text=True))
    assert identity['production_code_hash'] == manifest['production_code_hash']
    assert identity['runtime'] == manifest['runtime']
    records=[]
    for name,module in [('negative-history-controls','evaluation.cycle12_legal_controls'),
                        ('recoveries-holdouts','evaluation.cycle12_legal_recovery')]:
        receipt=out/'control-completion/commands'/(name+'.json')
        log=out/'control-completion/logs'/(name+'.txt')
        argv=[py,'-u','-m',module,'--out',str(out)]
        if receipt.exists():
            old=read_json(receipt)
            assert old['argv']==argv and old['identity']==identity and old['returncode']==0
            assert old['log_sha256']==sha(log)
            records.append(old)
            continue
        log.parent.mkdir(parents=True,exist_ok=True)
        started=time.time()
        with log.open('w') as stream:
            result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=source,env=env,
                stdout=stream,stderr=subprocess.STDOUT,timeout=24*3600)
        row=dict(argv=argv,identity=identity,source_head=START,started_unix=started,
            elapsed_seconds=time.time()-started,returncode=result.returncode,
            log_sha256=sha(log),driver_sha256=sha(__file__))
        write_json(receipt,row)
        assert result.returncode==0,log
        records.append(row)
        print('C14 BASELINE CONTROL COMPLETE',name,flush=True)
    negative=read_json(out/'legal/negative-controls/verified.json')
    history=read_json(out/'legal/temporal/summary.json')
    recovery=read_json(out/'legal/recovery/verified.json')
    assert negative['passed'] and negative['cases']==287
    assert history['passed'] and history['cases']==27
    assert recovery['passed'] and recovery['production_code_hash']==manifest['production_code_hash']
    while not (out/'legal-proof-parity.json').exists():
        if time.monotonic()-began > 24*3600:
            raise TimeoutError('Baseline legal proof comparison')
        time.sleep(5)
    parity=read_json(out/'legal-proof-parity.json')
    assert parity['passed'] and (parity['shards'],parity['rows']) == (206,584112)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    write_json(out/'control-completion/verified.json',dict(passed=True,commands=records,
        predecessor_receipt_sha256=sha(prior),source_head=START,source_clean=True,
        original_failed_attempt='commands/negative-history-controls.attempt-1.json',
        cause='The original orchestration omitted the existing predecessor receipt required by the unchanged historical control runner.',
        scope='Fresh controls executed against the clean starting source after supplying the genuine historical prerequisite. Original failure and all successful legal/test outputs remain retained.'))
    write_json(out/'legal-reproduction.json',dict(passed=True,source_head=START,source_clean=True,
        tests=588,legal_shards=206,legal_rows=584112,negative_controls=287,history_controls=27,
        recoveries=2,holdouts=76,proof_parity_sha256=sha(out/'legal-proof-parity.json'),
        control_completion_sha256=sha(out/'control-completion/verified.json'),
        scope='Fresh starting-source legal/test replay and separately executed controls; the missing-prerequisite orchestration failure is retained and resolved. Research reproduction is separately required.'))
    print('C14 BASELINE LEGAL REPRODUCTION COMPLETE',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='artifacts/cycle14/baseline')
    parser.add_argument('--source',required=True)
    args=parser.parse_args();run(args.out,args.source)
