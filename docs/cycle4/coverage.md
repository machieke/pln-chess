# Complete error and abstention coverage

The baseline case ledger contains 2588 unresolved/error cases, with full descriptors, evidence IDs, selected and losing hypotheses, and references to full native proof traces. Counts include every C3 unknown, incomplete, false legal and false negative on the declared regression and new holdout splits.

| Primary cause | Cases |
|---|---:|
| attacked-destination | 137 |
| blocker-composition | 502 |
| board-boundary | 1009 |
| castling-history-transit | 92 |
| double-check | 43 |
| en-passant-history | 2 |
| friendly-destination | 347 |
| geometry-abstraction-mismatch | 183 |
| pin-exposure | 245 |
| promotion | 28 |

The priority order is frequency first. Boundary and occupancy witnesses generalize broadly; attack chains address global illegality; pooled local projections address missing capture/context matches. Historical preconditions remain an explicit source of unresolved legal moves. Secondary tags are retained so mutually exclusive primary labels do not erase overlapping causes.

The dedicated 49-case Cycle 2 regression has transitions `{'supported -> unknown -> contradicted': 49}`. The complete C2 → C3 → C4 proofs are retained; all 49 were unknown in C3.

The older eight independent-game positions still have zero exact move sets. Improved recall does not erase that failure. Full C4 evaluation cases retain every remaining unknown and every observed error; regressions.json records any false legal case in the default configuration.

The separate [coverage regression ledger](../../artifacts/cycle4/coverage-regressions.json) records one oracle-legal move, `e1g1`, that C3 supported and C4 leaves unknown. Both retain the local TV `(0.9750000000000001, 0.4950000000000001)`; C4 additionally requires explicit scoped history instead of assuming FEN castling rights prove it. The affected position is `3qk2r/1bp1ppbp/2p3Nn/p1n1P3/P5p1/1P1P4/1R2BPPP/2B1K2R w K - 6 25`. This loss is included in the reported 37 missed legal moves on the new holdout.

The [in-board metrics](../../artifacts/cycle4/in-board-metrics.json) also score only candidates whose destination exists, so boundary rejections cannot conceal unresolved in-board moves. The primary reports retain the unchanged full candidate grammar for comparability.
