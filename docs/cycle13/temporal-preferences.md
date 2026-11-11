# Immediate and continuation-conditioned preferences

The 60 fixed plans provide 120 two-/three-ply endpoint comparisons, split into 36 training, 12 calibration and 12 test source games. The temporal fit joins immediate and training continuation observations while preserving shared ancestry and distinct horizons. The held-out source games never update it. Endpoint labels use the original actor's perspective, including explicit mate outcomes.

| Panel | Continued answers | Continued accuracy | Immediate answers | Immediate accuracy | Both answered | Reversals | Reference changes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2-calibration | 2 | 0.500 | 4 | 0.500 | 1 | 0 | 3 |
| 2-test | 2 | 0.000 | 2 | 0.500 | 0 | 0 | 5 |
| 2-train | 18 | 1.000 | 13 | 1.000 | 12 | 0 | 12 |
| 3-calibration | 4 | 0.250 | 4 | 0.750 | 4 | 2 | 3 |
| 3-test | 1 | 1.000 | 2 | 1.000 | 2 | 0 | 6 |
| 3-train | 18 | 1.000 | 15 | 1.000 | 15 | 0 | 13 |


The no-continuation arm uses the original immediate belief against the same endpoint labels. The continuation arm changes observations and training evidence together, so an observed difference does not isolate a causal effect of temporal information. Equal statuses may simply mean equal abstention. Unexamined responses are unknown, and local relational improvements do not guarantee an outcome.

There are 0 native joint temporal theorems. The branch and endpoint explanations are complete for their supplied bounded workload, not exhaustive chess futures.

Evidence: [temporal/summary.json](../../artifacts/cycle13/temporal/summary.json), [temporal/preferences.json.xz](../../artifacts/cycle13/temporal/preferences.json.xz), [ablations/temporal.json](../../artifacts/cycle13/ablations/temporal.json).
