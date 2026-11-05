# Cycle 5 model card

This is a research model of learned relative constraints and proof gaps. It is not a complete chess engine and cannot select or certify legal moves. Default C5 intentionally emits no positive global legality labels while the positive composition theorem is missing. Zero observed false positives therefore cannot be used as evidence of useful positive accuracy.

Training combines the unchanged C4 reference checkpoint with 42 typed premise hypotheses, revised from eligible historical training observations and a synthetic factorial curriculum. Exact counts, versions, lineage and native revisions are in the delivered checkpoint and ledger. The grammar, local projections and finite symbolic induction proposals are supplied inductive biases.

The dataset distinguishes a clean premise-only combination experiment from full-model comparisons containing the C4 prior. Synthetic duplicate observations share dependence groups. Independent game evaluation uses a fixed new seed and game-level clusters, with validation kept separate. Small samples, synthetic family grouping and the limited candidate grammar restrict conclusions.

Inspect both raw TVs and their proposition scopes. Local admissibility, lack of a destination conflict, a temporal claim and complete global legality are different propositions. Unknown is neither legal nor illegal. Unsupported native composition, missing temporal evidence, contradictory labels and exhausted work budgets remain visible.

The main unresolved risks are lost positive coverage, incomplete temporal/safety composition, coarse abstraction errors outside the tested distribution, limited native induction utility, and inherited proof-memory costs. Exact performance and all failures are in [generalization results](generalization-results.md) and [performance](performance.md).
