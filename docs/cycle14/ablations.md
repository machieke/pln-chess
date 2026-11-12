# Matched ablations

Each contrast below uses the same evaluation rows, references and ancestry groups. Differences are right arm minus left arm. Percentage differences are percentage points. `correct/answered` displays directional answers only; unknown references remain outside agreement scoring. The [full receipt](../../artifacts/cycle14/ablations/summary.json) binds both checkpoint names, all denominators and 1,000 paired source-group bootstrap replicates.

| Factor | Split | Horizon | Left correct/answered | Right correct/answered | Coverage difference | Correct-yield difference | Yield 95% interval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| supervision-matched-historical | test | 1 | 32/58 | 23/49 | -6.2% | -6.2% | -12.5%–0.0% |
| supervision-matched-historical | source-holdout | 1 | 4/9 | 7/12 | 12.0% | 12.0% | -4.3%–29.6% |
| additional-independent-evidence | test | 1 | 23/49 | 22/42 | -4.8% | -0.7% | -5.7%–4.6% |
| additional-independent-evidence | source-holdout | 1 | 7/12 | 7/12 | 0.0% | 0.0% | 0.0%–0.0% |
| descriptor-matched-supervision | test | 1 | 22/42 | 24/42 | 0.0% | 1.4% | -6.7%–8.8% |
| descriptor-matched-supervision | source-holdout | 1 | 7/12 | 3/5 | -28.0% | -16.0% | -40.0%–8.3% |
| concept-evidence | test | 1 | 24/42 | 2/4 | -26.2% | -15.2% | -21.1%–-9.2% |
| concept-evidence | source-holdout | 1 | 3/5 | 1/1 | -16.0% | -8.0% | -20.0%–0.0% |
| dependent-repeated-labels | test | 1 | 23/49 | 23/49 | 0.0% | 0.0% | 0.0%–0.0% |
| dependent-repeated-labels | source-holdout | 1 | 7/12 | 7/12 | 0.0% | 0.0% | 0.0%–0.0% |
| unsafe-dependence | test | 1 | 23/49 | 23/49 | 0.0% | 0.0% | 0.0%–0.0% |
| unsafe-dependence | source-holdout | 1 | 7/12 | 7/12 | 0.0% | 0.0% | 0.0%–0.0% |
| temporal-supervision | test | 1 | 32/58 | 23/49 | -6.2% | -6.2% | -12.5%–0.0% |
| temporal-supervision | test | 2 | 3/7 | 2/6 | -3.0% | -3.0% | -10.7%–0.0% |
| temporal-supervision | test | 3 | 4/12 | 6/14 | 7.1% | 7.1% | 0.0%–17.9% |
| temporal-supervision | source-holdout | 1 | 4/9 | 7/12 | 12.0% | 12.0% | -4.3%–29.6% |
| temporal-supervision | source-holdout | 2 | 0/0 | 0/0 | 0.0% | 0.0% | 0.0%–0.0% |
| temporal-supervision | source-holdout | 3 | 0/0 | 0/0 | undefined | undefined | undefined–undefined |
| temporal-descriptor | test | 1 | 22/42 | 24/42 | 0.0% | 1.4% | -6.7%–8.8% |
| temporal-descriptor | test | 2 | 4/7 | 2/3 | -12.1% | -6.1% | -15.2%–0.0% |
| temporal-descriptor | test | 3 | 9/14 | 4/7 | -25.0% | -17.9% | -37.9%–4.8% |
| temporal-descriptor | source-holdout | 1 | 7/12 | 3/5 | -28.0% | -16.0% | -40.0%–8.3% |
| temporal-descriptor | source-holdout | 2 | 0/0 | 0/0 | 0.0% | 0.0% | 0.0%–0.0% |
| temporal-descriptor | source-holdout | 3 | 0/0 | 0/0 | undefined | undefined | undefined–undefined |
| temporal-concepts | test | 1 | 24/42 | 2/4 | -26.2% | -15.2% | -21.1%–-9.2% |
| temporal-concepts | test | 2 | 2/3 | 0/0 | -9.1% | -6.1% | -14.7%–0.0% |
| temporal-concepts | test | 3 | 4/7 | 0/0 | -25.0% | -14.3% | -28.6%–-3.2% |
| temporal-concepts | source-holdout | 1 | 3/5 | 1/1 | -16.0% | -8.0% | -20.0%–0.0% |
| temporal-concepts | source-holdout | 2 | 0/0 | 0/0 | 0.0% | 0.0% | 0.0%–0.0% |
| temporal-concepts | source-holdout | 3 | 0/0 | 0/0 | undefined | undefined | undefined–undefined |

