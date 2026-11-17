"""Local-only, immutable, checksummed evidence packs. No network operations."""
import argparse
from collections import defaultdict
import json
from pathlib import Path,PurePosixPath
import tarfile

from scripts.cycle14_evidence import sha256,matches,install

GROUPS=('capabilities','learning','evaluation','evaluation-pre-freeze','diagnostics','performance','preservation','reproduction','pilots','supplement')
SCHEMA='cycle15-local-evidence-v1'


def safe(root,relative):
    name=PurePosixPath(relative)
    if not relative or name.is_absolute() or '..' in name.parts or str(name)!=relative or '\\' in relative:
        raise ValueError('Unsafe evidence path')
    root=Path(root).resolve();path=root.joinpath(*name.parts)
    for parent in [path,*path.parents]:
        if parent==root:break
        if parent.is_symlink():raise ValueError('Symlink in evidence destination')
    return path


def load(path):
    manifest=json.loads(Path(path).read_text())
    if manifest.get('schema')!=SCHEMA:raise ValueError('Unsupported manifest')
    names=set();assets={a['name']:a for a in manifest['assets']}
    if len(assets)!=len(manifest['assets']):raise ValueError('Duplicate asset')
    for name in assets:
        if Path(name).name!=name or not name.endswith('.tar'):raise ValueError('Unsafe asset name')
    for row in manifest['files']:
        safe('/tmp/c15-validation',row['path'])
        if row['path'] in names or row['asset'] not in assets:raise ValueError('Duplicate path or unknown asset')
        names.add(row['path'])
        if type(row['bytes']) is not int or row['bytes']<0:raise ValueError('Invalid size')
        if len(row['sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['sha256']):raise ValueError('Invalid hash')
    return manifest


def build(source,packs,manifest_path,limit=512*1024*1024):
    source=Path(source).resolve();packs=Path(packs).resolve();packs.mkdir(parents=True,exist_ok=True)
    if any(packs.iterdir()) or Path(manifest_path).exists():raise ValueError('Choose an unused pack generation and manifest')
    paths=sorted({p for group in GROUPS for p in (source/group).rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and not p.is_relative_to(source/'reproduction/source')}|
                 {p for p in source.iterdir() if p.is_file() and p.suffix in ('.json','.log','.xml')
                  and p.name!='finish.log'})
    objects={};files=[]
    for path in paths:
        if path.is_symlink():raise ValueError('Evidence source must be an ordinary file')
        h=sha256(path);size=path.stat().st_size
        if size>limit-10240:raise ValueError('One evidence file exceeds pack size')
        objects.setdefault(h,path);files.append(dict(path=str(path.relative_to(source)),sha256=h,bytes=size,mode=0o644))
    assets=[];assignment={};pack=None;used=0
    try:
        for h,path in sorted(objects.items()):
            size=path.stat().st_size;stored=512+((size+511)//512)*512
            if pack is None or used+stored+10240>limit:
                if pack:pack.close()
                name=f'cycle15-evidence-{len(assets)+1:03d}.tar';assets.append(dict(name=name))
                pack=tarfile.open(packs/name,'w',format=tarfile.USTAR_FORMAT);used=0
            info=tarfile.TarInfo('objects/'+h);info.size=size;info.mode=0o644;info.mtime=0
            with path.open('rb') as stream:pack.addfile(info,stream)
            used+=stored;assignment[h]=name
    finally:
        if pack:pack.close()
    for row in files:row['asset']=assignment[row['sha256']]
    for asset in assets:
        path=packs/asset['name'];asset.update(bytes=path.stat().st_size,sha256=sha256(path))
    manifest=dict(schema=SCHEMA,original_local_root=str(source),assets=assets,files=files,
        counts=dict(files=len(files),unique_objects=len(objects),original_bytes=sum(r['bytes'] for r in files),
                    pack_bytes=sum(a['bytes'] for a in assets)),remote_publication=False,
        scope='Generated research and preservation evidence; excludes checkouts, dependency environments and packs')
    Path(manifest_path).parent.mkdir(parents=True,exist_ok=True)
    Path(manifest_path).write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    return manifest['counts']


def verify(root,manifest):
    changed=[r['path'] for r in manifest['files'] if not matches(safe(root,r['path']),r)]
    return dict(passed=not changed,files=len(manifest['files']),missing_or_changed=changed)


def restore(root,packs,manifest):
    groups=defaultdict(list)
    for row in manifest['files']:
        target=safe(root,row['path'])
        if target.exists() and not matches(target,row):raise ValueError('Refusing to replace different evidence')
        groups[row['asset']].append(row)
    for asset in manifest['assets']:
        source=Path(packs)/asset['name']
        if not matches(source,asset):raise ValueError('Pack checksum mismatch')
        objects=defaultdict(list)
        for row in groups[asset['name']]:objects[row['sha256']].append(row)
        seen=set()
        with tarfile.open(source,'r:') as archive:
            for member in archive:
                h=member.name.removeprefix('objects/')
                if member.name!='objects/'+h or h not in objects or h in seen or not member.isfile():
                    raise ValueError('Unexpected or duplicate pack member')
                seen.add(h)
                for row in objects[h]:
                    if row['bytes']!=member.size:raise ValueError('Member size mismatch')
                    target=safe(root,row['path'])
                    if target.exists():continue
                    with archive.extractfile(member) as stream:install(stream,target,row)
        if seen!=set(objects):raise ValueError('Incomplete pack')
    result=verify(root,manifest)
    if not result['passed']:raise ValueError('Restoration verification failed')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('build','verify','restore'))
    p.add_argument('--root',required=True);p.add_argument('--packs');p.add_argument('--manifest',required=True)
    a=p.parse_args()
    result=build(a.root,a.packs,a.manifest) if a.command=='build' else verify(a.root,load(a.manifest)) if a.command=='verify' else restore(a.root,a.packs,load(a.manifest))
    print(json.dumps(result,indent=2))
    if result.get('passed') is False:raise SystemExit(1)
