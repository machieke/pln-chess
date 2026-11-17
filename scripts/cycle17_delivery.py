"""Evidence transport, independent reproduction and publication-size preflight."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from research.cycle16.records import record
from scripts.cycle15_baseline import sha
from scripts.cycle17_baseline import START


def historical(out):
    out = Path(out); baseline = read_json(out/'baseline.json')
    Runtime().verify()
    assert Runtime().manifest == baseline['runtime']
    assert production_code_hash() == baseline['operational_source']
    protected = read_json(out/'protected-files.json')
    changed = [p for p, wanted in protected.items() if sha(ROOT/p) != wanted]
    assert not changed, changed
    from scripts.cycle14_evidence import load_manifest, verify
    from scripts.cycle15_evidence import load, verify as verify_local
    receipts = {'cycle14': verify(ROOT, load_manifest(ROOT/'publication/cycle14/manifest.json'))}
    for cycle in (15, 16):
        manifest = load(ROOT/f'publication/cycle{cycle}/manifest.json')
        receipts[f'cycle{cycle}'] = verify_local(manifest['original_local_root'], manifest)
    assert all(r['passed'] for r in receipts.values())
    return record(out/'historical-final.json', dict(passed=True, tracked_files=len(protected), changed=changed,
        historical=receipts, runtime_unchanged=True, operational_source=production_code_hash(),
        accepted_checkpoint_sha256=sha(ROOT/'artifacts/cycle12/model/C12-default.json')))


def reproduce(out, source):
    out = Path(out).resolve(); source = Path(source).resolve(); out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, 'PLN_CHESS_ROOT': str(source), 'PYTHONPATH': str(source/'src')+':'+str(source)}
    # Audit-hook denial proves these commands cannot read historical bulk or PGN.
    guard = '''import sys, runpy
def deny(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        path = str(args[0])
        if any(x in path for x in ('artifacts/cycle14', 'artifacts/cycle15', 'artifacts/cycle16', '.pgn')):
            raise RuntimeError('Historical evidence forbidden in minimal reproduction: '+path)
sys.addaudithook(deny)
'''
    commands = [
        [str(source/'.venv/bin/python'), '-c', guard+"sys.argv=['research.cycle17','minimal','--out',sys.argv[1]]; runpy.run_module('research.cycle17',run_name='__main__')", str(out/'minimal')],
        [str(source/'.venv/bin/python'), '-c', guard+"from training.cycle17_shared_evidence import evidence,fit; fit(evidence(),sys.argv[1],'D-AB')", str(out/'refit')],
        [str(source/'.venv/bin/python'), '-m', 'research.cycle17.reference_cli', '--out', str(out/'reference.json')],
    ]
    receipts = []
    for i, argv in enumerate(commands):
        log = out/f'command-{i}.log'
        with log.open('w') as stream:
            process = subprocess.run(argv, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT)
        receipts.append(dict(argv=argv, returncode=process.returncode, log=str(log), log_sha256=sha(log)))
        record(out/f'command-{i}.json', receipts[-1])
        if process.returncode:
            raise RuntimeError(str(log))
    model = read_json(out/'refit/model.json'); original = read_json(source/'artifacts/cycle17/learning/D-AB/model.json')
    assert model['rules'] == original['rules'] and model['structure_hash'] == original['structure_hash']
    results = read_json(out/'minimal/summary.json')['arms']
    assert all(results[a]['result']['stages']['Attack']['classification']=='supported-positive' for a in ('D-AB', 'D-BA'))
    assert all(results[a]['result']['stages']['Attack']['classification']=='unknown' for a in ('S-AA', 'S-BB', 'overlap-1', 'overlap-6'))
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source, text=True)
    return record(out/'verified.json', dict(passed=True, source_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
        commands=receipts, checkout_clean=True, exact_native_refit=True, historical_bulk_and_pgn_access_denied=True,
        scope='Clean Git checkout and existing verified dependencies; minimal native arms, actual refit, separate reference CLI; no fresh dependency installation'))


def compact(out):
    out = Path(out).resolve(); target = ROOT/'artifacts/cycle17'
    def publish(relative, destination=None):
        path = out/relative; dest = target/(destination or relative)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and sha(dest) != sha(path):
            raise ValueError('Refusing to replace different compact evidence: '+str(dest))
        shutil.copy2(path, dest)
    for group in ('baseline-replay', 'minimal-final', 'controls', 'evaluation', 'historical-evaluation', 'performance'):
        publish(group+'/summary.json')
    publish('reference-final/results.json')
    for relative in ('historical-final.json', 'training-audit.json', 'resource-census.json', 'supplement/proof-audit.json',
        'reproduction/verified.json', 'preservation/cycle17-verification.json', 'performance/proof-integrity.json'):
        publish(relative)
    # Complete training ledgers and revision receipts are modest and useful for review.
    for path in sorted((out/'learning').rglob('*.json')):
        publish(str(path.relative_to(out)))
    minimal = read_json(out/'minimal-final/summary.json')
    published = {}
    for arm, value in minimal['arms'].items():
        sources = {'native': value['result']['proof']}
        if value['witness']['diagnostic']:
            sources['guard'] = value['witness']['diagnostic']['proof']
        published[arm] = {}
        for kind, proof in sources.items():
            assert sha(proof['path']) == proof['sha256']
            relative = Path(proof['path']).relative_to(out)
            destination = f'witnesses/{arm}-{kind}.json'
            publish(str(relative), destination)
            published[arm][kind] = dict(path='artifacts/cycle17/'+destination, sha256=proof['sha256'])
    baseline = read_json(out/'baseline-replay/summary.json')
    for kind, proof in [('native', baseline['real_case']['proof']), ('guard', baseline['witness']['diagnostic']['proof'])]:
        destination = f'witnesses/historical-shared-{kind}.json'
        publish(str(Path(proof['path']).relative_to(out)), destination)
        published.setdefault('historical-shared', {})[kind] = dict(path='artifacts/cycle17/'+destination, sha256=proof['sha256'])
    write_json(target/'witnesses/index.json', published)
    return published


def pack(out):
    from scripts import cycle15_evidence as transport
    out = Path(out).resolve(); manifest_path = ROOT/'publication/cycle17/manifest.json'
    excluded = {'packs', 'restored-evidence', 'source', 'reproduction-source'}
    original = transport.GROUPS
    try:
        transport.GROUPS = tuple(sorted(p.name for p in out.iterdir() if p.is_dir() and p.name not in excluded))
        transport.build(out, out/'packs', manifest_path)
    finally:
        transport.GROUPS = original
    manifest = transport.load(manifest_path)
    mapping = {a['name']: a['name'].replace('cycle15-', 'cycle17-', 1) for a in manifest['assets']}
    for asset in manifest['assets']:
        old = asset['name']; asset['name'] = mapping[old]; (out/'packs'/old).rename(out/'packs'/asset['name'])
    for row in manifest['files']:
        row['asset'] = mapping[row['asset']]
    manifest.update(study='Cycle 17', transport_format='Unchanged Cycle 15 content-addressed local evidence format',
        availability='Local packs only; ordinary Git contains selected compact evidence; no bulk upload authorized')
    write_json(manifest_path, manifest)
    manifest = transport.load(manifest_path)
    assert transport.verify(out, manifest)['passed']
    restored = transport.restore(out/'restored-evidence', out/'packs', manifest)
    return record(ROOT/'artifacts/cycle17/restoration.json', dict(**restored, counts=manifest['counts'],
        manifest_sha256=sha(manifest_path), local_root=str(out), bulk_remote_publication=False))


def preflight(out):
    """Audit all new reachable blobs, not only tip files. No network writes."""
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['git', 'merge-base', '--is-ancestor', START, head], check=True)
    assert subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip() == 'cycle17-shared-evidence-semantics'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], text=True)
    changes = subprocess.check_output(['git', 'diff', '--name-status', START, head], text=True).splitlines()
    assert all(line.startswith('A\t') for line in changes), changes
    names = [line.split('\t', 1)[1] for line in changes]
    assert all('cycle17' in p or p == 'PLN_Chess_Cycle_17_Codex_Brief.md' for p in names)
    suspicious = []
    for name in names:
        data = (ROOT/name).read_bytes()
        if re.search(rb'(?m)^-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----', data) or re.search(rb'gh[pousr]_[A-Za-z0-9]{30,}', data):
            suspicious.append(name)
    assert not suspicious, suspicious
    objects = subprocess.check_output(['git', 'rev-list', '--objects', START+'..'+head], text=True)
    inventory = subprocess.check_output(['git', 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)'], input=objects, text=True)
    blobs = []
    for line in inventory.splitlines():
        fields = line.split(' ', 3)
        if fields[1] == 'blob':
            blobs.append(dict(oid=fields[0], bytes=int(fields[2]), path=fields[3] if len(fields)>3 else None))
    assert max(b['bytes'] for b in blobs) <= 10*1024**2
    assert sum(b['bytes'] for b in blobs) <= 100*1024**2
    return record(Path(out), dict(passed=True, starting_commit=START, local_head=head,
        new_unique_blobs=len(blobs), new_blob_bytes=sum(b['bytes'] for b in blobs), largest_blob=max(b['bytes'] for b in blobs),
        inventory=blobs, only_cycle17_additions=True, secret_scan_passed=True,
        scope='Reachable unpublished range size and local file scan; remote identity and final availability verified separately'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('command', choices=('historical', 'reproduce', 'compact', 'pack', 'preflight'))
    p.add_argument('--out', required=True); p.add_argument('--source'); a = p.parse_args()
    if a.command == 'reproduce' and not a.source:
        p.error('--source is required')
    result = reproduce(a.out, a.source) if a.command == 'reproduce' else globals()[a.command](a.out)
    print(json.dumps(result, indent=2))
