# Structural generalization and abstention

The frozen checkpoint is evaluated on 100 held-out complete games, 500 nonterminal positions, 128 controlled adversarial positions and 80 special-move positions. Complete candidate sets and in-board sets are reported separately. Registered operational training examples are empty; isolated dependence ablations retrain controls only. The dataset generator and replay tests verify that every reference legal move occurs in the bounded candidate grammar. [Dataset and leakage manifest](../../artifacts/cycle9/datasets/manifest.json).

| Piece (held-out games) | Candidates | Recall | False legal | False illegal | Unknown |
|---|---|---|---|---|---|
| Bishop | 12320 | 100.000% | 0 | 0 | 76 |
| King | 5000 | 99.952% | 0 | 0 | 170 |
| Knight | 3288 | 100.000% | 0 | 0 | 41 |
| Pawn | 6363 | 100.000% | 0 | 0 | 49 |
| Queen | 8792 | 100.000% | 0 | 0 | 74 |
| Rook | 14364 | 100.000% | 0 | 0 | 211 |

| Held-out unknown family | Candidates |
|---|---|
| friendly-destination | 432 |
| castling-history-transit | 170 |
| promotion | 19 |

The [full structural metrics](../../artifacts/cycle9/analysis/evaluation-summary.json) group movement geometry, ray length, intermediate/destination occupancy, capture type, king exposure, pins, double checks, check resolution, promotion choice, castling, en passant, missing history and unknown sensory observations. These are offline evaluation labels; no oracle is introduced into production inference. Empty/unobserved strata are not evidence of robustness.

Primary-cause screening distinguishes missing hypotheses, supporting observations, dependence conflicts, thresholds, missing history and native-composition/specific-abstraction limits. Some categories remain ambiguous without a controlled intervention and are named accordingly; the taxonomy is not presented as a proven causal diagnosis. All major observed failure categories have representative native traces in the [proof archive](../../artifacts/cycle9/analysis/failure-proofs.json.xz) and [navigable index](../../artifacts/cycle9/analysis/failure-index.json). Each record retains rule IDs, evidence, native TVs, row proof hashes and its original evaluation shard.

| Representative index | Mode | Failure family | Fixture / move | Classification |
|---|---|---|---|---|
| 0 | experimental | insufficient-evidence | c9-independent-games-0200 / e4e5 | unknown |
| 1 | experimental | geometry-abstraction-mismatch | c9-independent-games-0200 / c3a4 | unknown |
| 2 | experimental | castling-history-transit | c9-independent-games-0200 / g2e2 | unknown |
| 3 | experimental | friendly-destination | c9-independent-games-0202 / c4d2 | unknown |
| 4 | experimental | promotion | c9-independent-games-0203 / a3a1q | unknown |
| 5 | experimental | promotion | c9-independent-games-0207 / e2e1q | unknown |
| 6 | experimental | en-passant-history | c9-special-moves-0893 / g5f6 | unknown |
| 7 | experimental | castling-history-transit | c9-special-moves-0900 / e1g1 | unknown |
| 8 | operational | friendly-destination | c9-adversarial-0718 / b3a1 | unknown |
| 9 | operational | castling-history-transit | c9-adversarial-0785 / c2e2 | unknown |
| 10 | operational | en-passant-history | c9-adversarial-0797 / g5f6 | unknown |
| 11 | operational | promotion | c9-development-0040 / e3e1q | unknown |

The adversarial study evaluates 64 counterfactual pairs with shared provenance: relevant occupancy/attack edits test sensitivity; irrelevant blocker edits test invariance. Outcomes, including unsupported members and any errors, remain explicit in [paired results](../../artifacts/cycle9/analysis/adversarial-pairs.json.xz) and the [pair summary](../../artifacts/cycle9/analysis/verification.json). All 287 historical native negative/removal controls remain valid; promotion transformations are retained separately.

The development-only history experiment resolves 2/2 castling abstentions at unchanged raw TVs and thresholds. Missing events, suppressed temporal evidence and removed rights remove positive support. The native graph still does not prove universal king safety or historical legal play. No final held-out labels informed this intervention. [Full experiment](../../artifacts/cycle9/abstention/development-experiment.json.xz).

Dependence ablations show stable native beliefs under duplicates and explicitly shared ancestry, deterministic replay, stable checkpoint reconstruction, and removal of the selected learned hypothesis after retracting every source group. The conflict intervention deliberately flips an observation label, first assigning a separate source group and then the original group; it tests revision policy and is not an independently acquired chess counterexample. The ancestry intervention copies an observation and annotates its shared lineage; actual spatial transformations are exercised by the separate 32 historical promotion controls. An ambiguous same-group observation is excluded conservatively. Raw duplicate rows can change the audit ledger/model identity while leaving beliefs equal. Unannotated correlated sources remain a provenance risk. [Ablation values, exclusions and native revision expressions](../../artifacts/cycle9/dependence/summary.json).
