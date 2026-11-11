# Learned fork-role generalization

All three Cycle 12 test abstentions are resolved correctly: the pawn fork is supported, and the removed-target and friendly-target controls are contradicted. The test panel improves from 303 correct and three abstentions to 306 correct out of 306. All previously correct classifications are preserved. The same abstraction resolves three analogous king-role abstentions in calibration, yielding 64/64 correct there.

The missing rules were tied to attacker kind and component movement geometry. Cycle 13 learns a separate abstraction over two target roles, target occupancy/allegiance and the classifications of independently inferred attack components. It does not encode an attacker piece kind or a square. Twenty-one original Cycle 12 training examples produce three conditionals through 42 native revision nodes. No calibration, test or external tactical label enters this fit.

The original concept result and native proof remain available as `starting_conditional`. The generic fork conditional is evaluated independently, and only fills an original unknown classification. All 370 starting held-out native proofs remain canonically identical. This fallback policy preserves established answers; independent evaluation of the generic model avoids mistaking that policy for evidence of transfer.

On 48 independent generic-fork and counterfactual evaluations, the generic model gives 20 true positives, 24 true negatives, four abstentions and no wrong classified answers. Across the complete external concept panel, all 312 color, reflection, identity, target-removal, friendly-target and unknown-target controls pass. Transformed cases inherit their source ancestry and are not counted as independent games.

These are learned conditional conclusions on supplied role observations. The separately inferred attacks do not form a verified native conjunction. There are zero complete joint fork or strategic theorems.

Evidence: [resolution cases](../../artifacts/cycle13/forks/resolution.json), [native training](../../artifacts/cycle13/forks/native-training.json.xz), [complete concept results](../../artifacts/cycle13/concepts/summary.json). The original model is unchanged; the experimental fork model is `1ec0a73a377c7efa68fb5ac033677192a6cb287970104028604d9b3a6115fca3`.
