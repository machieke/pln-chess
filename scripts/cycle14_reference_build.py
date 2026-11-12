"""Fresh pinned offline-teacher build using one available verification worker."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import time

from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha
from scripts.cycle13_reference_bootstrap import ARCHIVE_SHA


def run(checkout,out):
    checkout,out=Path(checkout).resolve(),Path(out).resolve()
    directory=checkout/'.runtime/cycle13-reference'
    directory.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    archive=directory/'stockfish-18.tar'
    cache=ROOT/'.runtime/cycle13-reference/stockfish-18.tar'
    assert sha(cache)==ARCHIVE_SHA
    if archive.exists():assert sha(archive)==ARCHIVE_SHA
    else:shutil.copy2(cache,archive)
    source=directory/'stockfish/src'
    assert not (source/'stockfish').exists(),'Retain the existing build receipt; do not silently replace a built teacher'
    if not source.exists():
        with tarfile.open(archive) as bundle:bundle.extractall(directory,filter='data')
    registered=read_json(checkout/'artifacts/cycle13/sources/stockfish-source.json')
    assert all(sha(directory/'stockfish'/name)==value for name,value in registered['source_hashes'].items())
    argv=['make','-j1','build','ARCH=x86-64-avx2'];started=time.time()
    with (out/'one-worker-build.txt').open('w') as log:
        result=subprocess.run(['/usr/bin/time','-v',*argv],cwd=source,stdout=log,stderr=subprocess.STDOUT)
    receipt=dict(driver_sha256=sha(__file__),source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip(),
        archive_sha256=ARCHIVE_SHA,source_cache=str(cache),argv=argv,workers=1,
        returncode=result.returncode,started_unix=started,elapsed_seconds=time.time()-started,
        fresh_source_build=True,binary_sha256=sha(source/'stockfish') if (source/'stockfish').exists() else None,
        log_sha256=sha(out/'one-worker-build.txt'),
        scope='Fresh compiler execution from the pinned hash-verified release archive; local archive reuse avoids downloading identical source bytes. Only make parallelism differs from the four-worker bootstrap. Production inference never invokes this offline teacher.')
    receipt['byte_identical_binary']=receipt['binary_sha256']==registered['binary_sha256']
    write_json(out/'one-worker-build.json',receipt)
    assert result.returncode==0 and receipt['byte_identical_binary']


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--checkout',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();run(args.checkout,args.out)
