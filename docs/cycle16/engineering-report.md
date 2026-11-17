# Cycle 16 engineering report

Native PLN derives occupancy-constrained influence across two empty intervening
cells using the explicitly supplied finite conditional. The research decision
is **Outcome A: finite composition works; generic reuse remains blocked**.

All eight engineering packages are complete. Full preservation, benchmarks,
historical verification and actual evidence restoration pass. The
[package matrix](package-matrix.md) separates engineering completion from research
outcomes; the [acceptance receipt](../../artifacts/cycle16/acceptance.json) binds
the final reports and verification records to their exact hashes.

The starting commit is `e349c9c8c7c6506a367c28623e30373c59ffc59e`, from
`cycle15-native-consequences`. Work is isolated on
`cycle16-native-path-composition`, with experimental source frozen at
`86b7760d` (use the full identity in the
[source-provenance receipt](../../artifacts/cycle16/source-provenance.json)).
The main implementation, rules, corpus, training, evaluation, benchmarks and
tests remain byte-identical to that clean preservation checkout. Later commits
add audit helpers, compact evidence and reports. No remote write is authorized
or performed in this cycle.

| Claim | Result | Evidence |
| --- | --- | --- |
| A — Native applicability | Demonstrated: native rules bind unfamiliar entities and shared roles | [Baseline replay](../../artifacts/cycle16/baseline-replay/baseline-replay.json), [interventions](../../artifacts/cycle16/interventions/interventions.json) |
| B — Finite path composition | Demonstrated from two separate emptiness observations and a supplied two-cell ray conditional | [Minimal R/F/F-minus comparison](../../artifacts/cycle16/minimal/minimal.json), [occupancy panel](../../artifacts/cycle16/occupancy/occupancy.json) |
| C — Learned support | Native revision changes the new rule's TV and held-out support; source removal lowers confidence | [Learning and transfer](learning-and-transfer.md) |
| D — Generic reusable-rule reasoning | Not demonstrated: recursive rule reuse and shared learned ancestry remain blocked | [Counterexamples](reuse-counterexample.md) |

The original eleven rules, native adapter and runtime calculus are unchanged.
F adds exactly one coordinate-independent, declarative `clear-two` template.
Every inference loads the entire registered arm; no host path-length branch
selects a rule or supplies a clearance/attack answer. Exact rule identities and
training ancestry survive every use. No stamps are stripped, cloned or minted
per firing, and no native inference operator or evidence guard is modified.

The minimal F fixture returns Clear at confidence .92178405, Attack at
.866937899025, and correctly bound king exposure at .7911382323851379. R and
F-minus return unknown. Removing either emptiness premise, changing its state,
or changing the ray's shared roles removes sole support. The recursive premises
are available and structurally match, but overlap on `rule_extend-empty`.
The native guard rejects that pair. A separate direct-operator witness is never
counted as the experimental answer.

[All nine occupancy outcomes](finite-paths.md) hold for each of the three tested
slider configurations. Known obstruction supports NoAttack even if another
intervening cell is unknown. E/U, U/E and U/U remain ambiguous; all relevant
evaluation-only completions are retained. Clear and exposure are not inferred
negative from NoAttack. Scope is sliding influence, including friendly occupied
destinations, not legal capture, move legality, strategic preference or move choice.

The final held-out panel has 72 dependent endpoints from 24 source games.
F and L classify all 72 correctly, including 30 positives. R, F-minus, the
untrained prior and the shared learned chain classify 42 negatives and leave
30 positives unknown, with zero classified errors. The shared learned chain
does derive Clear on those positives; a native witness verifies that eleven
shared training-game stamps block a matched downstream attack composition.
All source-panel exposure queries remain unknown; controlled actor-king fixtures
provide the separate positive exposure evidence.

