# Performance, budgets and proofs

The [corrected benchmark](../../artifacts/cycle15/performance/summary.json)
passes all five workloads with ten repetitions each. The native workload is a
supplied-rule one-cell attack. Median and observed range are:

| Workload | Median | Observed range | Native inference per request |
| --- | --- | --- | --- |
| Cold, scoped, new states | 0.889 s | 0.877–1.040 s | One process |
| Cold, full scope, same new-state sequence | 1.087 s | 1.027–1.239 s | One process |
| Repeated native, materialized observations | 0.887 s | 0.878–1.136 s | One process |
| Stored-answer lookup | 0.187 ms | 0.165–0.290 ms | None |
| Complete proof reconstruction | 2.315 ms | 2.139–4.656 ms | None |

Stored-answer retrieval is not a native-inference speedup. The ten-repetition
samples are descriptive measurements of this workload, not a broad latency SLA.

The [benchmark driver](../../evaluation/cycle15_performance.py) separates ten
repetitions each of scoped cold inference on new states, full-scope cold inference
on the same state sequence, repeated native inference with already materialized
observations, stored-answer lookup, and complete proof reconstruction. The last
two execute no native inference. The workload is a supplied-rule one-cell attack;
it is not a claim about broad chess latency. Measurement begins after the full
preservation workload finishes.
The host is shared with unrelated processes. These are wall-clock samples after
this cycle's competing workload stops, not an unloaded-machine latency guarantee.

## Budget findings

Capabilities use 24 steps and 64/128 task/belief limits, operational consequences
64 and 128/256, and generous diagnostics 128 and 256/512. Native queue limits are
strict upper bounds, so actual retained capacity is one less than the parameter.
The one-cell operational case has no answer at 8 or 24 steps and has support at
64 and 128. A longer empty path still has no support with the generous settings.

Native confidence selection can change with input order at a tie. Increasing
steps can replace a positive stored belief by a higher-confidence revised mixed
belief: [the supplemental probe](../../artifacts/cycle15/supplement/nonmonotone-answer.json)
shows that more steps need not preserve the answer. Reversing inputs in the tested
generous one-cell case preserves its answer; that is not an order-independence
theorem. [A real timeout](../../artifacts/cycle15/supplement/timeout-control.json)
returns incomplete without fallback. No matching belief after a bounded run is
unknown, not a negative claim.

## Evidence and data access

The [proof audit](../../artifacts/cycle15/supplement/proof-audit.json) checks 360
native result records from the matched evaluation. Every selected/returned stamp
belongs to supplied evidence. Original programs and outputs remain unchanged.
An audit corrects the early syntactic statement counter for native variable
renaming; the final adapter counts absent input statements modulo that renaming.
No detailed fired-rule tree is fabricated or reconstructed.

| Arm | Persistent host knowledge | Per-request native materialization | Persistent native state |
| --- | --- | --- | --- |
| A | 1,764 frozen field conditionals and their provenance | Existing host-selected conditional's four operator calculations | None |
| B | The same frozen field model | One observed conditional context, two channel rules, native derivation | None |
| C | Eleven supplied templates | Connected observed facts plus all eleven templates as tasks and beliefs | None |
| D | Eleven templates; five learned TVs with training ancestry | Same connected construction, stable learned rule stamps | None |

The [measured access census](../../artifacts/cycle15/supplement/data-access-census.json)
checks all 120 development/test endpoints per arm against their hashed raw
records. A executes four operators per query. B starts with one fact and two
conditionals, selects six tasks and retains six beliefs. C/D each supply 16–34
facts and eleven rules: 27–45 initial tasks/beliefs, 41–64 selected tasks, 41–71
retained beliefs, and 11–26 derived statements after variable normalization.
Their final task queues contain zero to seven items, so not every primary run
exhausts its queue. Host-grounded schema instances are zero. B's explicit host
selection of an old conditional remains a separate baseline behavior.

Knowledge/schema parsing, board identity maps, geometric neighborhood selection,
receipt indexes and SQLite proof objects are host infrastructure. Exact native
queue sizes, selected tasks, retained statements, repeated selected terms, process
counts, wall time, peak RSS and output bytes are in each result. Complete native
schema-instance/fired-operator counts are not exposed by the pinned interpreter;
the adapter reports that limit rather than inferring a complete trace.

Cycle 14's unchanged `ProofStore` stores the exact result as a content-addressed
host DAG. A request identity binds state/history, query, model, runtime, budgets
and the native program. Changed history misses the cache. Full import/expansion
is checked for exact JSON equality and retains evidence occurrence order. These
objects are not native beliefs and the store is not a native knowledge graph.
The [integrity receipt](../../artifacts/cycle15/performance/proof-integrity.json)
records 172 host proof objects, one cached request, ten cache hits, the expected
changed-history miss, and zero native-resident atoms. Exact complete JSON
expansion and fresh archive import both pass.

The first benchmark attempt exposed a Python tuple/list comparison mismatch:
sentence dataclass metadata contains tuples, while the existing store reconstructs
JSON arrays. The [audit](../../artifacts/cycle15/supplement/proof-json-contract.json)
verified that the original stored document exactly matches its retained raw JSON,
including all evidence occurrences. Its 30 native records, database and failed
log are preserved. The corrected benchmark uses a separate `performance/verified`
generation, normalizes the complete document at the JSON storage boundary, and
checks both full expansion equality and canonical SHA-256 after fresh archive
import. Neither inference nor historical `ProofStore` code changed.

The research limits are 10,000 native processes, 8 CPU-hours and 2 GiB generated
research evidence; legal preservation has its separate 24 CPU-hour/8 GiB limit.
Generated payloads remain external. Git receives compact source, tests, summaries,
the checkpoint, manifests and representative proofs. The local-only pack tool
reuses the existing checksum/atomic installation primitive, validates paths and
members, and refuses differing evidence. No release or remote upload is created.

The [resource census](../../artifacts/cycle15/resource-census.json) identifies 832
distinct retained native execution records, including reproduction and both
benchmark generations. Their measured native CPU sum is 936.67 seconds and peak
per-process RSS is 63,204 KiB; one timeout lacks a completed CPU measurement.
The cold benchmark alone peaks at 48,312 KiB. Legacy field operators are counted
separately (504 in 126 retained query records). These are lower bounds from the
retained records, not complete accounting of exploratory commands or test runs.
The 209 timed preservation jobs use 38,905.8 CPU-seconds; that sum excludes final
proof-comparison CPU. Generated research groups occupy 76,823,057 bytes and
preservation groups 1,559,746,495 bytes before packing/restoration copies.

The final [manifest](../../publication/cycle15/manifest.json) contains 1,960 files
and 1,949 content-addressed objects in four packs, totaling 1,641,830,400 bytes
(about 1.53 GiB). Each pack is below 512 MiB. The
[restoration receipt](../../artifacts/cycle15/restoration.json) records an actual
complete restore into a new external directory, followed by file-by-file SHA-256
verification with zero missing or changed files. The 559,024-byte manifest enters
Git; the packs and restored payloads remain local external files.
