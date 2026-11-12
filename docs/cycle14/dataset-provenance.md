# Corpus, ancestry and partitions

The frozen corpus contains **940 root comparisons in 940 registered connected ancestry groups**, including all 340 historical pairs and 600 new pairs. There are 200 untouched new final-test groups. Pair construction and partitioning preceded reference scores and fitting. [Source records and provenance](../../artifacts/cycle14/datasets/source-pairs.json), the [partition manifest](../../artifacts/cycle14/datasets/partitions.json), and the [registered contract](research-registration.md) are the authoritative machine inputs.

| Partition | New | Historical retained | Total |
|---|---:|---:|---:|
| Training | 200 | 222 | 422 |
| Development / selection | 80 | 0 | 80 |
| Diagnostic calibration | 60 | 0 | 60 |
| Final test | 200 | 0 | 200 |
| Source holdout | 60 | 0 | 60 |
| Historical calibration diagnostic | 0 | 62 | 62 |
| Historical test diagnostic | 0 | 56 | 56 |

Historical calibration and test failures were already exposed during prior development; they are regression diagnostics, not new final evidence. No outcome-dependent filtering or quota refill follows reference labeling. The final immediate test has 145 directional references, three nondirectional references and 52 unknowns, all retained.

| New collection | Root groups | Source terms |
|---|---:|---|
| Lichess rated games, January 2013 | 140 | CC0-1.0 |
| Lichess broadcasts, January 2024 | 140 | CC-BY-SA-4.0, credited broadcasters retained |
| TCEC Season 26 Division P | 60 | Source-specific attribution and terms in manifest |
| Frozen Lichess puzzle prefix | 260 | CC0-1.0 |

The source manifest includes each original archive path, SHA-256, original acquisition-receipt hash, publisher, license, attribution, target quota and realized count. The combined derived corpus is marked CC-BY-SA-4.0. Existing locally frozen archives were reused; this cycle does not claim that repeated downloads establish new independent sources. Rated, broadcast and puzzle strata share Lichess distribution. TCEC is the separately held-out family; historical TCEC examples remain in the mixed-source primary training set, so only the dedicated model excluding **all** TCEC training records supports an unseen-source comparison.

Connected ancestry joins source-game identity, normalized game URL, exact unordered candidate pair and registered relative raw geometry. Lichess perspective suffixes, fragments and query strings do not create new games. A generic publisher URL is not treated as a game ID. One primary pair is retained per eligible source game, while descendants, reversed order, reflections, translations, branches, teachers and budgets inherit the same group. Audits found zero source-game overlap, zero registered cross-partition ancestry overlap and zero new/historical raw geometry overlap. This does not prove independence of openings, players or every semantic motif.

Preparation first exposed an overly broad generic-URL ancestry merge. That rejected 681-record preparation is retained under [rejected-source-generation-1](../../artifacts/cycle14/preparation/rejected-source-generation-1/). It was corrected and re-registered before labels or fitting; the original baseline-lock configuration is also retained. The accepted 940-record source hash is `12538b10281594d37fb7f52dbd0aa0822b7028a5a656c02bf066555450c5eabb`, and partition hash is `ec805fe298f2cb85fb3b5e5c219e230438d208076bc61a6a2c5f5fb3e72a9ec5`.

There are 312 new quiet pairs and 288 other pairs. Theme quotas cover attraction, clearance, defense, deflection, discovered attack, exposed king, fork, interference, pin, promotion, quiet moves and trapped pieces. A puzzle tagged “promotion” may concern a later move: **none of the 600 selected new candidate roots actually promotes**. The 16 historical promotion pairs remain, but new promotion transfer is an explicit coverage shortfall. Theme metadata is a selection stratum, not a prediction feature or proof that the complete strategic theme is present at the selected root.

The temporal study freezes 180 new roots and 60 historical roots, giving 240 roots and 480 endpoint comparisons. The same 50 new test groups appear at two and three plies. Teacher PV prefixes are selected at the registered budget, without reference to model correctness. Short one- or two-ply lines remain incomplete at longer horizons; no successful substitute is chosen. The [temporal plans](../../artifacts/cycle14/datasets/temporal-plans.json) preserve history, actor, branch selection and ancestry.

The [concept transfer panel](../../artifacts/cycle14/datasets/concept-holdout.json) contains 80 new source games and raw structural families, disjoint from preference games and historical concept motifs. Each of eight limited structural targets has six positive and four negative cases. Its 258 transformations and counterfactual controls are dependent descendants, not 258 extra independent cases. Eleven overlapping raw families were excluded before native fitting or evaluation.
