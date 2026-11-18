"""Cycle19 frozen-source delivery, complete-range preflight and local packs."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from pln_chess.common import ROOT,read_json,write_json,digest
from scripts.cycle19_baseline import START,BRANCH
from research.cycle19.records import sha,record as immutable


def freeze(out):
    out=Path(out);head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain'],text=True)
    paths=sorted([*ROOT.glob('research/cycle19/*.py'),*ROOT.glob('scripts/cycle19_*.py'),*ROOT.glob('tests/test_cycle19_*.py'),*ROOT.glob('artifacts/cycle19/corpus-registration.json')])
    return immutable(out,dict(source_head=head,starting_commit=START,
        files={str(p.relative_to(ROOT)):sha(p) for p in paths},registration_sha256=sha(ROOT/'docs/cycle19/research-registration.md')))

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
    for cycle in (15,16,17,18):
        manifest=load(ROOT/f'publication/cycle{cycle}/manifest.json')
        checks[f'cycle{cycle}']=verify_external(manifest['original_local_root'],manifest)
    assert all(v['passed'] for v in checks.values())
    return immutable(out/'historical-final.json',dict(passed=True,protected_files=len(protected),changed=changed,
        external_evidence=checks,runtime_unchanged=True,operational_source=production_code_hash(),
        legal_checkpoint_sha256=sha(ROOT/'artifacts/cycle12/model/C12-default.json')))

def pack(out):
    from scripts import cycle15_evidence as transport
    out=Path(out).resolve();manifest_path=ROOT/'publication/cycle19/manifest.json'
    previous=transport.GROUPS
    try:
        transport.GROUPS=tuple(sorted(p.name for p in out.iterdir() if p.is_dir() and p.name not in ('packs','restored-evidence','source')))
        transport.build(out,out/'packs',manifest_path)
    finally:transport.GROUPS=previous
    manifest=transport.load(manifest_path)
    names={a['name']:a['name'].replace('cycle15-','cycle19-',1) for a in manifest['assets']}
    for asset in manifest['assets']:
        old=asset['name'];asset['name']=names[old];(out/'packs'/old).rename(out/'packs'/asset['name'])
    for item in manifest['files']:item['asset']=names[item['asset']]
    manifest.update(study='Cycle19',availability='Local packs only; no bulk upload authorized')
    write_json(manifest_path,manifest);manifest=transport.load(manifest_path)
    assert transport.verify(out,manifest)['passed']
    restored=transport.restore(out/'restored-evidence',out/'packs',manifest)
    return immutable(ROOT/'artifacts/cycle19/restoration.json',dict(**restored,counts=manifest['counts'],
        manifest_sha256=sha(manifest_path),local_root=str(out),bulk_remote_publication=False))

def preflight(out):
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',START,head],check=True)
    assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()==BRANCH
    assert not subprocess.check_output(['git','status','--porcelain'],text=True)
    changes=subprocess.check_output(['git','diff','--name-status',START,head],text=True).splitlines()
    assert changes and all(r.startswith('A\t') and ('cycle19' in r or r.endswith('PLN_Chess_Cycle_19_Codex_Brief.md')) for r in changes)
    objects=subprocess.check_output(['git','rev-list','--objects',START+'..'+head],text=True)
    inventory=subprocess.check_output(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)'],input=objects,text=True)
    blobs=[]
    for line in inventory.splitlines():
        oid,kind,size,*name=line.split(' ',3)
        if kind!='blob':continue
        data=subprocess.check_output(['git','cat-file','blob',oid])
        assert not re.search(rb'(?m)^-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',data),oid
        assert not re.search(rb'gh[pousr]_[A-Za-z0-9]{30,}',data),oid
        assert not re.search(rb'(?:github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{25,}|sk-proj-[A-Za-z0-9_-]{40,})',data),oid
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


def reproduce(out,source,meter):
    out=Path(out).resolve();source=Path(source).resolve();out.mkdir(parents=True,exist_ok=False)
    env={**os.environ,'PLN_CHESS_ROOT':str(source),'PYTHONPATH':str(source/'src')+':'+str(source)}
    guard='''import sys,runpy
def deny(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        path=str(args[0])
        if any(s in path for s in ('artifacts/cycle14','artifacts/cycle15/','artifacts/cycle16/','.pgn')):
            raise RuntimeError('Historical bulk/PGN forbidden: '+path)
sys.addaudithook(deny)
sys.argv=['research.cycle19','compact','--out',sys.argv[1],'--meter',sys.argv[2]]
runpy.run_module('research.cycle19',run_name='__main__')
'''
    log=out/'command.log';argv=[str(source/'.venv/bin/python'),'-c',guard,str(out/'compact'),str(meter)]
    with log.open('x') as stream:
        process=subprocess.run(['/usr/bin/time','-v',*argv],cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
    receipt=dict(argv=argv,returncode=process.returncode,log=str(log),log_sha256=sha(log))
    immutable(out/'command.json',receipt)
    if process.returncode:raise RuntimeError(str(log))
    assert read_json(out/'compact/verified.json')['passed']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    return immutable(out/'verified.json',dict(passed=True,source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        checkout_clean=True,command=receipt,historical_bulk_and_pgn_access_denied=True,
        dependencies='Verified existing Python environment and pinned native runtime; not a fresh dependency installation'))


def resources(out):
    out=Path(out);reservations=list((out/'meter').glob('*-reservation.json'));receipts=[read_json(p) for p in (out/'meter').glob('*-receipt.json')]
    categories={}
    for item in receipts:
        r=item['receipt'];c=categories.setdefault(item['category'],dict(calls=0,cpu_seconds=0,wall_seconds=0,peak_rss_kib=0,incomplete=0))
        c['calls']+=1;c['cpu_seconds']+=r['cpu_seconds'] or 0;c['wall_seconds']+=r['wall_seconds']
        c['peak_rss_kib']=max(c['peak_rss_kib'],r['peak_rss_kib'] or 0);c['incomplete']+=bool(r['incomplete'])
    jobs=[]
    for path in (out/'preservation/commands').glob('*.json'):
        receipt=read_json(path);log=Path(receipt['log']).read_text()
        cpu=sum(float(v) for v in re.findall(r'(?:User|System) time \(seconds\): ([\d.]+)',log))
        memory=re.search(r'Maximum resident set size \(kbytes\): (\d+)',log)
        jobs.append(dict(name=path.stem,returncode=receipt['returncode'],cpu_seconds=cpu,
            wall_seconds=receipt['elapsed_seconds'],peak_rss_kib=int(memory[1]) if memory else None))
    phases={p.stem:read_json(p) for p in (out/'study').glob('*-resources.json')}
    research_bytes=sum(p.stat().st_size for group in ('anchors','meter','study','compact-development','reproduction') for p in (out/group).rglob('*') if p.is_file())
    preservation_bytes=sum(p.stat().st_size for p in (out/'preservation').rglob('*') if p.is_file())
    value=dict(native_reserved=len(reservations),native_receipts=len(receipts),native_categories=categories,
        unreturned_reservations=len(reservations)-len(receipts),native_incomplete=sum(c['incomplete'] for c in categories.values()),
        research_native_cpu_seconds=sum(c['cpu_seconds'] for c in categories.values()),phases=phases,
        preservation_jobs=jobs,preservation_cpu_seconds=sum(j['cpu_seconds'] for j in jobs),
        research_bytes=research_bytes,preservation_bytes=preservation_bytes,
        observer=read_json(out/'preservation-observer-summary.json'),
        publication_reserve_calls=70,ceiling=4000,
        scope='Native receipts are subsets of phase child CPU; do not add overlapping counters. Observer CPU/RSS are sampled lower bounds. Final published replay receipt is external to this sealed evidence root.')
    assert value['native_reserved']+70<=4000 and value['research_native_cpu_seconds']<=12*3600
    assert research_bytes<=2*1024**3 and preservation_bytes<=8*1024**3 and value['preservation_cpu_seconds']<=24*3600
    return immutable(out/'resources.json',value)


def compact(out):
    """Publish principal inputs/proofs; index bulk calls without copying them."""
    out=Path(out);dest=ROOT/'artifacts/cycle19';dest.mkdir(exist_ok=True)
    copied={}
    def portable(value,proofs=True):
        if isinstance(value,list):return [portable(v,proofs) for v in value]
        if not isinstance(value,dict):return value
        value=dict(value)
        if {'path','sha256'}<=value.keys() and Path(value['path']).is_absolute():
            source=Path(value['path']);assert sha(source)==value['sha256']
            if proofs:
                target=dest/'proofs'/(value['sha256']+source.suffix);target.parent.mkdir(exist_ok=True)
                if not target.exists():shutil.copy2(source,target)
                copied[str(target.relative_to(ROOT))]=sha(target);value['path']=str(target.relative_to(ROOT))
            else:value['path']='local-pack:'+str(source.relative_to(out))
        return {k:portable(v,proofs) for k,v in value.items()}
    def save(relative,value,proofs=True):
        target=dest/relative;write_json(target,portable(value,proofs));copied[str(target.relative_to(ROOT))]=sha(target)
    for name in ('source-provenance.json','historical-final.json','resources.json','preservation/cycle19-verification.json','reproduction/verified.json'):
        save(name,read_json(out/name),False)
    save('anchors/summary.json',read_json(out/'anchors/summary.json'))
    for name in ('episodes.json','manual-fixtures.json','novelty.json','query-meaning.json'):
        save('measurement/'+name,read_json(out/'study/measurement'/name),False)
    save('learning/models.json',read_json(out/'study/learning/models.json'))
    for arm in ('D-AB','D-BA','S-AA','S-BB','P'):
        save('learning/'+arm+'/ledger.json',read_json(out/'study/learning'/arm/'ledger.json'))
    for name in ('summary.json','leave-one-result.json','binding-controls.json','removed-support.json','unknown-correction.json','identity-correction.json'):
        save('lifecycle/'+name,read_json(out/'study/lifecycle'/name))
    for name in ('incremental','full'):
        value=read_json(out/'study/lifecycle'/(name+'.json'));value.pop('snapshot')
        save('lifecycle/'+name+'.json',value)
    metrics=read_json(out/'study/evaluation/summary.json');save('native-results.json',metrics,False)
    rows=[read_json(p) for p in sorted((out/'study/evaluation/rows').glob('*.json'))]
    natural=[r for r in rows if r['variant']=='natural']
    from research.cycle19.corpus import roots
    order={r['id']:i for i,r in enumerate(roots())}
    natural.sort(key=lambda r:order[r['root']]);rows.sort(key=lambda r:(order[r['root']],r['variant']))
    train={digest(r['endpoint_locations']) for r in roots() if r['split'] in ('A','B')}
    new_endpoint={r['id'] for r in roots() if r['split']=='test' and digest(r['endpoint_locations']) not in train}
    down={r['id'] for r in roots() if r['split']=='test' and r['direction']=='-y'}
    selectors={
        'positive':lambda r:r['variant']=='natural' and r['measurement']['Clear']['value'] is True and r['arm']=='D-AB',
        'blocked':lambda r:r['variant']=='natural' and r['measurement']['Attack']['value'] is False and r['arm']=='F',
        'missing':lambda r:r['variant']=='EU' and r['arm']=='D-AB',
        'new-endpoint':lambda r:r['root'] in new_endpoint and r['variant']=='natural' and r['arm']=='D-AB',
        'heldout-direction':lambda r:r['root'] in down and r['variant']=='natural' and r['arm']=='D-AB',
        'shared-limitation':lambda r:r['split']=='A' and r['variant']=='natural' and r['arm']=='S-AA'}
    demonstrations={}
    for name,selector in selectors.items():
        selected=next((r for r in rows if selector(r)),None)
        if selected is None and name=='blocked':selected=next(r for r in rows if r['variant']=='OE' and r['arm']=='F')
        demonstrations[name]=selected
        if selected:save('demonstrations/'+name+'.json',selected)
    controls=read_json(out/'study/lifecycle/summary.json')
    demonstrations['source-removal']=controls['leave_one'];demonstrations['environment-correction']=controls['correction']
    save('demonstrations/source-removal.json',controls['leave_one']);save('demonstrations/environment-correction.json',controls['correction'])
    save('demonstrations/index.json',{k:dict(available=v is not None,path='artifacts/cycle19/demonstrations/'+k+'.json') for k,v in demonstrations.items()})
    save('evaluation-index.json',[dict(root=r['root'],game=r['game'],variant=r['variant'],population=r['population'],split=r['split'],arm=r['arm'],
        measurements={k:r['measurement'][k]['value'] for k in ('Clear','Attack')},
        stages=r['native']['stages']) for r in rows],False)
    target=dest/'preservation/tests.xml';target.parent.mkdir(exist_ok=True);shutil.copy2(out/'preservation/tests.xml',target)
    copied[str(target.relative_to(ROOT))]=sha(target)
    return immutable(dest/'compact-inventory.json',dict(files=copied,bytes=sum((ROOT/p).stat().st_size for p in copied)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('freeze','historical','pack','preflight','reproduce','resources','compact'))
    p.add_argument('--out',required=True);p.add_argument('--source');p.add_argument('--meter');a=p.parse_args()
    result=reproduce(a.out,a.source,a.meter) if a.command=='reproduce' else globals()[a.command](a.out)
    print('passed',a.command)
