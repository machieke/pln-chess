# Inference performance

The initial profile identified repeated immutable-state identities/FENs, square scans, dataclass copying and native-TV export. Cycle 9 removes that redundant host work. It changes no native formula, rule ordering, proof field or learned descriptor. [Pre-edit profile](../../artifacts/cycle9/performance/baseline-warm.txt), [optimized profile](../../artifacts/cycle9/performance/C9-optimized-profile.txt).

| Workload | Native cache mode | C8 p50 s | C9 p50 s | C9 p95 s | C9 p99 s | p50 reduction |
|---|---|---|---|---|---|---|
| single | reference | 2.009 | 1.866 | 1.892 | 1.892 | 7.1% |
| single | cold | 2.037 | 1.829 | 1.872 | 1.872 | 10.2% |
| single | warm | 0.402 | 0.235 | 0.244 | 0.244 | 41.5% |
| sparse | reference | 3.001 | 2.822 | 2.848 | 2.848 | 5.9% |
| sparse | cold | 1.829 | 1.627 | 1.691 | 1.691 | 11.1% |
| sparse | warm | 0.564 | 0.418 | 0.429 | 0.429 | 25.9% |
| full-214 | reference | 26.317 | 25.959 | 26.056 | 26.056 | 1.4% |
| full-214 | cold | 4.770 | 4.008 | 4.246 | 4.246 | 16.0% |
| full-214 | warm | 3.463 | 2.748 | 2.799 | 2.799 | 20.7% |
| promotion-heavy | reference | 2.853 | 2.643 | 2.815 | 2.815 | 7.3% |
| promotion-heavy | cold | 1.749 | 1.562 | 1.629 | 1.629 | 10.7% |
| promotion-heavy | warm | 0.522 | 0.366 | 0.375 | 0.375 | 29.8% |
| adversarial | reference | 7.683 | 7.384 | 7.462 | 7.462 | 3.9% |
| adversarial | cold | 3.387 | 3.090 | 3.210 | 3.210 | 8.8% |
| adversarial | warm | 1.380 | 1.045 | 1.089 | 1.089 | 24.3% |
| independent-game | reference | 23.344 | 22.612 | 22.969 | 22.969 | 3.1% |
| independent-game | cold | 6.005 | 5.244 | 5.444 | 5.444 | 12.7% |
| independent-game | warm | 3.838 | 3.108 | 3.132 | 3.132 | 19.0% |

Seven repetitions per arm and six workloads produce 252 samples. Reference means native-operator caching disabled; cold means a new native session; warm reuses that session. Immutable input objects and loaded checkpoints are prepared before inference timing, matching the original benchmark convention. Exact complete candidate payload digests match reference/cold/warm and the original/optimized implementations. Every warm sample has zero native invocations and every sample is untruncated. [Original samples](../../artifacts/cycle9/performance/C8-original.json), [optimized samples](../../artifacts/cycle9/performance/C9-optimized.json).

The original and optimized arms ran serially at different times on the same shared host, after other study workers stopped. They are matched fixtures, not a randomized alternating timing trial; unrelated host activity may contribute to timing differences. Cold refers to native-session caching, not a new operating-system process or an unloaded checkpoint.

Historical Cycle 7 full-position p50 targets are 4.038 seconds cold and 2.778 seconds warm; their provenance was verified through the protected Cycle 8 manifest. They are historical host-specific measurements, not same-session C7 samples. The matched C8/C9 table supplies the current direct comparison. Research-target flags use point estimates; no statistical test establishes superiority over historical C7 timing.

Checkpoint size is 2,905,103 bytes. The single checkpoint-load observations were 0.478 seconds before and 0.317 seconds after; they are not repeated timing estimates. Native calls, grounded atoms, hit rates and parent/child RSS are retained for every workload. Memory figures are separate cumulative high-water marks; they are not simultaneous total process-tree memory. p95/p99 are sample maxima and cannot establish reliable tail latency.

Inspector diagnostic decoration took a median 6.950 ms, with JSON serialization taking 2.710 ms in the single-candidate smoke workload. This adds zero native calls and preserves the input native result. Calibration is read and integrity-checked once per inspector response. [Presentation measurements](../../artifacts/cycle9/smoke/verified.json).
