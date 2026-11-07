# Matched evaluation and independent-game evidence

Counts separate supported legal, supported illegal, abstention and incomplete results. C6 columns are independently reproduced, with the new C7 split executed against the frozen C6 checkpoint. All rows use identical candidate grammars, oracle labels, thresholds and split membership. Canonical C7 offline arms allow 100,000 scheduled native nodes after the development pilot exhausted the shared 20,000-node production cap on one two-pass position (20,186 nodes when completed). The production cap remains 20,000 and reports incomplete honestly. C6 baselines finish within their original cap. Backoff is an explicit semantic experiment; its additional proof nodes are not described as cache-equivalent.

| Split | C6 TP / TN / unknown / incomplete | C7 default | C6 recall / exact sets | C7 recall / exact sets | C7 false legal / false illegal / self-check |
|---|---:|---:|---:|---:|---:|
| cycle3-independent-games | 260 / 1398 / 39 / 0 | 260 / 1398 / 39 / 0 | 95.238% / 0.000% | 95.238% / 0.000% | 0 / 0 / 0 |
| cycle4-independent-games | 762 / 3808 / 80 / 0 | 762 / 3808 / 80 / 0 | 95.369% / 41.667% | 95.369% / 41.667% | 0 / 0 / 0 |
| cycle5-combination-holdout | 183 / 327 / 6 / 0 | 183 / 327 / 6 / 0 | 98.387% / 78.571% | 98.387% / 78.571% | 0 / 0 / 0 |
| cycle5-independent-games | 855 / 5450 / 122 / 0 | 855 / 5450 / 122 / 0 | 95.318% / 31.250% | 95.318% / 31.250% | 0 / 0 / 0 |
| cycle5-structural-holdout | 60 / 109 / 7 / 0 | 60 / 109 / 7 / 0 | 96.774% / 66.667% | 96.774% / 66.667% | 0 / 0 / 0 |
| cycle5-validation | 257 / 1251 / 35 / 0 | 257 / 1251 / 35 / 0 | 95.539% / 37.500% | 95.539% / 37.500% | 0 / 0 / 0 |
| cycle6-adversarial | 220 / 387 / 13 / 0 | 220 / 387 / 13 / 0 | 97.778% / 75.000% | 97.778% / 75.000% | 0 / 0 / 0 |
| cycle6-independent-games | 877 / 5058 / 108 / 0 | 877 / 5058 / 108 / 0 | 96.799% / 37.500% | 96.799% / 37.500% | 0 / 0 / 0 |
| cycle6-validation | 207 / 1040 / 34 / 0 | 207 / 1040 / 34 / 0 | 95.392% / 28.571% | 95.392% / 28.571% | 0 / 0 / 0 |
| cycle7-independent-games | 1094 / 5144 / 128 / 0 | 1094 / 5144 / 128 / 0 | 96.049% / 37.500% | 96.049% / 37.500% | 0 / 0 / 0 |
| frozen-adversarial | 225 / 964 / 19 / 0 | 225 / 964 / 19 / 0 | 99.119% / 91.667% | 99.119% / 91.667% | 0 / 0 / 0 |
| frozen-heldout-transfer | 832 / 1752 / 51 / 0 | 832 / 1752 / 51 / 0 | 97.767% / 75.000% | 97.767% / 75.000% | 0 / 0 / 0 |

| New independent training games | Evaluation split | Recall | Exact sets | False legal / false illegal / self-check |
|---:|---|---:|---:|---:|
| 0 | cycle6-independent-games | 97.572% | 46.875% | 0 / 0 / 0 |
| 0 | cycle7-independent-games | 97.542% | 53.125% | 4 / 4 / 0 |
| 2 | cycle6-independent-games | 100.000% | 100.000% | 0 / 0 / 0 |
| 2 | cycle7-independent-games | 99.298% | 84.375% | 4 / 4 / 0 |
| 4 | cycle6-independent-games | 100.000% | 100.000% | 0 / 0 / 0 |
| 4 | cycle7-independent-games | 99.298% | 84.375% | 4 / 4 / 0 |
| 8 | cycle6-independent-games | 100.000% | 100.000% | 0 / 0 / 0 |
| 8 | cycle7-independent-games | 99.298% | 84.375% | 4 / 4 / 0 |

