"""Only validated timing-derived identities may differ in research replay."""
from types import SimpleNamespace

import pytest

from pln_chess.common import read_json,write_json
from pln_chess.pln import Runtime
from pln_chess.cycle13.api import PreferenceOptions
from pln_chess.cycle14.api import identity_for,present
from pln_chess.cycle14.proofs import ProofStore
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha
from scripts.cycle14_reproduce import compare_responses


PLAN=dict(id='synthetic-verifier-control',fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
    branches=dict(A=[['a1a2']],B=[['a1b1']]),history=None,response_selection='Synthetic verifier fixture')


def fixture(directory,clock,*,strength=.8,history=None):
    runtime=Runtime(timeout=900)
    models={name:SimpleNamespace(version='fixture-'+name) for name in
        ('legal_model','field_model','concept_model','fork_model','preference_model')}
    identity=identity_for(PLAN['fen'],['a1a2','a1b1'],models,PreferenceOptions(timeout_seconds=900),
        runtime,history,'cycle14-registered-response/'+PLAN['id'],branches=PLAN['branches'],
        horizons=[2,3],selection_provenance=PLAN['response_selection'])
    target=directory/'responses'/PLAN['id']
    with ProofStore() as store:
        root=store.put(dict(execution=dict(elapsed_seconds=clock),
            native=dict(truth_value=dict(strength=strength,confidence=.4),evidence_ids=['same','same'])))
        stored=dict(fen=PLAN['fen'],runtime_version=runtime.version,
            model_versions={name.removesuffix('_model'):model.version for name,model in models.items()},
            execution=dict(elapsed_seconds=clock),fixture_scope='Synthetic host-verifier control; no native inference claim')
        handle=store.publish(root,stored,identity)
        summary=present(store,store.request(handle),'summary',elapsed=clock)
        pack(target/'archive.json.xz',store.archive(root))
    write_json(target/'result.json',dict(summary=summary,archive_sha256=sha(target/'archive.json.xz')))
    write_json(directory/'datasets/response-plans.json',dict(records=[PLAN]))
    pack(directory/'responses/diagnostics.json.xz',[])
    write_json(directory/'responses/summary.json',dict(passed=True,fixture=True))
    return target/'result.json'


def test_changed_clocks_roots_and_valid_handles_preserve_scientific_evidence(tmp_path):
    left,right=tmp_path/'left',tmp_path/'right';a=fixture(left,1);b=fixture(right,2)
    assert read_json(a)['summary']['proof_handle']!=read_json(b)['summary']['proof_handle']
    compared=compare_responses(left,right)
    assert all(row['exact'] for row in compared)
    assert len(compared[0]['validated_request_bindings'])==2


@pytest.mark.parametrize('mutation',['truth-value','handle','root','request-history'])
def test_changed_native_value_or_invalid_identity_is_rejected(tmp_path,mutation):
    left,right=tmp_path/'left',tmp_path/'right';fixture(left,1)
    path=fixture(right,2,strength=.7 if mutation=='truth-value' else .8,
        history={'initial_fen':PLAN['fen'],'moves':[]} if mutation=='request-history' else None)
    if mutation in ('handle','root'):
        row=read_json(path)
        row['summary']['proof_'+mutation]=('proof-request:' if mutation=='handle' else '')+'0'*64
        write_json(path,row)
    with pytest.raises(AssertionError):compare_responses(left,right)
