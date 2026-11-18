"""Frozen-source integrity, compact evidence, local pack and Git range checks."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3
import subprocess
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle20_baseline import START,BRANCH
from research.cycle19.records import record,sha

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def freeze(out):
    assert not git('status','--porcelain')
    files=[*sorted((ROOT/'research/cycle20').glob('*.py')),*sorted((ROOT/'research/cycle20').glob('*.pl')),
           *sorted((ROOT/'scripts').glob('cycle20*.py')),*sorted((ROOT/'tests').glob('test_cycle20*.py')),
           ROOT/'docs/cycle20/research-registration.md']
    assert git('branch','--show-current')==BRANCH
    return record(out/'source-freeze.json',dict(head=git('rev-parse','HEAD'),baseline=START,
        tree=git('rev-parse','HEAD^{tree}'),files={str(p.relative_to(ROOT)):sha(p) for p in files}))

def verify_frozen(out):
    frozen=read_json(out/'source-freeze.json')
    for name,h in frozen['files'].items():assert sha(ROOT/name)==h,name
    return frozen

def historical(out):
    from scripts.cycle14_evidence import load_manifest,verify
    from scripts.cycle15_evidence import load,verify as verify_external
    frozen=verify_frozen(out);baseline=read_json(out/'registration/baseline.json')
    protected=read_json(out/'registration/protected-files.json')
    assert not [p for p,h in protected.items() if sha(ROOT/p)!=h]
    original=Path(baseline['original_checkout'])
    checks={'cycle14':verify(original,load_manifest(ROOT/'publication/cycle14/manifest.json'))}
    for cycle in range(15,20):
        manifest=load(ROOT/f'publication/cycle{cycle}/manifest.json')
        checks[f'cycle{cycle}']=verify_external(manifest['original_local_root'],manifest)
    assert all(v['passed'] for v in checks.values())
    r=Runtime();assert r.manifest==baseline['runtime'] and production_code_hash()==baseline['operational_source']
    cp=ROOT/'artifacts/cycle12/model/C12-default.json'
    assert sha(cp)==baseline['legal_checkpoint_sha256'] and read_json(cp)['version']==baseline['legal_semantic_identity']
    return record(out/'protected-final.json',dict(passed=True,source=frozen['head'],protected=len(protected),manifests=checks,
        accepted_checkpoint=sha(cp),semantic_model=read_json(cp)['version'],runtime= digest(r.manifest)))

def catalog(out):
    from research.cycle15.native_reasoner import parse
    from research.cycle20.state import sentence
    from research.cycle20.native import decode
    directory=out/'meter';db=sqlite3.connect(directory/'starts.sqlite')
    counts=Counter();indexed={};errors=[];no_receipt=[];recategorized=[]
    for n,phase in db.execute('select n,phase from starts order by n'):
        counts[phase]+=1;path=directory/f'{n:05d}.json'
        if not path.exists():
            no_receipt.append(dict(n=n,phase=phase));continue
        receipt=read_json(path)['receipt'];ref=digest(receipt)
        indexed[ref]=str(path.relative_to(out))
        if receipt['incomplete']:errors.append(dict(n=n,phase=phase,timeout=receipt['timed_out']))
        if phase in ('comparison-A','comparison-BC') and '(C20STATE ' in receipt['stdout']:
            # Apply final transport validation to all native tuples, including
            # observations produced before the stamp namespace control was added.
            lines=receipt['stdout'].splitlines()
            qs=[l for l in lines if l.startswith('(C20READ ')]
            queues,selected,_,_=decode(receipt,qs,1)
            for queue in queues:
                for row in queue:sentence(row)
            recategorized.append(ref)
    archive=Path(read_json(ROOT/'publication/cycle19/manifest.json')['original_local_root'])
    comparisons=0
    def tuples(text,marker):
        return [line[len(marker):] for line in text.splitlines() if line.startswith(marker)]
    for file in sorted((out/'comparison-A/rows').glob('*.json')):
        row=read_json(file)
        new=read_json(out/indexed[row['receipt']])['receipt']
        for old_hash in row['baseline_proofs']:
            old=read_json(archive/'study/evaluation/raw'/(old_hash+'.json'))['receipt']
            for before,after in [('(C15STATE ','(C20STATE '),('(SELECTED ','(SELECTED ')]:
                assert tuples(old['stdout'],before)==tuples(new['stdout'],after),(file,old_hash,before)
            for before,after in [('c15tasks','c20tasks'),('c15beliefs','c20beliefs')]:
                assert tuples(old['program'],'(= ('+before+') ')==tuples(new['program'],'(= ('+after+') '),(file,before)
            comparisons+=1
    assert comparisons==2512
    record(out/'catalog/native-receipts.json',indexed)
    return record(out/'catalog/summary.json',dict(reserved=sum(counts.values()),by_phase=dict(counts),
        stdio_receipts=len(indexed),resident_processes_without_file_runner_receipt=no_receipt,
        incomplete_file_runner=errors,revalidated_panel_native_outputs=len(recategorized),
        exact_raw_legacy_stages=comparisons,exact_fresh_input_tuple_text=True,final_transport_verified=True,ceiling=6000))

def pack(out):
    from scripts import cycle15_evidence as transport
    target=ROOT/'publication/cycle20/manifest.json';previous=transport.GROUPS
    try:
        transport.GROUPS=tuple(sorted(d.name for d in out.iterdir() if d.is_dir() and d.name not in ('packs','restored-evidence')))
        transport.build(out,out/'packs',target)
    finally:transport.GROUPS=previous
    m=transport.load(target);names={a['name']:a['name'].replace('cycle15-','cycle20-',1) for a in m['assets']}
    for a in m['assets']:
        old=a['name'];a['name']=names[old];(out/'packs'/old).rename(out/'packs'/a['name'])
    for item in m['files']:item['asset']=names[item['asset']]
    m.update(study='Cycle 20',availability='Checksummed local evidence packs')
    write_json(target,m);m=transport.load(target)
    assert transport.verify(out,m)['passed']
    restored=transport.restore(out/'restored-evidence',out/'packs',m)
    return record(ROOT/'artifacts/cycle20/restoration.json',dict(**restored,counts=m['counts'],manifest_sha256=sha(target),
        bulk_remote_publication=False))

def preflight(out):
    head=git('rev-parse','HEAD')
    assert not git('status','--porcelain') and git('branch','--show-current')==BRANCH
    subprocess.run(['git','merge-base','--is-ancestor',START,head],cwd=ROOT,check=True)
    changes=git('diff','--name-status',START,head).splitlines()
    assert changes and all(line.startswith('A\t') and ('cycle20' in line or line.endswith('PLN_Chess_Cycle_20_Codex_Brief.md')) for line in changes)
    objs=git('rev-list','--objects',START+'..'+head)
    details=subprocess.check_output(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize) %(rest)'],input=objs+'\n',text=True,cwd=ROOT)
    blobs=[]
    for line in details.splitlines():
        oid,kind,size,*path=line.split(' ',3)
        if kind!='blob':continue
        data=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
        if re.search(rb'(?m)^-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{25,}|sk-proj-[A-Za-z0-9_-]{40,}|https?://[^/\s:]+:[^/\s@]+@',data):
            raise ValueError('Potential credential in object '+oid)
        blobs.append(dict(oid=oid,bytes=int(size),path=path[0]))
    largest=max(b['bytes'] for b in blobs);total=sum(b['bytes'] for b in blobs)
    assert largest<=10*1024**2 and total<=100*1024**2
    urls={}
    for label,args in [('fetch',[]),('push',['--push'])]:
        urls[label]=git('remote','get-url',*args,'--all','origin').splitlines()
        assert urls[label] and all(u in ('ssh://git@github.com/machieke/pln-chess','git@github.com:machieke/pln-chess.git','https://github.com/machieke/pln-chess.git') for u in urls[label]),'Unexpected destination'
    rewrites=subprocess.run(['git','config','--get-regexp',r'url\..*\.(insteadof|pushinsteadof)'],cwd=ROOT,capture_output=True,text=True)
    assert rewrites.returncode in (0,1) and all('dhall-lang' in line for line in rewrites.stdout.splitlines()),'Unreviewed URL rewrite'
    return record(out,dict(passed=True,baseline=START,head=head,branch=BRANCH,blobs=blobs,largest=largest,new_unique_bytes=total,
        new_unique_blobs=len(blobs),secret_pattern_scan=True,includes_superseded=True,urls=urls,destination_rewrites=0))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','historical','catalog','pack','preflight'));p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();globals()[a.mode](a.out.resolve());print(a.mode,'passed',flush=True)
