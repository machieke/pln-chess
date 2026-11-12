"""Validate the late cached-join repair after isolated benchmarking closes."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from pln_chess.common import ROOT,digest,read_json,write_json
from scripts.cycle9_baseline import sha


def run(out,source=None):
    out=Path(out).resolve()
    assert read_json(out/'performance/summary.json')['passed'],'Finish isolated benchmarking first'
    target=out/'verification/schedule-recovery.json'
    assert not target.exists(),'Preserve the prior recovery receipt'
    incident=read_json(out/'verification/schedule-incident.json')
    current=read_json(out/'current/verified.json');assert current['passed']
    source=Path(source or current['checkout']).resolve()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    assert head==current['source_head']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    replay=out/'clean-research/proof-replay'
    proof=read_json(replay/'verified.json');assert proof['passed'] and proof['archives']==1180
    assert sha(replay/'verified.json')==incident['full_proof_receipt_sha256']
    assert sha(replay/'stream-complete-shard1-of-3.json')==incident['shard1_completion_sha256']
    assert sha(out/'current/verified.json')==incident['current_legal_receipt_sha256']
    assert sha(out/'clean-research/verified.json')==incident['clean_research_receipt_sha256']
    frozen={str((replay/name).relative_to(out)):value for name,value in proof['receipts'].items()}
    for name in ('clean-research/proof-replay/verified.json',
            'clean-research/proof-replay/stream-complete-shard1-of-3.json',
            'clean-research/verified.json','clean-research/comparison.json','current/verified.json'):
        frozen[name]=sha(out/name)
    assert all(sha(out/name)==value for name,value in frozen.items())
    wrapper=ROOT/'scripts/cycle14_replay_stream.py';wrapper_sha=sha(wrapper)
    commands=[]

    def command(name,argv,cwd,env):
        log=out/'verification/logs'/(name+'.txt');log.parent.mkdir(parents=True,exist_ok=True)
        assert not log.exists(),'Preserve prior command logs'
        began=time.time()
        with log.open('x') as stream:
            result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=cwd,env=env,
                stdout=stream,stderr=subprocess.STDOUT)
        record=dict(name=name,argv=argv,cwd=str(cwd),returncode=result.returncode,
            started_unix=began,elapsed_seconds=time.time()-began,log_sha256=sha(log))
        write_json(out/'verification/commands'/(name+'.json'),record)
        assert result.returncode==0,log
        commands.append(record)
        return log

    xml=out/'verification/stream-completion-controls.xml'
    command('proof-stream-controls',[sys.executable,'-m','pytest','-q',
        str(ROOT/'tests/test_cycle14_stream_completion.py'),'--junitxml='+str(xml)],ROOT,dict(os.environ))
    suites=list(ET.parse(xml).getroot().iter('testsuite'))
    assert sum(int(s.get('tests',0)) for s in suites)==3
    assert not any(int(s.get(key,0)) for s in suites for key in ('failures','errors','skipped'))
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',C14_OUT=str(out),TMPDIR='/dev/shm')
    for cycle in range(6,14):env.pop(f'C{cycle}_OUT',None)
    argv=[str(source/'.venv/bin/python'),'-u',str(wrapper),'--source',str(out),
        '--out',str(replay),'--shard','1','--shards','3']
    for attempt in (1,2):
        log=command('proof-shard1-recovery-'+str(attempt),argv,source,env)
        assert 'C14 COMPLETE PROOF SHARD REVALIDATED 1 385' in log.read_text()
        assert all(sha(out/name)==value for name,value in frozen.items())
    assert sha(wrapper)==wrapper_sha
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    write_json(target,dict(passed=True,source_head=head,source_checkout=str(source),
        production_code_hash=proof['production_code_hash'],incident_sha256=sha(out/'verification/schedule-incident.json'),
        recovery_driver_sha256=sha(__file__),repaired_stream_wrapper_sha256=wrapper_sha,
        native_proof_verifier_sha256=sha(source/'evaluation/cycle14_proof_replay.py'),
        test_source_sha256=sha(ROOT/'tests/test_cycle14_stream_completion.py'),test_xml_sha256=sha(xml),
        unit_controls=3,cached_shard_archives=385,successful_revalidations=2,
        unchanged_native_receipts=len(proof['receipts']),unchanged_receipt_map_sha256=digest(frozen),
        original_shard_completion_sha256=incident['shard1_completion_sha256'],commands=commands,
        original_failure_retained=True,
        scope='The cached join validates the same registered archives and preserves the original immutable completion, including its telemetry. Three host-verifier controls reject changed native-verifier identity or archive count. Two fresh-process cached joins pass without rewriting any of the 1180 native receipts or the complete research/legal gates; this is not a new native corpus execution.'))
    print('C14 CACHED SHARD JOIN RECOVERY PASSED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    parser.add_argument('--source');args=parser.parse_args();run(args.out,args.source)
