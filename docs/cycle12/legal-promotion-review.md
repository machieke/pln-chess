# En-passant promotion review

Promoted the unchanged Cycle 11 special-local legal checkpoint. The decision follows the complete population review, not selection by an en-passant descriptor.
The candidate is `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`; the selected default is `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`.
Field and concept checkpoints are excluded from the legal default allowlist.

| Cohort | Old exact sets | Candidate exact sets | Old recall | Candidate recall | False legal | False illegal | Self-check FP |
|---|---|---|---|---|---|---|---|
| External FEN-only | 793/1020 | 793/1020 | 99.2645% | 99.2645% | 0 | 0 | 0 |
| External history-assisted | 1018/1020 | 1020/1020 | 99.9939% | 100.0000% | 0 | 0 | 0 |
| C9 adversarial | 112/128 | 112/128 | 99.2333% | 99.2333% | 0 | 0 | 0 |
| C9 special moves | 71/80 | 71/80 | 99.2537% | 99.2537% | 0 | 0 | 0 |
| C10 synthetic adversarial | 98/112 | 98/112 | 99.2227% | 99.2227% | 0 | 0 | 0 |

| Candidate cohort | Precision | Recall | F1 | Abstention | Incomplete | Positive misses incl. abstention |
|---|---|---|---|---|---|---|
| External FEN-only | 100.0000% | 99.2645% | 99.6309% | 1.5841% | 0 | 240 |
| External history-assisted | 100.0000% | 100.0000% | 100.0000% | 1.4451% | 0 | 0 |
| C9 adversarial | 100.0000% | 99.2333% | 99.6152% | 1.6533% | 0 | 16 |
| C9 special moves | 100.0000% | 99.2537% | 99.6255% | 1.8125% | 0 | 9 |
| C10 synthetic adversarial | 100.0000% | 99.2227% | 99.6098% | 1.6680% | 0 | 14 |

| Candidate cohort | False-positive rate | Supported false-negative rate | Positive miss rate incl. abstention |
|---|---|---|---|
| External FEN-only | 0.0000% | 0.0000% | 0.7355% |
| External history-assisted | 0.0000% | 0.0000% | 0.0000% |
| C9 adversarial | 0.0000% | 0.0000% | 0.7667% |
| C9 special moves | 0.0000% | 0.0000% | 0.7463% |
| C10 synthetic adversarial | 0.0000% | 0.0000% | 0.7773% |

False-positive rates use all reference-negative candidates; supported false-negative rates count false-illegal
answers over all reference-positive candidates. Positive miss rates additionally count unknown/incomplete positives.
All 206 review jobs cover 26 historical suites, 48 Cycle 9 shards and 132 Cycle 10 shards, including every
one of the 1,020 external test positions in both operational FEN-only and history-assisted conditions.
The summary records 584,112 candidate rows (overlapping cohorts/modes are not independent samples),
2 changed classifications and 0 losses of previously supported classifications.
Every row's native proof DAG was rehashed; model changes legitimately change proof identities.
The unchanged old checkpoint has a separate exact native-proof parity replay against the fresh starting baseline.

The two known development recoveries, 76 independent controlled legal holdouts, 39 reused historical interventions,
all 27 history controls and all 287 negative/evidence-removal controls were rerun.
Order changes and duplicate deliveries preserve semantic history, native TVs and native proof IDs while retaining separate delivery audits.
Conflicts, missing claims, wrong model/runtime bindings and tampered receipts remain explicit.

Removing geometry, destination, ray, boundary or temporal evidence retracts the recovered en-passant prediction to unknown.
Removing exposure evidence still leaves the operational special-local conclusion supported. This inherited limitation is retained
and is not presented as a complete safety proof. Strict and experimental modes remain unknown on both recovered cases.
The model was frozen before Cycle 12; no new legal training or held-out tuning occurred.

The existing explicit-checkpoint API remains available. The CLI's verified default changes only when the Cycle 12
receipt matches production source, runtime, registrations and the legal allowlist. Older explicit output-root overrides
retain their existing selection behavior. Strategic code is blocked during the tested legal inference path.

Evidence: [legal/promotion-decision.json](../../artifacts/cycle12/legal/promotion-decision.json), [legal/cohort-comparison.json](../../artifacts/cycle12/legal/cohort-comparison.json),
[legal/recovery/verified.json](../../artifacts/cycle12/legal/recovery/verified.json), [legal/temporal/summary.json](../../artifacts/cycle12/legal/temporal/summary.json),
[legal/negative-controls/verified.json](../../artifacts/cycle12/legal/negative-controls/verified.json), [current/proof-parity.json](../../artifacts/cycle12/current/proof-parity.json).
