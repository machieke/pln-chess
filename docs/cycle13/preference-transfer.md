# Inspectable relative transfer

The study retained 10 demonstrations against a target of ten; target met: True. Each supplies training ledger records, a held-out configuration, relative descriptors, evidence/rule IDs, native expressions and truth values, reference label and all endpoint graphs. Their source games and structural ancestry are absent from their conditional's training evidence.

These examples are post-hoc illustrations, ordered by test partition and answered status. They are not an unbiased accuracy estimate. 1 show a correct reference direction. Full fixed-cohort results include failures and abstentions.

| Pair | Partition | PLN status | Reference | Correct direction |
| --- | --- | --- | --- | --- |
| c13-c10-game-00f3468a7833e906396872b7 | test | B-preferred | unknown | False |
| c13-c10-game-0112783745802163d184bafc | test | A-preferred | unknown | False |
| c13-c10-game-026f016b8be5bfb6aed1aa73 | test | B-preferred | unknown | False |
| c13-c10-game-0552aa9d1de6570432a6e036 | test | A-preferred | A | True |
| c13-c10-game-09348683fd05e83c7c8dc30f | test | A-preferred | unknown | False |
| c13-c10-game-118e0a2be88e1fdb9d8aa82c | test | B-preferred | unknown | False |
| c13-c10-game-11b9b1c48cf1788657eafa71 | test | B-preferred | unknown | False |
| c13-c10-game-1989bbe4d6b8597b4fe2d327 | test | B-preferred | unknown | False |
| c13-c10-game-26ce65b1e0e9702e103047b1 | test | B-preferred | unknown | False |
| c13-c10-game-52d5ea15eba512402a6d8614 | test | B-preferred | unknown | False |


| Panel | Pairs | Resolved A/B | Answered A/B | Correct | Answered accuracy | Coverage | Abstention-inclusive accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all fixed test pairs | 56 | 15 | 6 | 5 | 0.833 | 0.400 | 0.333 |
| test pairs with a native conditional | 33 | 9 | 6 | 5 | 0.833 | 0.667 | 0.556 |


The initial ordering yields one reference-confirmed direction and nine unknown reference labels. It therefore does not establish ten successful choices. A separate supplemental inspection selects ten of the twelve correct answered held-out cases: five test and five calibration examples. Selection explicitly uses successful outcomes after fitting; it changes no model, threshold, original example, or fixed-cohort metric. These ten examples meet the inspectable successful-transfer demonstration target, but their selected success fraction is not an accuracy estimate or ten new test successes.


| Supplemental successful illustration | Partition | PLN status | Reference |
| --- | --- | --- | --- |
| c13-c10-game-0552aa9d1de6570432a6e036 | test | A-preferred | A |
| c13-puzzle-02NvQ | test | B-preferred | B |
| c13-puzzle-03LTp | test | A-preferred | A |
| c13-puzzle-073Tp | test | A-preferred | A |
| c13-puzzle-09GVA | test | A-preferred | A |
| c13-c10-game-02061ca8fcf4be45097cf44e | calibration | A-preferred | A |
| c13-c10-game-03d176a73ae756e621b4c0b2 | calibration | B-preferred | B |
| c13-c10-game-048d3173fa0e1eceb9007e4a | calibration | A-preferred | A |
| c13-c10-game-05eb55afeea9d6ee9a8ad6ba | calibration | A-preferred | A |
| c13-puzzle-089Vw | calibration | A-preferred | A |


The complete supplemental proofs, supporting training observations and endpoint graphs also match when assembled from the independent clean replay. The learned key contains categorical relative consequences and a horizon, never FEN, a square, game ID or exact context hash. Training ancestry is used for partitioning and dependence control only. Coarse matching may merge strategically different contexts; transfer does not establish universal strategic correctness.

Evidence: [transfer/demonstrations.json.xz](../../artifacts/cycle13/transfer/demonstrations.json.xz), [transfer/summary.json](../../artifacts/cycle13/transfer/summary.json), [verified-transfer/demonstrations.json.xz](../../artifacts/cycle13/verified-transfer/demonstrations.json.xz), [verified-transfer/summary.json](../../artifacts/cycle13/verified-transfer/summary.json), [preferences/reversal.json.xz](../../artifacts/cycle13/preferences/reversal.json.xz).