| Ablation | Split | Recall | Exact sets | False legal / false illegal / self-check |
|---|---|---:|---:|---:|
| ablation-no-attack-exposure | cycle6-independent-games | 100.000% | 46.875% | 175 / 0 / 175 |
| ablation-no-attack-exposure | cycle7-independent-games | 99.298% | 40.625% | 61 / 4 / 57 |
| ablation-no-backoff | cycle6-independent-games | 100.000% | 100.000% | 0 / 0 / 0 |
| ablation-no-backoff | cycle7-independent-games | 99.298% | 84.375% | 0 / 0 / 0 |
| ablation-no-dependence | cycle6-independent-games | 100.000% | 100.000% | 0 / 0 / 0 |
| ablation-no-dependence | cycle7-independent-games | 99.298% | 84.375% | 0 / 4 / 0 |
| ablation-no-learned-negatives | cycle6-independent-games | 100.000% | 46.875% | 175 / 0 / 175 |
| ablation-no-learned-negatives | cycle7-independent-games | 99.298% | 40.625% | 61 / 0 / 57 |
| ablation-no-new-training | cycle6-independent-games | 97.572% | 46.875% | 0 / 0 / 0 |
| ablation-no-new-training | cycle7-independent-games | 97.542% | 53.125% | 4 / 4 / 0 |
| ablation-no-temporal | cycle6-independent-games | 100.000% | 100.000% | 0 / 0 / 0 |
| ablation-no-temporal | cycle7-independent-games | 99.298% | 84.375% | 4 / 4 / 0 |

The C7 family split contains 32 positions from 16 synthetic games with Sicilian/French opening prefixes. Training uses 16 positions from eight separately seeded queen-pawn games. Full positions, game IDs and transformation lineages are disjoint. Relative submotifs intentionally overlap; `datasets/structural-audit.json` quantifies that overlap. These are generated games, not an external human-game benchmark.

The active selector sees frozen-model coverage and relative structure before labels are attached. Independent-game budgets 0/2/4/8 correspond to 0/48/96/192 newly selected examples. Repeated source groups are excluded per hypothesis in dependence-aware training. The zero-new-training arm still pools historical evidence into coarse conditionals; the frozen arm adds no pooled rules.

Full metrics include precision, recall, F1, abstention, in-board-only results, per-piece and per-family results, self-check errors, legal-candidate denominator, empty-terminal exact matches and proof coverage. They are in `artifacts/cycle7/comparison.json` and the referenced evaluation archives. Paired per-position changes and game-cluster bootstrap intervals (1,000 draws, seed 707) are in `paired/` and `learning-curves.json`; small cluster counts limit interpretation. No universal zero-error claim follows from these samples.

Ablations execute no backoff, no attack/exposure, no temporal evidence, no dependence handling, no learned negatives and no new training. The no-history game arm is a measured null control because all game inputs already use FEN-only metadata; event-backed causal cases are tested separately. Dependence removal disables training deduplication and runtime overlap guards while retaining true source IDs. Destructive ablations are ineligible for default selection. Independent-premise removal belongs to the isolated native laboratory.

Every observed error or loss of a frozen supported classification, including intentional strict abstentions and destructive ablations, has an artifact path, candidate ID, native proof references and evidence groups in `proofs/all-regressions.json.xz`. Representative positive and unresolved proofs are in `proofs/representative-examples.json.xz`.

See [structural-analysis.md](structural-analysis.md) for the separate structural-motif metrics and exact ablation scopes. In particular, no learned negatives removes negative proof paths and their bridges; it retains marginal counterevidence and is not positive-only retraining. The exact-only ablation is diagnostic and is not promoted after observing these holdouts.
