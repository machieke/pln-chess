# Cycle 8 evaluation and acceptance

Selected default: **C8-promotion-relative**, operational. New learning promoted: **True**. The clean study ran 81 registered evaluations after 38 exact C7 baseline replays. The same seeded candidate grammar, oracle labels and split membership apply within each comparison. All raw reports retain ordered native proofs.

| Split | C7 recall | Default recall | Promotion candidate recall | C7 exact sets | Default exact sets | Candidate exact sets | Default FL / FI / self-check | Candidate FL / FI / self-check |
|---|---|---|---|---|---|---|---|---|
| cycle3-independent-games | 95.238% | 100.000% | 100.000% | 0.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle4-independent-games | 95.369% | 99.750% | 99.750% | 41.667% | 91.667% | 91.667% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-combination-holdout | 98.387% | 100.000% | 100.000% | 78.571% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-independent-games | 95.318% | 99.777% | 99.777% | 31.250% | 93.750% | 93.750% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-structural-holdout | 96.774% | 96.774% | 96.774% | 66.667% | 66.667% | 66.667% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-validation | 95.539% | 99.628% | 99.628% | 37.500% | 87.500% | 87.500% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle6-adversarial | 97.778% | 99.111% | 99.111% | 75.000% | 90.000% | 90.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle6-independent-games | 96.799% | 100.000% | 100.000% | 37.500% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle6-validation | 95.392% | 100.000% | 100.000% | 28.571% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle7-independent-games | 96.049% | 99.649% | 99.649% | 37.500% | 87.500% | 87.500% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle8-adversarial | 84.960% | 92.084% | 92.084% | 33.333% | 88.889% | 88.889% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle8-combination-holdout | 92.676% | 100.000% | 100.000% | 50.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle8-independent-games | 97.122% | 100.000% | 100.000% | 43.750% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle8-validation | 89.968% | 100.000% | 100.000% | 45.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| frozen-adversarial | 99.119% | 100.000% | 100.000% | 91.667% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| frozen-heldout-transfer | 97.767% | 99.882% | 99.882% | 75.000% | 97.500% | 97.500% | 0 / 0 / 0 | 0 / 0 / 0 |

C7 columns are the independently replayed accepted checkpoint. The research candidate and conservative exact-only fallback were registered before any C8 training/evaluation outcomes. Both ran every established and new acceptance suite. A candidate requires zero observed false-legal, false-illegal, self-check and incomplete results; no lost prior supported decisions; no lower recall or exact-set accuracy; and all infrastructure/provenance gates. Destructive ablations are ineligible.

The [acceptance receipt](../../artifacts/cycle8/acceptance.json) lists every rejection reason and binds the default to model/source/runtime/registration hashes. [Paired changes](../../artifacts/cycle8/paired-summary.json) include 1,000 bootstrap draws, seed 808, clustered by game or constructed source group; color mirrors stay together. Historical standalone fixtures use fixture IDs. Small synthetic samples do not support population-wide guarantees.

The previous learned research model is also compared directly. Historical columns come from the immutable C7 replay, while C8 partitions run that unchanged checkpoint through the common evaluator.

| Split | C7 research recall | C8 candidate recall | C7 research exact sets | C8 candidate exact sets | C7 research FL / FI / self-check | C8 candidate FL / FI / self-check |
|---|---|---|---|---|---|---|
| cycle3-independent-games | 100.000% | 100.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle4-independent-games | 99.750% | 99.750% | 91.667% | 91.667% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-combination-holdout | 100.000% | 100.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-independent-games | 99.777% | 99.777% | 93.750% | 93.750% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-structural-holdout | 96.774% | 96.774% | 66.667% | 66.667% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle5-validation | 99.628% | 99.628% | 87.500% | 87.500% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle6-adversarial | 99.111% | 99.111% | 90.000% | 90.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle6-independent-games | 100.000% | 100.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle6-validation | 100.000% | 100.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle7-independent-games | 99.298% | 99.649% | 84.375% | 87.500% | 4 / 4 / 0 | 0 / 0 / 0 |
| cycle8-adversarial | 86.807% | 92.084% | 33.333% | 88.889% | 40 / 40 / 0 | 0 / 0 / 0 |
| cycle8-combination-holdout | 93.239% | 100.000% | 37.500% | 100.000% | 32 / 48 / 0 | 0 / 0 / 0 |
| cycle8-independent-games | 100.000% | 100.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| cycle8-validation | 92.233% | 100.000% | 55.000% | 100.000% | 24 / 48 / 0 | 0 / 0 / 0 |
| frozen-adversarial | 100.000% | 100.000% | 100.000% | 100.000% | 0 / 0 / 0 | 0 / 0 / 0 |
| frozen-heldout-transfer | 99.882% | 99.882% | 97.500% | 97.500% | 0 / 0 / 0 | 0 / 0 / 0 |

