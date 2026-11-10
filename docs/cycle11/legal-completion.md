# Legal completion and limitations

The accepted C8 checkpoint remains unchanged. Its full native proof parity is verified before and after Cycle 11 source changes. The experimental local revision recovered 2 of the two known en-passant abstentions.

| Fixture / candidate | Before | After | Native local TV after | Without history |
|---|---|---|---|---|
| c10-position-00861 / d5e6 | unknown | supported-legal | `{'confidence': 0.8459328358208955, 'strength': 0.9956521739130435}` | unknown |
| c10-position-01151 / d5c6 | unknown | supported-legal | `{'confidence': 0.8459328358208955, 'strength': 0.9956521739130435}` | unknown |

Both original cases already had native temporal eligibility `(1, 0.99)`. In `c10-position-00861`, the inherited positive observation had confidence zero, leaving the local conditional at its neutral prior. `c10-position-01151` lacked the signed local en-passant conditional. Complete published games, prefixes, predecessor evidence and old proof graphs are retained in [legal/en-passant-before.json.xz](../../artifacts/cycle11/legal/en-passant-before.json.xz). The old heuristic history taxonomy is not used as the causal diagnosis.

The isolated checkpoint revises exact existing local keys with 96 new controlled training observations in six layout groups, preserving color-transform ancestry. It uses native revision, the original thresholds and the frozen native source. Its 76 independent holdouts include EP king-exposure and promotion controls. Castling pseudo-legality in the offline reference includes attack-path conditions; this can create disagreement under a local descriptor that omits those conditions. Such observations are retained and dependence conflicts are disclosed, rather than relabeled to force success. [Training evidence and revisions](../../artifacts/cycle11/legal/training.json.xz); [holdout proofs](../../artifacts/cycle11/legal/independent-holdouts.json.xz).

The unresolved inventory contains 5,462 unknown/incomplete candidate rows, including negative as well as positive reference labels, and 58,419 native proof nodes. It covers all registered C9 adversarial/special, C10 synthetic and C10 external FEN/history populations. [legal/unresolved-baseline.json.xz](../../artifacts/cycle11/legal/unresolved-baseline.json.xz).

| Experimental cohort | Positions | Exact sets | Recall | False legal / illegal | Incomplete |
|---|---:|---:|---:|---:|---:|
| c10-external-selected/fen | 28 | 12 | 98.421% | 0 / 0 | 0 |
| c10-external-selected/history | 28 | 28 | 100.000% | 0 / 0 | 0 |
| c10-synthetic/fen | 112 | 98 | 99.223% | 0 / 0 | 0 |
| c9-adversarial/fen | 128 | 112 | 99.233% | 0 / 0 | 0 |
| c9-special/fen | 80 | 71 | 99.254% | 0 / 0 | 0 |

The experimental external panel contains 28/1020 positions, selected before training by potential exact-key applicability. Every candidate in each selected position is reevaluated, both FEN-only and with its actual published prefix. This is not a fresh full-external evaluation of the experimental checkpoint. The unchanged accepted model receives the complete external regression. [Panel definition](../../artifacts/cycle11/datasets/legal-regression-panel.json).

Synthetic predecessor/rights interventions for old adversarial fixtures remain labeled interventions, not reconstructed original histories. Geometry, destination, ray, boundary, exposure and temporal removals preserve the before/after proofs for both EP cases. Strict and experimental legality modes retain their positive-composition restrictions. Removing new learning or historical evidence is recorded separately. [All intervention outcomes](../../artifacts/cycle11/legal/summary.json); [legal/historical-interventions.json.xz](../../artifacts/cycle11/legal/historical-interventions.json.xz).

The experimental checkpoint recovers 16 previously unknown legal candidates across the 76 holdouts, with 76/76 exact complete legal-move sets and 0 false-legal / 0 false-illegal classifications. These independent controlled holdouts differ from the two known published development failures. Removing temporal evidence leaves 0 supported special candidates across holdouts and historical interventions.

For both published EP cases, removing geometry, destination, ray, boundary or temporal premises yields unknown. Removing exposure still leaves operational support; strict and experimental modes remain unknown even with the full evidence. This reflects the inherited operational projection and its missing complete positive-composition theorem, not a native proof of universal safety.

No experimental checkpoint is promoted. Remaining abstentions and errors are research outcomes. These finite panels cannot establish universal legal accuracy or a complete native positive safety proof.
