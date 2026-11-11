# Native conditional preference learning

The fixed corpus contains 340 pairs from 340 independent source games and ancestry groups: 222 training, 62 calibration and 56 test. It combines 148 published-game positions and 192 external tactical positions, including 141 quiet pairs and 16 promotion pairs. Candidate alternatives and A/B order were fixed by hashes before labels or PLN predictions.

The partition audit excludes shared source games and exact registered geometry/transform classes. It does not prove the absence of every semantically related tactical motif. Shared coarse learned consequence patterns are the intended transfer test; they must not be confused with an independent proof of semantic family separation.

The reference is pinned [Stockfish 18](https://github.com/official-stockfish/Stockfish/releases/tag/sf_18), restricted to two explicit roots and 20,000/80,000 nodes with one thread. The [Lichess puzzle source](https://database.lichess.org/#puzzles) is a frozen CC0 prefix. Scores and reference PVs remain offline supervision. A direction requires agreement at both budgets and the registered margin; score bounds, intermediate margins and disagreements remain unknown.

| Label | Reason | Pairs |
| --- | --- | --- |
| unknown | Unresolved score bound. | 218 |
| A | Same directional margin at both registered node budgets. | 47 |
| unknown | Budgets disagree, margin is intermediate, or mate distinction remains unresolved. | 12 |
| B | Same directional margin at both registered node budgets. | 62 |
| no-demonstrated-preference | Both comparisons fall within the registered ambiguity margin. | 1 |


Only registered training observations update the separate model. Unknown labels, incomplete packets and directional labels whose abstraction collapses A/B remain in the ledger but do not update a direction. Independent opposing labels remain visible; inconsistent dependent groups are withheld.

The primary model has 44 relative conditionals. Its native training report is:

```json
{
  "dataset_hash": "53e15d1c267b3bc8c014dfb47212360612873bb8de7f19e8d98d5b0cd3ae81d7",
  "dependence_handling": true,
  "excluded_observations": {
    "direction-collapses-under-relative-abstraction": 1,
    "unresolved-reference-label": 152
  },
  "executed_native_operators": 17,
  "heldout_labels_used": false,
  "hypotheses": 44,
  "label_counts": {
    "A": 22,
    "B": 47,
    "no-demonstrated-preference": 1,
    "unknown": 152
  },
  "native_cache_hits": 190,
  "native_joint_strategic_theorems": 0,
  "native_revision_nodes": 207,
  "neutral_prior": {
    "confidence": 0.05,
    "strength": 0.5
  },
  "observation_confidence": 0.5,
  "scope": "Three independent conditional channels, not normalized probabilities or a move-selection utility.",
  "training_examples": 222,
  "unique_evidence": 222
}
```

The host assembles a categorical packet from independently inferred field and concept records. Native revision learns three separate conditional channels, and native modus ponens applies those channels to the supplied packet. This is a native conditional derivation, not a native conjunction of uncertain fields, a complete strategic theorem, a proof of legality or an optimal move claim. No scalar strategic utility or automatic move selection is implemented.

Answered accuracy excludes abstentions and unknown teacher labels. Coverage and abstention-inclusive accuracy use all directionally labeled pairs. Ambiguous labels have separate diagnostics. Undefined ratios remain undefined. A thousand bootstrap replicates resample connected ancestry components; these intervals do not include teacher-label or source-selection uncertainty.

| Observed relational consequence | Pairs with that observation |
| --- | --- |
| attack_counterevidence_to_support | 262 |
| king_exposure_classification_changes | 45 |
| mobility_classification_changes | 340 |
| newly_queried_supported_attack | 0 |
| supported_defense_domain_removed | 0 |
| supported_defense_persists | 331 |
| supported_defense_to_counterevidence | 315 |


| Concept family | Pairs with structural candidates | Pairs with a supported conditional |
| --- | --- | --- |
| DiscoveredAttack | 337 | 15 |
| DiscoveredDefense | 338 | 7 |
| Fork | 323 | 175 |
| MultipleAttackers | 306 | 7 |
| OverloadedDefender | 303 | 0 |
| Pin | 296 | 246 |
| ThreatRemoval | 337 | 1 |
| TrappedPiece | 340 | 1 |


| Panel | Pairs | Resolved A/B | Answered A/B | Correct | Answered accuracy | Coverage | Abstention-inclusive accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 62 | 25 | 12 | 7 | 0.583 | 0.480 | 0.280 |
| test | 56 | 15 | 6 | 5 | 0.833 | 0.400 | 0.333 |
| test-ambiguous | 0 | 0 | 0 | 0 | undefined | undefined | undefined |
| test-external-tactical | 36 | 13 | 5 | 4 | 0.800 | 0.385 | 0.308 |
| test-independent-games | 20 | 2 | 1 | 1 | 1.000 | 0.500 | 0.500 |
| test-promotion | 3 | 1 | 1 | 1 | 1.000 | 1.000 | 1.000 |
| test-quiet | 25 | 4 | 2 | 2 | 1.000 | 0.500 | 0.500 |
| test-unknown-reference | 41 | 0 | 0 | 0 | undefined | undefined | undefined |
| train | 222 | 69 | 45 | 45 | 1.000 | 0.652 | 0.652 |


| Panel | Precision A | Precision B | Recall A | Recall B | Contradictions | Conditional proofs | Joint proofs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | 0.667 | 0.333 | 0.400 | 0.100 | 0 | 39 | 0 |
| test | 1.000 | 0.500 | 0.400 | 0.200 | 0 | 33 | 0 |
| test-ambiguous | undefined | undefined | undefined | undefined | 0 | 0 | 0 |
| test-external-tactical | 1.000 | 0.500 | 0.375 | 0.200 | 0 | 19 | 0 |
| test-independent-games | 1.000 | undefined | 0.500 | undefined | 0 | 14 | 0 |
| test-promotion | undefined | 1.000 | undefined | 1.000 | 0 | 1 | 0 |
| test-quiet | 1.000 | undefined | 0.667 | 0.000 | 0 | 16 | 0 |
| test-unknown-reference | undefined | undefined | undefined | undefined | 0 | 24 | 0 |
| train | 1.000 | 1.000 | 0.591 | 0.681 | 0 | 172 | 0 |


| Test metric | 95% lower | 95% upper | Valid bootstrap replicates |
| --- | --- | --- | --- |
| accuracy_including_abstention | 0.111 | 0.583 | 1000 |
| contradiction_rate | 0.000 | 0.000 | 1000 |
| directional_coverage | 0.143 | 0.647 | 1000 |
| pairwise_accuracy | 0.500 | 1.000 | 998 |


Evidence: [preferences/summary.json](../../artifacts/cycle13/preferences/summary.json), [learning/relational/ledger.jsonl](../../artifacts/cycle13/learning/relational/ledger.jsonl), [learning/relational/native-training.json.xz](../../artifacts/cycle13/learning/relational/native-training.json.xz), [model/C13-preference-relational.json](../../artifacts/cycle13/model/C13-preference-relational.json), [datasets/integrity.json](../../artifacts/cycle13/datasets/integrity.json), [ontology/manifest.json](../../artifacts/cycle13/ontology/manifest.json).
