"""Fresh final tests and actual default CLI selection after all acceptance gates."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha


def run(out,checkout,commit,test_workers=4):
    out=Path(out).resolve();checkout=Path(checkout).resolve();target=out/'final-checks'
    acceptance=read_json(out/'acceptance.json');assert acceptance['passed']
    code=production_code_hash();assert acceptance['production_code_hash']==code
    bootstrap(target/'bootstrap',checkout,commit)
    py=str(checkout/'.venv/bin/python');env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),
        PYTHONPATH=str(checkout/'src')+':'+str(checkout),C13_OUT=str(out),TMPDIR='/dev/shm')
    for cycle in range(6,13):env.pop(f'C{cycle}_OUT',None)
    started=time.time();log=target/'tests.txt'
    # Partition complete modules, preserving fixture scope within each module.
    # Every collected item belongs to exactly one shard. Each process receives
    # a distinct pytest cache and temporary root outside the clean checkout.
    collected=subprocess.check_output([py,'-m','pytest','--collect-only','-q'],cwd=checkout,env=env,text=True)
    (target/'collection.txt').write_text(collected)
    nodes=[line for line in collected.splitlines() if line.startswith('tests/') and '::' in line]
    assert len(nodes)==len(set(nodes)) and len(nodes)>=588
    counts=Counter(node.split('::',1)[0] for node in nodes)
    assert 1<=test_workers<=8
    shards=[[] for _ in range(test_workers)];sizes=[0]*test_workers
    temporary=checkout/'.runtime/cycle13-final-tests';temporary.mkdir(parents=True,exist_ok=True)
    for module,count in sorted(counts.items(),key=lambda item:(-item[1],item[0])):
        index=min(range(test_workers),key=lambda i:(sizes[i],i))
        shards[index].append(module);sizes[index]+=count
    assert set(counts)=={name for shard in shards for name in shard}
    assert sum(map(len,shards))==len(counts)
    def test_shard(index):
        prefix=target/f'tests-{index}';xml=prefix.with_suffix('.xml');output=prefix.with_suffix('.txt')
        argv=[py,'-m','pytest','-q',*shards[index],f'--junitxml={xml}',
            f'--basetemp={temporary}/temporary-{index}','-o',f'cache_dir={temporary}/cache-{index}']
        began=time.time()
        with output.open('w') as stream:
            result=subprocess.run(argv,cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipt=dict(argv=argv,returncode=result.returncode,expected_tests=sizes[index],
            modules=shards[index],elapsed_seconds=time.time()-began,log_sha256=sha(output))
        write_json(prefix.with_suffix('.command.json'),receipt)
        assert result.returncode==0,str(output)
        suites=ET.parse(xml).getroot().findall('testsuite')
        actual=sum(int(s.get('tests','0')) for s in suites)
        assert actual==sizes[index] and all(int(s.get(k,'0'))==0 for s in suites for k in ('failures','errors','skipped'))
        assert int(re.search(r'(\d+) passed',output.read_text())[1])==actual
        return dict(**receipt,passed=actual,junit_sha256=sha(xml))
    with ThreadPoolExecutor(max_workers=test_workers) as pool:
        test_results=list(pool.map(test_shard,range(test_workers)))
    tests=sum(row['passed'] for row in test_results);assert tests==len(nodes)
    write_json(target/'test-partition.json',dict(passed=True,collected_tests=nodes,tests=tests,
        exact_once=True,processes=test_workers,shards=test_results,
        scope='All collected tests executed once; complete modules partitioned across isolated pytest processes.'))
    log.write_text(f'{tests} passed across {test_workers} isolated pytest processes; all collected items executed exactly once.\n'
        +'\n'.join(f'tests-{i}.txt: {row["passed"]} passed' for i,row in enumerate(test_results))+'\n')
    model=acceptance['default_model_version'];rows=[]
    # No checkpoint argument is supplied: exercise the actual CLI selector.
    for name,mode in (('automatic-default',None),('strict','strict'),('experimental','experimental')):
        argv=[str(checkout/'.venv/bin/pln-chess'),'inspect','--fen','7k/8/8/8/R6p/8/8/6K1 w - - 0 1',
            '--move','a4h4','--format','json',*(['--mode',mode] if mode else [])]
        result=json.loads(subprocess.check_output(argv,cwd=checkout,env=env,text=True))
        assert result['model_version']==model and result['mode']==(mode or 'operational')
        assert not result['truncated']
        if mode is None:assert result['candidate']['classification']=='supported-legal'
        write_json(target/(name+'.json'),result)
        rows.append(dict(name=name,argv=argv,mode=result['mode'],model_version=result['model_version'],
            classification=result['candidate']['classification']))
    # Also execute the user's working checkout without any cycle output override.
    local_env=dict(os.environ,TMPDIR='/dev/shm')
    for cycle in range(6,14):local_env.pop(f'C{cycle}_OUT',None)
    local_env.pop('PLN_CHESS_ROOT',None);local_env.pop('PYTHONPATH',None)
    argv=[str(ROOT/'.venv/bin/pln-chess'),'inspect','--fen','7k/8/8/8/R6p/8/8/6K1 w - - 0 1',
        '--move','a4h4','--format','json']
    result=json.loads(subprocess.check_output(argv,cwd=ROOT,env=local_env,text=True))
    assert result['model_version']==model and result['mode']=='operational' and result['candidate']['classification']=='supported-legal'
    write_json(target/'working-checkout-default.json',result)
    assert sha(out/'model/C13-default.json')==sha(ROOT/'artifacts/cycle12/model/C12-default.json')
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    assert production_code_hash()==code
    write_json(target/'verified.json',dict(passed=True,tests=tests,source_head=commit,checkout=str(checkout),
        source_clean=True,production_code_hash=code,acceptance_sha256=sha(out/'acceptance.json'),
        default_model_version=model,original_legal_checkpoint_byte_identical=True,
        fresh_checkout_cli=rows,working_checkout_automatic_default_verified=True,
        tests_sha256=sha(log),test_partition_sha256=sha(target/'test-partition.json'),test_processes=test_workers,
        elapsed_seconds=time.time()-started,
        scope='Final full tests and operational/strict/experimental CLI defaults after source-bound acceptance. No experimental preference checkpoint is selected for legality.'))
    print('FINAL POST-ACCEPTANCE TESTS AND LEGAL DEFAULT VERIFIED',tests,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13')
    parser.add_argument('--checkout',required=True);parser.add_argument('--commit',required=True)
    parser.add_argument('--test-workers',type=int,default=4)
    args=parser.parse_args();run(args.out,args.checkout,args.commit,args.test_workers)
