"""Source-bound execution, read-only reports, local packs and Git preflight."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle18_baseline import START,BRANCH
from research.cycle18.contracts import sha


def immutable(path,value):
    path=Path(path)
    if path.exists():raise ValueError('Generation already exists: '+str(path))
    write_json(path,value)
    return value


def freeze(out):
    out=Path(out);head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain'],text=True)
    paths=sorted([*ROOT.glob('research/cycle18/*.py'),*ROOT.glob('scripts/cycle18_*.py'),*ROOT.glob('tests/test_cycle18_*.py')])
    return immutable(out,dict(source_head=head,starting_commit=START,
        files={str(p.relative_to(ROOT)):sha(p) for p in paths},registration_sha256=sha(ROOT/'docs/cycle18/research-registration.md')))


def historical(out):
    from pln_chess.pln import Runtime
    from pln_chess.cycle6.inference import production_code_hash
    from scripts.cycle14_evidence import load_manifest,verify
    from scripts.cycle15_evidence import load,verify as verify_external
    out=Path(out);baseline=read_json(out/'registration/baseline.json');protected=read_json(out/'registration/protected-files.json')
    Runtime().verify();assert Runtime().manifest==baseline['runtime']
    assert production_code_hash()==baseline['operational_source']
    changed=[p for p,h in protected.items() if sha(ROOT/p)!=h]
    assert not changed,changed
    checks={'cycle14':verify(ROOT,load_manifest(ROOT/'publication/cycle14/manifest.json'))}
    for cycle in (15,16,17):
        manifest=load(ROOT/f'publication/cycle{cycle}/manifest.json')
        checks[f'cycle{cycle}']=verify_external(manifest['original_local_root'],manifest)
    assert all(v['passed'] for v in checks.values())
    return immutable(out/'historical-final.json',dict(passed=True,protected_files=len(protected),changed=changed,
        external_evidence=checks,runtime_unchanged=True,operational_source=production_code_hash(),
        legal_checkpoint_sha256=sha(ROOT/'artifacts/cycle12/model/C12-default.json')))


def reproduce(out,source):
    out=Path(out).resolve();source=Path(source).resolve();out.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'PLN_CHESS_ROOT':str(source),'PYTHONPATH':str(source/'src')+':'+str(source)}
    guard='''import sys,runpy
def deny(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        path=str(args[0])
        if any(s in path for s in ('artifacts/cycle14','artifacts/cycle15','artifacts/cycle16','.pgn')):
            raise RuntimeError('Historical bulk/PGN forbidden: '+path)
sys.addaudithook(deny)
'''
    commands=[]
    for mode in ('contract','native'):
        argv=[str(source/'.venv/bin/python'),'-c',guard+"sys.argv=['research.cycle18',sys.argv[1],'--out',sys.argv[2]]; runpy.run_module('research.cycle18',run_name='__main__')",mode,str(out/mode)]
        log=out/(mode+'.log')
        with log.open('x') as stream:
            process=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipt=dict(argv=argv,returncode=process.returncode,log=str(log),log_sha256=sha(log))
        immutable(out/(mode+'-command.json'),receipt);commands.append(receipt)
        if process.returncode:raise RuntimeError(str(log))
    reference=read_json(out/'contract/reference_cases/summary.json')
    assert read_json(out/'native/summary.json')['passed']
    assert len(reference)==72
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    return immutable(out/'verified.json',dict(passed=True,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        checkout_clean=True,commands=commands,historical_bulk_and_pgn_access_denied=True,
        scope='Clean checkout; full 432-row contract mapping, 72 reference fits and controls, all decisive native replay; reused verified dependencies, not fresh dependency installation'))


def resources(out):
    out=Path(out);seen={}
    def walk(value):
        if isinstance(value,dict):
            if 'program_sha256' in value and 'cpu_seconds' in value and 'stdout' in value:
                key=sha_json(value);seen[key]=value
            else:
                for v in value.values():walk(v)
        elif isinstance(value,list):
            for v in value:walk(v)
    # Deliberate inclusion of development and clean-reproduction executions.
    for directory in ('native-development','native-development-2','native','reproduction/native',
                      'source-correction-001/native','source-correction-001/reproduction/native'):
        for path in (out/directory).rglob('*.json'):
            walk(read_json(path))
    receipts=list(seen.values());jobs=[]
    for path in (out/'preservation/commands').glob('*.json'):
        receipt=read_json(path);log=Path(receipt['log']).read_text()
        def number(pattern):
            match=re.search(pattern,log);return float(match.group(1)) if match else 0
        jobs.append(dict(name=path.stem,returncode=receipt['returncode'],
            cpu_seconds=number(r'User time \(seconds\): ([\d.]+)')+number(r'System time \(seconds\): ([\d.]+)'),
            peak_rss_kib=number(r'Maximum resident set size \(kbytes\): (\d+)')))
    interrupted_jobs=[]
    for path in (out/'source-correction-001/preservation/commands').glob('*.json'):
        receipt=read_json(path)
        log=out/'source-correction-001/preservation/logs'/Path(receipt['log']).name
        contents=log.read_text()
        values=re.findall(r'(?:User|System) time \(seconds\): ([\d.]+)',contents)
        interrupted_jobs.append(dict(name=path.stem,returncode=receipt['returncode'],
            cpu_seconds=sum(float(v) for v in values),source_head=receipt['source_head']))
    reference=read_json(out/'contract/resources.json')
    counts=dict(native_invocations=sum(r['native_processes'] for r in receipts),native_cpu_seconds=sum(r['cpu_seconds'] for r in receipts),
        native_peak_rss_kib=max((r['peak_rss_kib'] or 0 for r in receipts),default=0),native_incomplete=sum(bool(r['incomplete']) for r in receipts),
        preservation_jobs=len(jobs),preservation_cpu_seconds=sum(r['cpu_seconds'] for r in jobs),
        preservation_max_job_rss_kib=max((r['peak_rss_kib'] for r in jobs),default=0),reference=reference,
        research_output_bytes=sum(p.stat().st_size for group in ('contract','native','reproduction','native-development','native-development-2')
            for p in (out/group).rglob('*') if p.is_file()),
        preservation_output_bytes=sum(p.stat().st_size for p in (out/'preservation').rglob('*') if p.is_file()),
        scope='Unique retained native process receipts including development and reproduction; preservation timed commands include full tests. Aggregate proof-comparison overhead is outside those job CPU totals; external observer separately reports it. Do not add overlapping counters.',
        jobs=jobs,interrupted_completed_jobs=interrupted_jobs,
        interrupted_completed_job_cpu_seconds=sum(r['cpu_seconds'] for r in interrupted_jobs),
        original_replay_ceiling=200,amended_replay_ceiling=300,
        amendment='Recorded before required reruns; component/payload-bound generation correction. Partial job CPU not fully captured; interrupted observer retained separately.')
    assert counts['native_invocations']<=300 and counts['native_cpu_seconds']<=3600
    assert counts['research_output_bytes']<=64*1024**2
    assert counts['preservation_cpu_seconds']+counts['interrupted_completed_job_cpu_seconds']<=24*3600 and counts['preservation_output_bytes']<=8*1024**3
    counts['budget_passed']=True
    return immutable(out/'resources.json',counts)


def sha_json(value):
    from research.cycle18.contracts import identity
    return identity(value)


def correspondence(out):
    from research.cycle18.reporting import correspondence as report
    out=Path(out)
    return immutable(out/'correspondence.json',report(ROOT,out/'contract',out/'native'))


def compact(out):
    out=Path(out);dest=ROOT/'artifacts/cycle18';copied=[]
    paths=[]
    for group in ('contract','native'):
        paths.extend(p for p in (out/group).rglob('*') if p.is_file())
    for relative in ('correspondence.json','historical-final.json','resources.json','source-provenance.json',
        'reproduction/verified.json','preservation/cycle18-verification.json','preservation/tests.xml','preservation-observer-summary.json'):
        paths.append(out/relative)
    for path in paths:
        target=dest/path.relative_to(out);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert sha(target)==sha(path),target
        else:shutil.copy2(path,target)
        copied.append(str(target.relative_to(ROOT)))
    return dict(files=len(copied),bytes=sum((ROOT/p).stat().st_size for p in copied))


def pack(out):
    from scripts import cycle15_evidence as transport
    out=Path(out).resolve();manifest_path=ROOT/'publication/cycle18/manifest.json'
    previous=transport.GROUPS
    try:
        transport.GROUPS=tuple(sorted(p.name for p in out.iterdir() if p.is_dir() and p.name not in ('packs','restored-evidence','source')))
        transport.build(out,out/'packs',manifest_path)
    finally:transport.GROUPS=previous
    manifest=transport.load(manifest_path)
    names={a['name']:a['name'].replace('cycle15-','cycle18-',1) for a in manifest['assets']}
    for asset in manifest['assets']:
        old=asset['name'];asset['name']=names[old];(out/'packs'/old).rename(out/'packs'/asset['name'])
    for item in manifest['files']:item['asset']=names[item['asset']]
    manifest.update(study='Cycle18',availability='Local packs only; no bulk upload authorized')
    write_json(manifest_path,manifest);manifest=transport.load(manifest_path)
    assert transport.verify(out,manifest)['passed']
    restored=transport.restore(out/'restored-evidence',out/'packs',manifest)
    return immutable(ROOT/'artifacts/cycle18/restoration.json',dict(**restored,counts=manifest['counts'],
        manifest_sha256=sha(manifest_path),local_root=str(out),bulk_remote_publication=False))


def preflight(out):
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',START,head],check=True)
    assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()==BRANCH
    assert not subprocess.check_output(['git','status','--porcelain'],text=True)
    changes=subprocess.check_output(['git','diff','--name-status',START,head],text=True).splitlines()
    assert changes and all(r.startswith('A\t') and ('cycle18' in r or r.endswith('PLN_Chess_Cycle_18_Codex_Brief.md')) for r in changes)
    objects=subprocess.check_output(['git','rev-list','--objects',START+'..'+head],text=True)
    inventory=subprocess.check_output(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)'],input=objects,text=True)
    blobs=[]
    for line in inventory.splitlines():
        oid,kind,size,*name=line.split(' ',3)
        if kind!='blob':continue
        data=subprocess.check_output(['git','cat-file','blob',oid])
        assert not re.search(rb'(?m)^-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',data),oid
        assert not re.search(rb'gh[pousr]_[A-Za-z0-9]{30,}',data),oid
        blobs.append(dict(oid=oid,bytes=int(size),path=name[0] if name else None))
    assert max(b['bytes'] for b in blobs)<=10*1024**2
    assert sum(b['bytes'] for b in blobs)<=100*1024**2
    urls={}
    for mode,args in [('fetch',[]),('push',['--push'])]:
        urls[mode]=subprocess.check_output(['git','remote','get-url',*args,'--all','origin'],text=True).splitlines()
        assert len(urls[mode])==1 and urls[mode][0] in ('ssh://git@github.com/machieke/pln-chess','git@github.com:machieke/pln-chess.git','https://github.com/machieke/pln-chess.git')
    rewrites=subprocess.run(['git','config','--get-regexp',r'url\..*\.(insteadof|pushinsteadof)'],capture_output=True,text=True)
    assert rewrites.returncode in (0,1)
    assert all('dhall-lang' in r for r in rewrites.stdout.splitlines()),'Unexpected URL rewrite requires review'
    return immutable(out,dict(passed=True,starting_commit=START,local_head=head,branch=BRANCH,
        new_unique_blobs=len(blobs),new_blob_bytes=sum(b['bytes'] for b in blobs),largest_blob=max(b['bytes'] for b in blobs),
        blobs=blobs,secret_pattern_scan_passed=True,urls=urls,only_unrelated_dhall_rewrite=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('freeze','historical','reproduce','resources','correspondence','compact','pack','preflight'))
    p.add_argument('--out',required=True);p.add_argument('--source');a=p.parse_args()
    value=reproduce(a.out,a.source) if a.command=='reproduce' else globals()[a.command](a.out)
    print(json.dumps(value,sort_keys=True) if a.command not in ('resources','historical','preflight') else 'passed')
