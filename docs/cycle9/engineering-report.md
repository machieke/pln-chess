# Cycle 9 engineering report

The delivery retains the accepted C8 checkpoint and optimizes host state/serialization work while preserving native proof semantics. Starting commit: `36b5ea10395c0f41de4c03824ba6f8ee1c5dbad1`. Verified native-study source: `d26228d6064b52d8b769e3253c02793d264ebf7d`. Qualified application source: `898e17856fc2b15d1dd0b378c8d7239be5dc9cff`. Current production source hash: `e6135204b41a977d7e69722ddf46c833c1398f99ab2bf10ccc34559cd968e5a8`. Model version: `1217e17552ff611bebf0efc650245b05fb71c93a8175b579b025d6273d5d781d`. Local commit history and final working-tree status are reported with the delivery; these source commits are distinct from the final evidence/report commit.

The implementation memoizes identities, FEN and square lookup on immutable state objects; detaches mutable constructor sequences; hashes model dataclasses without a redundant deep copy; and exports native TVs directly as fresh dictionaries. Model hashes are deliberately not memoized, so changing evidence still changes model identity. Native arithmetic, native source pins, learned descriptors, inference thresholds and operational/strict/experimental policies are unchanged.

The final mobile check exposed overflow from the 64-character report hash. Source `898e17856fc2b15d1dd0b378c8d7239be5dc9cff` adds one CSS wrapping attribute. Every other production byte, including native inference, acceptance and JavaScript, is identical to the executed native study. The original verifier rechecked every native gate; all 365 tests and actual API/CLI smoke were rerun on the corrected source before browser verification. Native evaluations and timings were reused only after that exact one-attribute equivalence check. [Source equivalence](../../artifacts/cycle9/presentation/source-equivalence.json), [qualification](../../artifacts/cycle9/presentation/verified.json), [original receipts](../../artifacts/cycle9/presentation/native-study/), [current test log](../../artifacts/cycle9/presentation/pytest.txt).

## Historical acceptance comparison

| Historical cohort | C8 recall | C9 replay recall | C8 exact sets | C9 exact sets | Native proof parity |
|---|---|---|---|---|---|
| frozen-heldout-transfer | 99.882% | 99.882% | 97.500% | 97.500% | Exact |
| cycle7-independent-games | 99.649% | 99.649% | 87.500% | 87.500% | Exact |
| cycle8-independent-games | 100.000% | 100.000% | 100.000% | 100.000% | Exact |
| cycle8-adversarial | 92.084% | 92.084% | 88.889% | 88.889% | Exact |

All 16 historical operational suites and all 10 established strict/experimental comparisons replay exactly. [Original summaries](../../artifacts/cycle9/baseline/C8-promotion-relative-summary.json), [optimized regression receipt](../../artifacts/cycle9/regression/verified.json).

## New cohorts

| Cohort | Positions | All candidates | In-board | Recall | Exact sets | False legal | False illegal | Self-check FP | Unknown |
|---|---|---|---|---|---|---|---|---|---|
| development | 100 | 9056 | 4798 | 99.911% | 98/100 | 0 | 0 | 0 | 95 |
| calibration | 100 | 11402 | 6130 | 99.762% | 94/100 | 0 | 0 | 0 | 147 |
| independent-games | 500 | 50127 | 26493 | 99.992% | 499/500 | 0 | 0 | 0 | 621 |
| adversarial | 128 | 5504 | 3170 | 99.233% | 112/128 | 0 | 0 | 0 | 91 |
| special-moves | 80 | 3200 | 2349 | 99.254% | 71/80 | 0 | 0 | 0 | 58 |

| Held-out cohort | Population | Candidates | Precision | Recall | Coverage | Selective accuracy |
|---|---|---|---|---|---|---|
| independent-games | complete | 50127 | 100.000% | 99.992% | 98.761% | 100.000% |
| independent-games | in_board | 26493 | 100.000% | 99.992% | 97.656% | 100.000% |
| adversarial | complete | 5504 | 100.000% | 99.233% | 98.347% | 100.000% |
| adversarial | in_board | 3170 | 100.000% | 99.233% | 97.129% | 100.000% |
| special-moves | complete | 3200 | 100.000% | 99.254% | 98.188% | 100.000% |
| special-moves | in_board | 2349 | 100.000% | 99.254% | 97.531% | 100.000% |

| Held-out cohort | Source clusters | Recall 95% interval | Exact-set 95% interval |
|---|---|---|---|
| independent-games | 100 | 99.974% – 100.000% | 99.400% – 100.000% |
| adversarial | 64 | 98.841% – 99.538% | 82.031% – 92.188% |
| special-moves | 80 | 98.732% – 99.682% | 81.250% – 95.000% |

