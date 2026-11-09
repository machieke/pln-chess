"""Immutable C8 replay. This driver adds no production inference behavior."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

START = '36b5ea10395c0f41de4c03824ba6f8ee1c5dbad1'
ARMS = ('C8-promotion-relative', 'C8-strict', 'C8-experimental')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n')


def worker(out, arm):
    from pln_chess.common import ROOT, read_json, digest
    from pln_chess.pln import Runtime
    from pln_chess.cycle8.model import PromotionModel
    from pln_chess.cycle8.inference import Cycle8Options
    from scripts.cycle8_evaluate import jobs
    from evaluation.cycle8 import evaluate
    from evaluation.cycle3 import read_gzip
    from evaluation.cycle7_io import pack
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == START
    rt = Runtime(timeout=180)
    model = PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json', rt)
    mode = {'C8-strict': 'strict', 'C8-experimental': 'experimental'}.get(arm, 'operational')
    summary = {}
    fields = ('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids',
              'dependence_groups','proof_status','backoff','model_version','runtime_version')
    for name, path, split in jobs(ROOT/'artifacts/cycle8', arm):
        target = out/f'evaluation/{arm}-{name}.json.xz'
        report = evaluate(read_json(path), model, split, rt,
                          Cycle8Options(mode=mode, max_native_invocations=100000, timeout_seconds=180), target)
        old = read_gzip(ROOT/f'artifacts/cycle8/evaluation/{arm}-{name}.json.xz')
        assert [{k:r[k] for k in fields} for r in report['rows']] == [{k:r[k] for k in fields} for r in old['rows']], (arm,name)
        assert [p['predicted'] for p in report['positions']] == [p['predicted'] for p in old['positions']]
        assert all(digest([report['native_proof_dag'][i] for i in r['proof_refs']]) == r['proof_id'] for r in report['rows'])
        assert report['metrics']['incomplete'] == 0
        summary[name] = dict(metrics=report['metrics'], positions=len(report['positions']), rows=len(report['rows']),
            exact_native_proof_parity=True, dataset_hash=report['dataset_hash'], dataset_sha256=sha(path),
            model_version=model.version, artifact=str(target.relative_to(out)), sha256=sha(target),
            proof_hash=digest([r['proof_id'] for r in report['rows']]))
        write(out/f'{arm}-summary.json', summary)
        print(arm, name, 'EXACT PARITY', flush=True)


def run(snapshot, out):
    root = Path(__file__).resolve().parents[1]
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() == START
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=snapshot,text=True).strip() == START
    env = dict(os.environ, PYTHONPATH=f'{snapshot}/src:{snapshot}', PLN_CHESS_ROOT=str(snapshot), TMPDIR='/dev/shm')
    for name in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT'): env.pop(name,None)
    manifest = json.loads((root/'artifacts/cycle8/manifest.json').read_text())['files']
    assert all(sha(root/p)==v['sha256'] for p,v in manifest.items()), 'Historical C8 manifest mismatch'
    tracked = subprocess.check_output(['git','ls-tree','-r','--name-only',START],cwd=root,text=True).splitlines()
    protected = {p:sha(root/p) for p in tracked if p.startswith(('artifacts/','docs/','fixtures/','vendor/','configs/')) or p.endswith('.lock')}
    runtime = json.loads(subprocess.check_output([sys.executable,'-c','import json; from pln_chess.pln import Runtime; r=Runtime(); r.verify(); print(json.dumps(r.manifest))'],cwd=snapshot,env=env,text=True))
    write(out/'lock.json', dict(starting_head=START, snapshot=str(snapshot), runtime=runtime,
        working_tree=subprocess.check_output(['git','status','--short'],cwd=root,text=True),
        source_files={str(p.relative_to(root)):sha(p) for p in sorted((root/'src').rglob('*.py'))},
        protected_files=protected, historical_manifest_entries=len(manifest), historical_manifest_verified=True,
        model_identity=json.loads((root/'artifacts/cycle8/acceptance.json').read_text()),
        datasets={str(p.relative_to(root)):sha(p) for p in sorted((root/'artifacts').rglob('dataset.json'))},
        limitations=['Positive legality is partial conditional evidence.', 'Historical timing is host-specific.',
                     'This replay uses the existing pinned runtime; fresh bootstrap is a separate gate.']))
    def command(arm):
        argv=[sys.executable,str(Path(__file__).resolve()),'--out',str(out),'--worker',arm]
        log=out/f'logs/{arm}.txt';log.parent.mkdir(parents=True,exist_ok=True);started=time.time()
        with log.open('w') as stream:
            result=subprocess.run(argv,cwd=snapshot,env=env,stdout=stream,stderr=subprocess.STDOUT)
        write(out/f'commands/{arm}.json',dict(argv=argv,cwd=str(snapshot),source_head=START,
            driver_sha256=sha(__file__),environment={k:env[k] for k in ('PYTHONPATH','PLN_CHESS_ROOT','TMPDIR')},
            started_unix=started,elapsed_seconds=time.time()-started,returncode=result.returncode,log=str(log.relative_to(out))))
        if result.returncode: raise RuntimeError(f'{arm} failed: {log}')
        return len(json.loads((out/f'{arm}-summary.json').read_text()))
    with ThreadPoolExecutor(max_workers=3) as pool:
        counts=list(pool.map(command,ARMS))
    assert all(sha(root/p)==h for p,h in protected.items())
    write(out/'verified.json',dict(passed=True,evaluations=sum(counts),exact_native_proof_parity=True,
        starting_head=START,protected_files=len(protected),runtime=runtime))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--snapshot',type=Path);parser.add_argument('--worker',choices=ARMS)
    args=parser.parse_args()
    worker(args.out,args.worker) if args.worker else run(args.snapshot,args.out)
