# Cycle 7 engineering delivery

Starting HEAD: `ebe58a980d601ad8b8167a6533619c383109e08d`. Verified source HEAD: `a94b7816f0a97e253adc319acb4a8cb2f0e27996`. The final delivery HEAD is the local commit containing this report. No Cycle 7 push, PR, publication or external mutation was performed.

Default: **C7-frozen, operational**. Native positive composition: **not demonstrated** after the three-encoding budget. Tests: **318 passed**. Clean bootstrap and all mandatory acceptance checks passed. 721 prior-cycle files remain byte-identical. The frozen wrapper preserves every reproduced candidate classification and native proof, with a versioned proof-label migration.

| Package | Status | Evidence |
|---|---|---|
| C7-01 | complete | [evaluation.md](evaluation.md) |
| C7-02 | negative research finding | [native-feasibility.md](native-feasibility.md) |
| C7-03 | negative research finding | [native-feasibility.md](native-feasibility.md) |
| C7-04 | complete | [extension-proposal.md](extension-proposal.md) |
| C7-05 | negative research finding | [evaluation.md](evaluation.md) |
| C7-06 | complete | [temporal-and-negatives.md](temporal-and-negatives.md) |
| C7-07 | complete | [performance.md](performance.md) |
| C7-08 | complete | [architecture-and-api.md](architecture-and-api.md) |
| C7-09 | complete | [evaluation.md](evaluation.md) |
| C7-10 | complete | [reproduction.md](reproduction.md) |
| C7-11 | complete | [final-report.md](final-report.md) |
| C7-12 | complete | [decision-memo.md](decision-memo.md) |

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

New learning promoted: **False**. Rejection details, if any, are in `artifacts/cycle7/acceptance.json`. Candidate-model improvements cannot override observed-error gates. Research failures remain visible in the learning curves, raw native transcripts and per-candidate regression archive.

Full paired changes and bootstrap intervals, representative successes and unresolved abstentions, every recorded regression, native proofs, model hashes, data hashes and command receipts are linked from [evaluation.md](evaluation.md) and the artifact manifest. Runtime and exact cache parity are in [performance.md](performance.md). [reproduction.md](reproduction.md) records commands, pinned dependencies and limitations.

The [one-page decision memo](decision-memo.md) distinguishes continued work within pinned PLN, authorization for an upstream extension discussion, and accepting partial positives as a permanent boundary. No new calculus is presumed approved.
