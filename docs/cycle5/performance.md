# Matched performance

| Model / fixture | Candidates | Reference s / calls | Cold s / calls | Warm s / calls | Complete proof parity |
|---|---:|---:|---:|---:|---|
| C4 / game-0 | 214 | 23.792 / 16636 | 2.164 / 259 | 1.288 / 0 | True |
| C4 / c4-rook-two-blockers | 42 | 2.621 / 1546 | 0.961 / 150 | 0.148 / 0 | True |
| C4 / c4-independent-games-seed-426242-ply-24 | 226 | 24.017 / 16600 | 2.209 / 269 | 1.320 / 0 | True |
| C4 / c5-new-game | 218 | 23.420 / 16518 | 2.203 / 290 | 1.333 / 0 | True |
| C5 / game-0 | 214 | 25.157 / 16800 | 3.429 / 389 | 2.202 / 0 | True |
| C5 / c4-rook-two-blockers | 42 | 3.204 / 1642 | 1.568 / 244 | 0.290 / 0 | True |
| C5 / c4-independent-games-seed-426242-ply-24 | 226 | 25.199 / 16776 | 3.469 / 409 | 2.226 / 0 | True |
| C5 / c5-new-game | 218 | 24.776 / 16700 | 3.501 / 430 | 2.239 / 0 | True |

C4 checkpoint: 760,719 bytes; fresh-address-space peak: 215,356 KiB.


C5 checkpoint: 1,485,655 bytes; fresh-address-space peak: 277,924 KiB.


Full research parent peak: 3,770,104 KiB. Native subprocess-tree peak is not aggregated. Corpus timings are single measurements per mode/position; evaluation reports contain p50/p95 over positions, not repeated-run uncertainty.

C5 shares typed premise calculations within a position and exposes content-addressed DAG references. It still constructs the inherited C4 candidate proof occurrences. Cache scope includes runtime, model, ledger, position, policy, temporal receipt and suppressed families. Reference/cached comparisons require complete candidate, TV, classification, rule and evidence equality. Budgets count combined stages and estimated proof metadata; they are not OS memory caps. [Raw C5 benchmark](../../artifacts/cycle5/benchmarks/C5.json).

C5 is slower and uses more inference memory than C4 in this matched run. On the 214-candidate fixture, serialized complete candidate proofs grow from 61,658,061 to 86,910,124 bytes. Warm caching removes native calls but does not remove the inherited proof construction and serialization cost.
