# Cycle 8 consolidated engineering delivery

Starting commit: `c6ee658352395abe6e276cafdf1ddf59830a17a0`. Verified implementation: `4453b46217319fdbf22ac1d344c20111758798af`. The ending delivery commit is the commit containing this report; `git log c6ee658..HEAD` lists local cycle commits. No push was performed.

Default: **C8-promotion-relative, operational**. Tests: **347 passed**. The clean study reproduced 38 baseline evaluations and ran 81 C8 matrix evaluations. All 1366 protected historical files remain byte-identical; 236414 native row proofs were reconstructed and checked. New native positive composition remains **not demonstrated**. Its formal design and mathematical reference laboratory are separate from production.

| Package | Status | Evidence |
|---|---|---|
| C8-01 | complete | [evaluation.md](evaluation.md) |
| C8-02 | complete | [promotion-error-analysis.md](promotion-error-analysis.md) |
| C8-03 | complete | [ontology-and-curriculum.md](ontology-and-curriculum.md) |
| C8-04 | complete | [ontology-and-curriculum.md](ontology-and-curriculum.md) |
| C8-05 | complete | [ablations.md](ablations.md) |
| C8-06 | complete | [generalization-and-provenance.md](generalization-and-provenance.md) |
| C8-07 | complete | [native-composition-proposal.md](native-composition-proposal.md) |
| C8-08 | complete | [mathematical-validation.md](mathematical-validation.md) |
| C8-09 | complete | [native-composition-proposal.md](native-composition-proposal.md) |
| C8-10 | complete | [generalization-and-provenance.md](generalization-and-provenance.md) |
| C8-11 | complete | [performance.md](performance.md) |
| C8-12 | complete | [architecture-and-api.md](architecture-and-api.md) |
| C8-13 | complete | [evaluation.md](evaluation.md) |
| C8-14 | complete | [final-report.md](final-report.md) |

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

The promotion candidate correctly supports 8/8 original error cases. Generalization controls establish 26 successful source groups, including 18 strict held-out groups; mirrors are not independent samples. Each registered default candidate preserved all 287 negative/removal controls. See [generalization and provenance](generalization-and-provenance.md).

| Checkpoint | Fixture | Reference p50 s | Cold p50 s | Warm p50 s |
|---|---|---|---|---|
| C7-frozen | single-candidate | 0.987 | 0.960 | 0.161 |
| C7-frozen | full-214 | 25.680 | 4.038 | 2.778 |
| C7-frozen | promotion-heavy | 4.423 | 1.818 | 0.588 |
| C7-frozen | independent-game | 27.487 | 4.269 | 2.986 |
| C8-frozen | single-candidate | 1.047 | 0.977 | 0.214 |
| C8-frozen | full-214 | 26.185 | 4.636 | 3.300 |
| C8-frozen | promotion-heavy | 4.635 | 1.983 | 0.741 |
| C8-frozen | independent-game | 28.279 | 4.861 | 3.626 |
| C8-promotion-relative | single-candidate | 2.033 | 1.996 | 0.410 |
| C8-promotion-relative | full-214 | 26.418 | 4.672 | 3.334 |
| C8-promotion-relative | promotion-heavy | 4.671 | 2.097 | 0.821 |
| C8-promotion-relative | independent-game | 29.913 | 6.429 | 4.279 |
| C8-no-promotion-training | single-candidate | 1.098 | 1.076 | 0.272 |
| C8-no-promotion-training | full-214 | 26.327 | 4.744 | 3.345 |
| C8-no-promotion-training | promotion-heavy | 4.674 | 2.018 | 0.801 |
| C8-no-promotion-training | independent-game | 29.779 | 6.534 | 4.323 |

Performance tables show empirical p50 seconds. [Performance](performance.md) includes p95/p99, calls, grounding, memory, model/proof sizes and full cache parity. Five samples make tail estimates exploratory. [Evaluation](evaluation.md) includes precision, recall, F1, abstention, exact sets, promotion/per-piece metrics, paired intervals and validation-only calibration. [Ablations](ablations.md) retains failed and null experiments.

The [composition proposal](native-composition-proposal.md) separates conjunction, dependence, implication, aggregation and confidence. Exact finite checks and analytic arguments establish bounds conditional on supplied constraints; they do not establish STV calibration or a chess legality theorem. Existing-native, proposed-reference and unsupported results have distinct statuses.

Browser verification passed: **True**; [receipt](../../artifacts/cycle8/ui-verification.json). [Browser video, screenshots and logs](../../artifacts/cycle8/ui/2026-11-08_03-40-30_cycle-8-accepted-default-all-eight-promo/SUMMARY.md). [Reproduction](reproduction.md) documents the clean commands, lineage and evidence manifest. The [decision memo](decision-memo.md) answers all eight architectural questions.

Known limits: all new games are synthetic; constructed family separation uses complete configurations while atomic motifs recur; some extra pieces are remote; candidate grammar is an inductive bias; native positives remain partial learned conditionals; temporal replay is structural; confidence is uncalibrated; and small-sample performance/accuracy findings do not establish universal safety. The accepted default and research candidate remain separate whenever gates differ.
