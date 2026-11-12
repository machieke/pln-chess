"""Diagnostic profile of exact compact archive validation, with no native work."""
import argparse
import cProfile
import io
from pathlib import Path
import pstats
import time
from pln_chess.common import ROOT,write_json
from pln_chess.cycle14.proofs import ProofStore
from evaluation.cycle3 import read_gzip
from scripts.cycle9_baseline import sha


def run(archive_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    assert not (out/'profile.json').exists(),'Preserve earlier profile generations'
    archive=read_gzip(archive_path);profile=cProfile.Profile();started=time.perf_counter()
    with ProofStore() as store:
        profile.enable();root=store.import_archive(archive);expanded_hash=store.legacy_digest(root);profile.disable()
        assert expanded_hash==archive['canonical_legacy_sha256'];census=store.census()
    stream=io.StringIO();pstats.Stats(profile,stream=stream).sort_stats('cumulative').print_stats(35)
    (out/'functions.txt').write_text(stream.getvalue())
    write_json(out/'profile.json',dict(passed=True,elapsed_seconds=time.perf_counter()-started,
        artifact_sha256=sha(archive_path),proof_store_sha256=sha(ROOT/'src/pln_chess/cycle14/proofs.py'),
        census=census,native_interpreter_launches=0,
        scope='Instrumented storage diagnostic under concurrent study jobs; not a headline latency benchmark.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();run(args.archive,args.out)
