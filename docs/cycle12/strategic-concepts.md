# Strategic concept contracts

All eight concept families are experimental. A supplied role assignment is a
structural candidate. A trained rule is a conditional hypothesis. An executed
native TV rule establishes only its named conditional conclusion. These three
objects have different identities and must remain distinguishable in the API,
proof export and inspector.

| Family | Roles | Limited learned target | What remains unproved |
|---|---|---|---|
| Pin | attacker, intervening piece, target | PotentialPinAlignment | Universal legal restriction, strategic value, or a joint exposure theorem |
| Fork | attacker, target A, target B | PotentialMultipleTargetAttack | Native conjunction of the two influence relations or forced material gain |
| DiscoveredAttack | attacker, mover, target | NewAttackAfterSuppliedEdit | Legality or strategic merit of the supplied edit; native temporal implication |
| DiscoveredDefense | defender in attacker role, mover, target | NewDefenseAfterSuppliedEdit | Legal recapture or the sufficiency of the resulting defense |
| OverloadedDefender | defender, two wards, two opposing threats | CompetingDefenseObligations | That every available response fails to satisfy the obligations |
| TrappedPiece | subject | NoOrdinaryGeometricExit | Safe legal escape, unfavorable exits, strategic trapping or universal safety |
| MultipleAttackers | two attackers, one target | MultipleLocalAttackSources | Independent support, combined attack strength or a forced result |
| ThreatRemoval | attacker, remover in mover role, target | ThreatAbsentAfterSuppliedEdit | Absence of every other threat or complete safety of the target |

The grammar supplies role types, local relative geometry, occupancy observations,
ordinary movement candidates, and distance/symmetry pooling. It supplies no
positive concept truth values. Training observes limited labels offline and
revises positive and negative conditional channels with native `Truth_Revision`.
Inference uses the already authorized native modus ponens, negation and candidate
selection operators. No additional native inference operator is introduced.

## Composite observations and independent field evidence

The premise of a concept conditional is explicitly named
`ObservedStructuralRolePacket`. Its contents are grouped by the host from
supplied role occupancy and relative observations. The packet's observation
confidence is a declared sensor assumption. It is not the result of combining
uncertain field truth values and is not a native conjunction theorem.

Each concept also retains independently inferred field relations with their
native proofs, matched rules, evidence IDs and dependence groups. These relations
explain what the field model supports for each role. They are not silently fused
into the packet premise. Removing field-model learning may remove those proofs
without retracting a different conditional learned directly on the observed
packet. This separation is an explicit counterfactual control, not an implicit
claim that field beliefs caused the concept prediction.

Missing required observations withhold the packet. Missing learned conditionals
produce an unknown result. Exhausted inference budgets or failed native execution
produce an incomplete result. Neither unknown nor incomplete is a negative
strategic label. A supported packet conditional remains a partial concept
candidate when the full interpretation requires unavailable composition.

## Particular interpretation limits

An observed king target distinguishes an absolute-pin hypothesis from a relative
pin against a named nonking target. A line of pieces alone does not prove that the
intervening piece cannot move legally. Counterfactual exposure fields and any
separately requested legal classification must retain their own scope.

A fork retains two target-specific attack records. Targets have names and piece
types, but no hardcoded material scores. Pawn, knight, rook, queen and king cases
are included. The entire raw pawn-fork family is held out; no equivalent training
motif is inserted to force success.

Two defended pieces do not establish overload. The representation must retain
which opponent threatens each ward and what a supplied response changes. Even a
pair of unfavorable local consequences does not quantify over every possible
response. Strategic overload therefore remains unknown.

Trapping separates structural movement candidates, locally supported ordinary
mobility, contradicted mobility, unknown mobility, separately evidenced legal
exits, and unassessed exit quality. An empty list of supported exits cannot hide
unknown exits. A native no-ordinary-exit conditional is not a theorem of strategic
trapping.

## Evaluation scope

The registered controlled dataset has 533 examples in 221 raw structural
families: 70 training, 26 calibration and 125 test families. Calibration uses the
preregistered thresholds and does not tune the held-out results. Equivalent
translations, reflections, role permutations, ID changes and counterfactual
descendants are grouped before fitting. The audit also retains board-edge
topology for local mobility families.

This is one synthetic source with supplied abstractions. Different raw ray
lengths or role topologies can intentionally share a pooled conditional key;
the evaluation reports that overlap separately. Precision and recall apply to
the limited targets in the table, not to complete strategic concepts or playing
strength. Numerical results and preserved failures will be bound to the final
evaluation artifacts.
<!-- cycle12-measured-evidence -->

## Measured limited-target results

| Family | Limited target | N | TP | TN | FP | FN | Abstain | Precision | Recall incl. abstention | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| DiscoveredAttack | NewAttackAfterSuppliedEdit | 48 | 24 | 24 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| DiscoveredDefense | NewDefenseAfterSuppliedEdit | 48 | 24 | 24 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| Fork | PotentialMultipleTargetAttack | 24 | 7 | 14 | 0 | 0 | 3 | 100.0000% | 87.5000% | 93.3333% |
| MultipleAttackers | MultipleLocalAttackSources | 12 | 6 | 6 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| OverloadedDefender | CompetingDefenseObligations | 12 | 6 | 6 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| Pin | PotentialPinAlignment | 144 | 48 | 96 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| ThreatRemoval | ThreatAbsentAfterSuppliedEdit | 12 | 6 | 6 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| TrappedPiece | NoOrdinaryGeometricExit | 6 | 3 | 3 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |

| Family | False-positive rate | Supported false-negative rate | Positive misses incl. abstention | Abstention rate | Native conditional proofs | Complete joint proofs |
|---|---|---|---|---|---|---|
| DiscoveredAttack | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 48 | 0 |
| DiscoveredDefense | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 48 | 0 |
| Fork | 0.0000% | 0.0000% | 12.5000% | 12.5000% | 21 | 0 |
| MultipleAttackers | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 12 | 0 |
| OverloadedDefender | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 12 | 0 |
| Pin | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 144 | 0 |
| ThreatRemoval | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 12 | 0 |
| TrappedPiece | 0.0000% | 0.0000% | 0.0000% | 0.0000% | 6 | 0 |

The test panel contains 306 examples in 125 held-out raw structural families. It produces 303 classified answers,
124/125 supported positive targets and three fork abstentions, with zero false positives or supported false negatives.
Precision is conditional on a positive classification; recall includes abstained positives. Zero supported FN is not perfect recall.
The calibration partition is separate and does not tune thresholds. Its pawn fork family also abstains.

Every concept remains experimental. Native operators derive a limited conditional from an explicitly host-observed `ObservedStructuralRolePacket`. Component field proofs are separate; their uncertain truth values are not conjoined into that packet. Complete joint concept proofs, native temporal implications, strategic overload theorems and strategic trapping theorems all remain zero. No move score, search, ranking, material-value table or move selection is implemented.

364/370 calibration/test
examples share a supplied pooled conditional key with training. Raw family overlap is zero. This measures transfer through a
declared relative abstraction, not invention of the abstraction, arbitrary conjunction or external tactical generalization.

Evidence: [concepts/summary.json](../../artifacts/cycle12/concepts/summary.json), [concepts/rows.json.xz](../../artifacts/cycle12/concepts/rows.json.xz), [datasets/audit.json](../../artifacts/cycle12/datasets/audit.json).
