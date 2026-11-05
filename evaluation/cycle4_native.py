"""Executable native composition decision gate, with negative controls."""
import hashlib,re
from pathlib import Path
from pln_chess.common import ROOT,write_json
from pln_chess.pln import Runtime
from evaluation.cycle3_native import audit as earlier

PROBES={
 'three-independent-chain':'(let* (($b (Truth_ModusPonens (stv 1.0 0.99) (stv 0.98 0.9))) ($c (Truth_ModusPonens $b (stv 0.97 0.9)))) (Truth_ModusPonens $c (stv 0.96 0.9)))',
 'chain-unknown-middle':'(let* (($b (Truth_ModusPonens (stv 1.0 0.99) (stv 0.98 0.9))) ($c (Truth_ModusPonens $b (stv 0.5 0.0)))) (Truth_ModusPonens $c (stv 0.96 0.9)))',
 'chain-negative-middle':'(let* (($b (Truth_ModusPonens (stv 1.0 0.99) (stv 0.98 0.9))) ($c (Truth_ModusPonens $b (stv 0.01 0.9)))) (Truth_ModusPonens $c (stv 0.96 0.9)))',
 'deduction-measured':'(Truth_Deduction (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.5 0.8) (stv 0.9 0.8) (stv 0.8 0.8))',
 'deduction-inconsistent':'(Truth_Deduction (stv 0.9 0.8) (stv 0.1 0.8) (stv 0.5 0.8) (stv 0.9 0.8) (stv 0.8 0.8))',
 'deduction-zero-confidence-marginal':'(Truth_Deduction (stv 0.2 0.0) (stv 0.4 0.0) (stv 0.5 0.0) (stv 0.9 0.8) (stv 0.8 0.8))',
 'revision-independent-conflict':'(Truth_Revision (stv 1.0 0.8) (stv 0.0 0.8))',
 'revision-repeated-premise':'(Truth_Revision (stv 1.0 0.8) (stv 1.0 0.8))',
 'inversion-boundary-zero':'(Truth_inversion (stv 0.0 0.8) (stv 0.9 0.8))',
 'mp-certain':'(Truth_ModusPonens (stv 1.0 1.0) (stv 1.0 1.0))',
 'negation-unknown':'(Truth_Negation (stv 0.5 0.0))',
}
RAW={
 'conjunction-introduction':'(collapse (|- (A (stv 0.9 0.8)) (B (stv 0.9 0.8))))',
 'conjunction-elimination':'(collapse (|- ((And A B) (stv 0.9 0.8))))',
 'typed-variable-binding':'(collapse (|- ((Seen Rook Orthogonal) (stv 1.0 0.99)) ((Implication (Seen $p Orthogonal) (Pattern $p)) (stv 0.9 0.8))))',
 'wrong-variable-binding':'(collapse (|- ((Seen Bishop Diagonal) (stv 1.0 0.99)) ((Implication (Seen $p Orthogonal) (Pattern $p)) (stv 0.9 0.8))))',
 'inheritance-predicate':'(collapse (|- ((Evaluation (Predicate Blocked) (List (Concept Slider))) (stv 0.9 0.8)) ((Inheritance (Concept Rook) (Concept Slider)) (stv 0.95 0.8))))',
 'deduction-wrapper':'(collapse (|- ((Implication A B) (stv 0.9 0.8)) ((Implication B C) (stv 0.8 0.8))))',
 'correlated-gate':'(if (StampDisjoint (e1 e2) (e2 e3)) (Truth_Revision (stv 1.0 0.8) (stv 1.0 0.8)) (empty))',
 'independent-gate':'(if (StampDisjoint (e1) (e2)) (Truth_Revision (stv 1.0 0.8) (stv 1.0 0.8)) (empty))',
}

def audit(output=None):
    previous=earlier();runtime=Runtime(timeout=120);values=runtime.batch(list(PROBES.items()))
    body='(= (STV A) (stv 0.2 0.8))\n(= (STV B) (stv 0.4 0.8))\n(= (STV C) (stv 0.5 0.8))\n'
    body+='\n'.join(f'!(println! (C4PROBE {k} {v}))' for k,v in RAW.items())
    raw=runtime.execute(body)
    assert '(C4PROBE conjunction-introduction ())' in raw
    assert '(C4PROBE conjunction-elimination ())' in raw
    assert values['chain-unknown-middle'].confidence==0
    assert values['deduction-measured']==values['deduction-zero-confidence-marginal']
    assert values['deduction-inconsistent'].confidence==0
    assert values['revision-independent-conflict'].strength==.5
    records=[];source=runtime.library.read_text().splitlines()
    for name,expr in PROBES.items():
        symbols=sorted(set(re.findall(r'\((Truth_\w+)',expr)))
        records.append({'id':name,'expression':expr,'output':values[name].json(),'symbols':symbols,
                        'source_lines':{s:next(i for i,line in enumerate(source,1) if '(= ('+s+' ' in line) for s in symbols},
                        'evidence_overlap':'Truth functions do not inspect stamps; caller must enforce lineage.'})
    records += [{'id':k,'expression':v,'output':next((line for line in raw.splitlines() if line.startswith('(C4PROBE '+k+' ')),None)} for k,v in RAW.items()]
    result={'runtime':runtime.manifest,'previous_probes':previous,'records':records,'raw':raw,
            'decision':{'production':'Three separately learned conditional families can contribute along a unary native MP chain. This does not combine independent movement/path/safety conditions by conjunction.',
                        'deduction':'Native deduction verified with measured probability-consistent marginals; zero marginal confidence does not suppress output. Experimental only, not chosen for production.',
                        'inheritance':'Native predicate transfer verified; type membership must be supplied or learned. No automatically discovered slider taxonomy claimed.',
                        'conjunction':'Absent in pinned runtime. Optional upstream port was not shipped: no independently validated drop-in semantics.',
                        'nesting':'Nested implications are curried conditional applications, not a verified conjunction theorem.',
                        'negative_controls':'Unknown/missing chain edge kills confidence; shared-stamp gate rejects repeated support; wrong shape produces no binding.'}}
    if output:
        output=Path(output);write_json(output,result)
        output.with_suffix('.metta').write_text('!(import! &self "'+str(runtime.library)+'")\n'+body+'\n'+'\n'.join(f'!(println! ({k} {v}))' for k,v in PROBES.items())+'\n')
    return result
