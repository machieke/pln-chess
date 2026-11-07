# Bounded native feasibility result

**Native positive composition: not demonstrated.** Three encodings were tested; the search stopped at the preregistered budget. No extra native operator or probabilistic formula was added.

A is learned relative knight geometry; B is independently supervised opponent destination eligibility. Their examples and source groups are disjoint, and no training example contains the held-out combined knight capture. The witness is `f6h5` in `2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1`. These synthetic source groups do not establish empirical IID sampling; known shared ancestry is explicitly controlled.

## nested-implication

Existing MP can eliminate a supplied curried conditional; test whether independent facts alone provide it.

No rule introduces or learns A -> (B -> Eligible) from the two independent marginal curricula.

A+B:
```metta
(collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))
```
```text
(C7PROBE nested-implication-A+B ((Eligible (stv 0.9379612919547984 0.45556260336343357))))
```

delete-A:
```metta
(collapse (let ($p $tv) (|- (A (stv 0.5 0.0)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))
```
```text
(C7PROBE nested-implication-delete-A ((Eligible (stv 0.4819805194805195 0.0))))
```

delete-B:
```metta
(collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.5 0.0)) ($p $tv))))
```
```text
(C7PROBE nested-implication-delete-B ((Eligible (stv 0.48198051948051945 0.0))))
```

## product-antecedent

An explicit product/And antecedent might be constructed by native matching; test independent inputs and host-built sensor control.

No pinned introduction rule constructs the joint antecedent.

A+B:
```metta
(collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))
```
```text
(C7PROBE product-antecedent-A+B ())
```

delete-A:
```metta
(collapse (let ($p $tv) (|- (A (stv 0.5 0.0)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))
```
```text
(C7PROBE product-antecedent-delete-A ())
```

delete-B:
```metta
(collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.5 0.0))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))
```
```text
(C7PROBE product-antecedent-delete-B ())
```

host-joint-control:
```metta
(collapse (|- ((Product A B) (stv 0.9935064935064936 0.8020833333333335)) ((Implication (Product A B) Eligible) (stv 0.95 0.8))))
```
```text
(C7PROBE product-antecedent-host-joint-control ((Eligible (stv 0.9439610389610389 0.6056250000000001))))
```

## conditional-inheritance

Typed predicate inheritance is source-present; test its exact runtime signature and whether independently learned geometry/occupancy shares a type.

No native rule identifies KnightStep with OpponentDestination or intersects these types.

A+B:
```metta
(collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335))))
```
```text
(C7PROBE conditional-inheritance-A+B ())
```

delete-A:
```metta
(collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.5 0.0)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335))))
```
```text
(C7PROBE conditional-inheritance-delete-A ())
```

delete-B:
```metta
(collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.5 0.0))))
```
```text
(C7PROBE conditional-inheritance-delete-B ())
```

aligned-type-control:
```metta
(collapse (|- ((Evaluation (Predicate Eligible) (List (Concept KnightStep))) (stv 0.9935064935064936 0.8020833333333335)) ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335))))
```
```text
(C7PROBE conditional-inheritance-aligned-type-control ())
```

The native scheduler confirms the supplied-rule dependency:

```text
(C7PROBE scheduler-independent-only ())
```
```text
(C7PROBE scheduler-supplied-nested ((stv 0.9379612919547984 0.45556260336343357) (learn-A learn-B supplied-rule)))
```
```text
(C7PROBE scheduler-deleted-A ())
```
```text
(C7PROBE scheduler-deleted-B ())
```
```text
(C7PROBE scheduler-shared-stamp ())
```

The nested positive output includes `learn-A`, `learn-B`, and `supplied-rule`; deleting either premise or sharing their stamp removes the queried conclusion. This proves the mechanism depends on the supplied rule, not that the rule was learned from independent marginals. A host-built product is a sensor control, never native conjunction introduction.

The inventory distinguishes native truth functions, executable relational deduction/equivalence, and source-present predicate-transfer wrappers whose exact probes return empty. It records signatures, native STV domains, zero/one-confidence behavior, source locations and raw outputs. `BestConfidenceCandidate` selects one alternative and never combines premises. Revision at confidence one or with both confidences zero returns empty in the tested runtime.

All A-only/B-only, deletion, negative, contradiction, reversal and duplicate-correlation controls are in `artifacts/cycle7/native/laboratory.json`. Individual standalone MeTTa witnesses and the complete interpreter transcripts are adjacent. Rook obstruction and pawn capture composition were not attempted because the primary gate failed. This is a falsifiable result for the pinned operators and tested signatures, not an impossibility theorem about every PLN encoding.

The inventory production-integration flag is a static symbol-reference check across production source, not evidence that the default C7 scheduler invoked that operator. Actual default proof DAGs use modus ponens, negation and confidence choice; the training ledgers use revision. Optional legacy induction support remains separate from the frozen default.

See [extension-proposal.md](extension-proposal.md) for the missing introduction/dependence capability and [decision-memo.md](decision-memo.md) for the user decision. No proposed operator is enabled.
