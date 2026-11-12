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


## Registered final results

These scores use the frozen mappings and resolved directional references only. Lower Brier score and log loss indicate better diagnostic fit to that event; they do not establish useful move selection. Intervals resample source groups. Empty reliability bins and undefined selective risks remain visible.

| Panel | Diagnostic arm | Resolved N | Brier | Brier 95% interval | Log loss | Log-loss 95% interval |
| --- | --- | --- | --- | --- | --- | --- |
| Immediate final test | calibrated | 145 | 0.263855 | 0.249394–0.277782 | 0.722726 | 0.692471–0.751866 |
| Immediate final test | raw_A_strength | 145 | 0.297553 | 0.256727–0.340115 | 0.966777 | 0.795755–1.154293 |
| Two supplied plies | calibrated | 33 | 0.254280 | 0.236365–0.272740 | 0.701779 | 0.665741–0.738833 |
| Two supplied plies | raw_A_strength | 33 | 0.291006 | 0.219772–0.369830 | 0.904270 | 0.631426–1.226695 |
| Three supplied plies | calibrated | 28 | 0.281002 | 0.217200–0.344742 | 0.759968 | 0.623525–0.898225 |
| Three supplied plies | raw_A_strength | 28 | 0.280536 | 0.196563–0.382321 | 0.894863 | 0.573892–1.287388 |
| TCEC family holdout | calibrated | 25 | 0.248203 | 0.223002–0.277168 | 0.689676 | 0.637356–0.750483 |
| TCEC family holdout | raw_A_strength | 25 | 0.277726 | 0.203288–0.379851 | 0.859932 | 0.574897–1.265580 |

Reliability bin numbers 0–4 correspond to [0,.2), [.2,.4), [.4,.6), [.6,.8), and [.8,1]. These are evaluation-bin populations, separate from the calibration fitting populations retained in each frozen mapping.

| Panel | Arm | Bin | N | Mean diagnostic probability | Observed A fraction |
| --- | --- | --- | --- | --- | --- |
| Immediate final test | raw_A_strength | 0 | 23 | 0.039453 | 0.347826 |
| Immediate final test | raw_A_strength | 1 | 0 | undefined | undefined |
| Immediate final test | raw_A_strength | 2 | 101 | 0.500000 | 0.534653 |
| Immediate final test | raw_A_strength | 3 | 2 | 0.663793 | 0.000000 |
| Immediate final test | raw_A_strength | 4 | 19 | 0.976923 | 0.473684 |
| Immediate final test | calibrated | 0 | 0 | undefined | undefined |
| Immediate final test | calibrated | 1 | 2 | 0.333333 | 0.000000 |
| Immediate final test | calibrated | 2 | 120 | 0.484167 | 0.525000 |
| Immediate final test | calibrated | 3 | 23 | 0.692308 | 0.347826 |
| Immediate final test | calibrated | 4 | 0 | undefined | undefined |
| Two supplied plies | raw_A_strength | 0 | 4 | 0.025000 | 0.500000 |
| Two supplied plies | raw_A_strength | 1 | 0 | undefined | undefined |
| Two supplied plies | raw_A_strength | 2 | 27 | 0.500000 | 0.481481 |
| Two supplied plies | raw_A_strength | 3 | 0 | undefined | undefined |
| Two supplied plies | raw_A_strength | 4 | 2 | 0.983190 | 0.500000 |
| Two supplied plies | calibrated | 0 | 0 | undefined | undefined |
| Two supplied plies | calibrated | 1 | 0 | undefined | undefined |
| Two supplied plies | calibrated | 2 | 33 | 0.525069 | 0.484848 |
| Two supplied plies | calibrated | 3 | 0 | undefined | undefined |
| Two supplied plies | calibrated | 4 | 0 | undefined | undefined |
| Three supplied plies | raw_A_strength | 0 | 3 | 0.025000 | 0.333333 |
| Three supplied plies | raw_A_strength | 1 | 0 | undefined | undefined |
| Three supplied plies | raw_A_strength | 2 | 20 | 0.500000 | 0.450000 |
| Three supplied plies | raw_A_strength | 3 | 0 | undefined | undefined |
| Three supplied plies | raw_A_strength | 4 | 5 | 0.975000 | 0.600000 |
| Three supplied plies | calibrated | 0 | 0 | undefined | undefined |
| Three supplied plies | calibrated | 1 | 3 | 0.333333 | 0.333333 |
| Three supplied plies | calibrated | 2 | 0 | undefined | undefined |
| Three supplied plies | calibrated | 3 | 25 | 0.683333 | 0.480000 |
| Three supplied plies | calibrated | 4 | 0 | undefined | undefined |
| TCEC family holdout | raw_A_strength | 0 | 2 | 0.015104 | 0.500000 |
| TCEC family holdout | raw_A_strength | 1 | 1 | 0.203125 | 0.000000 |
| TCEC family holdout | raw_A_strength | 2 | 20 | 0.500000 | 0.650000 |
| TCEC family holdout | raw_A_strength | 3 | 0 | undefined | undefined |
| TCEC family holdout | raw_A_strength | 4 | 2 | 0.975000 | 0.500000 |
| TCEC family holdout | calibrated | 0 | 0 | undefined | undefined |
| TCEC family holdout | calibrated | 1 | 1 | 0.333333 | 0.000000 |
| TCEC family holdout | calibrated | 2 | 22 | 0.490909 | 0.636364 |
| TCEC family holdout | calibrated | 3 | 2 | 0.692308 | 0.500000 |
| TCEC family holdout | calibrated | 4 | 0 | undefined | undefined |

Selective-risk thresholds below are fixed diagnostics on native directional answers. No threshold was selected from final outcomes and native classifications remain unchanged.

| Panel | Diagnostic certainty threshold | Selected N | Wrong | Risk | Resolved-direction coverage |
| --- | --- | --- | --- | --- | --- |
| Immediate final test | 0.5 | 42 | 18 | 42.9% | 29.0% |
| Immediate final test | 0.6 | 42 | 18 | 42.9% | 29.0% |
| Immediate final test | 0.7 | 0 | 0 | undefined | 0.0% |
| Immediate final test | 0.8 | 0 | 0 | undefined | 0.0% |
| Immediate final test | 0.9 | 0 | 0 | undefined | 0.0% |
| Two supplied plies | 0.5 | 3 | 1 | 33.3% | 9.1% |
| Two supplied plies | 0.6 | 1 | 0 | 0.0% | 3.0% |
| Two supplied plies | 0.7 | 0 | 0 | undefined | 0.0% |
| Two supplied plies | 0.8 | 0 | 0 | undefined | 0.0% |
| Two supplied plies | 0.9 | 0 | 0 | undefined | 0.0% |
| Three supplied plies | 0.5 | 7 | 3 | 42.9% | 25.0% |
| Three supplied plies | 0.6 | 7 | 3 | 42.9% | 25.0% |
| Three supplied plies | 0.7 | 5 | 2 | 40.0% | 17.9% |
| Three supplied plies | 0.8 | 0 | 0 | undefined | 0.0% |
| Three supplied plies | 0.9 | 0 | 0 | undefined | 0.0% |
| TCEC family holdout | 0.5 | 4 | 2 | 50.0% | 16.0% |
| TCEC family holdout | 0.6 | 4 | 2 | 50.0% | 16.0% |
| TCEC family holdout | 0.7 | 0 | 0 | undefined | 0.0% |
| TCEC family holdout | 0.8 | 0 | 0 | undefined | 0.0% |
| TCEC family holdout | 0.9 | 0 | 0 | undefined | 0.0% |
