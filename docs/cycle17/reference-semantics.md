# Exact reference semantics

The finite reference models show that marginal information does not identify
shared uncertainty. Their numbers are illustrative probabilities under explicit
assumptions, not measured chess probabilities or native PLN truth values.
The [executable cases](../../research/cycle17/reference_models.py) use rational
arithmetic and finite enumeration. The dedicated reference command is the sole
non-test importer; a static import-boundary test covers source, research,
training, evaluation and scripts, including literal dynamic-import targets.
The native adapter, models, classification thresholds and caches never consume
these results. No alternative PLN operator has been implemented.

For two binary parameters with marginal means one half, the three explicit
joint laws give different joint-success probabilities:

| Assumed joint law | Nonzero elementary outcomes | Joint success |
| --- | --- | ---: |
| Independent | 00, 01, 10, 11, each weight 1/4 | 1/4 |
| Perfect positive association | 00, 11, each weight 1/2 | 1/2 |
| Perfect negative association | 01, 10, each weight 1/2 | 0 |

The marginal-only answer is the interval [0, 1/2], not a selected point in that
interval. Equal marginal means and flat overlap stamps cannot select a joint law.
Native `(strength, confidence)` additionally lacks an established interpretation
as the full posterior over these parameters; no Beta interpretation is assumed.

For a shared parameter theta equal to 1/4 or 3/4 with equal weight, two Bernoulli
applications conditionally independent given theta have joint success
E[theta²] = 5/16. Independently redrawing theta for each application instead gives
E[theta]² = 1/4. Repeating the *same event* gives P(E and E) = P(E) = 1/2.
Parameter reuse, redrawing and event reuse are different models.

Starting from that same two-point prior, one Bernoulli success yields posterior
weights (1/4, 3/4), predictive success 5/8, and joint success 7/16 for two future
conditionally independent predictions sharing the posterior parameter. Replaying
the same observed event leaves that posterior unchanged. Squaring its likelihood
as though two independent successes occurred instead yields weights (1/10, 9/10)
and prediction 7/10. The latter is a different observation model, not a valid
way to make one observation more informative by delivering it again.

Shared data do not impose a specific correlation. With independent fair latent
bits, a common datum reporting equality yields posterior mass on 00 and 11:
both marginals remain one half and joint success is one half. Under a different,
explicitly factorized model, a vector record contains one local Bernoulli success
for each of two independent two-point parameters. Product priors and likelihoods
preserve posterior factorization, giving joint predictive success 25/64. Merely
calling both inputs “one dataset” neither supplies nor refutes these assumptions.

The remaining exact controls are:

| Case | Assumptions and identified result |
| --- | --- |
| Diamond | Both branches are deterministic copies of the same event of probability 1/3; their conjunction remains 1/3, not 1/9 |
| Cycle | Deterministic A → B → A adds no external observation or likelihood; probability remains 1/3 |
| Unequal uncertainty | Marginals 1/4 and 3/4 give joint bounds [0, 1/4]; 3/16 requires an explicit independent-event assumption |
| False hypothesis | A deterministic hypothesis assigns zero likelihood to an observed success; with an alternative assigning likelihood one, its posterior becomes zero |
| Missing dependence | Return bounds and “not identified,” with no point estimate |

The false-hypothesis result assumes noise-free observation. A noisy likelihood
would be a different model. The diamond/cycle examples illustrate exact identity
relationships; they are not proofs about every possible native proof graph.

Native/reference comparison is qualitative. Shared learned chains and native
diamonds encounter a conservative admissibility restriction. The reference
models specify joint information that native flat stamps and simple truth values
do not retain. Their confidence interpretations are different or unspecified.
No implementation defect is established merely by unequal numerical answers.
The observed native direct structural witness remains an audit only: bypassing
the guard cannot provide an experimental prediction.

Reproduce the independent laboratory with:

```bash
.venv/bin/python -m research.cycle17.reference_cli --out /tmp/c17-reference.json
.venv/bin/python -m pytest -q tests/test_cycle17_reference.py
```

The committed [exact results](../../artifacts/cycle17/reference-final/results.json)
include assumptions, rational strings and separately measured laboratory time.