Full metrics below distinguish abstention from incomplete execution. Per-piece, per-family, promotion-specific, in-board-only, empty-terminal exact and proof-coverage results are in [comparison.json](../../artifacts/cycle8/comparison.json). Raw native confidence is not calibrated legality probability.

| Arm | Split | Precision | Recall | F1 | Abstention | FL / FI / self-check | Exact sets | Incomplete |
|---|---|---|---|---|---|---|---|---|
| C7-frozen | cycle8-adversarial | 100.000% | 84.960% | 91.869% | 15.564% | 0 / 0 / 0 | 33.333% | 0 |
| C7-frozen | cycle8-combination-holdout | 100.000% | 92.676% | 96.199% | 4.900% | 0 / 0 / 0 | 50.000% | 0 |
| C7-frozen | cycle8-independent-games | 100.000% | 97.122% | 98.540% | 2.368% | 0 / 0 / 0 | 43.750% | 0 |
| C7-frozen | cycle8-validation | 100.000% | 89.968% | 94.719% | 4.566% | 0 / 0 / 0 | 45.000% | 0 |
| C7-learned-8 | cycle8-adversarial | 94.269% | 86.807% | 90.385% | 11.360% | 40 / 40 / 0 | 33.333% | 0 |
| C7-learned-8 | cycle8-combination-holdout | 95.389% | 93.239% | 94.302% | 0.700% | 32 / 48 / 0 | 37.500% | 0 |
| C7-learned-8 | cycle8-independent-games | 100.000% | 100.000% | 100.000% | 1.150% | 0 / 0 / 0 | 100.000% | 0 |
| C7-learned-8 | cycle8-validation | 95.960% | 92.233% | 94.059% | 1.048% | 24 / 48 / 0 | 55.000% | 0 |
| C8-experimental | cycle6-independent-games | n/a | 0.000% | 0.000% | 16.300% | 0 / 0 / 0 | 0.000% | 0 |
| C8-experimental | cycle7-independent-games | n/a | 0.000% | 0.000% | 19.196% | 0 / 0 / 0 | 0.000% | 0 |
| C8-experimental | cycle8-adversarial | n/a | 0.000% | 0.000% | 44.365% | 0 / 0 / 0 | 0.000% | 0 |
| C8-experimental | cycle8-combination-holdout | n/a | 0.000% | 0.000% | 37.800% | 0 / 0 / 0 | 0.000% | 0 |
| C8-frozen | cycle3-independent-games | 100.000% | 95.238% | 97.561% | 2.298% | 0 / 0 / 0 | 0.000% | 0 |
| C8-frozen | cycle4-independent-games | 100.000% | 95.369% | 97.630% | 1.720% | 0 / 0 / 0 | 41.667% | 0 |
| C8-frozen | cycle5-combination-holdout | 100.000% | 98.387% | 99.187% | 1.163% | 0 / 0 / 0 | 78.571% | 0 |
| C8-frozen | cycle5-independent-games | 100.000% | 95.318% | 97.603% | 1.898% | 0 / 0 / 0 | 31.250% | 0 |
| C8-frozen | cycle5-structural-holdout | 100.000% | 96.774% | 98.361% | 3.977% | 0 / 0 / 0 | 66.667% | 0 |
| C8-frozen | cycle5-validation | 100.000% | 95.539% | 97.719% | 2.268% | 0 / 0 / 0 | 37.500% | 0 |
| C8-frozen | cycle6-adversarial | 100.000% | 97.778% | 98.876% | 2.097% | 0 / 0 / 0 | 75.000% | 0 |
| C8-frozen | cycle6-independent-games | 100.000% | 96.799% | 98.374% | 1.787% | 0 / 0 / 0 | 37.500% | 0 |
| C8-frozen | cycle6-validation | 100.000% | 95.392% | 97.642% | 2.654% | 0 / 0 / 0 | 28.571% | 0 |
| C8-frozen | cycle7-independent-games | 100.000% | 96.049% | 97.985% | 2.011% | 0 / 0 / 0 | 37.500% | 0 |
| C8-frozen | cycle8-adversarial | 100.000% | 84.960% | 91.869% | 15.564% | 0 / 0 / 0 | 33.333% | 0 |
| C8-frozen | cycle8-combination-holdout | 100.000% | 92.676% | 96.199% | 4.900% | 0 / 0 / 0 | 50.000% | 0 |
| C8-frozen | cycle8-independent-games | 100.000% | 97.122% | 98.540% | 2.368% | 0 / 0 / 0 | 43.750% | 0 |
| C8-frozen | cycle8-validation | 100.000% | 89.968% | 94.719% | 4.566% | 0 / 0 / 0 | 45.000% | 0 |
| C8-frozen | frozen-adversarial | 100.000% | 99.119% | 99.558% | 1.573% | 0 / 0 / 0 | 91.667% | 0 |
| C8-frozen | frozen-heldout-transfer | 100.000% | 97.767% | 98.871% | 1.935% | 0 / 0 / 0 | 75.000% | 0 |
| C8-no-choice-context | cycle7-independent-games | 100.000% | 99.649% | 99.824% | 1.288% | 0 / 0 / 0 | 87.500% | 0 |
| C8-no-choice-context | cycle8-adversarial | 100.000% | 92.084% | 95.879% | 11.360% | 0 / 0 / 0 | 88.889% | 0 |
| C8-no-choice-context | cycle8-combination-holdout | 100.000% | 100.000% | 100.000% | 0.700% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-choice-context | cycle8-independent-games | 100.000% | 100.000% | 100.000% | 1.184% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-choice-context | cycle8-validation | 100.000% | 100.000% | 100.000% | 1.048% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-dependence | cycle7-independent-games | 100.000% | 99.649% | 99.824% | 1.272% | 0 / 0 / 0 | 87.500% | 0 |
| C8-no-dependence | cycle8-adversarial | 100.000% | 92.084% | 95.879% | 11.002% | 0 / 0 / 0 | 88.889% | 0 |
| C8-no-dependence | cycle8-combination-holdout | 100.000% | 100.000% | 100.000% | 0.700% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-dependence | cycle8-independent-games | 100.000% | 100.000% | 100.000% | 1.150% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-dependence | cycle8-validation | 100.000% | 100.000% | 100.000% | 0.973% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-destination-context | cycle7-independent-games | 100.000% | 99.298% | 99.648% | 1.351% | 0 / 4 / 0 | 84.375% | 0 |
| C8-no-destination-context | cycle8-adversarial | 100.000% | 86.807% | 92.938% | 13.148% | 0 / 40 / 0 | 61.111% | 0 |
| C8-no-destination-context | cycle8-combination-holdout | 100.000% | 93.239% | 96.501% | 2.300% | 0 / 48 / 0 | 62.500% | 0 |
| C8-no-destination-context | cycle8-independent-games | 100.000% | 100.000% | 100.000% | 1.150% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-destination-context | cycle8-validation | 100.000% | 92.233% | 95.960% | 1.946% | 0 / 48 / 0 | 70.000% | 0 |
| C8-no-promotion-training | cycle3-independent-games | 100.000% | 100.000% | 100.000% | 1.120% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-promotion-training | cycle4-independent-games | 100.000% | 99.750% | 99.875% | 0.968% | 0 / 0 / 0 | 91.667% | 0 |
| C8-no-promotion-training | cycle5-combination-holdout | 100.000% | 100.000% | 100.000% | 0.581% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-promotion-training | cycle5-independent-games | 100.000% | 99.777% | 99.888% | 1.042% | 0 / 0 / 0 | 93.750% | 0 |
| C8-no-promotion-training | cycle5-structural-holdout | 100.000% | 96.774% | 98.361% | 3.977% | 0 / 0 / 0 | 66.667% | 0 |
| C8-no-promotion-training | cycle5-validation | 100.000% | 99.628% | 99.814% | 1.231% | 0 / 0 / 0 | 87.500% | 0 |
| C8-no-promotion-training | cycle6-adversarial | 100.000% | 99.111% | 99.554% | 1.613% | 0 / 0 / 0 | 90.000% | 0 |
| C8-no-promotion-training | cycle6-independent-games | 100.000% | 100.000% | 100.000% | 1.076% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-promotion-training | cycle6-validation | 100.000% | 100.000% | 100.000% | 1.405% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-promotion-training | cycle7-independent-games | 100.000% | 99.298% | 99.648% | 1.414% | 0 / 0 / 0 | 84.375% | 0 |
| C8-no-promotion-training | cycle8-adversarial | 100.000% | 86.807% | 92.938% | 14.937% | 0 / 0 / 0 | 61.111% | 0 |
| C8-no-promotion-training | cycle8-combination-holdout | 100.000% | 93.239% | 96.501% | 4.700% | 0 / 0 / 0 | 62.500% | 0 |
| C8-no-promotion-training | cycle8-independent-games | 100.000% | 100.000% | 100.000% | 1.184% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-promotion-training | cycle8-validation | 100.000% | 92.233% | 95.960% | 3.743% | 0 / 0 / 0 | 70.000% | 0 |
| C8-no-promotion-training | frozen-adversarial | 100.000% | 100.000% | 100.000% | 1.407% | 0 / 0 / 0 | 100.000% | 0 |
| C8-no-promotion-training | frozen-heldout-transfer | 100.000% | 99.882% | 99.941% | 1.252% | 0 / 0 / 0 | 97.500% | 0 |
| C8-promotion-relative | cycle3-independent-games | 100.000% | 100.000% | 100.000% | 1.120% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | cycle4-independent-games | 100.000% | 99.750% | 99.875% | 0.968% | 0 / 0 / 0 | 91.667% | 0 |
| C8-promotion-relative | cycle5-combination-holdout | 100.000% | 100.000% | 100.000% | 0.581% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | cycle5-independent-games | 100.000% | 99.777% | 99.888% | 1.011% | 0 / 0 / 0 | 93.750% | 0 |
| C8-promotion-relative | cycle5-structural-holdout | 100.000% | 96.774% | 98.361% | 3.977% | 0 / 0 / 0 | 66.667% | 0 |
| C8-promotion-relative | cycle5-validation | 100.000% | 99.628% | 99.814% | 1.231% | 0 / 0 / 0 | 87.500% | 0 |
| C8-promotion-relative | cycle6-adversarial | 100.000% | 99.111% | 99.554% | 1.613% | 0 / 0 / 0 | 90.000% | 0 |
| C8-promotion-relative | cycle6-independent-games | 100.000% | 100.000% | 100.000% | 1.059% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | cycle6-validation | 100.000% | 100.000% | 100.000% | 1.405% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | cycle7-independent-games | 100.000% | 99.649% | 99.824% | 1.288% | 0 / 0 / 0 | 87.500% | 0 |
| C8-promotion-relative | cycle8-adversarial | 100.000% | 92.084% | 95.879% | 11.360% | 0 / 0 / 0 | 88.889% | 0 |
| C8-promotion-relative | cycle8-combination-holdout | 100.000% | 100.000% | 100.000% | 0.700% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | cycle8-independent-games | 100.000% | 100.000% | 100.000% | 1.184% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | cycle8-validation | 100.000% | 100.000% | 100.000% | 1.048% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | frozen-adversarial | 100.000% | 100.000% | 100.000% | 1.407% | 0 / 0 / 0 | 100.000% | 0 |
| C8-promotion-relative | frozen-heldout-transfer | 100.000% | 99.882% | 99.941% | 1.252% | 0 / 0 / 0 | 97.500% | 0 |
| C8-strict | cycle6-independent-games | n/a | 0.000% | 0.000% | 16.300% | 0 / 0 / 0 | 0.000% | 0 |
| C8-strict | cycle7-independent-games | n/a | 0.000% | 0.000% | 19.196% | 0 / 0 / 0 | 0.000% | 0 |
| C8-strict | cycle8-adversarial | n/a | 0.000% | 0.000% | 44.365% | 0 / 0 / 0 | 0.000% | 0 |
| C8-strict | cycle8-combination-holdout | n/a | 0.000% | 0.000% | 37.800% | 0 / 0 / 0 | 0.000% | 0 |
| C8-strict | cycle8-independent-games | n/a | 0.000% | 0.000% | 20.636% | 0 / 0 / 0 | 0.000% | 0 |
| C8-strict | cycle8-validation | n/a | 0.000% | 0.000% | 25.374% | 0 / 0 / 0 | 0.000% | 0 |

Each incorrect supported decision and each loss of a previously supported decision is retained with its exact evaluation artifact, FEN/move, proof references, evidence IDs and host decision in [all-regressions.json.xz](../../artifacts/cycle8/proofs/all-regressions.json.xz). This includes intended strict-mode abstentions and destructive ablations. Representative successful and unresolved native proofs are in [representative-examples.json.xz](../../artifacts/cycle8/proofs/representative-examples.json.xz).

Calibration is diagnostic only: empirical strength-decile mappings are fitted on C8 validation and scored on other partitions, separately for all candidates, in-board candidates and promotion candidates. [calibration.json](../../artifacts/cycle8/calibration.json) reports Brier score, log loss, ECE, raw-strength Brier score and native-confidence bins. No mapping affects training, STVs, classification or acceptance. Correlated candidate rows and imbalanced easy negatives limit interpretation.
