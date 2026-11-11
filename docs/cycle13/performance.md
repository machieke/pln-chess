# Complete-output performance and exact incremental parity

Four fixed workloads cover one pair, three separate pair requests, one supplied two-ply comparison and one supplied three-ply comparison. Each full/incremental arm runs five repetitions in fresh worker processes, with a cold and warm request per worker: 40 processes and 80 measured workload requests. Arm order alternates. Workloads were hash-selected without preference outcomes. Other Cycle 13 native jobs were stopped before the benchmark. The host remained shared with unrelated services and projects; its affinity and background load were recorded, and exclusive machine ownership is not claimed.

| Workload | Arm | Cache | Median s | Native ops | Processes | Atoms | Hits | Proof bytes | JSON MiB | Archive MiB | Parent MiB | Child MiB | Truncation | Timeouts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single | full | cold | 7.065 | 187 | 8 | 7839 | 4452 | 12389093 | 51.549 | 2.628 | 263.328 | 98.895 | 0.000 | 0 |
| single | full | warm | 4.154 | 0 | 0 | 7839 | 4621 | 12389093 | 51.549 | 2.628 | 285.145 | 98.895 | 0.000 | 0 |
| single | incremental | cold | 6.975 | 187 | 8 | 7839 | 3187 | 12389093 | 51.549 | 2.628 | 262.699 | 98.125 | 0.000 | 0 |
| single | incremental | warm | 3.954 | 0 | 0 | 7839 | 2609 | 12389093 | 51.549 | 2.628 | 280.254 | 98.125 | 0.000 | 0 |
| multiple | full | cold | 18.385 | 474 | 17 | 20735 | 11554 | 31819466 | 137.859 | 6.842 | 612.520 | 133.551 | 0.000 | 0 |
| multiple | full | warm | 13.410 | 205 | 4 | 20735 | 11793 | 31819466 | 137.859 | 6.842 | 682.250 | 612.520 | 0.000 | 0 |
| multiple | incremental | cold | 17.943 | 474 | 17 | 20735 | 7736 | 31819466 | 137.859 | 6.842 | 613.449 | 137.254 | 0.000 | 0 |
| multiple | incremental | warm | 13.286 | 205 | 4 | 20735 | 7004 | 31819466 | 137.859 | 6.842 | 681.773 | 613.449 | 0.000 | 0 |
| two-ply | full | cold | 13.498 | 449 | 15 | 13334 | 7683 | 21269564 | 139.111 | 7.127 | 595.812 | 151.500 | 0.000 | 0 |
| two-ply | full | warm | 10.555 | 261 | 6 | 13334 | 7830 | 21269564 | 139.111 | 7.127 | 653.324 | 595.812 | 0.000 | 0 |
| two-ply | incremental | cold | 13.440 | 449 | 15 | 13334 | 5550 | 21269564 | 139.111 | 7.127 | 595.496 | 150.797 | 0.000 | 0 |
| two-ply | incremental | warm | 10.327 | 261 | 6 | 13334 | 4863 | 21269564 | 139.111 | 7.127 | 648.684 | 595.496 | 0.000 | 0 |
| three-ply | full | cold | 18.892 | 609 | 21 | 18439 | 10595 | 29422008 | 174.090 | 8.885 | 734.930 | 187.648 | 0.000 | 0 |
| three-ply | full | warm | 15.206 | 418 | 10 | 18439 | 10729 | 29422008 | 174.090 | 8.885 | 816.949 | 734.930 | 0.000 | 0 |
| three-ply | incremental | cold | 18.476 | 609 | 21 | 18439 | 6851 | 29422008 | 174.090 | 8.885 | 733.684 | 186.355 | 0.000 | 0 |
| three-ply | incremental | warm | 14.568 | 418 | 10 | 18439 | 6261 | 29422008 | 174.090 | 8.885 | 806.699 | 733.684 | 0.000 | 0 |


All twenty runs per workload have exact semantic and native-proof parity. Full recomputation clears dependency-bound relation records before each state; incremental retains them. Both retain identical pure native math memoization. Query domains are rebuilt in both arms, preventing omitted or stale targets from becoming false evidence. The timing intervention therefore isolates dependency reuse under the same native formula cache.

The measured median timing differences are small. Native operator and interpreter-launch medians are identical between full and incremental arms for every workload/cache condition. Dependency reuse does not eliminate query-domain reconstruction or complete proof construction. These five-repetition measurements do not establish a broad or statistically significant speedup; export size and proof construction remain material costs.

Elapsed time covers the complete API return, excluding archive/JSON transport serialization, model loading and interpreter imports. Cold means empty inference caches in a fresh worker with its models already loaded. Native operator calls and interpreter process launches are distinct counts. The table's proof-byte counter summarizes native traces; per-run receipts also report the entire uncompressed JSON package and compressed archive sizes, including graphs and metadata. Peak parent and maximum-child RSS are reported separately, not added into an aggregate working set. Parent peaks include API construction, semantic validation and archive serialization; warm measurements retain the cold output/caches and previous peak. Repetitions measure runtime variation, not additional independent chess examples. Per-run timings, ranges, counters, errors and full proofs are retained.

The cumulative maximum-child counter covers process-launch effects as well as execution; it is not an isolated measurement of the native interpreter's working set. Several warm child maxima track the preceding parent peak, consistent with inherited memory during process creation. No interpreter-only memory claim is inferred from those values.

Evidence: [performance/summary.json](../../artifacts/cycle13/performance/summary.json), [performance/workloads.json](../../artifacts/cycle13/performance/workloads.json), [performance/isolation.json](../../artifacts/cycle13/performance/isolation.json).
