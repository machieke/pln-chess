# Performance and proof provenance

| Wrapper | Candidates | Reference s / calls | Cold s / calls | Warm s / calls | Peak KiB |
|---|---:|---:|---:|---:|---:|
| C6 | 214 | 26.087 / 16800 | 3.738 / 389 | 2.477 / 0 | 260320 |
| C6 | 226 | 29.020 / 18915 | 4.013 / 398 | 2.689 / 0 | 281940 |
| C6 | 226 | 25.059 / 16041 | 3.785 / 403 | 2.399 / 0 | 281940 |
| C7 | 214 | 25.832 / 16800 | 3.814 / 389 | 2.444 / 0 | 262120 |
| C7 | 226 | 29.168 / 18915 | 4.071 / 398 | 2.722 / 0 | 283712 |
| C7 | 226 | 24.984 / 16041 | 3.970 / 403 | 2.529 / 0 | 283712 |

The scheduler now computes its unchanged runtime-version digest once per batch rather than once per node. The initial 214-candidate profile recorded 16,800 repeated version-digest calls. No native expression, TV, rule ID, evidence ID or proof node was changed by this optimization. The benchmark verifies whole-candidate equality between reference, cold and warm runs. Frozen evaluation proof IDs also match C6.

The initial development timing ran alongside other experiments; final C6/C7 timing processes run serially after evaluation workers finish. These are single-host measurements, not statistically established speedups. Checkpoints, RSS, native calls, scheduled calls, cache hits, duplicate proof occurrences, serialized API bytes and interned DAG bytes are recorded in `artifacts/cycle7/benchmarks/`. Export interning is not claimed to reduce live Python proof memory.

Peak RSS is the Linux process high-water mark, cumulative within each wrapper benchmark process; it is not a separate allocation measurement for each arm. Grounding still repeats relative descriptors across layers, and native proof metadata repeats across candidate exports. Those costs are measured rather than removed through a change to proof identity. Backoff itself is a semantic second-pass experiment and is not covered by the cache-equivalent optimization claim.