These cohorts have no historical C8 measurement on the same complete test population; the table is a new study of the unchanged model under the optimized implementation. Complete and in-board metrics, source-game/pair bootstrap intervals, per-piece scores and all structural strata are retained in the [evaluation summary](../../artifacts/cycle9/analysis/evaluation-summary.json). No final held-out outcome was used to alter learning or thresholds. [Protocol](study-protocol.md).

Intervals use 500 deterministic source-cluster bootstrap draws. Related opening families can remain correlated; finite zero-error results do not bound population risk to zero. [Dataset coverage](../../artifacts/cycle9/analysis/dataset-coverage.json) separately records phase, material, pawn structures, opening/structural families, check multiplicity, castling rights and en-passant metadata. These are descriptive counts, not additional independent samples.

## Mode comparisons and research targets

| Mode | Matched cohort | Positions | Recall | Exact sets | False legal | False illegal | Unknown |
|---|---|---|---|---|---|---|---|
| operational | independent-games | 25 | 100.000% | 100.000% | 0 | 0 | 22 |
| operational | special-moves | 80 | 99.254% | 88.750% | 0 | 0 | 58 |
| strict | independent-games | 25 | 0.000% | 0.000% | 0 | 0 | 671 |
| strict | special-moves | 80 | 0.000% | 0.000% | 0 | 0 | 1327 |
| experimental | independent-games | 25 | 0.000% | 0.000% | 0 | 0 | 671 |
| experimental | special-moves | 80 | 0.000% | 0.000% | 0 | 0 | 1327 |

The independent-game comparison above uses the same first 25 registered positions in every mode; it does not compare 500 operational positions with 25 strict positions. All modes score the same 80 special-move positions. Strict positive abstention reflects the missing native joint theorem, even when local evidence is strong. [Shard receipts and native proofs](../../artifacts/cycle9/evaluation/).

| Research target | Threshold | Measured | Met |
|---|---|---|---|
| independent-games exact sets | 0.85 | 0.998 | Yes |
| adversarial exact sets | 0.95 | 0.875 | No |
| independent-game recall | 0.98 | 0.999916 | Yes |
| false_positive | 0 | 0 | Yes |
| false_illegal | 0 | 0 | Yes |
| self_check_false_legal | 0 | 0 | Yes |
| full-214 cold p50 seconds | 4.03765 | 4.00829 | Yes |
| full-214 warm p50 seconds | 2.77778 | 2.74769 | Yes |

Proportions in the target table are fractions, not percentages. Error totals cover all 908 new operational positions. Historical zero-error gates passed separately. [Target assessment](../../artifacts/cycle9/analysis/research-targets.json).

## Verification and interfaces

365 tests passed; 26 original baseline and 26 optimized historical evaluations passed; 287/287 negative controls preserved; 90,511 new and 81,944 historical row proofs reconstructed; 252 serial benchmark samples passed full candidate/proof identity checks. The fresh runtime and dependency lock are recorded in the [bootstrap receipt](../../artifacts/cycle9/bootstrap-context.json). Native-source hashes and all protected historical files remain unchanged. Actual CLI export and accepted API behavior passed [application smoke checks](../../artifacts/cycle9/smoke/verified.json); the browser verified diagnostics, calibration export, failure proof navigation, temporal categories, strict/incomplete modes, invalid-input clearing and 390-pixel mobile layout with zero captured console/server errors. [UI receipt](../../artifacts/cycle9/ui-verification.json), [recording and screenshots](../../artifacts/cycle9/ui/2026-11-09_15-33-45_cycle-9-accepted-model-calibrated-diagno/SUMMARY.md).

The API adds `research_report` and `inspect_temporal_v9`. CLI commands add `research-report`, `calibration-export` and `temporal-inspect-v9`. Existing public inference paths remain available. Empirical mapping lookup occurs only in diagnostic presentation, after native inference, and carries `native: false` and `changes_classification: false`.

## Research findings and limits

Supplied events resolve 2 developmental castling abstentions without changing native TVs; the full graph, rule IDs, evidence, source game and counterfactual controls are retained. [Abstention study](../../artifacts/cycle9/abstention/development-experiment.json.xz). Dependence policies remain unchanged after duplicate, correlation, conflict and retraction controls. [Evidence audit](../../artifacts/cycle9/dependence/summary.json). The [composition decision](architecture-decision.md) recommends existing operators operationally and no production extension.

Games are synthetic; opening and adversarial family dependence remains; special-move history is often incomplete; empirical calibration may shift across cohorts; native confidence is not calibrated correctness probability; positive legality remains partial; p95/p99 timing estimates are sample maxima. [Calibration](calibration-report.md), [performance](performance-report.md), [generalization](generalization-analysis.md).

Recommended Cycle 10 priorities: evaluate diverse human/engine game provenance under frozen splits; study temporal evidence transport and long histories; target remaining structural failure families through independently acquired relational evidence; improve calibration under shift with family-level uncertainty; and, only after explicit authorization, specify a bounded isolated credal prototype with proof certificates and a statistical front end. No new operator or universal-correctness claim follows from this delivery.
