# Performance, preservation and proof scope

A primary request runs two fresh native processes, one each for Clear and Attack.
Both receive raw observations and the whole registered rule set. The host never
injects one stage's derived answer as another stage's premise. Optional exposure
is outside this cycle's primary request and timing scope.

The [budget controls](../../artifacts/cycle17/controls/summary.json) retain all
registered tiers. Counts below are per stage; both stages have the same observed
selected/retained/remaining counts within each listed arm and tier.

| Arm | Tier: steps / tasks / beliefs | Selected / retained / remaining | Clear / Attack |
| --- | --- | ---: | --- |
| D-AB | Small: 24 / 64 / 128 | 24 / 42 / 18 | Unknown / unknown |
| S-AA | Small: 24 / 64 / 128 | 24 / 42 / 18 | Unknown / unknown |
| Recursive | Small: 24 / 64 / 128 | 24 / 40 / 16 | Unknown / unknown |
| D-AB | Medium: 64 / 128 / 256 | 49 / 49 / 0 | Positive / positive |
| S-AA | Medium: 64 / 128 / 256 | 47 / 47 / 0 | Positive / unknown |
| Recursive | Medium: 64 / 128 / 256 | 43 / 43 / 0 | Unknown / unknown |
| D-AB | Generous: 128 / 256 / 512 | 49 / 49 / 0 | Positive / positive |
| S-AA | Generous: 128 / 256 / 512 | 47 / 47 / 0 | Positive / unknown |
| Recursive | Generous: 128 / 256 / 512 | 43 / 43 / 0 | Unknown / unknown |

Small-budget missing answers have remaining tasks. Medium/generous shared-arm
failure retains a structurally corresponding pair with overlapping training
stamps; the separate native guard diagnostic rejects it. Queue exhaustion is
not a completeness proof. The 8/8 retention-pressure control selects eight
tasks, retains seven beliefs and returns unknown. An actual .001-second timeout
returns incomplete. A supplied-rule confidence .05 diagnostic returns support
below the unchanged .1 display threshold; this differs from missing support.
Actual Query API and reversed-input controls preserve the disjoint positive
attack. No general order-independence or scheduler-completeness claim follows.

Every retained native record includes the exact input program, initial facts and
rules, runtime/model identities, selected-task output, returned beliefs and
stamps, query channels, budgets, process exit and timing. The
[proof audit](../../artifacts/cycle17/supplement/proof-audit.json) verifies that
all output stamps originate in that execution's inputs. The
[witness index](../../artifacts/cycle17/witnesses/index.json) exposes decisive raw
programs and outputs in ordinary Git. A native-revalidated structural witness
is post-hoc analysis; the runtime exposes neither every attempted pair nor a
complete fired-rule tree. Diagnostic parent fields remain null when unobserved.

The unchanged Cycle 14 `ProofStore` stores complete JSON in a host content-addressed
graph. [Integrity checks](../../artifacts/cycle17/performance/proof-integrity.json)
compare exact complete expansion, import an archive into a fresh store, and
require changed history and changed knowledge to miss the answer cache. Cached
lookup and full reconstruction execute zero native processes. Host proof objects
are not persistent native beliefs. Exact reconstruction preserves the available
raw record; it does not invent a missing fired-rule tree.

The [benchmark driver](../../evaluation/cycle17_performance.py) runs ten repeats
for each of six native workloads and two cache workloads. The
[workload census](../../artifacts/cycle17/performance/workloads.json) derives small
measurement tables directly from the hash-bound retained samples. The
[execution receipt](../../artifacts/cycle17/benchmark-command.json) binds it to
the clean frozen source and starts it only after preservation and its process
observer finish. The machine can still have unrelated activity. Cold inference
means fresh native interpreters; operating-system file caches are not flushed.
Native wall time spans `infer()` including both stages and response construction,
while evidence serialization follows the timed request. A fast unknown answer
is not treated as a correctness-preserving speedup.

The [full preservation receipt](../../artifacts/cycle17/preservation/cycle17-verification.json)
is authoritative for 206 shards / 584,112 candidate rows, canonical native proof
comparison, 287 removal controls, 27 history controls, both en-passant recoveries
and 76 controlled legal holdouts. The complete frozen-source suite has 748 tests,
zero failures, zero errors and zero skips. Its [JUnit receipt](../../artifacts/cycle17/preservation/tests.xml)
records 2534.831 seconds. Initial interrupted attempts and same-source resumption
are disclosed in the [reproduction guide](reproduction.md); no partial run counts
as full preservation. The original unchanged driver's receipt is retained beside
the wrapper's explicitly Cycle 17 receipt.

[Historical integrity](../../artifacts/cycle17/historical-final.json) preserves
23,570 starting tracked files. The separate Cycle 14, 15 and 16 evidence manifests
verify 14,597, 1,960 and 3,798 files respectively; these are separate populations,
not counts to sum as unique files. Accepted checkpoint SHA-256 remains
`5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8`
and semantic identity remains
`a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`.
Operational source identity remains
`e88ff7969885be101af2ceedbbdf5d5499f4253b361a8cee18ff1814f055282c`.
PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1` and PeTTa
`ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f` retain their locked source hashes.

[Resource accounting](../../artifacts/cycle17/resource-census.json) deduplicates
retained research-process receipts and reads GNU-time output from the 209
completed preservation commands. It does not fully meter early interrupted work,
exploratory commands or the final parallel proof-comparison CPU. The separate
[process observer](../../artifacts/cycle17/preservation-resource-observation.json)
samples the main preservation process tree every two seconds and records observed
CPU and per-process high-water RSS lower bounds, including the comparison phase.
It starts during the resumed run and excludes the independent distant-tail worker
tree; that worker's completed command costs remain in the timed-job census.
The observer is not a certified simultaneous-memory maximum or complete cycle-wide
CPU measurement. Do not add overlapping CPU counters from the two receipts.

Registered ceilings are 10,000 research native processes, eight measured research
CPU-hours and 2 GiB research payload, separately from 24 measured completed-job
preservation CPU-hours and 8 GiB preservation payload. Pack and restored copies
are separate storage overhead. Closing receipts add small amounts after the
census; final manifest totals describe the sealed population. Reference-laboratory
cost is separate: zero native processes and approximately .000249 seconds inside
its `run()` function, excluding interpreter startup. These rational toy results
never enter native proofs, model parameters, classifications or production caches.

The [local manifest](../../publication/cycle17/manifest.json) and
[restoration receipt](../../artifacts/cycle17/restoration.json) bind all sealed
files and actual restore verification. Bulk packs remain local, with each pack
at most 512 MiB. The Git size gate separately inventories every newly reachable
blob across the entire Cycle 17 range, including superseded versions. Remote
publication does not include the bulk proof store or repeated historical exports.
