"""Check that response verification ignores clocks but rejects changed evidence."""
from pathlib import Path
import tempfile

from pln_chess.common import read_json, write_json
from pln_chess.cycle14.proofs import ProofStore
from evaluation.cycle7_io import pack
from scripts.cycle14_reproduce import compare_responses
from scripts.cycle9_baseline import sha


def fixture(root, elapsed, truth):
    with ProofStore() as store:
        object_=store.put(dict(proof_trace=[dict(native_expression='controlled-unit-expression',
            premises=['distinct-unit-evidence'],truth_value=truth)],execution={'elapsed_seconds':elapsed}))
        archive=store.archive(object_)
    pack(root/'responses/unit/archive.json.xz',archive)
    write_json(root/'responses/unit/result.json',dict(identity={'scope':'disclosed unit fixture'},
        summary=dict(proof_root=archive['root'],proof_handle='unit-request',execution={'elapsed_seconds':elapsed}),
        archive_sha256=sha(root/'responses/unit/archive.json.xz'),comparisons=['unchanged-unit-comparison']))
    pack(root/'responses/diagnostics.json.xz',[])
    write_json(root/'responses/summary.json',dict(passed=True,scope='unit fixture'))
    write_json(root/'datasets/response-plans.json',dict(records=[{'id':'unit'}]))


def run():
    with tempfile.TemporaryDirectory(prefix='c14-response-verifier-') as directory:
        first,second=Path(directory)/'first',Path(directory)/'second'
        fixture(first,1.0,{'strength':.3,'confidence':.5})
        fixture(second,9.0,{'strength':.3,'confidence':.5})
        assert len(compare_responses(first,second))==3
        fixture(second,9.0,{'strength':.4,'confidence':.5})
        try:compare_responses(first,second)
        except AssertionError:changed_evidence_rejected=True
        else:raise AssertionError('Changed evidence was hidden by telemetry normalization')
        fixture(second,9.0,{'strength':.3,'confidence':.5})
        record=read_json(second/'responses/unit/result.json');record['summary']['proof_root']='0'*64
        write_json(second/'responses/unit/result.json',record)
        try:compare_responses(first,second)
        except AssertionError:broken_binding_rejected=True
        else:raise AssertionError('Unbound archive root was ignored')
    write_json('artifacts/cycle14/verification/response-comparison-controls.json',dict(passed=True,
        changed_clocks_and_bound_archive_hashes_allowed=True,changed_native_evidence_rejected=changed_evidence_rejected,
        incorrect_archive_binding_rejected=broken_binding_rejected,verifier_sha256=sha('scripts/cycle14_reproduce.py'),
        control_driver_sha256=sha(__file__),scope='Synthetic host-verifier controls; no claim of new native inference or empirical preference success.'))
    print('C14 RESPONSE REPRODUCTION VERIFIER CONTROLS PASSED')


if __name__=='__main__':run()
