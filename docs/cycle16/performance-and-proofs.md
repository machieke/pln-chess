# Budgets, performance and proof scope

Each public request executes three fresh native derivations: Clear, Attack and
Exposure. Every stage receives the original observations and entire knowledge
arm. No returned Clear or Attack answer is injected by the host into another
stage. The benchmarks measure that complete three-stage request, rather than
calling one stage's latency the interface's total cost.

The [budget study](../../artifacts/cycle16/budgets/budgets-learning.json) uses
the registered tiers and unchanged strength/confidence display thresholds:

| Arm / tier | Steps / task limit / belief limit | Selected tasks per stage | Remaining tasks | Result |
| --- | --- | ---: | ---: | --- |
| R / small | 24 / 64 / 128 | 24 | 16 | All stages unknown |
| R / medium | 64 / 128 / 256 | 43 | 0 | All stages unknown |
| R / generous | 128 / 256 / 512 | 43 | 0 | All stages unknown |
| F / small | 24 / 64 / 128 | 24 | 18 | All stages unknown |
| F / medium | 64 / 128 / 256 | 49 | 0 | All stages positive |
| F / generous | 128 / 256 / 512 | 49 | 0 | Same positive TVs and stamps |

The native limiter retains strictly fewer than its size argument. A direct
two-item/limit-two audit retains one item, consistent with effective capacities
N−1. In [retention-pressure controls](../../artifacts/cycle16/supplement/bounded-controls.json),
the 8/8 queue setting loses 24 initial statements and returns unknown. That is
observed retention loss, not an invented per-item eviction trace. The Query API
also derives the finite attack. An actual .001-second timeout returns incomplete,
not a negative prediction. Queue exhaustion alone is not a completeness proof.

[Input reversal](../../artifacts/cycle16/interventions/interventions.json) leaves
the generous finite answer unchanged. Moving the .5-confidence emptiness
assumption from one cell to the other yields the same .43784742375 attack
confidence in these strength-one cases. This is a measured restricted symmetry,
not general conjunction equivalence or order independence. Reducing the finite
rule's confidence to .2 lowers attack confidence to .1825132419, still supported.
A separate [.05-rule-confidence control](../../artifacts/cycle16/supplement/below-threshold.json)
returns an actual attack statement at .045628310475, displayed as unknown below
the unchanged .1 threshold. Missing support and subthreshold support are distinct.

Every full record preserves its exact native program, initial facts/rules and
stamps, selected-task output, returned beliefs, positive/contrary channels,
runtime hashes, budgets, process exit, wall/CPU time and peak RSS. The
[provenance audit](../../artifacts/cycle16/supplement/proof-audit.json) checks that
every selected, retained, queued and answer stamp comes from that run's actual
inputs. A direct structural witness is labeled separately; no complete fired-
rule tree is reconstructed or claimed.

The unchanged Cycle 14 `ProofStore` retains full JSON documents in a host
content-addressed DAG. [Proof-integrity checks](../../artifacts/cycle16/performance/proof-integrity.json)
compare complete expansion with the original JSON, verify fresh archive import,
and require changed history and changed knowledge to miss the cache. Stored
answer lookup and full proof reconstruction execute zero native processes;
their timings are separate from fresh inference. Host proof objects are not
persistent native beliefs or a native knowledge graph.

The [benchmark driver](../../evaluation/cycle16_performance.py) measures ten
repetitions each of one-cell baseline, recursive two-cell, supplied finite,
learned finite, obstruction, unknown occupancy and distractor-rich input. Raw
samples retain classifications as well as time; a faster unknown result is not
treated as a correctness-preserving speedup. Benchmarking starts only after the
complete preservation run stops. The shared machine still has unrelated work,
so measured ranges are not an unloaded-host latency guarantee.
Cold inference here means fresh native processes; operating-system filesystem
caches are not cleared between repetitions.

The resource ceilings are 10,000 research native processes, eight research
CPU-hours and 2 GiB research payload, separately from 24 CPU-hours and 8 GiB
for preservation. [Resource accounting](../../artifacts/cycle16/resource-census.json)
deduplicates retained process receipts and states its limits; exploratory and
test processes are not silently counted as fully metered research records.
The final parallel legal-proof comparison is separate from those timed jobs.
A [live process observation](../../artifacts/cycle16/proof-comparison-resource-observation.json)
recorded a highest per-worker high-water RSS of 7.77 GiB partway through that
comparison. This is a lower bound on the final per-worker peak, not a measurement
of total simultaneous memory or a native request's memory cost. Its partial CPU
counters are retained without presenting them as complete phase accounting.
Source, compact examples and manifests stay in Git; bulk evidence stays external.
The [local manifest](../../publication/cycle16/manifest.json) and
[actual restoration receipt](../../artifacts/cycle16/restoration.json) bind the
pack contents and verify every restored file. Nothing is uploaded.