Temporal contrasts hold the endpoint reference target fixed even when the input contains only root observations. Immediate, continued and explicitly omitted input are evaluated under the same checkpoints where stated. Horizon-specific keys may cause an immediate-only model to abstain on unseen horizon keys; this is a representation limitation, not an empirical gain in reasoning.

| Split | Horizon | Matched temporal contrast | Coverage difference | Correct-yield difference | Yield 95% interval |
| --- | --- | --- | --- | --- | --- |
| test | 2 | combined-primary | -21.2% | -9.1% | -25.0%–6.5% |
| test | 2 | temporal-training-with-immediate-input | 0.0% | 0.0% | 0.0%–0.0% |
| test | 2 | temporal-training-with-same-continuation | 9.1% | 6.1% | 0.0%–14.7% |
| test | 2 | same-checkpoint-observation-context | -21.2% | -9.1% | -25.0%–6.5% |
| test | 2 | same-checkpoint-explicit-missingness | 9.1% | 6.1% | 0.0%–14.7% |
| test | 2 | omission-robust-same-checkpoint | 9.1% | 6.1% | 0.0%–14.7% |
| test | 3 | combined-primary | -7.1% | -3.6% | -20.0%–12.5% |
| test | 3 | temporal-training-with-immediate-input | 0.0% | 0.0% | 0.0%–0.0% |
| test | 3 | temporal-training-with-same-continuation | 25.0% | 14.3% | 3.2%–28.6% |
| test | 3 | same-checkpoint-observation-context | -7.1% | -3.6% | -20.0%–12.5% |
| test | 3 | same-checkpoint-explicit-missingness | 25.0% | 14.3% | 3.2%–28.6% |
| test | 3 | omission-robust-same-checkpoint | 25.0% | 14.3% | 3.2%–28.6% |
| source-holdout | 2 | combined-primary | 0.0% | 0.0% | 0.0%–0.0% |
| source-holdout | 2 | temporal-training-with-immediate-input | 0.0% | 0.0% | 0.0%–0.0% |
| source-holdout | 2 | temporal-training-with-same-continuation | 0.0% | 0.0% | 0.0%–0.0% |
| source-holdout | 2 | same-checkpoint-observation-context | 0.0% | 0.0% | 0.0%–0.0% |
| source-holdout | 2 | same-checkpoint-explicit-missingness | 0.0% | 0.0% | 0.0%–0.0% |
| source-holdout | 2 | omission-robust-same-checkpoint | 0.0% | 0.0% | 0.0%–0.0% |
| source-holdout | 3 | combined-primary | undefined | undefined | undefined–undefined |
| source-holdout | 3 | temporal-training-with-immediate-input | undefined | undefined | undefined–undefined |
| source-holdout | 3 | temporal-training-with-same-continuation | undefined | undefined | undefined–undefined |
| source-holdout | 3 | same-checkpoint-observation-context | undefined | undefined | undefined–undefined |
| source-holdout | 3 | same-checkpoint-explicit-missingness | undefined | undefined | undefined–undefined |
| source-holdout | 3 | omission-robust-same-checkpoint | undefined | undefined | undefined–undefined |

The training-only majority baseline is evaluation code and never enters production inference. Its class is chosen from training labels only; it answers every resolved test direction and retains unknown references outside agreement scoring.

| Split | Training majority | All | Directional references | Answered | Correct | Wrong | Answered accuracy | Directional coverage | Unknown reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | B | 200 | 145 | 145 | 74 | 71 | 51.0% | 100.0% | 52 |
| source-holdout | B | 60 | 25 | 25 | 10 | 15 | 40.0% | 100.0% | 34 |

Repeated reference analyses and continuations preserve channel truth values with dependence handling; the unsafe control inflates confidence in 135 rules. The [dependence report](evidence-dependence.md) distinguishes identical native beliefs from different delivery provenance. Concept additions, descriptor refinements and omission training are not assumed beneficial because they were implemented. These finite controlled comparisons do not establish strategic playing strength or isolate every interaction among supervision, abstraction and source distribution.
