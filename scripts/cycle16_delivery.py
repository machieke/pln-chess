"""Local source preparation, historical verification and compact evidence delivery."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import os
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.pln import Runtime
from scripts.cycle15_baseline import sha
from research.cycle16.records import record


def prepare(source):
    source=Path(source).resolve()
    for name in ('.venv','.runtime'):
        target=source/name
        if not target.exists():target.symlink_to(ROOT/name,target_is_directory=True)
    # Only missing, ignored historical evidence is linked. Tracked source and
    # receipts come from Git, never from the working tree.
    original=ROOT/'artifacts/cycle14';target=source/'artifacts/cycle14'
    def link_missing(old,new):
        if not new.exists():new.symlink_to(old,target_is_directory=old.is_dir())
        elif old.is_dir() and not new.is_symlink():
            for child in old.iterdir():link_missing(child,new/child.name)
    link_missing(original,target)
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)


def historical(out):
    out=Path(out);baseline=read_json(out/'baseline.json');runtime=Runtime()
    assert runtime.manifest==baseline['runtime']
    assert production_code_hash()==baseline['operational_source']
    protected=read_json(out/'protected-files.json')
    changed=[name for name,wanted in protected.items() if sha(ROOT/name)!=wanted]
    assert not changed,changed
    from scripts.cycle14_evidence import load_manifest,verify
    c14=verify(ROOT,load_manifest(ROOT/'publication/cycle14/manifest.json'))
    assert c14['passed']
    # The previous cycle's sealed local evidence is verified, never rewritten.
    from scripts.cycle15_evidence import load,verify as verify15
    manifest=load(ROOT/'publication/cycle15/manifest.json')
    c15=verify15(manifest['original_local_root'],manifest)
    assert c15['passed']
    return record(out/'historical-final.json',dict(passed=True,tracked_files=len(protected),changed=changed,
        cycle14=c14,cycle15=c15,runtime_unchanged=True,operational_source=production_code_hash(),
        accepted_checkpoint_sha256=sha(ROOT/'artifacts/cycle12/model/C12-default.json')))


def reproduce(out,source):
    out=Path(out).resolve();source=Path(source).resolve();out.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'PLN_CHESS_ROOT':str(source),'PYTHONPATH':str(source/'src')+':'+str(source)}
    commands=[['-m','research.cycle16','minimal','--out',str(out/'minimal'),'--proof-mode','summary'],
        ['-m','research.cycle16','compare','--out',str(out/'compare'),'--proof-mode','summary'],
        ['-c','from training.cycle16_paths import evidence,fit; import sys; fit(evidence(),sys.argv[1])',str(out/'learning')]]
    receipts=[]
    for i,command in enumerate(commands):
        argv=[str(source/'.venv/bin/python'),*command];log=out/f'command-{i}.log'
        with log.open('w') as stream:
            proc=subprocess.run(argv,cwd=source,env=env,stdout=stream,stderr=subprocess.STDOUT)
        receipts.append(dict(argv=argv,returncode=proc.returncode,log=str(log),log_sha256=sha(log)))
        record(out/f'command-{i}.json',receipts[-1])
        if proc.returncode:raise RuntimeError(str(log))
    model=read_json(out/'learning/model.json');original=read_json(out.parent/'learning/learned/model.json')
    assert model['rules']==original['rules'] and model['structure_hash']==original['structure_hash']
    comparison=read_json(out/'compare/results.json')
    assert all(comparison['F']['stages'][s]['classification']=='supported-positive' for s in ('Clear','Attack','Exposure'))
    assert comparison['R']['stages']['Attack']['classification']=='unknown'
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True)
    return record(out/'verified.json',dict(passed=True,commands=receipts,
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
        exact_learned_parameters_and_ancestry=True,checkout_clean=True,
        scope='Fresh Git checkout using verified existing runtime/virtualenv and historical evidence; '
            'minimal native diagnostics, R/F CLI comparison and native refit; not a fresh dependency installation or second full corpus run'))


def pack(out):
    """Reuse the unchanged Cycle 15 content-addressed transport format."""
    from scripts import cycle15_evidence as transport
    out=Path(out).resolve();manifest_path=ROOT/'publication/cycle16/manifest.json'
    excluded={'packs','restored-evidence','source','reproduction-source'}
    original_groups=transport.GROUPS
    try:
        transport.GROUPS=tuple(sorted(p.name for p in out.iterdir() if p.is_dir() and p.name not in excluded))
        transport.build(out,out/'packs',manifest_path)
    finally:transport.GROUPS=original_groups
    manifest=transport.load(manifest_path)
    # The transport schema stays identical. Asset names identify this study.
    mapping={a['name']:a['name'].replace('cycle15-','cycle16-',1) for a in manifest['assets']}
    for asset in manifest['assets']:
        old=asset['name'];new=mapping[old];(out/'packs'/old).rename(out/'packs'/new);asset['name']=new
    for row in manifest['files']:row['asset']=mapping[row['asset']]
    manifest['study']='Cycle 16';manifest['transport_format']='Unchanged Cycle 15 local evidence format'
    write_json(manifest_path,manifest)
    manifest=transport.load(manifest_path)
    assert transport.verify(out,manifest)['passed']
    restored=transport.restore(out/'restored-evidence',out/'packs',manifest)
    receipt=dict(**restored,counts=manifest['counts'],manifest_sha256=sha(manifest_path),
        local_root=str(out),pack_root=str(out/'packs'),remote_write_performed=False)
    write_json(ROOT/'artifacts/cycle16/restoration.json',receipt)
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','historical','pack','reproduce'));p.add_argument('--path',required=True)
    p.add_argument('--source')
    a=p.parse_args()
    if a.command=='reproduce' and not a.source:p.error('--source is required')
    result=reproduce(a.path,a.source) if a.command=='reproduce' else globals()[a.command](Path(a.path))
    print(json.dumps(result,indent=2))