Measured ten-repeat results are retained in the [timing summary](../../artifacts/cycle16/performance/summary.json) and [workload census](../../artifacts/cycle16/performance/workloads.json). Every listed outcome occurred in all ten repetitions. Wall time spans `infer()`, including three native runs and response construction; saving evidence JSON follows the timed request.

| Workload | Median seconds | Range seconds | Observed outcome |
| --- | ---: | ---: | --- |
| One-cell baseline | 2.9150 | 2.6475–3.0221 | Clear / Attack / Exposure positive |
| Two-cell recursive | 2.9552 | 2.8103–3.3733 | All unknown |
| Two-cell finite | 3.0590 | 2.9537–3.3129 | Clear / Attack / Exposure positive |
| Two-cell learned | 3.2368 | 3.1054–3.4461 | Clear / Attack / Exposure positive |
| Known obstruction | 3.3828 | 3.1616–3.6801 | Attack negative; Clear / Exposure unknown |
| Unknown occupancy | 3.3450 | 3.0621–3.6473 | All unknown |
| Distractor-rich finite | 6.5289 | 6.3199–6.9000 | All unknown; 20 tasks remain per stage |

The scoped finite request completes 49 selected tasks per stage. The distractor-rich request reaches all 64 permitted steps and leaves 20 tasks per stage queued. Its unknown result is a bounded execution observation, not a repaired or disproved inference. No correctness-preserving speedup is claimed.

| Workload | Median native CPU seconds | Selected / retained beliefs across three stages | Highest native-process RSS (MiB) | Median full request JSON (KiB) |
| --- | ---: | ---: | ---: | ---: |
| One-cell baseline | 2.735 | 132 / 132 | 44.88 | 211.26 |
| Two-cell recursive | 2.785 | 129 / 129 | 39.64 | 200.73 |
| Two-cell finite | 2.900 | 147 / 147 | 43.02 | 228.99 |
| Two-cell learned | 3.025 | 147 / 147 | 43.30 | 271.83 |
| Known obstruction | 3.175 | 144 / 144 | 43.98 | 224.75 |
| Unknown occupancy | 3.165 | 132 / 132 | 43.09 | 207.41 |
| Distractor-rich finite | 6.345 | 192 / 252 | 89.93 | 373.73 |

Cached answer lookup has median 0.2668 ms (range 0.1667–0.7865 ms); full proof reconstruction has median 4.8992 ms (range 3.1643–15.3716 ms), ten repetitions each. Both execute zero native processes. The benchmark uses 210 fresh native processes. Its stored example has 196 host proof objects, zero persistent native atoms, exact complete-JSON roundtrip and fresh archive import, and both history/knowledge cache-miss controls pass.

Across retained research evidence, the census identifies 2,164 unique native process receipts, 3287.62 measured CPU seconds (0.913 hours), and 89.93 MiB highest native-process RSS. The one incomplete native receipt is the deliberate timeout control. The provenance audit checks 2,083 derivation records, 94,959 selected statements, 95,612 retained statements, 702 queued statements and 706 answer channels, with no unexplained stamps.

The 209 completed preservation jobs account for 40481.19 CPU seconds (11.245 hours); their highest per-job RSS is 5.462 GiB. These totals exclude fully accounting for the interrupted partial attempt, exploratory commands and final parallel proof-comparison CPU. They must not be presented as complete cycle-wide measurements. The separate live comparison observation above captures part of that omitted phase.

At census time, research payload is 344,863,015 bytes (328.89 MiB) and preservation payload is 1,571,503,578 bytes (1.464 GiB), below the registered storage ceilings. Final sealed totals also include the closing receipts; pack and restoration copies are separate transport/storage overhead.

Final sealing retains 3,798 files / 3,786 unique content objects, totaling 1,916,394,776 payload bytes (1.785 GiB). Four local packs occupy 1,915,996,160 bytes (1.784 GiB); every pack is below 512 MiB. All 3,798 files were actually restored to a separate directory and checksum-verified with no missing or changed contents. The source evidence, pack set and restored copy coexist outside Git. Final Git blob size is checked across every new local commit before delivery, separately from these external payload totals.
