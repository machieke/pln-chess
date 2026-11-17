# Matched training design

The [frozen registration](research-registration.md) and
[source manifest](../../artifacts/cycle17/corpus-registration.json) contain 54
distinct new source games, excluding all 42 registered Cycle 16 games. Group A
and group B each contain twelve natural rook positions whose two intervening
cells are observed empty. Six further games form development and 24 form test.
Every descendant remains grouped with its actual game. No renamed game,
transformed copy or checkpoint hash is substituted for source ancestry.

Selection scans the already licensed TCEC season 26 division P PGN in source
order, with deterministic preferences for phase (plies 12–39, 40–79, 80 onward)
and rook direction (+x, +y, -x, -y). Ten roots use the registered fallback when
the preferred combination is unavailable. Training selection checks the supplied
antecedent's natural empty cells. Development/test selection does not use attack
labels or occupancy outcomes. All twelve phase/direction combinations occur
across the full registration. A and B each contain four roots per phase; B has
three in every direction, while A has direction counts 4/3/3/2. The
[group audit](../../artifacts/cycle17/training-audit.json) records these differences,
repeated opening codes and actual native stamp intersections. Final novelty
counts are in the evaluation receipt. “New” means new to the registered Cycle
16/17 panels, not a new collection or a guarantee against all earlier project exposure.

For each training root, the preparation ledger retains nine occupancy conditions
for each of the two target conditionals. The admitted EE row uses the *natural
original position*. The other eight are explicitly dependent synthetic exclusion
controls. Only the two natural, antecedent-satisfying rows per root are eligible.
Thus there are 432 preparation records: 48 eligible records and 384 excluded
conditional rows. Conditional admission is exact; a blocked path does not refute
an implication that assumes emptiness. Unknown observations do not become negatives.

The terminal antecedent is established during evidence preparation by rook kind,
the observed two-cell geometry and evaluation-only clearance/influence checks.
Those checks are not inference facts. Held-out native requests contain raw
piece-relative observations and the whole registered rule set, with no injected
Clear, Attack or reference label. Tests disable the evaluation oracle during
native inference.

Native revision starts at `(stv .5 0)` and consumes one `(stv 1 .5)` observation
per admitted source and rule. All admitted outcomes are positive. The observation
confidence .5 is a supplied trust assumption, not a learned or calibrated value.
The exact source/rule deduplication ledger rejects repeated delivery. Structures
come from the unchanged twelve-rule finite knowledge file; no structure discovery
is claimed. No model's parameters are manually overwritten to force equality.

| Arm | Clearance sources | Rook terminal sources | Samples per rule | Unique games across pair | Shared games |
| --- | --- | --- | --- | ---: | ---: |
| S-AA | A | A | 12 / 12 | 12 | 12 |
| S-BB | B | B | 12 / 12 | 12 | 12 |
| D-AB | A | B | 12 / 12 | 24 | 0 |
| D-BA | B | A | 12 / 12 | 24 | 0 |
| Overlap 1 | A | A[:1] + B[:11] | 12 / 12 | 23 | 1 |
| Overlap 6 | A | A[:6] + B[:6] | 12 / 12 | 18 | 6 |

All twelve targeted rule parameters in these six arms have strength 1 and
confidence **.923076923076923**, obtained by actual native revision. The overlap
sweep reuses D-AB for zero and S-AA for full overlap; it changes actual admitted
sets, not stamp strings. [Parameter and membership comparisons](../../artifacts/cycle17/learning/summary.json)
and complete small learning ledgers/revision receipts are committed.

The successful minimal D-AB/D-BA Attack ancestry uses exactly `clear-two` and
`rook-attack`, plus one ray, two emptiness occurrences and a piece-kind occurrence.
Both rule parameters are learned; their structures, raw-observation confidence
.99, geometry encoding and admission conventions are supplied. The full arm also
loads the unchanged auxiliary templates. In particular, negative obstruction
support uses supplied `obstruction` confidence .95. Success therefore does not
mean every template or trust assumption was learned.

Anchors preserve supplied F, learned-clearance with a supplied terminal, both
untrained priors, each one-rule-prior replacement, the original Cycle 16 shared
checkpoint, and rule removals. The actual remove-A refit starts from the prior
and admits no clearance observations while still fitting the B terminal.
The leave-one-A refit admits eleven clearance roots and twelve terminal roots.
Replay performs native fitting again, then rejects duplicate ancestry deliveries;
parameters, declarations and ancestry agree exactly with the unreplayed D-AB model.

Different game ancestry is recorded provenance separation. It does not eliminate
shared engines, openings, collection or publisher, and it does not establish
statistical independence. All-positive admission cannot test negative-example
learning or noisy-label robustness. Bishop and queen tests are secondary synthetic
capability controls with supplied terminals; the learned pair study is rook-only.
