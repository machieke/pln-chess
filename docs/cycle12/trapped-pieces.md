# Restricted and uncertain mobility

The `NoOrdinaryGeometricExit` target classifies six held-out controlled records correctly: three positive and three negative.
The board-edge topology is included in the raw family audit. This target concerns the supplied ordinary movement fan,
not strategically favorable moves or global king safety.

Three additional valid-board diagnostics separate geometric and legal evidence:

| Case | No-ordinary-exit conditional | Reference legal exits | Supported legal exits | Unknown candidate moves |
|---|---|---|---|---|
| no-ordinary-exit | supported | [] | [] | [] |
| escape-opened | contradicted | ['a8b6'] | ['a8b6'] | [] |
| unknown-exit-cell | unknown | None | [] | ['a8(-1,5)', 'a8(-1,9)', 'a8b6', 'a8(1,9)', 'a8(-2,6)', 'a8(-2,8)', 'a8c7', 'a8(2,8)'] |

The knight on a8 has its ordinary exits obstructed in the positive case; opening b6 produces a separately supported legal exit.
With b6 unknown, the conditional abstains and legal candidates remain unknown. Unknown mobility is never converted to zero mobility.
The unknown list retains the legal learner's seeded proposals, including off-board coordinate proposals; it is not a list of established exits.
Legal exits come from the unchanged operational learner; evaluation-only reference exits are stored separately and are null for
unknown observations or deliberately incomplete local boards.

Attack/exposure field components and supported legal exits retain their own proof scope. Exit desirability, material cost and
the absence of every safe strategic alternative are unassessed. Complete strategic trapping proofs remain zero.

Evidence: [concepts/trapping-diagnostics.json.xz](../../artifacts/cycle12/concepts/trapping-diagnostics.json.xz), [concepts/partial-semantics-summary.json](../../artifacts/cycle12/concepts/partial-semantics-summary.json).
