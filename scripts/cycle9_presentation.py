"""Requalify the sole CSS wrapping correction against executed native evidence.

This is intentionally not a general source-change waiver: the entire production
tree must equal the executed study byte for byte except one exact HTML attribute.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.cycle6.inference import production_code_hash


def run(out,study):
    out=Path(out).resolve();study=Path(study).resolve();target=out/'presentation';original=target/'native-study'
    original.mkdir(parents=True,exist_ok=True)
    for name in ('verification.json','acceptance.json','pytest.txt','smoke/verified.json'):
        saved=original/name
        if not saved.exists():saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/name,saved)
    base=read_json(original/'verification.json');base_head=base['source_head']
    assert base['passed'] and all(base['checks'].values())
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=study,text=True).strip()==base_head
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base_head,'--','src'],cwd=ROOT,text=True).splitlines()
    old={p:subprocess.check_output(['git','show',base_head+':'+p],cwd=ROOT) for p in paths if p.endswith('.py')}
    current={str(p.relative_to(ROOT)):p.read_bytes() for p in (ROOT/'src').rglob('*.py')}
    assert set(old)==set(current)
    changed=sorted(p for p in old if old[p]!=current[p]);assert changed==['src/pln_chess/cli/web9.py'],changed
    before=b'<p id="c9-status" role="status">';after=b'<p id="c9-status" role="status" style="overflow-wrap:anywhere">'
    assert old[changed[0]].count(before)==1 and current[changed[0]]==old[changed[0]].replace(before,after)
    hashes=lambda files:{p:hashlib.sha256(raw).hexdigest() for p,raw in sorted(files.items())}
    assert digest(hashes(old))==base['production_code_hash']
    assert digest(hashes(current))==production_code_hash()
    write_json(target/'source-equivalence.json',dict(passed=True,base_head=base_head,
        current_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        old_production_code_hash=base['production_code_hash'],new_production_code_hash=production_code_hash(),
        changed_files=changed,exact_old_fragment=before.decode(),exact_new_fragment=after.decode(),
        original_file_hashes=hashes(old),current_file_hashes=hashes(current),
        scope='All native inference, arithmetic, model, API, acceptance and JavaScript bytes are identical. The only production delta is a CSS overflow-wrap attribute on the report-status paragraph.'))
    commands=[]
    def command(name,cwd,args):
        env=dict(os.environ,PLN_CHESS_ROOT=str(cwd),PYTHONPATH=f'{cwd}/src:{cwd}',C9_OUT=str(out),TMPDIR='/dev/shm');env.pop('C8_OUT',None)
        argv=[str(cwd/'.venv/bin/python'),*args];started=time.time();log=target/(name+'.txt')
        with log.open('w') as stream:r=subprocess.run(argv,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(name=name,argv=argv,cwd=str(cwd),source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cwd,text=True).strip(),
            returncode=r.returncode,elapsed_seconds=time.time()-started,log=str(log.relative_to(out))))
        write_json(target/'commands.json',commands);assert r.returncode==0,(name,log)
    # Re-run the original fail-closed verifier over every original proof/cache/data
    # receipt, using the unmodified executed production tree and its fresh runtime.
    command('native-evidence-reverification',study,['-m','scripts.cycle9_verify','--out',str(out)])
    assert read_json(out/'verification.json')==base
    command('pytest',ROOT,['-m','pytest','-q'])
    test_log=(target/'pytest.txt').read_text();match=re.search(r'(\d+) passed',test_log)
    assert match and int(match[1])==base['test_count'] and not re.search(r'\d+ failed|ERRORS|FAILURES',test_log)
    receipt=read_json(out/'acceptance.json');receipt.update(production_code_hash=production_code_hash(),
        native_study_production_code_hash=base['production_code_hash'],presentation_equivalence='presentation/source-equivalence.json')
    write_json(out/'acceptance.json',receipt)
    verification={**base,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'production_code_hash':production_code_hash(),'native_study_source_head':base_head,
        'native_study_production_code_hash':base['production_code_hash'],'test_log':'presentation/pytest.txt',
        'presentation_only_change':True,'presentation_equivalence':'presentation/source-equivalence.json'}
    write_json(out/'verification.json',verification)
    command('application-smoke',ROOT,['-m','scripts.cycle9_smoke','--out',str(out)])
    write_json(target/'verified.json',dict(passed=True,source_head=verification['source_head'],
        native_study_source_head=base_head,production_code_hash=production_code_hash(),tests=int(match[1]),
        native_checks_reverified=True,all_inference_bytes_identical=True,
        scope='Native results and timings reused only after exact one-attribute CSS equivalence and original gate reverification. Full tests and actual API/CLI smoke rerun on the corrected source. Browser verification is recorded separately.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--study-checkout',required=True)
    a=p.parse_args();run(a.out,a.study_checkout)