Source selection, occupancy variants and grouping were registered before fitting.
There are 12 training, six development and 24 test games. All 48 test query
identifiers and all 24 game ancestries are new, but endpoint locations and the
two coarse geometry strata overlap completely. The sample heavily reuses opening
configurations and includes 23 rook/one bishop test roots. Queen evidence is a
separate synthetic orthogonal panel. No independent geometry transfer, broad
accuracy estimate, negative-example learning or noisy-label robustness is claimed.

The native execution/proof boundary remains explicit: selected tasks, returned
beliefs and stamps are retained; a full fired-rule tree is not exposed.
Small-budget absence, low-confidence support, conflict, invalid query domains
and incomplete execution are distinct. [Performance and proofs](performance-and-proofs.md)
documents the budget ladder, exact stored-JSON reconstruction and separate
native-versus-cache measurements. [Reproduction](reproduction.md) provides the
actual CLI and full-preservation commands, with the interrupted attempt preserved.

The accepted Cycle 12 checkpoint and operational `src/` implementation remain
the baseline. The accepted checkpoint file SHA-256 is
`5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8`;
its semantic version is
`a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`.
The registered operational source hash is
`e88ff7969885be101af2ceedbbdf5d5499f4253b361a8cee18ff1814f055282c`.
PLN remains pinned to `4405956947c4b53c7ff01bd565aa3b114bc970a1` and PeTTa
to `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`.

The [complete preservation receipt](../../artifacts/cycle16/preservation/cycle16-verification.json)
confirms all 206 shards and 584,112 candidate rows, with exact native proof parity
and zero classification changes. All 732 tests pass with zero failures, errors or
skips; all 287 negative controls, 27 history controls, both known en-passant
recoveries and 76 controlled legal holdouts pass. This is the completed resumed
source-bound run; the interrupted attempt remains in the sealed evidence.
[Historical verification](../../artifacts/cycle16/historical-final.json) finds
no changes to 23,491 baseline tracked files, 14,597 Cycle 14 evidence files or
1,960 Cycle 15 evidence files. These are separate verification populations and
are not summed as distinct files.

The [ten-repeat measurements](performance-and-proofs.md) give median complete
three-stage request times of 3.059 seconds for supplied finite rules and 3.237
seconds for learned finite rules. The recursive two-cell arm takes 2.955 seconds
and remains unknown. Distractor-rich input takes 6.529 seconds and also remains
unknown at the fixed budget, with 20 tasks per stage still queued. Cached lookup
and full proof reconstruction take 0.267 ms and 4.899 ms respectively, with zero
native inference processes; neither is presented as fresh reasoning.

The provenance audit passes across 2,083 derivation records. Retained research
receipts account for 2,164 native processes and 3,287.62 CPU seconds; 209 completed
preservation jobs account for 40,481.19 CPU seconds. Interrupted/exploratory work
and final parallel proof-comparison CPU are not fully metered. The report keeps
the comparison's separately observed memory use distinct from native inference.

The [manifest](../../publication/cycle16/manifest.json) seals 3,798 files and
3,786 unique content objects: 1,916,394,776 payload bytes and 1,915,996,160 bytes
in four local packs, each below 512 MiB. [Actual restoration](../../artifacts/cycle16/restoration.json)
verifies every file with no missing or changed contents. Bulk data stays outside
Git at `/home/purplezky/cycle16-evidence-20261117`. Source, compact examples,
summaries and manifests are the Git delivery; no pack is uploaded.

[Clean reproduction](../../artifacts/cycle16/reproduction/verified.json) executes
minimal diagnostics, the R/F/F-minus CLI comparison and a native refit from a
fresh checkout, preserving learned parameters and ancestry exactly. It reuses
verified installed dependencies and does not claim a fresh installation or a
second complete research-corpus execution.

The next proposed experiment is a separately authorized study of shared model
uncertainty versus repeated observation evidence, starting from the retained
learned-chain, diamond, replay and cycle counterexamples. A bounded three-cell
template can be considered later; it would still not establish generic recursion.
