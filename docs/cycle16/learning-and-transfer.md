# Native learning and transfer

Learning the new finite conditional changes held-out native support. Learning
the downstream rules from the same source episodes exposes a separate shared-
ancestry composition failure. Neither result is structure discovery.

[Frozen corpus registration](../../artifacts/cycle16/corpus-registration.json)
selects one compatible two-cell query from each of 42 existing TCEC games, using
source order, ply order and square order without attack labels. Splits are 12
training, six development and 24 test source episodes. Selection begins at ply
12 and takes the first compatible pair, so common opening configurations dominate.
No external data was acquired and the selection was not retuned after results.

Every root retains its original observed state plus dependent E/E and O/E
counterfactuals for evaluation. Training retains all nine occupancy variants,
but only E/E satisfies the supplied conditional's antecedents. Blocked and
unknown antecedents are excluded; a blocked path is not negative evidence for
an all-empty conditional. The exact frozen training record guard rejects test
labels, forged ancestry, changed state identity and modified labels.

Native revision starts from `(stv .5 0)` and admits `(stv label .5)` once per
source-game ancestry and template. All admitted labels are positive. The
[learned checkpoint](../../artifacts/cycle16/learning/learned/model.json) changes
only `clear-two` to strength 1, confidence .923076923076923. The fuller
[shared-chain checkpoint](../../artifacts/cycle16/learning/shared-chain/model.json)
also learns the rook rule from eleven episodes and bishop rule from one; no
queen terminal training example occurs. Unobserved terminal parameters remain
at their registered priors. Supplied F uses .95 assumed confidence throughout.
Original declarations and rule identities remain exact; no old checkpoint or
another rule's support is copied into the new template.

The [learning summary](../../artifacts/cycle16/learning/summary.json), native
revision transcripts and ledgers retain admission, exclusions, observation and
state identities, label generation, ancestry and checkpoint lineage. Duplicate
delivery leaves parameters and ancestry unchanged. Ledger-bearing versions can
differ because replay records rejected deliveries and new execution receipts.
An actual leave-one-source native refit lowers held-out attack confidence from
.8423688087692307 to .8365190253749999; both remain supported. The untrained prior
returns unknown. No threshold change is used to demonstrate learning.

The matched final evaluation has **72 dependent endpoints from 24 test games**:
30 positive and 42 negative attack references. [Results](../../artifacts/cycle16/evaluation/summary.json):

| Arm | Correct | Wrong | Unknown | Positive recall, including abstention |
| --- | ---: | ---: | ---: | ---: |
| R: unchanged recursive knowledge | 42 | 0 | 30 | 0% |
| F: supplied finite rule | 72 | 0 | 0 | 100% |
| F-minus: remove only clear-two | 42 | 0 | 30 | 0% |
| Untrained finite prior | 42 | 0 | 30 | 0% |
| L: learned clear-two, supplied terminal rules | 72 | 0 | 0 | 100% |
| Learned finite and downstream rules, shared ancestry | 42 | 0 | 30 | 0% |

F, L and the shared learned chain each derive Clear on all 30 positive endpoints.
The shared learned chain cannot carry that support into Attack. The other 42
endpoints have NoAttack support, while Clear remains unknown. All source-panel
exposure queries remain unknown; target/owner combinations do not establish the
registered exposure premises. Positive exposure is demonstrated separately in
the controlled opposing-slider/actor-king panel. There are no conflicting or
incomplete final endpoints. Development similarly gives F/L 18 correct endpoints;
R/F-minus/prior/shared-chain give 11 correct negatives and seven unknown positives.

The [actual shared-ancestry witness](../../artifacts/cycle16/supplement/shared-training-witness.json)
finds eleven shared training-game stamps between returned clearance and a
returned terminal partial implication. The native structural operator can bind
them, but `StampDisjoint` rejects the pair. This localizes a real learned-chain
failure rather than merely attributing every unknown result to provenance.

The [transfer audit](../../artifacts/cycle16/supplement/transfer-audit.json)
separates four kinds of novelty:

| Axis | Held-out result |
| --- | --- |
| Source episodes | 24 new game ancestries, zero overlap with training/development |
| Query identifiers | All 48 attacker/target identifiers are new |
| Endpoint locations | Zero unseen pairs; 22/24 test roots use the same a1-to-d1 configuration |
| Coarse relative geometry | Zero unseen strata; orthogonal and diagonal two-cell shapes were already seen |

Training contains eleven rook and one bishop roots; test contains 23 rook and
one bishop roots. Queen capability comes from the separately identified
synthetic panel, not an independent held-out queen population. Renaming,
translation and reflection are dependent structural controls, not new geometry
families. The original state and its occupancy variants remain in one group;
some original clear states duplicate the E/E physical configuration.

The narrow two-cell design cannot support a meaningful independent coarse-
geometry generalization estimate. This limitation and overlap policy were
registered before fitting. Distinct games from the same engine tournament and
repeated opening configurations are not claimed statistically independent.
No population confidence interval or general chess-accuracy claim is made.
The result supports native parameter revision and transfer to unseen bindings
and episodes under supplied structure, not arbitrary geometry transfer,
negative-example learning, noisy-supervision robustness or calibrated probability.
