"""Fresh, immutable Cycle 12 replay before Cycle 13 production development.

The driver is new orchestration. All inference runs in the explicit starting
checkout, against the accepted Cycle 12 checkpoint and original datasets.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
import time

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha

START = 'b000898a0a1f46e556f161982f2c0e6d3944c322'


def run(out, source, workers=6):
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('Choose one through eight isolated legal replay workers')
    out, source = Path(out).resolve(), Path(source).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        from scripts.cycle10_bootstrap import run as bootstrap
        bootstrap(out.parent / 'baseline-bootstrap', source, START)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip() == START
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True)
    env = dict(os.environ, PLN_CHESS_ROOT=str(source), PYTHONPATH=f'{source}/src:{source}', TMPDIR='/dev/shm')
    for cycle in range(6, 14):
        env.pop(f'C{cycle}_OUT', None)
    py = str(source / '.venv/bin/python')
    probe = '''import json,sys,importlib.metadata
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle12.acceptance import default_checkpoint,accepted_model
from pln_chess.learning import Model
from pln_chess.common import ROOT
r=Runtime();r.verify();p=default_checkpoint(ROOT/'artifacts/cycle10/model/C10-default.json');m=Model.load(p,r)
assert accepted_model(m)
print(json.dumps(dict(runtime=r.manifest,production_code_hash=production_code_hash(),python=sys.version,
default_checkpoint=str(p.relative_to(ROOT)),accepted_model=m.version,
dependencies={k:importlib.metadata.version(k) for k in ('pytest','chess','setuptools')})))'''
    identity = json.loads(subprocess.check_output([py, '-c', probe], cwd=source, env=env, text=True))
    manifest_path = out / 'manifest.json'
    if not manifest_path.exists():
        original = read_json(source / 'artifacts/cycle12/manifest.json')
        for section, entries in original['entries'].items():
            base = source / ('artifacts/cycle12' if section == 'artifacts' else 'docs/cycle12')
            for relative, entry in entries.items():
                assert sha(base / relative) == entry['sha256'], relative
        tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', START], cwd=source, text=True).splitlines()
        protected = {p: sha(source / p) for p in tracked
                     if p.startswith(('artifacts/', 'docs/', 'fixtures/', 'vendor/', 'configs/')) or p.endswith('.lock')}
        write_json(manifest_path, dict(schema=13, starting_head=START, checkout=str(source), checkout_clean=True,
            initial_working_tree=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
            identity=identity, protected_files=protected, cycle12_manifest_sha256=sha(source/'artifacts/cycle12/manifest.json'),
            verified_cycle12_files={k:len(v) for k,v in original['entries'].items()},
            thresholds=read_json(source/'configs/cycle12.json')['thresholds'], started_unix=time.time()))
        models = [source/'artifacts/cycle12/model/C12-default.json',
                  source/'artifacts/cycle11/model/C11-field-trained.json',
                  source/'artifacts/cycle12/model/C12-concept-trained.json']
        write_json(out/'model-identities.json', {str(p.relative_to(source)):dict(sha256=sha(p),version=read_json(p)['version']) for p in models})
        write_json(out/'dataset-identities.json', {p:sha(source/p) for p in tracked if '/datasets/' in p and (source/p).is_file()})
    else:
        assert read_json(manifest_path)['identity'] == identity

    def command(name, args, overrides=None):
        argv=[py,*args];receipt=out/'commands'/f'{name}.json'
        effective=dict(env,**(overrides or {}))
        if receipt.exists():
            old=read_json(receipt)
            if old['source_head']==START and old['argv']==argv and old['returncode']==0:
                print('RESUME',name,flush=True);return
        log=out/'logs'/f'{name}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        started=time.time()
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=source,env=effective,stdout=stream,stderr=subprocess.STDOUT)
        write_json(receipt,dict(argv=argv,cwd=str(source),source_head=START,identity=identity,
            started_unix=started,elapsed_seconds=time.time()-started,returncode=result.returncode,
            log=str(log.relative_to(out)),driver_sha256=sha(__file__),environment_overrides=overrides or {}))
        if result.returncode:raise RuntimeError(str(log))
        print('BASELINE PASSED',name,flush=True)

    # Legacy study entry points require an already verified starting gate.
    # This explicitly carries Cycle 12 acceptance; it is not the new replay receipt.
    write_json(out/'baseline/reproduction-receipt.json',dict(passed=True,
        scope='Carried starting Cycle 12 acceptance for legacy driver preconditions; not a fresh replay claim.',
        reference=str(source/'artifacts/cycle12/acceptance.json'),
        reference_sha256=sha(source/'artifacts/cycle12/acceptance.json')))
    from scripts.cycle12_legal_review import panel
    population=panel(out,source)
    population['candidate']='artifacts/cycle12/model/C12-default.json'
    for job in population['jobs']:
        job['reference']=f"artifacts/cycle12/legal/evaluation/{job['id']}.json.xz"
    population.pop('hash');population['hash']=digest(population)
    write_json(out/'legal/panel.json',population)

    def legal():
        with ThreadPoolExecutor(max_workers=workers) as pool:
            jobs=[pool.submit(command,'legal-'+job['id'],['-m','scripts.cycle12_legal_review',
                '--out',str(out),'--source',str(source),'--worker',job['id']]) for job in population['jobs']]
            for job in jobs:job.result()

    def controls():
        command('history-and-negative-controls',['-m','evaluation.cycle12_legal_controls','--out',str(out)])
        command('accepted-recoveries-and-holdouts',['-m','evaluation.cycle12_legal_recovery','--out',str(out)])

    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs=[pool.submit(command,'tests',['-m','pytest','-q']),pool.submit(legal),pool.submit(controls)]
        for job in jobs:job.result()
    from scripts.cycle12_baseline import compare_reports
    actual=[out/f"legal/evaluation/{j['id']}.json.xz" for j in population['jobs']]
    reference=[source/j['reference'] for j in population['jobs']]
    with ProcessPoolExecutor(max_workers=4) as pool:
        comparisons=list(pool.map(compare_reports,actual,reference))
    receipts=[read_json(p.with_name(p.name.removesuffix('.json.xz')+'.receipt.json')) for p in actual]
    assert all(r['passed'] and not r['changes'] for r in receipts)
    write_json(out/'proof-parity.json',dict(passed=True,comparisons=comparisons,
        rows=sum(r['rows'] for r in receipts),shards=len(receipts),exact_native_proof_parity=True))

    research=out/'research'
    write_json(research/'baseline/reproduction-receipt.json',dict(passed=True,
        scope='New complete accepted-model legal replay passed before research.',
        proof_parity_sha256=sha(out/'proof-parity.json')))
    stages=(('concept-data','training.cycle12_data'),('concept-controls','training.cycle12_controls'),
        ('sequences','training.cycle12_sequences'),('dataset-audit','evaluation.cycle12_data_audit'),
        ('concept-learning','training.cycle12_learning'),('concept-evaluation','evaluation.cycle12_concepts'),
        ('dependence','evaluation.cycle12_dependence'),('partial-semantics','evaluation.cycle12_partial_semantics'),
        ('evolution','evaluation.cycle12_evolution'))
    for name,module in stages:
        command('research-'+name,['-m',module,'--out',str(research)],dict(C12_OUT=str(research)))
    from scripts.cycle12_research_replay import comparison_value
    from evaluation.cycle3 import read_gzip
    research_comparisons=[]
    for row in read_json(source/'artifacts/cycle12/clean-research/verified.json')['comparisons']:
        relative=row['path'];a=research/relative;b=source/'artifacts/cycle12'/relative
        if row.get('byte_identical'):
            assert sha(a)==sha(b),relative
            research_comparisons.append(dict(path=relative,byte_identical=True,sha256=sha(a)))
        else:
            load=read_gzip if relative.endswith('.xz') else read_json
            actual_hash=digest(comparison_value(relative,load(a)))
            assert actual_hash==digest(comparison_value(relative,load(b))),relative
            research_comparisons.append(dict(path=relative,semantic_identical=True,semantic_sha256=actual_hash))
    write_json(out/'research-parity.json',dict(passed=True,comparisons=research_comparisons,
        equality_exclusions=['execution','incremental','concepts/trapping-diagnostics.json.xz/*/legal_candidates/peak_process_rss_kib']))
    protected=read_json(manifest_path)['protected_files']
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    tests=(out/'logs/tests.txt').read_text();count=int(re.search(r'(\d+) passed',tests)[1])
    assert count==534
    write_json(out/'reproduction-receipt.json',dict(passed=True,starting_head=START,identity=identity,
        checkout=str(source),checkout_clean=True,test_count=count,legal_shards=len(receipts),
        legal_rows=sum(r['rows'] for r in receipts),negative_controls=287,
        history_controls=27,recoveries=2,holdouts=76,exact_native_proof_parity=True,
        research_comparisons=len(research_comparisons),protected_files=len(protected),
        model_identity_sha256=sha(out/'model-identities.json'),dataset_identity_sha256=sha(out/'dataset-identities.json'),
        completed_unix=time.time(),scope='Fresh starting source, dependencies and native runtime; complete accepted Cycle 12 legal and research replay.'))
    print('CYCLE 13 STARTING BASELINE VERIFIED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--source',required=True)
    parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args();run(args.out,args.source,args.workers)
