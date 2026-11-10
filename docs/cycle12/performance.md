# Runtime, memory and cache comparisons

Six workloads run in 7 fresh worker processes each, sequentially after the native study workers stop.
Every field comparison first requires exact native proof, evidence and dependency graph parity.
The workloads cover rook obstruction, promotion, en passant, en-passant exposure, the 32-piece starting position and a 21-piece published middlegame.
The opening also measures a seven-state observed temporal replay with the frozen field model and no concept checkpoint.
Concept work separately measures eight explicit conditional queries from controlled fixtures.
Legal work separately times the old accepted and frozen candidate models over full FEN candidate sets.
An additional completeness audit checks all 42 workers. All seven timed temporal hashes match a fresh, complete
seven-state native replay performed after timing finishes; that extra replay is excluded from benchmark durations.

| Workload | Full successor median s | Dependency successor median s | Full / incremental |
|---|---|---|---|
| en-passant | 3.753 | 3.434 | 1.093× |
| en-passant-exposure | 3.758 | 3.838 | 0.979× |
| promotion | 2.816 | 2.687 | 1.048× |
| published-midgame | 19.690 | 15.159 | 1.299× |
| rook-obstruction | 4.572 | 4.261 | 1.073× |
| standard-opening | 31.582 | 26.788 | 1.179× |

| Workload | Condition | Median s | Empirical p95 s | Native operators median | Python peak MiB max |
|---|---|---|---|---|---|
| en-passant | dependency-parent-preparation | 5.386 | 5.539 | 74 | 50.62 |
| en-passant | eight-concept-conditional-queries | 2.514 | 2.565 | 32 | 7.38 |
| en-passant | full-cold | 4.247 | 4.334 | 74 | 44.13 |
| en-passant | full-warm-existing-cache | 3.505 | 3.605 | 0 | 37.06 |
| en-passant | legal-accepted-full-fen | 3.786 | 3.879 | 231 | 12.40 |
| en-passant | legal-candidate-full-fen | 4.199 | 4.250 | 231 | 12.52 |
| en-passant | successor-dependency-reuse | 3.434 | 3.550 | 0 | 33.31 |
| en-passant | successor-full-cold | 3.753 | 3.847 | 72 | 34.39 |
| en-passant-exposure | dependency-parent-preparation | 5.436 | 5.533 | 72 | 51.03 |
| en-passant-exposure | eight-concept-conditional-queries | 2.522 | 2.546 | 32 | 7.38 |
| en-passant-exposure | full-cold | 4.282 | 4.332 | 72 | 44.50 |
| en-passant-exposure | full-warm-existing-cache | 3.533 | 3.552 | 0 | 37.38 |
| en-passant-exposure | legal-accepted-full-fen | 2.699 | 2.745 | 231 | 8.42 |
| en-passant-exposure | legal-candidate-full-fen | 3.119 | 3.177 | 231 | 8.56 |
| en-passant-exposure | successor-dependency-reuse | 3.838 | 3.899 | 2 | 33.33 |
| en-passant-exposure | successor-full-cold | 3.758 | 3.772 | 74 | 34.43 |
| promotion | dependency-parent-preparation | 3.057 | 3.112 | 70 | 26.19 |
| promotion | eight-concept-conditional-queries | 2.418 | 2.438 | 32 | 7.31 |
| promotion | full-cold | 2.571 | 2.615 | 70 | 22.67 |
| promotion | full-warm-existing-cache | 1.897 | 1.932 | 0 | 18.98 |
| promotion | legal-accepted-full-fen | 2.820 | 2.835 | 150 | 9.08 |
| promotion | legal-candidate-full-fen | 2.881 | 2.921 | 150 | 9.12 |
| promotion | successor-dependency-reuse | 2.687 | 2.709 | 2 | 22.36 |
| promotion | successor-full-cold | 2.816 | 2.832 | 66 | 23.89 |
| published-midgame | dependency-parent-preparation | 22.941 | 23.528 | 80 | 240.82 |
| published-midgame | eight-concept-conditional-queries | 2.417 | 2.471 | 32 | 7.32 |
| published-midgame | full-cold | 19.219 | 19.650 | 80 | 210.07 |
| published-midgame | full-warm-existing-cache | 16.364 | 16.780 | 0 | 177.37 |
| published-midgame | legal-accepted-full-fen | 13.253 | 13.600 | 456 | 38.84 |
| published-midgame | legal-candidate-full-fen | 13.361 | 13.615 | 456 | 38.85 |
| published-midgame | successor-dependency-reuse | 15.159 | 15.618 | 0 | 182.63 |
| published-midgame | successor-full-cold | 19.690 | 20.268 | 80 | 209.89 |
| rook-obstruction | dependency-parent-preparation | 5.363 | 5.424 | 72 | 50.35 |
| rook-obstruction | eight-concept-conditional-queries | 2.528 | 2.552 | 32 | 7.38 |
| rook-obstruction | full-cold | 4.271 | 4.327 | 72 | 43.89 |
| rook-obstruction | full-warm-existing-cache | 3.489 | 3.503 | 0 | 36.83 |
| rook-obstruction | legal-accepted-full-fen | 4.000 | 4.018 | 225 | 13.08 |
| rook-obstruction | legal-candidate-full-fen | 3.760 | 3.813 | 225 | 13.07 |
| rook-obstruction | successor-dependency-reuse | 4.261 | 4.320 | 2 | 39.74 |
| rook-obstruction | successor-full-cold | 4.572 | 4.629 | 74 | 43.81 |
| standard-opening | dependency-parent-preparation | 37.059 | 37.390 | 74 | 390.17 |
| standard-opening | eight-concept-conditional-queries | 2.397 | 2.468 | 32 | 7.31 |
| standard-opening | full-cold | 30.861 | 31.053 | 74 | 340.86 |
| standard-opening | full-warm-existing-cache | 26.486 | 26.693 | 0 | 288.35 |
| standard-opening | legal-accepted-full-fen | 17.675 | 17.834 | 363 | 60.07 |
| standard-opening | legal-candidate-full-fen | 16.013 | 16.097 | 363 | 60.10 |
| standard-opening | seven-state-temporal-replay | 202.033 | 202.903 | 80 | 1131.51 |
| standard-opening | successor-dependency-reuse | 26.788 | 26.835 | 4 | 314.30 |
| standard-opening | successor-full-cold | 31.582 | 31.771 | 78 | 340.44 |

