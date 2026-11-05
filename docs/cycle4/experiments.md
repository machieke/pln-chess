# Cycle 4 experiments

| Model / split | Precision | Recall | F1 | Abstention | Exact sets | False legal | False illegal | Self-check FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C3 / frozen-heldout-transfer | 100.00% | 95.53% | 97.72% | 18.14% | 67.50% | 0 | 0 | 0 |
| C3 / frozen-adversarial | 100.00% | 97.36% | 98.66% | 28.23% | 75.00% | 0 | 0 | 0 |
| C3 / cycle3-independent-games | 100.00% | 88.64% | 93.98% | 29.82% | 0.00% | 0 | 0 | 0 |
| C3 / cycle4-structural-combination | 100.00% | 94.12% | 96.97% | 22.63% | 75.00% | 0 | 0 | 0 |
| C3 / cycle4-independent-games | 100.00% | 92.24% | 95.96% | 25.05% | 29.17% | 0 | 0 | 0 |
| C4-full / frozen-heldout-transfer | 100.00% | 97.77% | 98.87% | 3.15% | 75.00% | 0 | 0 | 0 |
| C4-full / frozen-adversarial | 100.00% | 99.12% | 99.56% | 2.32% | 91.67% | 0 | 0 | 0 |
| C4-full / cycle3-independent-games | 100.00% | 95.24% | 97.56% | 3.89% | 0.00% | 0 | 0 | 0 |
| C4-full / cycle4-structural-combination | 100.00% | 95.80% | 97.85% | 3.23% | 83.33% | 0 | 0 | 0 |
| C4-full / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 3.27% | 41.67% | 0 | 0 | 0 |

## Ablations on the independent game holdout

| Model / split | Precision | Recall | F1 | Abstention | Exact sets | False legal | False illegal | Self-check FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C3 / cycle4-independent-games | 100.00% | 92.24% | 95.96% | 25.05% | 29.17% | 0 | 0 | 0 |
| C4-conservative / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 4.39% | 41.67% | 0 | 0 | 0 |
| C4-coverage / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 3.27% | 41.67% | 0 | 0 | 0 |
| C4-full / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 3.27% | 41.67% | 0 | 0 | 0 |
| C4-no-dependence / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 3.25% | 41.67% | 0 | 0 | 0 |
| C4-no-exposure / cycle4-independent-games | 94.66% | 95.37% | 95.01% | 3.42% | 16.67% | 43 | 0 | 43 |
| C4-no-induction / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 3.27% | 41.67% | 0 | 0 | 0 |
| C4-observations / cycle4-independent-games | 94.66% | 95.37% | 95.01% | 20.11% | 16.67% | 43 | 0 | 43 |

Every report scores complete candidate sets; abstentions count against recall and exact sets. Per-piece and special-move metrics, raw candidates, proof depth, work counters and game-cluster bootstrap intervals are inside each compressed report. The new holdout has 12 games and 24 sampled positions. Confidence intervals are exploratory, not an assurance of zero risk.

C4-no-induction is a declared equivalence control: production induction is already disabled. Its aggregate entries alias C4-full and are not presented as independent experimental runs. The separate laboratory does execute revision-only, native-induction and manually seeded abstraction arms.

All threshold settings were registered before holdout evaluation. Conservative thresholds can remove weak attack warnings as well as weak positive claims, so risk is not necessarily monotonic. All ablation false legal cases and complete threshold-failure proofs are retained under ablations/. No failing threshold was adopted in production.

Specifically, the conservative ablation has two adversarial and one validation self-check false positives, despite zero on the new game holdout. Default C4 has zero observed false legal and false illegal cases, while one previously supported legal castle now abstains under stricter history requirements; see [coverage-regressions.json](../../artifacts/cycle4/coverage-regressions.json). [In-board-only metrics](../../artifacts/cycle4/in-board-metrics.json) supplement the full candidate grammar. [Verification](verification.md) distinguishes fresh-process inference memory from the 2.26 GiB full research report cost and documents the final diagnostic-only correction.

Induction population: {'A': 16, 'B': 16, 'BA': 16, 'BC': 16, 'C': 79, 'N': 86}. Native induced TV: {'confidence': 0.46972477064220186, 'strength': 1.0}. 28 Cycle 2/3 formulas reproduced. Five distance-transfer control classifications become supported, while the same manually seeded abstraction already succeeds; production benefit remains unestablished.

Calibration is fit only on validation rows. Raw native TVs remain unchanged. calibration.json reports Brier, log loss and ECE on structural and game holdouts; confidence is not treated as a calibrated probability.
