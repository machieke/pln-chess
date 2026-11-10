"""Compact review index extracted from the complete native worked proofs."""
import argparse
from pathlib import Path
from pln_chess.common import digest, write_json
from evaluation.cycle3 import read_gzip


def run(out):
    out=Path(out)
    examples=read_gzip(out/'fields/worked-examples.json.xz')
    records=[]
    for example in examples:
        case,comparison=example['case'],example['comparison']
        family=case['selected_field']
        source=case['selected_piece_square']
        before=comparison['before']
        entity=next(p['id'] for p in before['pieces'] if source==chr(97+p['square'][0])+str(p['square'][1]+1))
        original={r['relation_id']:r for r in before['relations'] if r['family']==family and r['source_entity']==entity}
        after={r['relation_id']:r for r in comparison['after']['relations'] if r['family']==family and r['source_entity']==entity}
        identifiers=sorted(original.keys()&after.keys())
        # Deterministic review selection after evaluation, never training or an
        # accuracy sample. Prefer an epistemic transition, then positive support.
        identifiers.sort(key=lambda key:(original[key]['classification']==after[key]['classification'],
            after[key]['classification']!='supported',original[key]['target_square']))
        selected=identifiers[0] if identifiers else None
        a,b=original.get(selected),after.get(selected)
        for relation in (a,b):
            if relation is not None:assert digest(relation['proof_trace'])==relation['proof_id']
        records.append(dict(example=case['id'],description=case['description'],family=family,
            candidate=case['move'],candidate_classification=comparison['candidate']['classification'],
            before_fen=before['fen'],after_fen=comparison['after']['fen'],
            source_entity=entity,before=a,after=b,change_truth_value=None,
            full_artifact='fields/worked-examples.json.xz',
            selection='Post-evaluation deterministic review example; no statistical inference or model selection.'))
    write_json(out/'fields/worked-proof-index.json',dict(schema=11,examples=records,
        proof_scope='Native unary local conditionals; host-observed context and diagnostic before/after comparison.'))
    print('Extracted',len(records),'review examples',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
