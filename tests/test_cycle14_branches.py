"""Controlled native branch disagreement is preserved without aggregation."""
from pln_chess.common import digest, write_json
from pln_chess.cycle13.api import PreferenceOptions, PreferenceSession
from pln_chess.cycle14.model import PreferenceModel
from pln_chess.cycle14.ontology import project
from pln_chess.cycle14.proofs import ProofStore
from pln_chess.cycle14.temporal import analyze_continuations
from evaluation.cycle14_profile import models
from training.cycle14_learning import train


def test_opposed_native_branch_answers_remain_separate(runtime, tmp_path):
    # These deliberately assigned labels exercise interface semantics. They
    # are not engine supervision, independent research games or chess advice.
    fen='r6k/8/8/8/8/8/8/R3K3 w - - 0 1'
    branches={'A':[['a1a2','a8a2'],['a1a2','a8b8']],
        'B':[['a1b1','a8a4']]}
    loaded=models(runtime)
    loaded['preference_model']=PreferenceModel(runtime.version,abstraction='role-change-v1')
    session=PreferenceSession(runtime)
    options=PreferenceOptions(max_candidates=2,timeout_seconds=900)
    with ProofStore() as store:
        initial=analyze_continuations(fen,branches,**loaded,store=store,
            runtime=runtime,session=session,options=options,horizons=(2,),_prepared=True)
        packets=initial['role_packets']
        assert len(packets)==2
        keys=[project(p,'role-change-v1')['rule_id'] for p in packets]
        assert keys[0]!=keys[1]
        rows=[]
        for branch,(packet,label) in enumerate(zip(packets,('A','B'))):
            for repeat in range(3):
                name=f'unit-branch-{branch}-{repeat}'
                rows.append(dict(id=name,fen=fen,moves=['a1a2','a1b1'],packet=packet,
                    label=label,split='train',source='controlled-unit-assigned-labels',
                    source_game=name,dependence_group=name,transformation_lineage=[name],
                    temporal_context={'horizon':2},model_versions={},
                    reference_evidence_id=name,label_generation='unit-g1'))
        write_json(tmp_path/'baseline/research/verified.json',dict(passed=True,scope='unit fixture'))
        loaded['preference_model']=train(rows,runtime,tmp_path/'fit',dataset_hash=digest(rows),
            abstraction='role-change-v1',baseline_root=tmp_path,variant='unit-branch-disagreement')
        result=analyze_continuations(fen,branches,**loaded,store=store,runtime=runtime,
            session=session,options=options,horizons=(2,))
        assert [r['preference']['status'] for r in result['comparisons']]==['A-preferred','B-preferred']
        assert all(r['preference']['conditional_proof_complete'] for r in result['comparisons'])
        assert all(r['preference']['proof_id'] for r in result['comparisons'])
        assert result['global_robust_preference'] is None
        assert result['automatic_move_selection'] is False
        assert result['joint_proof_complete'] is False
        assert result['exhaustive_response_coverage'] is False
        archive=store.archive(result['proof_root'])
    with ProofStore() as restored:
        root=restored.import_archive(archive)
        assert restored.legacy_digest(root)==archive['canonical_legacy_sha256']
