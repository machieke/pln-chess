"""Strict opt-in inputs, history identity and isolated archive HTTP transfer."""
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import replace
import pytest

from pln_chess.common import ROOT,canonical
from pln_chess.domain import Position,parse_square
from pln_chess.cycle13.api import PreferenceOptions
from pln_chess.cycle14.api import identity_for
from pln_chess.cycle14.proofs import ProofStore
from pln_chess.cycle14.inspector import inspect
from evaluation.cycle14_profile import models


def test_request_identity_binds_all_cache_dependencies(runtime):
    loaded={k.removesuffix('_model'):v for k,v in models(runtime).items()};position=Position.from_fen('4k3/8/8/8/8/8/8/R3K3 w - - 0 1')
    options=PreferenceOptions();moves=['a1a2','a1b1']
    def identity(p=position,m=moves,models_=loaded,o=options,h=None,**extra):return identity_for(p,m,models_,o,runtime,h,'unit',**extra)
    original=identity();history={'initial_fen':position.fen(),'moves':[]}
    changed=[identity(h=history),identity(m=list(reversed(moves))),identity(o=replace(options,max_candidates=1)),
        identity(p=replace(position,unknown_squares=frozenset([parse_square('d4')]))),
        identity(branches={'A':[['a1a2','e8e7']],'B':[['a1b1','e8f7']]}),identity(horizon=3)]
    modified=dict(loaded);modified['preference']=type(loaded['preference'])(runtime.version)
    changed.append(identity(models_=modified))
    assert all(v!=original for v in changed)
    assert len({canonical(v) for v in changed})==len(changed)


@pytest.mark.parametrize('field',['label','reference_label','score','pv','source_game','proof_id'])
def test_inspector_rejects_reference_and_identity_feature_injection(field):
    with pytest.raises(ValueError,match='reference labels and scores'):
        inspect({'fen':'4k3/8/8/8/8/8/8/R3K3 w - - 0 1','move_a':'a1a2','move_b':'a1b1',field:'forbidden'})


def test_downloaded_archive_http_has_exact_bytes_and_rejects_corruption(tmp_path):
    with ProofStore() as store:
        original={'proofs':[{'native_expression':'(Truth_Revision (STV 1.0 0.5) (STV 0.0 0.5))','values':[1.0,-0.0,True,'α']}]*40}
        archive=store.archive(store.put(original))
    with socket.socket() as bound:bound.bind(('127.0.0.1',0));port=bound.getsockname()[1]
    env=dict(os.environ,C14_PROOF_STORE=str(tmp_path/'proofs.sqlite'))
    with (tmp_path/'server.log').open('w') as log:
        child=subprocess.Popen([sys.executable,'-m','pln_chess','serve','--port',str(port)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        try:
            url=f'http://127.0.0.1:{port}'
            for _ in range(100):
                try:
                    with urllib.request.urlopen(url+'/favicon.ico',timeout=1):break
                except (OSError,urllib.error.URLError):time.sleep(.05)
            def request(value):return urllib.request.urlopen(urllib.request.Request(url+'/cycle14-expand',data=canonical(value).encode(),headers={'Content-Type':'application/json'}),timeout=15)
            with request({'archive':archive}) as response:
                raw=response.read();assert int(response.headers['Content-Length'])==len(raw)
                assert raw==canonical(original).encode()
                assert hashlib.sha256(raw).hexdigest()==response.headers['X-Proof-Legacy-SHA256']
            archive['objects'].pop(next(iter(archive['objects'])))
            with pytest.raises(urllib.error.HTTPError) as error:request({'archive':archive})
            assert error.value.code==400
        finally:
            child.terminate();child.wait(timeout=10)


def test_research_reference_disclosure_cannot_enter_inference(tmp_path,monkeypatch):
    from pln_chess.common import write_json
    from pln_chess.cli.research14 import reference
    monkeypatch.setenv('C14_OUT',str(tmp_path))
    write_json(tmp_path/'datasets/source-pairs.json',{'records':[dict(id='registered-unit',split='train',fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',moves=['a1a2','a1b1'],history=None,source={'cohort':'unit'})]})
    write_json(tmp_path/'labels/immediate-g1/records/registered-unit.json',dict(label='unknown',reason='budget-disagreement',generation='unit',evidence_id='unit-reference',original_actor='White',horizon=1))
    disclosed=reference('registered-unit');assert disclosed['label']=='unknown' and disclosed['inference_input'] is False
    with pytest.raises(ValueError):reference('../outside')
    with pytest.raises(ValueError):inspect(disclosed)
