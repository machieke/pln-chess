# Evaluation and diagnostic calibration

Four questions have separate denominators: whether offline reference search resolved a direction, whether PLN answered, whether that answer agreed, and whether it transferred to an independent context. [Metric code](../../evaluation/cycle14_metrics.py) retains all registered cases. Unknown references are not scored as model failures or successes, and model abstentions are not counted as correct negative predictions.

| Metric | Definition |
|---|---|
| Reference resolution | (directional + no-demonstrated-preference references) / all registered comparisons |
| Answered directional accuracy | correct directional answers / answered resolved directions |
| Directional coverage | answered resolved directions / resolved directions |
| Correct-answer yield | correct directional answers / resolved directions |
| All-case answer rate | directional model answers, including on unknown references / all registered comparisons |
| Effective sample size | registered connected source-ancestry groups, not branches, budgets or file count |

Every result contains `N_all`, `N_directional`, `N_nondirectional`, `N_reference_unknown`, `N_answered`, `N_correct`, `N_wrong`, directional abstentions, all-case abstentions, contradictions and incomplete observations. Nondirectional support has its own count. An undefined ratio remains null; it is never converted to zero or perfect accuracy. A model can answer on an unknown reference, but no agreement claim is made for that answer.

Uncertainty intervals use 1,000 deterministic percentile bootstrap replicates, resampling whole source-ancestry components. Paired comparisons resample the same groups on both arms. Reports include the number of replicates in which an accuracy denominator exists. Two horizons share their root groups, and response crossproducts remain clustered by their ten roots. Finite bootstrap intervals do not remove source bias or establish universal transfer. Sparse zero-error answered subsets require particular restraint.

The event calibrated is **“the operational reference direction is displayed candidate A, conditional on a resolved A/B reference.”** Calibration uses only the reserved 60 immediate calibration roots and the 20-root temporal subset at each horizon. Each model/horizon receives its own mapping. Five fixed equal-width bins of raw A-channel strength use Laplace smoothing; an empty bin maps to 0.5. The mapping is frozen before final prediction and binds its calibration IDs and ancestry groups.

Native A, B and nondirectional channels are independent conditional truth values. They are not renormalized. The host diagnostic mapping does not alter native strength, confidence, classification thresholds, evidence, proofs or production behavior. Reports compare raw A-strength and calibrated Brier/log loss only as diagnostic scoring on resolved A/B outcomes. Log loss clips probabilities to `[1e-6, 1-1e-6]` solely for finite host scoring. Unknown and nondirectional references are excluded from that binary event.

[Frozen mappings](../../artifacts/cycle14/evaluation-freeze.json) precede final outcomes. [Evaluation summaries](../../artifacts/cycle14/evaluation/summary.json) include reliability-bin populations, clustered score intervals and selective-risk tables at fixed diagnostic certainty thresholds. The latter do not select a new production threshold or move policy. Final scores and the interpretation of small calibration groups are included in the [engineering report](engineering-report.md).
