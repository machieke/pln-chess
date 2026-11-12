"""Exact native proof parity across the new compact boundary."""
from dataclasses import replace

from evaluation.cycle14_profile import models
from pln_chess.common import canonical,digest
from pln_chess.cycle12.temporal import semantic_replay
from pln_chess.cycle13.api import compare_moves as legacy,PreferenceOptions
from pln_chess.cycle14.api import compare_moves,retrieve
from pln_chess.cycle14.proofs import ProofStore


def test_native_summary_expands_to_legacy_and_survives_restart(runtime,tmp_path):
    loaded=models(runtime);position='4k3/8/8/8/8/8/8/R3K3 w - - 0 1'
    options=PreferenceOptions(max_candidates=4)
    expected=legacy(position,'a1a2','a1b1',**loaded,runtime=runtime,options=options)
    path=tmp_path/'proofs.sqlite'
    with ProofStore(path) as store:
        summary=compare_moves(position,'a1a2','a1b1',**loaded,runtime=runtime,options=options,store=store)
        expanded=store.expand(summary['proof_root'])
        assert semantic_replay(expanded)==semantic_replay(expected)
        assert store.legacy_digest(summary['proof_root'],omit_keys=('execution','incremental'))==digest(semantic_replay(expected))
        assert len(canonical(summary))<len(canonical(expected))*.1
        calls=runtime.invocations
        warm=compare_moves(position,'a1a2','a1b1',**loaded,runtime=runtime,options=options,store=store)
        assert warm['delivery']['request_cache_hit'] and runtime.invocations==calls
        assert warm['proof_handle']==summary['proof_handle']
        # A different native work budget must never reuse a complete answer.
        limited=compare_moves(position,'a1a2','a1b1',**loaded,runtime=runtime,
            options=replace(options,max_native_invocations=0),store=store)
        assert not limited['delivery']['request_cache_hit']
        assert limited['proof_handle']!=summary['proof_handle'] and limited['execution']['truncated']
    with ProofStore(path) as restarted:
        result=retrieve(restarted,summary['proof_handle'],view='proof_graph',limit=8)
        assert len(result['proof_graph']['nodes'])==8
        archive=retrieve(restarted,summary['proof_handle'],view='full_archive')['archive']
    with ProofStore() as fresh:
        root=fresh.import_archive(archive)
        assert fresh.legacy_digest(root)==digest(expanded)


def test_continuation_graph_has_exact_legacy_proofs_and_explicit_branch_gaps(runtime):
    from pln_chess.cycle13.temporal import analyze_continuations as original
    from pln_chess.cycle14.temporal import analyze_continuations
    loaded=models(runtime,True);position='4k3/8/8/8/8/8/8/R3K3 w - - 0 1'
    branches={'A':[['a1a2','e8e7']],'B':[['a1b1','e8f7']]}
    options=PreferenceOptions(max_candidates=2,timeout_seconds=900)
    expected=original(position,branches,**loaded,runtime=runtime,options=options,horizons=(2,3))
    with ProofStore() as store:
        summary=analyze_continuations(position,branches,**loaded,runtime=runtime,options=options,
            horizons=(2,3),store=store)
        assert store.legacy_digest(summary['proof_root'],omit_keys=('execution','incremental'))==digest(semantic_replay(expected))
        assert summary['branch_coverage']['A'][0]['missing_horizons']==[3]
        assert not summary['exhaustive_response_coverage'] and summary['global_robust_preference'] is None
        assert summary['comparisons'][1]['preference']['status']=='incomplete'
