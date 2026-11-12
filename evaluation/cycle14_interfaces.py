"""Actual CLI process restarts, opt-in trained models and archive reconstruction."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from pln_chess.common import ROOT,read_json,digest
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle14.proofs import ProofStore
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out,verification_root=None):
    out=Path(out).resolve();target=Path(verification_root).resolve() if verification_root else out/'interfaces'
    target.mkdir(parents=True,exist_ok=True);store=target/'proofs.sqlite';records=[]
    env=dict(os.environ,C14_OUT=str(out),C14_PROOF_STORE=str(store),TMPDIR='/dev/shm')
    def command(name,args):
        argv=[sys.executable,'-m','pln_chess',*map(str,args)];began=time.time()
        process=subprocess.run(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        (target/(name+'.stderr.txt')).write_text(process.stderr)
        assert process.returncode==0,process.stderr
        result=json.loads(process.stdout);atomic_json(target/(name+'.json'),result)
        records.append(dict(name=name,argv=argv,returncode=process.returncode,elapsed_seconds=time.time()-began,
            output_sha256=sha(target/(name+'.json')),stderr_sha256=sha(target/(name+'.stderr.txt'))));return result
    fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1'
    payload=dict(fen=fen,move_a='a1a2',move_b='a1b1',preference_model='primary-immediate',max_candidates=2)
    atomic_json(target/'compare-input.json',payload)
    summary=command('compare',['compact-compare','--input',target/'compare-input.json','--store',store])
    assert summary['inspector_model']['requested']=='primary-immediate' and not summary['execution']['truncated']
    warm=command('restart-compare',['compact-compare','--input',target/'compare-input.json','--store',store])
    assert warm['proof_handle']==summary['proof_handle'] and warm['delivery']['request_cache_hit']
    page=command('graph-page',['proof-view','--handle',summary['proof_handle'],'--store',store,'--view','proof_graph','--offset','16','--limit','16'])
    assert page['proof_graph']['offset']==16 and len(page['proof_graph']['nodes'])==16
    archive=command('full-archive',['proof-view','--handle',summary['proof_handle'],'--store',store,'--view','full_archive'])
    expanded=command('reconstruct',['proof-expand','--input',target/'full-archive.json','--output',target/'reconstructed.json'])
    assert sha(target/'reconstructed.json')==archive['archive']['canonical_legacy_sha256']==expanded['canonical_legacy_sha256']
    # The reconstructed file is intentionally retained as a complete CLI audit.
    payload=dict(fen=fen,branches={'A':[['a1a2','e8e7','a2a3']],'B':[['a1b1','e8f7','b1b2']]},
        horizons=[2,3],preference_model='primary-temporal',max_candidates=2,selection_provenance='Controlled supplied CLI lines')
    atomic_json(target/'temporal-input.json',payload)
    temporal=command('continuations',['compact-continuations','--input',target/'temporal-input.json','--store',store])
    assert len(temporal['comparisons'])==2 and temporal['global_robust_preference'] is None
    assert temporal['inspector_model']['requested']=='primary-temporal'
    # Empty-evidence inspection is an explicit counterfactual, separate from
    # choosing a move or mutating the accepted legal model.
    payload=dict(fen=fen,move_a='a1a2',move_b='a1b1',preference_model='empty',max_candidates=2)
    atomic_json(target/'removal-input.json',payload)
    empty=command('preference-evidence-removed',['compact-compare','--input',target/'removal-input.json','--store',store])
    assert not empty['preference']['conditional_proof_complete'] and empty['preference']['status']=='indeterminate'
    assert empty['model_versions']['legal']==summary['model_versions']['legal']
    atomic_json(target/'verified.json',dict(passed=True,production_code_hash=production_code_hash(),commands=records,
        actual_cli_processes=len(records),durable_restart_reuse=True,exact_archive_reconstruction=True,
        paginated_graph=True,trained_immediate_model=summary['model_versions']['preference'],
        trained_temporal_model=temporal['model_versions']['preference'],legal_model=summary['model_versions']['legal'],
        empty_evidence_counterfactual=True,experimental_preference_is_opt_in=True,automatic_move_selection=False,
        browser_evidence='ui/browser-downloads/http-framed/integrity.json',
        scope='Actual separate CLI processes plus durable proof store. Browser verification is separately recorded using ProofShot.'))
    print('C14 CLI AND DURABLE ARCHIVE VERIFIED',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='artifacts/cycle14');p.add_argument('--verification-root');a=p.parse_args();run(a.out,a.verification_root)
