"""Validate a response handle before excluding execution-derived identities."""
from types import SimpleNamespace

from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.pln import Runtime
from pln_chess.cycle13.api import PreferenceOptions
from pln_chess.cycle14.api import identity_for
from pln_chess.cycle14.proofs import SCHEMA


def validate_response_handle(summary, plan, *, diagnostic=False, runtime=None):
    runtime=runtime or Runtime(timeout=900)
    branches=plan['branches']
    assert summary['runtime_version']==runtime.version
    assert summary['proof_store_schema']==SCHEMA and summary['view']=='summary'
    assert summary['fen']==Position.from_fen(plan['fen']).fen()
    models={name+'_model':SimpleNamespace(version=version)
        for name,version in summary['model_versions'].items()}
    assert set(models)=={'legal_model','field_model','concept_model','fork_model','preference_model'}
    identity=identity_for(plan['fen'],[branches['A'][0][0],branches['B'][0][0]],models,
        PreferenceOptions(timeout_seconds=900),runtime,plan.get('history'),
        plan['id'] if diagnostic else 'cycle14-registered-response/'+plan['id'],
        branches=branches,horizons=[2,3],
        selection_provenance='Controlled diagnostic' if diagnostic else plan['response_selection'])
    # These are the fields added by production present(), after publish().
    stored={key:value for key,value in summary.items()
        if key not in ('proof_handle','proof_root','proof_store_schema','view','delivery')}
    expected='proof-request:'+digest([SCHEMA,identity,summary['proof_root'],stored])
    assert summary['proof_handle']==expected,'Response handle does not bind its registered request, root and stored summary'
    return dict(handle=expected,request_identity_sha256=digest(identity),
        stored_summary_sha256=digest(stored),proof_root=summary['proof_root'])
