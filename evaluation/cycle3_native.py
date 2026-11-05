"""Executed composition boundary; no newly invented truth functions."""
import re
from pln_chess.common import ROOT,write_json
from pln_chess.pln import Runtime
from evaluation.cycle2_native import audit as previous

PROBES={
 'independent-premises':'(collapse (|- (A (stv 0.9 0.8)) (B (stv 0.9 0.8))))',
 'joint-sensor-conditional':'(collapse (|- ((And A B) (stv 1.0 0.99)) ((Implication (And A B) C) (stv 0.9 0.8))))',
 'joint-sensor-elimination':'(collapse (|- ((And A B) (stv 0.9 0.8))))',
 'nested-implication':'(let ($b $btv) (|- (A (stv 1.0 0.99)) ((Implication A (Implication B C)) (stv 0.9 0.8))) (collapse (|- (B (stv 1.0 0.99)) ($b $btv))))',
 'grounded-binding':'(collapse (|- ((Seen Rook Orthogonal) (stv 1.0 0.99)) ((Implication (Seen Rook Orthogonal) (Pattern Rook)) (stv 0.9 0.8))))',
 'unbound-query':'(collapse (|- ((Seen Rook Orthogonal) (stv 1.0 0.99)) ((Implication (Seen $piece Orthogonal) (Pattern $piece)) (stv 0.9 0.8))))',
 'contradiction-not-revision':'(collapse (|- (A (stv 0.9 0.8)) ((Not A) (stv 0.9 0.8))))',
 'shared-stamp':'(StampDisjoint (source-a source-b) (source-b source-c))',
 'distinct-stamp':'(StampDisjoint (source-a) (source-b))',
 'zero-confidence-revision':'(collapse (Truth_Revision (stv 0.5 0.0) (stv 0.9 0.0)))',
 'invalid-confidence-one':'(collapse (Truth_Revision (stv 0.9 1.0) (stv 0.1 0.5)))',
 'multiple-counters':'(BestConfidenceCandidate (((stv 0.95 0.9) (local)) ((stv 0.02 0.8) (attack1)) ((stv 0.01 0.85) (attack2))))',
 'stronger-counter':'(BestConfidenceCandidate (((stv 0.95 0.8) (local)) ((stv 0.02 0.9) (attack))))',
 'low-confidence-mp':'(Truth_ModusPonens (stv 1.0 0.01) (stv 0.95 0.9))',
 'zero-strength-mp':'(Truth_ModusPonens (stv 0.0 0.9) (stv 1.0 0.9))',
}


def audit(output=None):
    prior=previous();runtime=Runtime(timeout=90)
    body='\n'.join(f'!(println! (C3PROBE {name} {expr}))' for name,expr in PROBES.items())
    raw=runtime.execute(body)
    records=[{'id':name,'expression':expr,'result':next((line for line in raw.splitlines() if line.startswith('(C3PROBE '+name+' ')),None)} for name,expr in PROBES.items()]
    assert '(C3PROBE independent-premises ())' in raw
    assert '(C3PROBE joint-sensor-elimination ())' in raw
    assert '(C3PROBE joint-sensor-conditional ((C (stv 0.9 0.7128000000000001))))' in raw
    source=runtime.library.read_text().splitlines()
    operators=[]
    for index,line in enumerate(source,1):
        if re.match(r'\(= \((Truth_|Stamp|BestConfidence|\|-)',line):
            operators.append({'line':index,'signature':line,'source':'vendor/pln/lib_pln.metta'})
    result={'runtime':runtime.manifest,'cycle2_probes':prior,'records':records,'raw':raw,'operators':operators,
            'decision':{'production':'Native conditional MP and unary exposure chains, revision, negation and confidence choice.',
                        'joint_sensor':'Explicit And atom can be an MP antecedent; its observation must be supplied. This does not construct And from A and B.',
                        'unsupported':'Conjunction introduction/elimination; no safe king conclusion from missing attack hypotheses.',
                        'stamps':'Truth_* functions do not enforce stamps. Host scheduler selects alternatives and never revises overlapping inference paths.',
                        'upstream':'Cycle 2 pinned opt-in branch probes retained in artifacts/cycle2/upstream-audit.json; no alternate adopted.'}}
    if output:
        write_json(output,result)
        from pathlib import Path
        Path(output).with_suffix('.metta').write_text('!(import! &self "'+str(runtime.library)+'")\n'+body+'\n')
    return result