Maximum fresh-worker high-water RSS is 6222.61 MiB; the terminated-child high-water RSS statistic is
2051.22 MiB. These are separate process maxima, not total concurrent memory.
The retained raw key `max_native_child_peak_rss_kib` comes from `getrusage(RUSAGE_CHILDREN).ru_maxrss`: it covers all
terminated child commands and may include inherited memory around process launch. It is not an isolated native runtime working-set measurement.
Worker RSS includes retained comparison outputs. Per-condition Python peaks use tracemalloc, whose allocation tracking adds overhead.
Hardware: Intel(R) Xeon(R) W-2225 CPU @ 4.10GHz; 8 logical CPUs,
8 available in process affinity, cgroup CPU quota/period `None`;
MemTotal:       82091776 kB. Platform: Linux 5.4.0-216-generic.

Cold means a new inference/session cache, not flushed operating-system or filesystem caches. Warm means the existing Cycle 11 field cache.
Dependency parent preparation is timed separately; successor reuse excludes that preparation. Model/runtime loading is excluded.
Field observations, native inference, proof assembly, graph construction and internal identity/validation hashes are included;
additional parity digest calculation is outside the timed condition. Seven repetitions give weak tail resolution: p95 here is the
empirical maximum, not an estimated population tail. Cache/native call reductions are not automatically latency reductions.
Full worker records retain execution counters, reuse/schedule counts, proof hashes and memory scope.

Seven repetitions have weak tail resolution. Tracemalloc adds overhead; reported p95 is the empirical maximum. Legal accuracy is measured in separate complete replay cohorts. No strategic search or ranking is benchmarked.

Evidence: [performance/summary.json](../../artifacts/cycle12/performance/summary.json), [performance/semantic-verification.json](../../artifacts/cycle12/performance/semantic-verification.json),
[performance/workers](../../artifacts/cycle12/performance/workers), [performance/commands](../../artifacts/cycle12/performance/commands).
