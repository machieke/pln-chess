"""Native counterexamples to transitive preference, using disclosed assumptions.

These are controlled categorical packets, not chess examples or empirical
supervision. They never enter the registered corpus or its measured accuracy.
"""
import argparse
import copy
from pathlib import Path
from pln_chess.common import digest,write_json,read_json
from pln_chess.pln import Runtime
from pln_chess.cycle12.ontology import CONCEPTS
from pln_chess.cycle13.ontology import GRAMMAR,FIELDS,seal,project,reverse_packet
from pln_chess.cycle13.inference import infer_preferences
from training.cycle13_learning import train
from evaluation.cycle7_io import pack


def controlled_packet(first,second):
    def counts(value):
        return dict(supported=value,contradicted=0,unknown=0,incomplete=0,queried=value)
    def profile(values):
        return dict(fields={name:counts(value) for name,value in zip(FIELDS,values)},
            concepts={name:counts(0) for name in CONCEPTS},concept_scope='bounded-role-candidates')
    return seal(dict(schema=GRAMMAR,profiles=dict(before=profile((0,0,0,0)),A=profile(first),B=profile(second)),
        horizon=1,complete=True,gaps=['Controlled supplied count assumptions; no native endpoint field proofs.'],
        source='controlled-nontransitivity-assumptions',candidate_descriptors=dict(A={},B={}),
        provenance=dict(empirical_chess_example=False,scope='Abstract preference consistency counterexample only.')))


def run(out):
    out=Path(out);assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    runtime=Runtime(timeout=600)
    profiles=dict(A=(2,1,0,0),B=(1,0,2,0),C=(0,2,1,0))
    edges=(('A','B'),('B','C'),('C','A'))
    records=[]
    for a,b in edges:
        identifier='controlled-edge-'+a+b
        records.append(dict(id=identifier,fen='4k3/8/8/8/8/8/8/R3K3 w - - 0 1',moves=['a1a2','a1b1'],
            packet=controlled_packet(profiles[a],profiles[b]),label='A',split='train',source_game='controlled-assumptions',
            source='Explicit cyclic preference assumptions for a native consistency probe; not reference-engine evidence.',
            dependence_group=identifier,transformation_lineage=[identifier],temporal_context=dict(horizon=1),
            model_versions={},reference_evidence_id='controlled-label:'+identifier))
    assert len({project(r['packet'])['rule_id'] for r in records})==3
    model=train(records,runtime,out/'consistency/learning',dataset_hash=digest(records),baseline_root=out,
        variant='C13-controlled-nontransitive-conditionals')
    result=infer_preferences([r['packet'] for r in records],model,runtime=runtime)
    assert all(r['status']=='A-preferred' for r in result['comparisons'])
    reverse=infer_preferences([reverse_packet(r['packet']) for r in records],model,runtime=runtime)
    assert all(r['status']=='B-preferred' for r in reverse['comparisons'])
    reduced=copy.deepcopy(model)
    removed=project(records[-1]['packet'])['rule_id']
    reduced.hypotheses.pop(removed)
    missing=infer_preferences([reverse_packet(records[-1]['packet'])],reduced,runtime=runtime)['comparisons'][0]
    assert missing['status']=='indeterminate' and not missing['conditional_proof_complete']
    for row in result['comparisons']+reverse['comparisons']:
        values=runtime.batch([(n['id'],n['native_expression']) for n in row['proof_trace']])
        assert all(values[n['id']].json()==n['truth_value'] for n in row['proof_trace'])
        assert not row['joint_proof_complete']
    pack(out/'consistency/counterexample.json.xz',dict(profiles=profiles,assumptions=records,
        cycle_edges=[dict(preferred=a,other=b,result=r) for (a,b),r in zip(edges,result['comparisons'])],
        reversed=reverse,removed_rule=removed,unsupported_transitive_query=missing))
    write_json(out/'consistency/summary.json',dict(passed=True,native_cycle_edges=3,reversal_checks=3,
        native_proofs_replayed=6,unobserved_transitive_query='indeterminate',transitive_operator_introduced=False,
        empirical_chess_examples=0,registered_data_contaminated=False,model_version=model.version,
        scope='Native conditionals preserve explicitly supplied cyclic assumptions. This demonstrates absence of an unjustified transitive inference; it is not a measured inconsistency rate for real chess.'))
    print('NATIVE CONSISTENCY CONTROLS PASSED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13')
    run(parser.parse_args().out)
