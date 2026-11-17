# Cycle 15 engineering report

Cycle 15 demonstrates native reusable rule binding and a limited raw-observation
chess consequence. Its research decision is **Outcome 2: native binding works;
raw chess consequence remains partial**. All eight engineering packages are
delivered. [Local acceptance](../../artifacts/cycle15/acceptance.json), complete
legal preservation, benchmarks and actual evidence-pack restoration pass.

The starting publication commit is
`d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d`. Work is isolated on
`cycle15-native-consequences`; only local commits are authorized. The native
calculus, operational APIs, historical files and accepted Cycle 12 en-passant
checkpoint remain unchanged. The operational source hash is
`e88ff7969885be101af2ceedbbdf5d5499f4253b361a8cee18ff1814f055282c`.
No remote write, deployment or autonomous move selection occurs.
Final rehashing confirms that all
[23,391 protected historical files](../../artifacts/cycle15/historical-files-final.json)
and all [14,597 Cycle 14 evidence files](../../artifacts/cycle15/historical-cycle14-final.json)
are unchanged. The accepted default checkpoint still has SHA-256
`5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8`.

The [eight-package matrix](package-matrix.md) separates engineering completion
from research success. [Registration](research-registration.md) defines the
study; [native capabilities](native-capabilities.md) documents the exact API and
runtime; [relative knowledge](relative-knowledge.md) explains the typed contract;
[blocker consequences](blocker-consequences.md) distinguishes the two stages.

| Outcome | Finding |
| --- | --- |
| Native execution | An absent conclusion and a multi-rule chain derive through `PLN.Derive`; rule and premise removal retract sole support |
| Relational binding | Native variables bind unfamiliar entities and preserve repeated/shared roles; no host grounding is used |
| Evidence learning | Native revision updates five supplied templates; replay is idempotent; parameter effects transfer to held-out typed combinations, with limited independence |
| Chess consequence | One intervening cell supports positive attack/exposure; occupied rays support negative attack; longer empty paths abstain |

The [41 native probes](../../artifacts/cycle15/capabilities/matrix.json) also expose
shared-stamp diamond/recursion failures, missing marginal behavior, strict queue
bounds, tie order sensitivity and unsupported variable queries. These limitations
are retained as counterexamples. No direct truth-function fallback is used for
experimental inference. Native truth-value calls are separately labeled training
or frozen-baseline audit operations.

The controlled corpus has 24 training, 12 development and 48 held-out registered
typed families. Final evaluation has 96 dependent before/after endpoints. Connected arms
C/D classify 52 correctly, make zero classified errors and abstain on 44. Positive
recall including abstention is 8.33%, negative coverage 100%, and total native
schema transfer coverage 54.17%. The four positive final cases are one bishop
and three queen configurations; positive rook evidence is pilot/development
evidence, not an extra independent final-test success. Role/ownership contrasts
are dependent diagnostics, not a separate population-level transfer estimate.

The post-hoc [partition audit](../../artifacts/cycle15/supplement/partition-audit.json)
collapses those 48 typed test families to 44 geometry groups, only 37 wholly
unseen in training/development. All four positive final cases share coarser
geometry with a different training kind. The strictly unseen subset has 41
correct negatives and 41 unknown positives. The stronger independent-geometry
transfer target is not met; primary predictions and splits are not changed.

Frozen baseline A and the same conditional knowledge through derivation B answer
all 96 final endpoints correctly; they agree across all 120 development/test
endpoints. There is no new accuracy advantage. The separate equal-count challenge
has identical aggregate counts over all 315 attack-field queries per position—26
supported, 284 contradicted, five unknown—while the specified connected attack
changes. The old field still retains individual query rows; this challenge
isolates what aggregate counts discard. [Learning/transfer](learning-and-transfer.md) retains all counts and
uncertainty limits.

Stage A's imported-attack exposure chain succeeds only with the tested matching
king/owner/state roles. Stage B derives the attack and exposure from lower-level
observations for the one-cell case. The host endpoint comparison is not a native
“attack created” theorem. Missing support, conflicting channels and incomplete
execution remain distinct. Proofs retain exact programs, selected tasks, returned
beliefs/stamps and process receipts, without inventing a fired-rule tree.

All admitted template-conditioned training outcomes are positive in this designed
corpus. Revision/transfer is demonstrated; noisy-label robustness, calibrated
probabilities and learned rule structure are not. Replayed observations reject
48 duplicate admissions. Removing one ancestry lowers the relevant prediction
confidence from 0.806561 to 0.790101. Four final-test one-cell cases change from
unknown under the prior to supported under the learned parameters.

The complete source-bound suite at `4ee2ca4` passes 698 tests. Final isolated
research tests pass 35 and local transport tests pass three; these overlap with
the earlier suite and are not added together as independent tests. The final
research changes tighten admission, correct telemetry and classify malformed
native truth values as incomplete; operational `src/`
remains byte-identical. All 287 negative and 27 history controls pass. Complete
legal replay covers **584,112 candidates across 206 shards**, with zero
classification changes and exact canonical native-proof parity. Both en-passant
recoveries and all 76 controlled legal holdouts pass. The clean source checkout,
accepted checkpoint hash and complete comparison hash are recorded in the
[preservation receipt](../../artifacts/cycle15/preservation/verified.json).

[Source provenance](../../artifacts/cycle15/delivery-source.json) records the
implementation hashes and separates the full preservation checkout from the
later supplemental-test source. Subsequent audit/report commits do not change
inference inputs or the accepted operational implementation. The 698-test suite
includes historical field, concept and preference tests; it is not a fresh replay
of every historical research campaign.
The [benchmark source addendum](../../artifacts/cycle15/benchmark-source-addendum.json)
records the later correction from Python container equality to the existing
store's exact JSON contract. The failed attempt and its complete matching JSON
payload remain inspectable; the corrected benchmark runs in a new generation.

The final [performance/proof report](performance-and-proofs.md) separates native
inference, stored answer lookup and proof reconstruction. [Reproduction](reproduction.md)
contains working CLI, study and restoration commands. Fresh source reproduction
passes all 41 capability outcomes, exact learned parameters/ancestry and the
blocker CLI. It reuses verified dependencies and does not claim another full
held-out evaluation or dependency installation.

The final [local manifest](../../publication/cycle15/manifest.json) covers 1,960
files and 1,949 unique objects in four external packs totaling 1,641,830,400 bytes.
An [actual complete restoration](../../artifacts/cycle15/restoration.json)
verifies every file with no missing or changed content. Git contains the compact
manifest and reports, not these packs. The benchmark reports median scoped/full
cold inference of 0.889/1.087 seconds, stored-answer retrieval of 0.187 ms and
complete proof reconstruction of 2.315 ms; retrieval performs no native inference.

The [architecture decision](architecture-decision.md) recommends a focused
two-intermediate-cell evidence-reuse experiment before another consequence family
or preference campaign. No new native operator or evidence-policy change is
authorized by this delivery.
