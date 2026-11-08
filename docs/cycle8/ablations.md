# Ablations and failed experiments

| Arm | Split | Recall | Exact sets | FL / FI / self-check | Promotion recall |
|---|---|---|---|---|---|
| C8-promotion-relative | cycle7-independent-games | 99.649% | 87.500% | 0 / 0 / 0 | 100.000% |
| C8-promotion-relative | cycle8-adversarial | 92.084% | 88.889% | 0 / 0 / 0 | 91.667% |
| C8-promotion-relative | cycle8-combination-holdout | 100.000% | 100.000% | 0 / 0 / 0 | 100.000% |
| C8-promotion-relative | cycle8-independent-games | 100.000% | 100.000% | 0 / 0 / 0 | n/a |
| C8-promotion-relative | cycle8-validation | 100.000% | 100.000% | 0 / 0 / 0 | 100.000% |
| C8-no-promotion-training | cycle7-independent-games | 99.298% | 84.375% | 0 / 0 / 0 | 0.000% |
| C8-no-promotion-training | cycle8-adversarial | 86.807% | 61.111% | 0 / 0 / 0 | 50.000% |
| C8-no-promotion-training | cycle8-combination-holdout | 93.239% | 62.500% | 0 / 0 / 0 | 50.000% |
| C8-no-promotion-training | cycle8-independent-games | 100.000% | 100.000% | 0 / 0 / 0 | n/a |
| C8-no-promotion-training | cycle8-validation | 92.233% | 70.000% | 0 / 0 / 0 | 45.455% |
| C8-no-destination-context | cycle7-independent-games | 99.298% | 84.375% | 0 / 4 / 0 | 0.000% |
| C8-no-destination-context | cycle8-adversarial | 86.807% | 61.111% | 0 / 40 / 0 | 50.000% |
| C8-no-destination-context | cycle8-combination-holdout | 93.239% | 62.500% | 0 / 48 / 0 | 50.000% |
| C8-no-destination-context | cycle8-independent-games | 100.000% | 100.000% | 0 / 0 / 0 | n/a |
| C8-no-destination-context | cycle8-validation | 92.233% | 70.000% | 0 / 48 / 0 | 45.455% |
| C8-no-choice-context | cycle7-independent-games | 99.649% | 87.500% | 0 / 0 / 0 | 100.000% |
| C8-no-choice-context | cycle8-adversarial | 92.084% | 88.889% | 0 / 0 / 0 | 91.667% |
| C8-no-choice-context | cycle8-combination-holdout | 100.000% | 100.000% | 0 / 0 / 0 | 100.000% |
| C8-no-choice-context | cycle8-independent-games | 100.000% | 100.000% | 0 / 0 / 0 | n/a |
| C8-no-choice-context | cycle8-validation | 100.000% | 100.000% | 0 / 0 / 0 | 100.000% |
| C8-no-dependence | cycle7-independent-games | 99.649% | 87.500% | 0 / 0 / 0 | 100.000% |
| C8-no-dependence | cycle8-adversarial | 92.084% | 88.889% | 0 / 0 / 0 | 91.667% |
| C8-no-dependence | cycle8-combination-holdout | 100.000% | 100.000% | 0 / 0 / 0 | 100.000% |
| C8-no-dependence | cycle8-independent-games | 100.000% | 100.000% | 0 / 0 / 0 | n/a |
| C8-no-dependence | cycle8-validation | 100.000% | 100.000% | 0 / 0 / 0 | 100.000% |

Removing destination context pools occupancy and destination piece type. Removing choice context pools promotion choice and resulting identity. Removing dependence handling counts repeated source-group records and disables overlap guards while retaining true evidence IDs. No-promotion-training retains the C7 exact-only learner without C8 transition evidence. Native training ledgers report the actual revised evidence and exclusions. Null outcomes do not establish that a distinction or safeguard is unnecessary outside this corpus.

Initial development failures are retained under `artifacts/cycle8/development/`: a native negation probe used the wrong symbol casing and returned an unevaluated expression; the corrected signature produced a native STV. A zero-budget test exposed an absent diagnostic `typed_premises` list in C7; initialization fixed the exception without changing completed native derivations. The initial focused run was 26 passed / 1 failed; the corrected focused run passed 28 tests. Full clean-suite results are reported separately. The browser pilot required a persistent ProofShot output config to collect the command timeline; the final verification repeats the flows with that config.

The first final browser pass passed all functional checks, but the subsequent cleanup check found a detached ProofShot server still running. Its exact verifier source and evidence remain in `development/ui-first-final-pass/`. The corrected verifier records ownership of its server process group, closes that group after recording, and checks that the port has closed. The full browser pass was repeated. Production inference did not change.

That repetition exposed a browser-tool timing/state issue: a resize command returned success while the measured viewport was still 1280 pixels. The mobile assertion failed, and owned-server cleanup still completed. `development/ui-viewport-retry/` preserves the exact verifier and failed run. The final verifier creates a fresh isolated session, waits for the actual requested viewport, and invalidates stale success receipts before running; the 390-pixel layout requirement remains unchanged.

No failed experiment was removed to improve an acceptance metric. All candidate-specific release failures, if any, are listed in [acceptance.json](../../artifacts/cycle8/acceptance.json). The isolated composition laboratory did not demonstrate a new native joint introduction rule.

Removing dependence safeguards increased native positive confidence in 52/56 matched learned hypotheses. [ablation-belief-effects.json](../../artifacts/cycle8/ablation-belief-effects.json) retains both native STVs and record/group counts for every key. An unchanged accuracy result would not make repeated ancestry independent evidence. These are diagnostic comparisons of native outputs, not replacement confidence formulas.
