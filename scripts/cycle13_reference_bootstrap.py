"""Fetch/build the pinned offline teacher without changing production dependencies."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

from pln_chess.common import ROOT, read_json, write_json

URL='https://github.com/official-stockfish/Stockfish/releases/download/sf_18/stockfish-ubuntu-x86-64-avx2.tar'
ARCHIVE_SHA='536c0c2c0cf06450df0bfb5e876ef0d3119950703a8f143627f990c7b5417964'


def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def run(directory,out):
    directory,out=Path(directory).resolve(),Path(out).resolve()
    directory.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    archive=directory/'stockfish-18.tar'
    if not archive.exists():
        with urllib.request.urlopen(URL,timeout=120) as response,archive.open('wb') as stream:
            shutil.copyfileobj(response,stream)
    assert sha(archive)==ARCHIVE_SHA,'Pinned reference archive hash mismatch'
    source=directory/'stockfish/src'
    if not source.exists():
        with tarfile.open(archive) as bundle:bundle.extractall(directory,filter='data')
    registered=read_json(ROOT/'artifacts/cycle13/sources/stockfish-source.json')
    assert all(sha(directory/'stockfish'/p)==value for p,value in registered['source_hashes'].items())
    # Use the same unchanged source build on every host; no upgraded system
    # library or globally installed chess engine is required.
    binary=source/'stockfish'
    if not binary.exists():
        with (out/'build.txt').open('w') as log:
            subprocess.run(['make','-j4','build','ARCH=x86-64-avx2'],cwd=source,stdout=log,stderr=subprocess.STDOUT,check=True)
    for name,value in registered['networks'].items():assert sha(source/name)==value,name
    identity=subprocess.check_output([str(binary)],input='uci\nquit\n',text=True)
    assert 'id name Stockfish 18' in identity
    write_json(out/'verified.json',dict(passed=True,binary=str(binary),binary_sha256=sha(binary),
        registered_binary_sha256=registered['binary_sha256'],byte_identical_binary=sha(binary)==registered['binary_sha256'],
        source_and_networks_identical=True,archive_sha256=ARCHIVE_SHA,uci_identity=identity,
        scope='Offline labeling dependency only. Compiler-dependent executable differences require an explicit labeling identity; native PLN dependencies are unchanged.'))
    return binary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--directory',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();print(run(args.directory,args.out))
