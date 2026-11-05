# Native capability audit

PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`, SHA-256 `cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`. The vendored source is unchanged. Exact signatures and complete native formula definitions are stored with source line locations in `artifacts/cycle6/native-probes/audit.json`; executable input is `audit.metta`. Recorded stdout is retained for every wrapper probe and raw STVs for every direct truth-function probe.

| Symbol | Source lines | Runtime status |
|---|---:|---|
| `Truth_c2w` | 71–72 | source-inspected |
| `Truth_w2c` | 75–76 | source-inspected |
| `Truth_or` | 79–80 | source-inspected |
| `Truth_Deduction` | 84–99 | directly-executed |
| `Truth_Induction` | 102–110 | directly-executed |
| `Truth_Abduction` | 112–121 | directly-executed |
| `Truth_ModusPonens` | 124–126 | directly-executed |
| `Truth_SymmetricModusPonens` | 129–133 | directly-executed |
| `Truth_Revision` | 136–143 | directly-executed |
| `Truth_Negation` | 147–148 | directly-executed |
| `Truth_inversion` | 150–153 | directly-executed |
| `Truth_equivalenceToImplication` | 156–162 | directly-executed |
| `Truth_transitiveSimilarity` | 174–181 | directly-executed |
| `Truth_evaluationImplication` | 197–204 | directly-executed |
| `|-` | 211–213 | wrapper-executed; inspect individual probe |
| `|-` | 216–218 | wrapper-executed; inspect individual probe |
| `|-` | 226–229 | wrapper-executed; inspect individual probe |
| `|-` | 236–242 | wrapper-executed; inspect individual probe |
| `|-` | 246–251 | wrapper-executed; inspect individual probe |
| `|-` | 254–259 | wrapper-executed; inspect individual probe |
| `|-` | 263–267 | wrapper-executed; inspect individual probe |
| `|-` | 270–274 | wrapper-executed; inspect individual probe |
| `|-` | 277–281 | wrapper-executed; inspect individual probe |
| `|-` | 284–284 | wrapper-executed; inspect individual probe |
| `|-` | 287–288 | wrapper-executed; inspect individual probe |
| `|-` | 291–292 | wrapper-executed; inspect individual probe |
| `|-` | 295–297 | wrapper-executed; inspect individual probe |
| `|-` | 299–301 | wrapper-executed; inspect individual probe |
| `|-` | 304–308 | wrapper-executed; inspect individual probe |
| `|-` | 311–315 | wrapper-executed; inspect individual probe |
| `|-` | 319–323 | wrapper-executed; inspect individual probe |
| `StampDisjoint` | 335–342 | source-inspected |
| `BestConfidenceCandidate` | 412–413 | directly-executed |

Modus ponens, deduction, induction, abduction, revision, negation, inversion, similarity/equivalence, symmetric MP, evaluation implication and evidence choice have executable probes. The library's symbolic inheritance/implication rules require their exact term shapes and supplied marginal STVs; source presence is distinguished from successful wrapper execution. Direct truth functions do not inspect evidence stamps. `StampDisjoint` must gate overlapping provenance; `BestConfidenceCandidate` is a selector, not dependence-aware contradictory-evidence fusion. Deduction's marginal confidence does not gate output, and induction assumes the explicitly recorded population marginals.

The local upstream checkout history is captured in the audit. No claim is made that those local refs are the latest remote head. No upstream repository was changed or pushed.

**Independent-premise positive composition: not achieved.** Three separately identified observations revise A and B through the native revision operator, with disjoint groups. The bare facts do not derive a novel C. Supplied nesting and relation chains can execute, but already contain relations to C; they are mechanism controls, not evidence of learned unseen conjunction. No new operator was activated.

**independent**

```metta
(collapse (|- (A (stv 0.9913793103448276 0.7532467532467534)) (B (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE independent ())
```

**missing-A**

```metta
(collapse (|- (B (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE missing-A ())
```

**missing-B**

```metta
(collapse (|- (A (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE missing-B ())
```

**swapped**

```metta
(collapse (|- (B (stv 0.9913793103448276 0.7532467532467534)) (A (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE swapped ())
```

**contradictory-B**

```metta
(collapse (|- (A (stv 0.9913793103448276 0.7532467532467534)) ((Not B) (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE contradictory-B ())
```

**renamed**

```metta
(collapse (|- (X (stv 0.9913793103448276 0.7532467532467534)) (Y (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE renamed ())
```

**correlated**

```metta
(collapse (if (StampDisjoint (source shared) (other shared)) (|- (A (stv 0.9913793103448276 0.7532467532467534)) (B (stv 0.9913793103448276 0.7532467532467534))) (empty)))
```

```text
(C6PROBE correlated ())
```

**inheritance-chain**

```metta
(collapse (|- ((Inheritance A B) (stv 0.9913793103448276 0.7532467532467534)) ((Inheritance B C) (stv 0.9913793103448276 0.7532467532467534))))
```

```text
(C6PROBE inheritance-chain (((Inheritance A C) (stv 0.9828824811732065 0.5576404115365157))))
```

**nested-full**

```metta
(collapse (let ($rule $tv) (|- (A (stv 0.9913793103448276 0.7532467532467534)) ((Implication A (Implication B C)) (stv 0.95 0.8))) (|- (B (stv 0.9913793103448276 0.7532467532467534)) ($rule $tv))))
```

```text
(C6PROBE nested-full ((C (stv 0.9340346313912009 0.3992186164149332))))
```

**nested-missing-A**

```metta
(collapse (let ($rule $tv) (|- (A (stv 0.5 0.0)) ((Implication A (Implication B C)) (stv 0.95 0.8))) (|- (B (stv 0.9913793103448276 0.7532467532467534)) ($rule $tv))))
```

```text
(C6PROBE nested-missing-A ((C (stv 0.48099137931034486 0.0))))
```

**nested-missing-B**

```metta
(collapse (let ($rule $tv) (|- (A (stv 0.9913793103448276 0.7532467532467534)) ((Implication A (Implication B C)) (stv 0.95 0.8))) (|- (B (stv 0.5 0.0)) ($rule $tv))))
```

```text
(C6PROBE nested-missing-B ((C (stv 0.4809913793103448 0.0))))
```

This is a limitation of the audited executable rule set and tested representations. It is not a universal impossibility theorem about every PLN implementation. A future extension would require separate authorization, source and semantic review, and the same independent-premise counterfactual tests.

The optional local-history addendum inspects conjunction-related Maxima experiments separately from executable MeTTa. The pinned `Consistency_ImplicationImplicantConjunction` helper was executed and returned Boolean `true`; it supplies no STV and introduces no conjunction inference rule. See `artifacts/cycle6/native-source-addendum.json` for exact expressions, stdout, local commit and source hashes.
