# Bounded response coverage

The registered response panel contains **180 conditional comparisons in 10 root groups**, with at most three supplied branches per candidate. Its labels comprise 106 directional, four nondirectional and 70 unknown observations. Twenty primary references are reused and 160 additional reference analyses are retained. The branch crossproducts are dependent, not 180 independent positions.

| Panel | All | Directional references | Answered | Correct | Wrong | Answered accuracy | Directional coverage | Unknown reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Supplied branch crossproducts | 180 | 106 | 8 | 6 | 2 | 75.0% | 7.5% | 70 |

Directional answers come from only **3 of the ten root groups**. The whole-root bootstrap accuracy interval is 0.0%–100.0% (974/1000 defined replicates); directional coverage is 0.0%–16.0% (1000/1000 defined replicates). The dependent crossproducts do not provide eight independent answered groups.

| Root | Directional references | Answered | Correct | Wrong | Incomplete | Expanded proof occurrences |
| --- | --- | --- | --- | --- | --- | --- |
| c14-c10-game-16804d0851a8e2ce425cdcb1 | 4 | 0 | 0 | 0 | 10 | 2968935 |
| c14-c10-game-45763b4652b0996455abc1a5 | 11 | 3 | 3 | 0 | 3 | 2233223 |
| c14-c10-game-7c369dafdf0ffb3f73ebe1d7 | 17 | 2 | 0 | 2 | 0 | 3011899 |
| c14-c10-game-be728bae43522537e089bbcf | 2 | 0 | 0 | 0 | 5 | 3595003 |
| c14-c10-game-e2109e55ab452a9611160c04 | 9 | 0 | 0 | 0 | 0 | 1954485 |
| c14-puzzle-03EWF | 9 | 0 | 0 | 0 | 6 | 1240944 |
| c14-puzzle-03qSg | 14 | 0 | 0 | 0 | 0 | 1611376 |
| c14-puzzle-07Vwb | 9 | 3 | 3 | 0 | 6 | 1445621 |
| c14-puzzle-08ct3 | 17 | 0 | 0 | 0 | 0 | 1223453 |
| c14-puzzle-0ANFN | 14 | 0 | 0 | 0 | 0 | 1202873 |

There are 0 panels with opposing supported branch-conditioned directions, 30 incomplete endpoint comparisons, 5 branch occurrences with unknown legality and 0 with supported illegality. Offline enumeration records 478 unexamined legal replies across the candidate roots. No exhaustive coverage or global robust preference is asserted. [Every result and archive](../../artifacts/cycle14/responses/) retains branch indices, ancestry, selection provenance and coverage.

Selection retains the registered teacher-assisted PV and adds up to two deterministic hash-sampled legal replies and actor continuations. It does not use PLN success. Teacher, sampled and controlled diagnostic branches are explicitly identified; a published game continuation is not inferred from a teacher PV. Supplied lines are hypothetical conditional evidence, never an optimal-response search.

The king-exposing candidate remains a diagnostic branch with separate legality status. Missing two/three-ply endpoints remain incomplete. A fourth response branch is rejected. A controlled native test produces opposing A/B answers on two supplied branches and verifies that both survive archive reconstruction while global preference and automatic selection remain absent. [Native branch test](../../tests/test_cycle14_branches.py) and [test receipt](../../artifacts/cycle14/branch-semantics-unit.txt) are disclosed unit evidence, not independent strategic successes.

Identical final board layouts reached through different supplied histories have distinct request identities. The inspector exposes branch coverage and before/after conditional outputs; no average, product or minimum of branch strengths is labeled a native robust conclusion.

The first dense archive attempt exceeded the interactive serialization limit and is retained. Offline export, import and full comparison use a separately registered ten-million object-occurrence limit; 4 panels exceed the default interactive limit of two million. The default interface still rejects those full exports explicitly. See [the storage policy](proof-storage.md); summaries and paginated graphs remain available, and no scientific predictions or cohort membership changed.
