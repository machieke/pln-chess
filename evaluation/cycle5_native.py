"""Literal capability probes. Unsupported composition remains an explicit gap."""
import re
from pathlib import Path
from pln_chess.pln import Runtime
from pln_chess.common import write_json
from evaluation.cycle4_native import audit as previous_audit

PROBES = {
 'independent-geometry-destination':'(collapse (|- ((Geometry Knight Jump) (stv 0.95 0.9)) ((Destination Opponent) (stv 0.98 0.8))))',
 'compound-antecedent-supplied':'(collapse (|- ((And Geometry Destination) (stv 0.9 0.8)) ((Implication (And Geometry Destination) Local) (stv 0.95 0.8))))',
 'compound-antecedent-missing':'(collapse (|- (Geometry (stv 0.9 0.8)) ((Implication (And Geometry Destination) Local) (stv 0.95 0.8))))',
 'curried-supplied-rule':'(collapse (let ($b $tv) (|- (Geometry (stv 0.9 0.8)) ((Implication Geometry (Implication Destination Local)) (stv 0.95 0.8))) (|- (Destination (stv 0.98 0.8)) ($b $tv))))',
 'curry-from-joint':'(collapse (|- ((Implication (And Geometry Destination) Local) (stv 0.95 0.8))))',
 'uncurry-from-nested':'(collapse (|- ((Implication Geometry (Implication Destination Local)) (stv 0.95 0.8))))',
 'intensional-conjunction':'(collapse (|- ((IntensionalInheritance A B) (stv 0.9 0.8)) ((IntensionalInheritance A C) (stv 0.9 0.8))))',
 'context-combination':'(collapse (|- ((Context Board Geometry) (stv 0.9 0.8)) ((Context Board Destination) (stv 0.9 0.8))))',
 'scope-matched':'(collapse (|- ((Seen Knight Opponent) (stv 0.9 0.8)) ((Implication (Seen $p $d) (Typed $p $d)) (stv 0.95 0.8))))',
 'scope-repeated-variable-mismatch':'(collapse (|- ((Seen Knight Opponent) (stv 0.9 0.8)) ((Implication (Seen $p $p) Same) (stv 0.95 0.8))))',
 'shared-ancestor':'(collapse (if (StampDisjoint (geometry source1) (destination source1)) (Truth_Revision (stv 1.0 0.8) (stv 1.0 0.8)) (empty)))',
 'independent-stamps':'(if (StampDisjoint (geometry source1) (destination source2)) (Truth_Revision (stv 1.0 0.8) (stv 1.0 0.8)) (empty))'
}

def audit(output=None):
    previous=previous_audit();rt=Runtime(timeout=180)
    body='\n'.join(f'!(println! (C5PROBE {k} {v}))' for k,v in PROBES.items())
    raw=rt.execute(body);source=rt.library.read_text().splitlines()
    records=[]
    for key,expr in PROBES.items():
        line=next(x for x in raw.splitlines() if x.startswith('(C5PROBE '+key+' '))
        records.append({'id':key,'expression':expr,'output':line,'native_source':'vendor/pln/lib_pln.metta',
                        'input_truth_values':re.findall(r'\(stv [^()]+\)',expr),
                        'source_lines':[i for i,s in enumerate(source,1) if '(= (|-' in s or '(= (StampDisjoint' in s],
                        'premises':'Literal independently named facts; supplied compound/nested rules are explicit experimental assumptions.',
                        'status':'native-partial' if key in ('compound-antecedent-supplied','curried-supplied-rule') else 'probe-only'})
    for key in ('independent-geometry-destination','compound-antecedent-missing','context-combination','shared-ancestor'):
        assert f'(C5PROBE {key} ())' in raw,key
    result={'runtime':rt.manifest,'previous_audit':previous,'records':records,'raw':raw,
            'decision':'No demonstrated native independent-premise conjunction. Supplied compound antecedents and curried rules do not learn an unseen conjunction. Strict positive planner leaves global legality unknown.'}
    if output:
        write_json(output,result);Path(output).with_suffix('.metta').write_text('!(import! &self "'+str(rt.library)+'")\n'+body+'\n')
    return result
