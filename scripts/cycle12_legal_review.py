"""Complete candidate review, including every established legal cohort.

The candidate is the byte-identical Cycle 11 special-local checkpoint. The
source checkout is explicit, clean and independently bootstrapped. Results,
including failures, are retained before the promotion decision is calculated.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha, ARMS


def panel(out,source):
    from scripts.cycle8_evaluate import jobs as historical_jobs
    out,source=Path(out),Path(source)
    jobs=[]
    for arm in ARMS:
        for name,path,split in historical_jobs(source/'artifacts/cycle8',arm):
            relative=path.relative_to(source) if path.is_relative_to(source) else path.relative_to(ROOT)
            jobs.append(dict(id='historical-'+arm+'-'+name,dataset=str(relative),split=split,fixtures=None,
                mode={'C8-strict':'strict','C8-experimental':'experimental'}.get(arm,'operational'),history=False,
                reference=f'artifacts/cycle11/current/historical/regression/{arm}-{name}.json.xz',cohort='historical/'+name))
    assert len(jobs)==26
    for group,cycle in (('historical',9),('external',10)):
        for path in sorted((source/f'artifacts/cycle11/current/{group}/evaluation').glob('*.receipt.json')):
            old=read_json(path);identity=old['identity']
            data=read_json(source/f'artifacts/cycle{cycle}/datasets/dataset.json')
            ids=identity['fixtures'];selected=[p for p in data['positions'] if p['id'] in ids]
            assert len(selected)==len(ids)
            fixture=selected[0]
            jobs.append(dict(id=f'cycle{cycle}-'+path.name.removesuffix('.receipt.json'),
                dataset=f'artifacts/cycle{cycle}/datasets/dataset.json',split=fixture['split'],fixtures=ids,
                mode=identity['mode'],history=identity.get('arm')=='temporal',
                reference=f'artifacts/cycle11/current/{group}/'+old['artifact'],
                cohort=f'cycle{cycle}/'+fixture['split']+'/'+identity['mode']+'/'+('history' if identity.get('arm')=='temporal' else 'fen')))
    assert len(jobs)==206
    payload=dict(schema=12,jobs=jobs,candidate='artifacts/cycle11/model/C11-special-local.json',
        candidate_version=read_json(source/'configs/cycle12.json')['promotion_candidate_version'] if (source/'configs/cycle12.json').exists() else read_json(ROOT/'configs/cycle12.json')['promotion_candidate_version'],
        population='26 historical suites, 48 Cycle 9 shards, all 132 Cycle 10 FEN/history and secondary-mode shards; no descriptor-based external selection.',
        candidate_selection='Frozen Cycle 11 checkpoint, no Cycle 12 training or retuning.')
    payload['hash']=digest(payload)
    write_json(out/'legal/panel.json',payload)
    return payload


def worker(out,source,identifier):
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from pln_chess.cycle6.inference import production_code_hash
    from evaluation.cycle8 import evaluate
    from evaluation.cycle10_temporal_eval import evaluate_temporal
    from evaluation.cycle3 import read_gzip
    out,source=Path(out),Path(source)
    manifest=read_json(out/'legal/panel.json')
    job=next(j for j in manifest['jobs'] if j['id']==identifier)
    runtime=Runtime(timeout=180)
    model=PromotionModel.load(source/manifest['candidate'],runtime)
    assert model.version==manifest['candidate_version']
    data=read_json(source/job['dataset'])
    if job['fixtures'] is not None:
        lookup={p['id']:p for p in data['positions']}
        data={**data,'positions':[lookup[i] for i in job['fixtures']]}
    target=out/f'legal/evaluation/{identifier}.json.xz'
    receipt=target.with_name(identifier+'.receipt.json')
    identity=dict(production_code_hash=production_code_hash(),model_version=model.version,runtime_version=runtime.version,
        dataset_sha256=sha(source/job['dataset']),job=job,panel_hash=manifest['hash'],driver_sha256=sha(__file__))
    if receipt.exists():
        previous=read_json(receipt)
        if previous['identity']==identity and target.exists() and previous['sha256']==sha(target):
            print('VERIFIED RESUME',identifier,flush=True);return
    evaluator=evaluate_temporal if job['history'] else evaluate
    report=evaluator(data,model,job['split'],runtime,
        Cycle8Options(mode=job['mode'],timeout_seconds=180,max_native_invocations=100000),target)
    assert all(digest([report['native_proof_dag'][i] for i in r['proof_refs']])==r['proof_id'] for r in report['rows'])
    old=read_gzip(source/job['reference'])
    assert [(r['fixture'],r['move'],r['label']) for r in report['rows']]==[(r['fixture'],r['move'],r['label']) for r in old['rows']]
    changes=[];regressions=[]
    for a,b in zip(old['rows'],report['rows']):
        if a['classification']!=b['classification']:
            change=dict(fixture=b['fixture'],move=b['move'],label=b['label'],before=a['classification'],after=b['classification'],
                before_tv=a['truth_value'],after_tv=b['truth_value'],before_proof=a['proof_id'],after_proof=b['proof_id'],
                added_evidence=sorted(set(b['evidence_ids'])-set(a['evidence_ids'])))
            changes.append(change)
            if a['classification'] in ('supported-legal','supported-illegal'):
                regressions.append(change)
    gates=dict(no_false_legal=report['metrics']['false_positive']==0,
        no_false_illegal=report['metrics']['false_illegal']==0,
        no_self_check_false_legal=report['metrics']['self_check_false_legal']==0,
        complete=report['metrics']['incomplete']==0,preserved_supported_classifications=not regressions,
        native_proofs_verified=True)
    write_json(receipt,dict(identity=identity,artifact=str(target.relative_to(out)),sha256=sha(target),
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        native_proofs_verified=True,rows=len(report['rows']),positions=len(report['positions']),metrics=report['metrics'],
        before_metrics=old['metrics'],changes=changes,regressions=regressions,gates=gates,passed=all(gates.values()),
        comparison_scope='Complete candidate population and native proof rehash. Checkpoint/model identity changes are expected; no claim of byte-identical proofs between learned models.'))
    print('CANDIDATE',identifier,gates,flush=True)


def run(out,source,workers=6):
    out,source=Path(out).resolve(),Path(source).resolve()
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    manifest=panel(out,source)
    env=dict(os.environ,PLN_CHESS_ROOT=str(source),PYTHONPATH=f'{source}/src:{source}',TMPDIR='/dev/shm')
    for name in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT','C11_OUT','C12_OUT'):env.pop(name,None)
    def command(job):
        identifier=job['id']
        argv=[str(source/'.venv/bin/python'),str(Path(__file__).resolve()),'--out',str(out),'--source',str(source),'--worker',identifier]
        log=out/f'legal/logs/{identifier}.txt';log.parent.mkdir(parents=True,exist_ok=True)
        started=time.time()
        with log.open('w') as stream:result=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write_json(out/f'legal/commands/{identifier}.json',dict(argv=argv,returncode=result.returncode,started_unix=started,
            elapsed_seconds=time.time()-started,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
            log=str(log.relative_to(out))))
        if result.returncode:raise RuntimeError(str(log))
        print('CANDIDATE REVIEW',identifier,flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for _ in pool.map(command,manifest['jobs']):pass
    receipts=[read_json(out/f"legal/evaluation/{j['id']}.receipt.json") for j in manifest['jobs']]
    write_json(out/'legal/regression-summary.json',dict(passed=all(r['passed'] for r in receipts),
        panel_hash=manifest['hash'],candidate_version=manifest['candidate_version'],shards=len(receipts),
        rows=sum(r['rows'] for r in receipts),positions=sum(r['positions'] for r in receipts),
        failures=[r['artifact'] for r in receipts if not r['passed']],
        changes=sum(len(r['changes']) for r in receipts),
        regressions=sum(len(r['regressions']) for r in receipts),
        totals={k:sum(r['metrics'][k] for r in receipts) for k in ('false_positive','false_illegal','self_check_false_legal','incomplete')},
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        scope=manifest['population'],promotion_decided=False))
    print('COMPLETE CANDIDATE POPULATION REVIEW FINISHED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--source',required=True)
    parser.add_argument('--worker');parser.add_argument('--workers',type=int,default=6)
    args=parser.parse_args()
    if args.worker:worker(args.out,args.source,args.worker)
    else:run(args.out,args.source,args.workers)
