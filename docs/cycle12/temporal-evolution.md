# Supplied sequences and deterministic field evolution

All 12 supplied sequences (50 moves, 62 states) pass deterministic
semantic replay and independent full-field/graph recomputation. The learner observes the sequences; it does not plan them.

| Sequence | Moves | States | Partial candidates | Replay | Artifact |
|---|---|---|---|---|---|
| developing-attack | 6 | 7 | 156 | exact | [open](../../artifacts/cycle12/temporal/developing-attack.json.xz) |
| discovered-attack-preparation | 4 | 5 | 32 | exact | [open](../../artifacts/cycle12/temporal/discovered-attack-preparation.json.xz) |
| defender-removal | 4 | 5 | 44 | exact | [open](../../artifacts/cycle12/temporal/defender-removal.json.xz) |
| pin-formation-release | 4 | 5 | 32 | exact | [open](../../artifacts/cycle12/temporal/pin-formation-release.json.xz) |
| knight-fork-creation | 4 | 5 | 32 | exact | [open](../../artifacts/cycle12/temporal/knight-fork-creation.json.xz) |
| pawn-fork-escape | 4 | 5 | 36 | exact | [open](../../artifacts/cycle12/temporal/pawn-fork-escape.json.xz) |
| mobility-restriction | 4 | 5 | 31 | exact | [open](../../artifacts/cycle12/temporal/mobility-restriction.json.xz) |
| promotion-threat | 4 | 5 | 15 | exact | [open](../../artifacts/cycle12/temporal/promotion-threat.json.xz) |
| king-exposure | 4 | 5 | 34 | exact | [open](../../artifacts/cycle12/temporal/king-exposure.json.xz) |
| discovered-defense | 4 | 5 | 42 | exact | [open](../../artifacts/cycle12/temporal/discovered-defense.json.xz) |
| en-passant-ray | 4 | 5 | 26 | exact | [open](../../artifacts/cycle12/temporal/en-passant-ray.json.xz) |
| captured-blocker-queen-ray | 4 | 5 | 54 | exact | [open](../../artifacts/cycle12/temporal/captured-blocker-queen-ray.json.xz) |

Every state retains stable piece identity within its observed segment, event/source lineage, model versions, native field proofs,
partial concept candidates and typed endpoint changes. Promotion changes piece kind; captures remove identities; en passant
tracks both the moved pawn and the removed pawn. The initial opening includes all 32 pieces.

Observed state changes, unchanged learned conditional beliefs, native query results and visual projections are distinct.
Creation/removal of a field-domain member is distinct from a positive/negative inference. Strengthening and weakening compare
raw endpoint native values; they are not evidence that the checkpoint learned during replay. Persistence is a host comparison with null TV.
Concept persistence tracks named roles and piece identities, without treating omitted bounded candidates as negative evidence.

Four controls pass: a missing move with an observed successor starts a new identity segment; a missing move without a successor
leaves the state unknown; a conflicting successor is retained as a conflict; zero observation confidence leaves all queried fields unknown.
No transition inference or field delta is asserted across a history gap. Structural replay does not certify legal historical play.

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

Endpoint precision/recall is against offline field references, not prediction of future events or strategic sequence quality.
The full field records, native expressions, event receipts and graphs match on repeat after excluding only execution/cache counters.
Native temporal theorems remain zero.

Evidence: [temporal/summary.json](../../artifacts/cycle12/temporal/summary.json), [temporal/controls](../../artifacts/cycle12/temporal/controls), [incremental/parity.json](../../artifacts/cycle12/incremental/parity.json).
