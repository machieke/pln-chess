"""Source-bound C13 preservation and independent legal replay for Cycle 14."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha

START = '54353579e7921f9b47f43bbde1aa61cb887bc6e4'


def lock(out):
    out = Path(out).resolve()
    destination = out / 'manifest.json'
    if destination.exists():
        result = read_json(destination)
        assert result['starting_head'] == START
        return result
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == START
    from pln_chess.pln import Runtime
    from pln_chess.learning import Model
    from pln_chess.cycle6.inference import production_code_hash
    runtime = Runtime(); runtime.verify()
    tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], text=True).splitlines()
    protected = {p: sha(ROOT / p) for p in tracked if p.startswith(
        ('artifacts/', 'docs/', 'fixtures/', 'vendor/', 'configs/')) or p.endswith('.lock')}
    models = [
        'artifacts/cycle12/model/C12-default.json',
        'artifacts/cycle13/model/C13-default.json',
        'artifacts/cycle11/model/C11-field-trained.json',
        'artifacts/cycle12/model/C12-concept-trained.json',
        'artifacts/cycle13/model/C13-fork-role.json',
        'artifacts/cycle13/model/C13-preference-relational.json',
        'artifacts/cycle13/model/C13-preference-temporal.json',
    ]
    legal = Model.load(ROOT / models[0], runtime)
    assert legal.version == read_json(ROOT / 'configs/cycle14.json')['accepted_legal_model_version']
    assert sha(ROOT / models[0]) == sha(ROOT / models[1])
    result = dict(schema=14, starting_head=START,
        initial_working_tree=subprocess.check_output(['git', 'status', '--short'], text=True),
        runtime=runtime.manifest, production_code_hash=production_code_hash(),
        accepted_legal_version=legal.version,
        models={p: dict(sha256=sha(ROOT/p), version=read_json(ROOT/p)['version']) for p in models},
        protected_files=protected, starting_manifest_sha256=sha(ROOT/'artifacts/cycle13/artifact-manifest.json'),
        dataset_identities={p: h for p, h in protected.items() if '/datasets/' in p},
        dependency_lock_sha256=sha(ROOT/'requirements-dev.lock'),
        runtime_lock_sha256=sha(ROOT/'configs/runtime-lock.json'),
        registration_sha256=sha(ROOT/'configs/cycle14.json'), started_unix=time.time(),
        status='Source identity verified; execution reproduction is separately required')
    write_json(destination, result)
    write_json(out/'discrepancies.json', dict(discrepancies=[], reproduction_pending=True))
    print('C14 BASELINE LOCKED', len(protected), 'historical files', flush=True)
    return result


def run(out, source, workers=4):
    out, source = Path(out).resolve(), Path(source).resolve()
    manifest = read_json(out/'manifest.json')
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip() == START
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    py = str(source/'.venv/bin/python')
    env = {k:v for k,v in os.environ.items() if not (k.startswith('C') and k.endswith('_OUT'))}
    env.update(PLN_CHESS_ROOT=str(source), PYTHONPATH=f'{source}/src:{source}', TMPDIR='/dev/shm')
    population = read_json(source/'artifacts/cycle13/baseline/legal/panel.json')
    for job in population['jobs']:
        job['reference'] = f"artifacts/cycle13/current/legal/evaluation/{job['id']}.json.xz"
    population.pop('hash'); population['hash'] = digest(population)
    write_json(out/'legal/panel.json', population)

    def command(name, args):
        argv=[py,*args]; path=out/'commands'/f'{name}.json'
        identity=dict(source_head=START, argv=argv, driver_sha256=sha(__file__),
            production_code_hash=manifest['production_code_hash'])
        if path.exists():
            old=read_json(path)
            assert old['identity']==identity, 'Use a new execution generation for changed inputs'
            if old['returncode']==0:
                print('BASELINE RESUME', name, flush=True); return
        attempt=1
        while (out/'logs'/f'{name}.{attempt}.txt').exists(): attempt+=1
        log=out/'logs'/f'{name}.{attempt}.txt'; log.parent.mkdir(parents=True,exist_ok=True)
        started=time.time()
        with log.open('w') as stream:
            process=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipt=dict(identity=identity,returncode=process.returncode,elapsed_seconds=time.time()-started,
            started_unix=started,log=str(log.relative_to(out)),log_sha256=sha(log))
        write_json(out/'commands'/f'{name}.attempt-{attempt}.json', receipt)
        write_json(path,receipt)
        if process.returncode: raise RuntimeError(str(log))
        print('C14 BASELINE PASSED', name, flush=True)

    def legal():
        def shard(job):
            command('legal-'+job['id'], ['-m','scripts.cycle12_legal_review','--out',str(out),
                '--source',str(source),'--worker',job['id']])
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for _ in pool.map(shard,population['jobs']): pass
        from scripts.cycle12_baseline import compare_reports
        comparisons=[]
        for job in population['jobs']:
            comparisons.append(compare_reports(out/f"legal/evaluation/{job['id']}.json.xz",source/job['reference']))
        receipts=[read_json(out/f"legal/evaluation/{job['id']}.receipt.json") for job in population['jobs']]
        assert len(receipts)==206 and sum(r['rows'] for r in receipts)==584112
        assert all(r['passed'] and not r['changes'] for r in receipts)
        write_json(out/'legal-proof-parity.json',dict(passed=True,shards=206,rows=584112,
            comparisons=comparisons,exact_native_proof_parity=True))

    def tests_and_controls():
        collection=subprocess.check_output([py,'-m','pytest','--collect-only','-q'],cwd=source,env=env,text=True)
        (out/'collection.txt').write_text(collection)
        nodes=[line for line in collection.splitlines() if line.startswith('tests/') and '::' in line]
        assert len(nodes)==588 and len(set(nodes))==588
        counts=Counter(n.split('::',1)[0] for n in nodes); shards=[[],[]]; sizes=[0,0]
        for name,count in sorted(counts.items(),key=lambda v:(-v[1],v[0])):
            i=min(range(2),key=lambda j:(sizes[j],j)); shards[i].append(name); sizes[i]+=count
        def test(index):
            xml=out/f'tests-{index}.xml'
            command('tests-'+str(index),['-m','pytest','-q',*shards[index],f'--junitxml={xml}',
                '--basetemp',str(source/f'.runtime/c14-baseline-tests-{index}'),
                '-o',f'cache_dir={source}/.runtime/c14-baseline-cache-{index}'])
            suites=ET.parse(xml).getroot().findall('testsuite')
            assert sum(int(s.get('tests','0')) for s in suites)==sizes[index]
            assert all(int(s.get(k,'0'))==0 for s in suites for k in ('failures','errors','skipped'))
        with ThreadPoolExecutor(max_workers=2) as pool:
            for _ in pool.map(test,range(2)): pass
        write_json(out/'tests.json',dict(passed=True,tests=588,exact_once=True,collection=nodes,partitions=shards))
        command('negative-history-controls',['-m','evaluation.cycle12_legal_controls','--out',str(out)])
        command('recoveries-holdouts',['-m','evaluation.cycle12_legal_recovery','--out',str(out)])

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(legal),pool.submit(tests_and_controls)]
        for future in futures: future.result()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    assert read_json(out/'legal/negative-controls/verified.json')['passed']
    assert read_json(out/'legal/temporal/summary.json')['passed']
    assert read_json(out/'legal/recovery/verified.json')['passed']
    write_json(out/'legal-reproduction.json',dict(passed=True,source_head=START,source_clean=True,
        tests=588,legal_shards=206,legal_rows=584112,negative_controls=287,history_controls=27,
        recoveries=2,holdouts=76,proof_parity_sha256=sha(out/'legal-proof-parity.json'),
        scope='Fresh execution under the frozen C13 source; research reproduction is a separate required receipt'))
    print('C14 BASELINE LEGAL REPRODUCTION COMPLETE',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=('lock','run'))
    parser.add_argument('--out',default='artifacts/cycle14/baseline'); parser.add_argument('--source')
    parser.add_argument('--workers',type=int,default=4); args=parser.parse_args()
    if args.action=='lock': lock(args.out)
    else: run(args.out,args.source,args.workers)
