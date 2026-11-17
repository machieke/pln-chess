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

The resource ceilings are 10,000 research native processes, eight research
CPU-hours and 2 GiB research payload, separately from 24 CPU-hours and 8 GiB
for preservation. [Resource accounting](../../artifacts/cycle16/resource-census.json)
deduplicates retained process receipts and states its limits; exploratory and
test processes are not silently counted as fully metered research records.
Source, compact examples and manifests stay in Git; bulk evidence stays external.
The [local manifest](../../publication/cycle16/manifest.json) and
[actual restoration receipt](../../artifacts/cycle16/restoration.json) bind the
pack contents and verify every restored file. Nothing is uploaded.
