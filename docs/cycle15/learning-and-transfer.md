# Native learning and transfer

[The corpus registration](../../artifacts/cycle15/corpus-registration.json) fixes
24 training, 12 development and 48 final-test typed families before fitting.
Ray direction, length, blocker position and attacker kind define a root. Its
before/after observations, translations, renamed entities and scenario variants
remain dependent descendants. These are designed synthetic families from one
generator, not 84 independently sampled games. Bootstrap intervals describe this
panel conditionally and do not estimate broad chess strength.

The [coarser partition audit](../../artifacts/cycle15/supplement/partition-audit.json)
finds that treating attacker kinds as dependent variants collapses training,
development and test to 23, 11 and 44 geometry groups. Seven test roots share
geometry with training/development under another kind. Only 37 geometry groups
(41 typed roots, 82 endpoints) are wholly unseen. On that subset C/D return 41
correct negatives, 41 unknown positives and no classified errors: positive recall
is zero. Thus **48 independent unseen geometry groups and positive transfer to
unseen ray geometry are not demonstrated**. The primary counts and splits are
retained unchanged, rather than retroactively relabeling independence.

All four positive final cases are held-out kind/geometry combinations whose
coarser geometry was seen under another kind. Entity and board-location transfer
remain demonstrated within that narrow scope. The geometry-cluster sensitivity
interval for overall positive recall is 1.96%–17.02%; it still is not a natural-game
population estimate. The shared obstruction template also admits two training
kind variants from one geometry under the registered policy, so its independence
assumption is weaker than its 24 distinct ancestry identifiers suggest.

[Training](../../training/cycle15_consequences.py) learns truth values for four
slider templates and the obstruction template. Logical structures are supplied.
The [checkpoint](../../artifacts/cycle15/learning/model.json) records ancestry,
structure identity and a ledger hash. The 96 training ledger records comprise
48 admitted native revisions, 24 negative attack observations whose clearance
antecedent is unsatisfied, and 24 unknown-observation controls. Negative attacks
also supply the correctly conditioned positive obstruction hypothesis.

All admitted conditional outcomes in this controlled corpus are positive.
This cycle therefore demonstrates revision and parameter transfer, not robustness
to erroneous supervision or discovery of rule structures. Opposing-support
semantics is tested separately in the native capability matrix.

Training starts at `(stv 0.5 0.0)` and uses finite `(stv label 0.5)` observations.
Each update executes native `|-` revision on the two belief truth values; the
exact expression and native output are retained. There is no Python confidence
arithmetic. Final strengths are 1.0; confidence is 0.857143 for bishop, 0.888889
for rook, 0.75 for queen/orthogonal, 0.875 for queen/diagonal and 0.96 for
obstruction. These are native support values, not calibrated error probabilities.

Each template admits a root ancestry once. Replaying all records rejects 48
duplicate admissions and preserves every learned parameter and ancestry list.
Removing one queen/diagonal training ancestry reduces the development prediction
confidence from 0.806561 to 0.790101, while leaving its supported classification.
Changing the terminal rule to its untrained prior removes support.
[Learning interventions](../../artifacts/cycle15/diagnostics/learning-interventions.json)
retain these outcomes; final-test prior-versus-trained checks are also included
in the supplemental evidence.

## Matched final panel

| Arm | Correct | Wrong | Unknown | Positive recall, counting abstention | Negative coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| A: frozen field conditional | 96 | 0 | 0 | 100% | 100% |
| B: same conditional knowledge via native derivation | 96 | 0 | 0 | 100% | 100% |
| C: connected facts, supplied templates | 52 | 0 | 44 | 8.33% | 100% |
| D: connected facts, learned template TVs | 52 | 0 | 44 | 8.33% | 100% |

There are 48 positive and 48 negative reference endpoints. C and D answer the
four positive one-cell endpoints and all 48 blocked endpoints. Their native
schema transfer coverage is 52/96, or 54.17%. No tested final endpoint is
conflicting or incomplete. A and B have zero classification differences across
all 120 development/test endpoints. B retains the old descriptor input to isolate
execution; it is not represented as the connected architecture.

The [matched summary](../../artifacts/cycle15/evaluation/summary.json) and
[evaluation driver](../../evaluation/cycle15_consequences.py) preserve counts,
references, arm identities and raw evidence links. Answered accuracy is 100% on
this panel, with a degenerate all-correct bootstrap interval; the substantial
abstention and designed sample make a general accuracy claim inappropriate.
No preference-accuracy comparison is made.

The [root bootstrap coverage receipt](../../artifacts/cycle15/supplement/coverage-uncertainty.json)
gives 95% intervals of 2.08%–16.67% for positive recall and 51.04%–58.33% for
overall classified coverage (1,000 draws, seed 15). These describe uncertainty
within the synthetic design, without treating before/after rows as independent.

The [information-loss challenge](../../artifacts/cycle15/supplement/information/field-information-loss.json)
checks all 315 attack-field queries in each mirrored fixture. Both have 26
supported, 284 contradicted and five unknown field results, yet the specified
attacker/target reference and connected conclusion change. This is a connectivity
diagnostic, separate from the final statistical panel.

Native disjoint stamps are not a statistical independence guarantee. Distinct
atomic observations from one state keep distinct occurrence stamps and share
host ancestry metadata. Learned rules retain stable rule and training-ancestry
stamps across firings. The recursive and diamond failures expose the resulting
conservative reuse boundary; no fresh stamps are minted to bypass it.
