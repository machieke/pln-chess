# Independent limited-target concept learning

The registered dataset has 533 examples in 221 canonical raw structural families:
70 training families / 163 records, 26 calibration / 64 records, and 125 test / 306 records.
The partition is by raw motif ancestry, including counterfactual descendants, role permutations and equivalent transformations.
All 850 symmetry checks pass; split overlap and equivalent raw motif overlap are zero.
The 12 supplied sequences have 50 unique observed event IDs and are demonstration data, not additional concept training.

Training creates 61 relative packet hypotheses from 163 observations using
326 logical native revision nodes. Repeated native arithmetic expressions use the existing runtime
cache: 12 operators execute and 314 calls hit that cache.
Each logical evidence update still has its own source/evidence identity and retained trace. The neutral prior is (0.5, 0.05).
The seed is 121212; observed packet confidence is 0.99; training observation confidence is
0.5. Fixed thresholds are strength ≥0.8 / ≤0.2 with confidence ≥0.25.
No held-out labels tune the thresholds or descriptor grammar.
Raw native strength and confidence are separate quantities; neither is presented as an empirically calibrated strategic probability.
The calibration partition evaluates the fixed thresholds. No strategic probability calibrator is fitted in this cycle.

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

Every concept remains experimental. Native operators derive a limited conditional from an explicitly host-observed `ObservedStructuralRolePacket`. Component field proofs are separate; their uncertain truth values are not conjoined into that packet. Complete joint concept proofs, native temporal implications, strategic overload theorems and strategic trapping theorems all remain zero. No move score, search, ranking, material-value table or move selection is implemented.

The grammar supplies roles, local relative geometry, a movement candidate vocabulary, symmetry normalization, role-kind coarsening
and unique component-profile pooling. It does not supply positive concept truth values. The learned knowledge is a conditional
association under that supplied grammar. Of 370 calibration/test records, 364
reuse a training conditional key and 6 have unseen keys.
There are no absolute-square constants, FEN keys, piece IDs or complete-board hashes in learned descriptors.
This is one synthetic data source: raw family independence is not independence of external studies or annotators.

Native `Truth_Revision` updates positive and negative conditional channels. Training collapses connected declared source/motif/
transformation components; contradictory dependent components are withheld. Seven measured controls pass:
declared_transform_values_identical, duplicate_values_identical, independent_conflict_changes_values, retracted_group_absent, retraction_changes_values, shared_conflict_changes_values, unsafe_duplicates_change_values. Deliberately hiding duplicate ancestry changes confidence, exposing the dependence assumption.
Shared conflicts and independent conflicts are handled separately, and retracting an evidence group removes it from provenance.
The injected conflict labels are controls rather than observed chess labels.

Before the first fit, retained dataset drafts were corrected for symmetric role grouping, trapping board-edge topology,
structural edit grammar, and withholding legal references on incomplete boards. All limited labels, final counts and split assignments
were retained. Training began only after the complete baseline receipt passed. No held-out failure triggered retraining.
The pawn fork family remains an explicit transfer failure. A development graph-node collision under duplicate queries with unequal
proof budgets was fixed without changing the trained checkpoint; the failed output and regression test are retained.

Evidence: [datasets/audit.json](../../artifacts/cycle12/datasets/audit.json), [learning/main/ledger.json.xz](../../artifacts/cycle12/learning/main/ledger.json.xz),
[learning/main/native-training.json.xz](../../artifacts/cycle12/learning/main/native-training.json.xz), [learning/dependence.json](../../artifacts/cycle12/learning/dependence.json),
[concepts/summary.json](../../artifacts/cycle12/concepts/summary.json), [retained/pre-graph-budget-fix](../../artifacts/cycle12/retained/pre-graph-budget-fix).
