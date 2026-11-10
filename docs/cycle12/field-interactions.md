# Relational field interactions

17 before/after demonstrations pass exact independent full recomputation of their successor fields and graphs.
The panel includes the ten requested interaction categories plus discovered defense, double-check resolution,
knight/rook and pawn/bishop discoveries. Each compressed package retains initial FEN, supplied edit, structural
successor, relative observations, endpoint native proofs, evidence IDs, unknown relations and offline references.

| Demonstration | Reference relations | Host comparisons | Partial candidates | Proof package |
|---|---|---|---|---|
| rook-obstruction | 1110 | 645 | 8 | [open](../../artifacts/cycle12/interactions/rook-obstruction.json.xz) |
| bishop-diagonal | 852 | 516 | 7 | [open](../../artifacts/cycle12/interactions/bishop-diagonal.json.xz) |
| knight-relocation | 606 | 385 | 3 | [open](../../artifacts/cycle12/interactions/knight-relocation.json.xz) |
| pinned-defender | 1124 | 645 | 16 | [open](../../artifacts/cycle12/interactions/pinned-defender.json.xz) |
| discovered-attack | 868 | 516 | 8 | [open](../../artifacts/cycle12/interactions/discovered-attack.json.xz) |
| king-exposure | 864 | 514 | 13 | [open](../../artifacts/cycle12/interactions/king-exposure.json.xz) |
| multiple-defenders | 1134 | 649 | 7 | [open](../../artifacts/cycle12/interactions/multiple-defenders.json.xz) |
| unknown-observation | 848 | 522 | 6 | [open](../../artifacts/cycle12/interactions/unknown-observation.json.xz) |
| promotion | 590 | 385 | 3 | [open](../../artifacts/cycle12/interactions/promotion.json.xz) |
| en-passant | 980 | 645 | 8 | [open](../../artifacts/cycle12/interactions/en-passant.json.xz) |
| rook-battery | 868 | 516 | 6 | [open](../../artifacts/cycle12/interactions/rook-battery.json.xz) |
| defended-minor | 868 | 516 | 5 | [open](../../artifacts/cycle12/interactions/defended-minor.json.xz) |
| double-check-resolution | 868 | 516 | 11 | [open](../../artifacts/cycle12/interactions/double-check-resolution.json.xz) |
| discovered-defense | 1134 | 649 | 10 | [open](../../artifacts/cycle12/interactions/discovered-defense.json.xz) |
| en-passant-exposure | 962 | 645 | 15 | [open](../../artifacts/cycle12/interactions/en-passant-exposure.json.xz) |
| knight-opens-rook-file | 868 | 516 | 8 | [open](../../artifacts/cycle12/interactions/knight-opens-rook-file.json.xz) |
| pawn-opens-bishop-attack | 1124 | 645 | 10 | [open](../../artifacts/cycle12/interactions/pawn-opens-bishop-attack.json.xz) |

| Panel | Field | Relations | Precision | Recall | F1 | Unknown | Incomplete | FP | FN | Conditional proofs |
|---|---|---|---|---|---|---|---|---|---|---|
| Interactions | attack | 9072 | 100.0000% | 99.4493% | 99.7239% | 371 | 0 | 0 | 0 | 8701 |
| Interactions | defense | 218 | 100.0000% | 100.0000% | 100.0000% | 14 | 0 | 0 | 0 | 204 |
| Interactions | king-exposure | 144 | 100.0000% | 100.0000% | 100.0000% | 63 | 0 | 0 | 0 | 81 |
| Interactions | mobility | 6234 | 100.0000% | 99.4104% | 99.7043% | 147 | 0 | 0 | 0 | 6087 |
| Sequence endpoints | attack | 28665 | 100.0000% | 100.0000% | 100.0000% | 827 | 0 | 0 | 0 | 27838 |
| Sequence endpoints | defense | 3712 | 100.0000% | 100.0000% | 100.0000% | 42 | 0 | 0 | 0 | 3670 |
| Sequence endpoints | king-exposure | 455 | 100.0000% | 100.0000% | 100.0000% | 88 | 0 | 0 | 0 | 367 |
| Sequence endpoints | mobility | 23342 | 100.0000% | 100.0000% | 100.0000% | 420 | 0 | 0 | 0 | 22922 |

| Panel | Field | False-positive rate | Supported false-negative rate | Positive misses incl. abstention | Abstention rate |
|---|---|---|---|---|---|
| Interactions | attack | 0.0000% | 0.0000% | 0.5507% | 4.0895% |
| Interactions | defense | 0.0000% | 0.0000% | 0.0000% | 6.4220% |
| Interactions | king-exposure | 0.0000% | 0.0000% | 0.0000% | 43.7500% |
| Interactions | mobility | 0.0000% | 0.0000% | 0.5896% | 2.3580% |
| Sequence endpoints | attack | 0.0000% | 0.0000% | 0.0000% | 2.8851% |
| Sequence endpoints | defense | 0.0000% | 0.0000% | 0.0000% | 1.1315% |
| Sequence endpoints | king-exposure | 0.0000% | 0.0000% | 0.0000% | 19.3407% |
| Sequence endpoints | mobility | 0.0000% | 0.0000% | 0.0000% | 1.7993% |

These are development demonstrations. The repeated endpoint records are neither independent holdouts nor tactical playing-strength tests.
Reference labels come only from evaluation. Attack, defense, ordinary geometric mobility and king-exposure have distinct local meanings;
supported mobility does not certify global move safety. Unknowns are retained in recall and coverage accounting.

All 38/38 field transformation/locality controls pass.
The host comparisons include 119 OpensAttack,
14 RemovesDefense,
2708 ChangesInfluence and
6584 PersistsAcrossMove records.
Those labels compare independently inferred endpoints and have no native change TV.
There is no scalar strategic score.

Evidence: [interactions/summary.json](../../artifacts/cycle12/interactions/summary.json), [interactions/transformations.json.xz](../../artifacts/cycle12/interactions/transformations.json.xz),
[incremental/parity.json](../../artifacts/cycle12/incremental/parity.json).
