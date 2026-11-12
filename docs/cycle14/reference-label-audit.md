# Reference supervision and uncertainty

The new protocol resolves 28 of the 41 previously unresolved immediate test references: 10 become A and 18 become B; 13 remain unknown. Across all 50 previously unresolved temporal observations, 34 become directional, one becomes `no-demonstrated-preference`, and 15 remain unknown. These are operational revisions under a different search protocol, not corrections established against true chess value. The [complete census](../../artifacts/cycle14/reference-audit/resolution-census.json) retains each original evidence ID, superseding ID, reason, and raw archive hash.

| Registered panel | Comparisons | A | B | No demonstrated preference | Unknown |
|---|---:|---:|---:|---:|---:|
| Immediate, all partitions | 940 | 337 | 340 | 15 | 248 |
| New immediate final test | 200 | 71 | 74 | 3 | 52 |
| Temporal, all partitions and horizons | 480 | 136 | 145 | 10 | 189 |
| New two-ply final test | 50 | 16 | 17 | 0 | 17 |
| New three-ply final test | 50 | 13 | 15 | 0 | 22 |
| Bounded response crossproducts | 180 | 66 | 40 | 4 | 70 |

The two temporal test rows share the same 50 root groups. The response panel has only ten independent groups, with 20 reused primary references and 160 additional analyses. Repetition, horizons, branches, and repeated search budgets never increase the independent training count.

| Cause of remaining uncertainty | Immediate, all | Temporal, all | Former 41 immediate unknowns | Former 50 temporal unknowns |
|---|---:|---:|---:|---:|
| Overlapping or one-sided bounds | 125 | 27 | 3 | 6 |
| Budget disagreement | 92 | 14 | 7 | 6 |
| Insufficient margin | 30 | 12 | 2 | 3 |
| Mate-order ambiguity | 1 | 0 | 1 | 0 |
| Missing candidate analysis / unavailable endpoint | 0 | 136 | 0 | 0 |
| Total unknown | 248 | 189 | 13 | 15 |

The [adapter](../../training/cycle14_reference.py) reads raw UCI `info` records independently. Each record retains the candidate, score type, bound flag, MultiPV index, depth, nodes, PV, actor, side to move, and perspective normalization. A perspective reversal negates ordinary scores and reverses lower/upper bounds. Mate distances remain ordinal mate values; no arbitrary centipawn substitution is used. An unflagged search report is not a proven minimax value. Interrupted or missing analyses cannot become a stable reference direction.

The pinned Stockfish build, executable and neural-network identities, compiler inputs, options and reset policy are recorded in the [fresh baseline reference bootstrap](../../artifacts/cycle14/baseline/research/reference-bootstrap/verified.json) and raw analysis manifests. Every candidate search starts after `ucinewgame`, `Clear Hash`, and `isready`, using one thread and 32 MiB hash. The new method searches each candidate separately under a root restriction, whereas the historical adapter used MultiPV. It reconstructs and verifies supplied game history. The original decision-maker remains the actor at every observation horizon, including odd plies.

Two node budgets, 20,000 and 80,000 per candidate, establish an operational direction only when both support the same direction with the registered 80-centipawn margin or compatible ordinal mate ordering. Only unresolved comparisons escalate to 320,000 and 1,280,000 nodes. Stable unflagged differences within 20 centipawns produce `no-demonstrated-preference`; this does not prove equivalence. Offline interval comparisons are neither statistical confidence intervals nor universal bounds on chess value. No model prediction enters escalation or branch selection.

Source inspection and synthetic fixtures demonstrated that aggregating successive python-chess 1.11.2 information dictionaries can leave an earlier bound flag alongside a later unflagged score. However, raw replay of all 41 historical immediate unknown pairs observed **zero such stale-bound pairs**. This defect is therefore not established as the cause of their uncertainty. Applying the registered interval policy to those old-budget reruns resolves 24/41; the full new restricted-search generation resolves 28/41. Those are different experiments and must not be conflated. The [raw audit receipt](../../artifacts/cycle14/reference-audit/verified.json) and [parser tests](../../tests/test_cycle14_reference.py) preserve the distinction.

Immediate searches reported 1,406,629,085 nodes, temporal searches 557,575,602, and additional response searches 250,017,774: 2,214,222,461 reported nodes for the primary new generations. Verification reruns and the initial adapter audit are additional work, accounted separately in the resource ledger. Node counts are engine-reported executed work, not the sum of maximum reserved budgets.

The [immediate generation](../../artifacts/cycle14/labels/immediate-g1/index.json), [temporal generation](../../artifacts/cycle14/labels/temporal-g1/index.json), and [response generation](../../artifacts/cycle14/labels/responses-g1/index.json) preserve raw transcripts and content hashes. Semantic observation identities exclude only elapsed time, UCI time/nps fields, and raw wire hashes; score flags, nodes, depth, candidate identity and PV remain scientific evidence. Original Cycle 13 files remain immutable. Unknown supervision is excluded from directional revision rather than entered as false evidence.
