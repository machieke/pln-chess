# Matched evaluation and performance

| Split | C4 legal / illegal / unknown / incomplete | C5 strict | C6 operational | C6 recall | C6 exact sets |
|---|---:|---:|---:|---:|---:|
| frozen-heldout-transfer | 832 / 1720 / 83 / 0 | 0 / 1752 / 883 / 0 | 832 / 1752 / 51 / 0 | 97.767333% | 75.000000% |
| frozen-adversarial | 225 / 955 / 28 / 0 | 0 / 964 / 244 / 0 | 225 / 964 / 19 / 0 | 99.118943% | 91.666667% |
| cycle3-independent-games | 260 / 1371 / 66 / 0 | 0 / 1398 / 299 / 0 | 260 / 1398 / 39 / 0 | 95.238095% | 0.000000% |
| cycle4-independent-games | 762 / 3736 / 152 / 0 | 0 / 3808 / 842 / 0 | 762 / 3808 / 80 / 0 | 95.369212% | 41.666667% |
| cycle5-validation | 257 / 1236 / 50 / 0 | 0 / 1251 / 292 / 0 | 257 / 1251 / 35 / 0 | 95.539033% | 37.500000% |
| cycle5-combination-holdout | 183 / 319 / 14 / 0 | 0 / 327 / 189 / 0 | 183 / 327 / 6 / 0 | 98.387097% | 78.571429% |
| cycle5-structural-holdout | 60 / 109 / 7 / 0 | 0 / 109 / 67 / 0 | 60 / 109 / 7 / 0 | 96.774194% | 66.666667% |
| cycle5-independent-games | 855 / 5375 / 197 / 0 | 0 / 5450 / 977 / 0 | 855 / 5450 / 122 / 0 | 95.317726% | 31.250000% |
| cycle6-validation | 207 / 1025 / 49 / 0 | 0 / 1040 / 241 / 0 | 207 / 1040 / 34 / 0 | 95.391705% | 28.571429% |
| cycle6-adversarial | 220 / 385 / 15 / 0 | 0 / 387 / 233 / 0 | 220 / 387 / 13 / 0 | 97.777778% | 75.000000% |
| cycle6-independent-games | 877 / 5013 / 153 / 0 | 0 / 5058 / 985 / 0 | 877 / 5058 / 108 / 0 | 96.799117% | 37.500000% |

Frozen exact-set accuracy is 75.000% (75% research target met). New independent-game exact-set accuracy is 37.500% (40% research target not met). These research targets are reported separately from mandatory correctness gates. Empty-terminal exact matches are cycle5-independent-games: 1, frozen-adversarial: 2; every other reported exact match has a nonempty legal move set.

Every frozen split uses its original members, source dataset hash, model and thresholds. Both baseline models were rerun; classifications, raw TVs, evidence/rule IDs, proof IDs and exact predicted sets match C5's preserved reports. Frozen inputs are copied in `baseline/inputs.json.xz`; immutable historical proof/report copies remain reachable through starting commit `6c7538cedeb52fa4a921e3549ac57022ff7874d8` and are verified unchanged. No prior artifact is rewritten.

The frozen baselines were executed in the prior clean checkout and reused here only after runtime, protected-input and frozen-source byte checks passed. `baseline/reuse.json` identifies both commits and every copied report hash; `executed_in_this_checkout` is false. This checkout freshly executes the C6 evaluations, new-dataset baselines, research, benchmarks and tests.

All-candidate and in-board metrics, confusion matrices, precision/recall/F1, error families, raw strength/confidence distributions and 300-draw clustered 95% bootstrap intervals are in each evaluation report. Empty-terminal exact matches are separated from nonempty exact sets. Confidence is not a calibrated probability. Exploratory strength-decile calibration is fitted on the declared validation split only and never affects inference.

`dataset-overlap-audit.json` checks every new sampled game position against all prior dataset positions and against one another under the preserved symmetry key. No overlap is present. Diagnostic adversarial fixtures deliberately include known regression contexts and are reported separately from independent games.

Four required variants are evaluated: frozen C4, strict C5/C6, C6 operational with negatives, and C6 operational without the new negatives. Every frozen classification changed from C4 links its host acceptance node and native proof in `verification.json`; new-split evaluation rows retain the equivalent decision and proof references alongside their matched C4 reports. All 49 historical cases and 238 C5 negatives are preserved, with 49 and 238 classification-changing removals. Every newer negative preserves the original C5 native proof exactly.

| Model/mode | Candidates | Reference seconds / calls | Cold seconds / calls | Warm seconds / calls | Peak KiB |
|---|---:|---:|---:|---:|---:|
| C4 | 214 | 23.883 / 16636 | 2.112 / 259 | 1.273 / 0 | 218536 |
| C5 | 214 | 25.137 / 16800 | 3.469 / 389 | 2.200 / 0 | 277912 |
| C6-operational | 214 | 25.813 / 16800 | 4.189 / 389 | 2.980 / 0 | 316328 |
| C6-strict | 214 | 25.671 / 16800 | 4.192 / 389 | 2.969 / 0 | 322280 |
| C6-experimental | 214 | 25.735 / 16800 | 4.148 / 389 | 2.975 / 0 | 323948 |

The operational cold/C4 cold ratio on 214 candidates is 1.983×; the ≤2× research target is met. If above target, the additional typed-premise execution, provenance expansion and complete proof export are explicit measured costs; no proof is silently truncated to improve timing. Four fixtures total 700 candidates. Reference, cold and warm runs have complete candidate/STV/classification/proof/evidence/rule parity in all three C6 modes. Warm calls are actual native calls, not logical scheduled nodes.

Fresh-process VmHWM measures live inference memory; it does not claim to cover all subprocesses. Reports separately measure repeated opponent frames, duplicate native proof occurrences, interpreter startup, complete candidate serialization and a lossless interned export. The interned evaluation export reduces duplicate storage; it is not represented as a reduction in the live API's full-proof memory.

Gates: `{'baseline': True, 'cache_parity': True, 'clean_bootstrap': True, 'frozen_errors': True, 'frozen_utility': True, 'native_probes': True, 'negatives': True, 'new_adversarial_errors': True, 'provenance': True, 'strict_abstention': True, 'tests': True}`. Default: `operational`. Observed correctness is empirical on these datasets, not universal legality.
