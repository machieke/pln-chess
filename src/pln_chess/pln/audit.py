"""Executable capability audit; expected values are regression assertions."""
from pln_chess.pln.runtime import Runtime, TV, NativeError
from pln_chess.common import ROOT, write_json

CASES = {
    "modus_ponens": ("(let ($a $t) (|- (A (stv 0.8 0.9)) ((Implication A B) (stv 0.9 0.8))) $t)", (0.724, 0.5184)),
    "revision": ("(let ($a $t) (|- (A (stv 1.0 0.5)) (A (stv 0.0 0.5))) $t)", (0.5, 2/3)),
    "negation": ("(let ($a $t) (|- ((Not A) (stv 0.9 0.8))) $t)", (0.1, 0.8)),
    "deduction": ("(Truth_Deduction (stv 0.5 0.9) (stv 0.5 0.9) (stv 0.5 0.9) (stv 0.8 0.8) (stv 0.7 0.8))", (0.62, 0.3584)),
    "induction": ("(Truth_Induction (stv 0.5 0.9) (stv 0.25 0.9) (stv 0.5 0.9) (stv 0.8 0.8) (stv 0.6 0.8))", (0.52, 0.384/1.384)),
    "choice": ("(let ($tv $ev) (BestConfidenceCandidate (((stv 0.3 0.8) (e)) ((stv 0.9 0.2) (e)))) $tv)", (0.3, 0.8)),
    "weight_to_confidence": ("(stv 0.5 (Truth_w2c 3.0))", (0.5, 0.75)),
    "bad_deduction": ("(Truth_Deduction (stv 0.9 0.9) (stv 0.1 0.9) (stv 0.5 0.9) (stv 0.9 0.8) (stv 0.7 0.8))", (1, 0)),
}

def runtime_audit(output=None):
    runtime = Runtime()
    values = runtime.batch([(name, expr) for name, (expr, _) in CASES.items()])
    records = []
    for name, (expr, expected) in CASES.items():
        tv = values[name]
        passed = abs(tv.strength-expected[0]) < 1e-10 and abs(tv.confidence-expected[1]) < 1e-10
        records.append({"id":name,"invocation":expr,"result":tv.json(),"passed":passed})
    # Verify native pattern grounding and inheritance at the rule layer, not only formulas.
    source = '''
(= (STV A) (stv 0.5 0.9))
(= (STV B) (stv 0.5 0.9))
(= (STV C) (stv 0.5 0.9))
!(println! (GROUND (|- ((Feature p m) (stv 1.0 0.9)) ((Implication (Feature p m) (Legal p m)) (stv 0.8 0.7)))))
!(println! (INHERIT (|- ((Inheritance A B) (stv 0.8 0.8)) ((Inheritance B C) (stv 0.7 0.8)))))
!(println! (INDUCT (|- ((Inheritance C A) (stv 0.8 0.8)) ((Inheritance C B) (stv 0.6 0.8)))))
!(println! (OVERLAP (StampDisjoint (e1 e2) (e2 e3))))
!(println! (DISJOINT (StampDisjoint (e1) (e2))))
!(println! (MISSING-AND (collapse (|- (A (stv 0.8 0.9)) (B (stv 0.6 0.9))))))
!(println! (ZERO-CHOICE (BestConfidenceCandidate (((stv 0.5 0.0) (e))))))
!(println! (C1-REV (collapse (Truth_Revision (stv 1.0 1.0) (stv 0.0 0.5)))))
'''
    raw = runtime.execute(source)
    required = ['(GROUND ((Legal p m) (stv 0.8', '(INHERIT ((Inheritance A C)', '(INDUCT ((Inheritance A B)', '(OVERLAP False)', '(DISJOINT True)', '(MISSING-AND ())', '(C1-REV ())', '(ZERO-CHOICE ())']
    # PeTTa prints lowercase booleans in some versions; record actual output.
    passed = all(x.lower() in raw.lower() for x in required) and all(r['passed'] for r in records)
    report = {"passed":passed,"runtime":runtime.manifest,"tests":records,"rule_layer_stdout":raw,
              "blockers":["No conjunction-introduction rule in audited PLN core; nested MP is not conjunction.",
                          "Revision with confidence=1 yields no result; finite evidence required.",
                          "Native induction is verified but requires population marginals; no automatic chess rule discovery is claimed."],
              "elapsed_seconds":runtime.elapsed}
    if output:
        write_json(output, report)
    if not passed:
        raise NativeError(f"Native smoke regression failed: {report}")
    return report
