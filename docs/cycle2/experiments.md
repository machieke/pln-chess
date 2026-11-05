# Cycle 2 experiments

| Variant | Definition |
|---|---|
| B0 | Frozen Cycle 1 model/checkpoint and categorical inference on the new, identical splits |
| B1 | Hierarchical local conditionals, native revision, independent attack channel |
| B2 | B1 plus guarded native induction as an alternative conditional, selected by native confidence |
| B3 | Movement obstruction motifs removed, including exact-context fallback; attack occupancy remains in its separate channel |
| B4 | Attack/exposure channel removed; exact fallback also excludes opponent and transit frames |
| B5 | Dependence exclusion disabled; diagnostic only, correlated curriculum observations can inflate confidence |
| B6 | Geometry-only and absolute-coordinate empirical baselines, confined to evaluation |
| B7 | Exact-context specialization disabled |

All B0–B5/B7 runs use complete candidate sets for every split. Cycle 2 learning admits only slider distances 1–2 (1,426 eligible training rows); train-split evaluation still includes all 2,746 candidates, including longer withheld rays. B0 is the frozen historical exception to this training mask. B6 predicts from empirical training frequencies and is explicitly not native PLN. B1 is the default Cycle 2 reproduction target; B2 is opt-in experimental induction. No threshold is selected using held-out labels. Supported/contradicted displays use the existing 0.8/0.2 strength and 0.25 confidence thresholds. Decisive competing conditionals or a contradictory learned exposure cause abstention; raw native values are still reported.

JSON reports include precision, recall, F1, selective accuracy, abstention, exact move sets, in-board and per-piece metrics, false-legal and self-check counts/rates, unseen-exact-context coverage, chosen tier, proof depth, native invocation counts and latency. Peak RSS is the Python evaluation process high-water mark, not isolated total runtime memory. Three hundred deterministic position-cluster bootstrap resamples give exploratory precision/recall intervals. Validation-only empirical strength bins score held-out Brier/log-loss/ECE; PLN confidence is never treated as calibrated event probability.

The baseline manifest distinguishes previously reported artifacts from the fresh Cycle 1 reproduction. B0 on the new dataset is the appropriate comparison for B1/B2; the old reported 0% recall is historical context only. Generalization examples include exact training ledger references, unseen test FEN/move, matched tier-4 rule and native TV. Native induction may lose to higher-confidence direct conditional evidence; equal B1/B2 metrics are an honest null result.
