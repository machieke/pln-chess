# Latency, native work and cache equivalence

| Checkpoint | Fixture | Reference p50 s | Cold p50 s | Warm p50 s |
|---|---|---|---|---|
| C7-frozen | single-candidate | 0.987 | 0.960 | 0.161 |
| C7-frozen | full-214 | 25.680 | 4.038 | 2.778 |
| C7-frozen | promotion-heavy | 4.423 | 1.818 | 0.588 |
| C7-frozen | independent-game | 27.487 | 4.269 | 2.986 |
| C8-frozen | single-candidate | 1.047 | 0.977 | 0.214 |
| C8-frozen | full-214 | 26.185 | 4.636 | 3.300 |
| C8-frozen | promotion-heavy | 4.635 | 1.983 | 0.741 |
| C8-frozen | independent-game | 28.279 | 4.861 | 3.626 |
| C8-promotion-relative | single-candidate | 2.033 | 1.996 | 0.410 |
| C8-promotion-relative | full-214 | 26.418 | 4.672 | 3.334 |
| C8-promotion-relative | promotion-heavy | 4.671 | 2.097 | 0.821 |
| C8-promotion-relative | independent-game | 29.913 | 6.429 | 4.279 |
| C8-no-promotion-training | single-candidate | 1.098 | 1.076 | 0.272 |
| C8-no-promotion-training | full-214 | 26.327 | 4.744 | 3.345 |
| C8-no-promotion-training | promotion-heavy | 4.674 | 2.018 | 0.801 |
| C8-no-promotion-training | independent-game | 29.779 | 6.534 | 4.323 |

| Checkpoint | Fixture | Arm | p50 s | p95 s | p99 s | Native calls | Grounded atoms | Cache hits | Misses | Peak KiB | Checkpoint bytes | Truncation | Timeout |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C7-frozen | single-candidate | cold | 0.960 | 1.000 | 1.000 | 66 | 91 | 28 | 66 | 47916 | 1644785 | 0.0 | 0.0 |
| C7-frozen | single-candidate | reference | 0.987 | 1.035 | 1.035 | 94 | 91 | 0 | 94 | 47916 | 1644785 | 0.0 | 0.0 |
| C7-frozen | single-candidate | warm | 0.161 | 0.176 | 0.176 | 0 | 91 | 94 | 0 | 47916 | 1644785 | 0.0 | 0.0 |
| C7-frozen | full-214 | cold | 4.038 | 4.122 | 4.122 | 389 | 19309 | 16411 | 389 | 478268 | 1644785 | 0.0 | 0.0 |
| C7-frozen | full-214 | reference | 25.680 | 25.707 | 25.707 | 16800 | 19309 | 0 | 16800 | 478268 | 1644785 | 0.0 | 0.0 |
| C7-frozen | full-214 | warm | 2.778 | 2.901 | 2.901 | 0 | 19309 | 16800 | 0 | 478268 | 1644785 | 0.0 | 0.0 |
| C7-frozen | promotion-heavy | cold | 1.818 | 1.837 | 1.837 | 272 | 2723 | 1904 | 272 | 478268 | 1644785 | 0.0 | 0.0 |
| C7-frozen | promotion-heavy | reference | 4.423 | 4.573 | 4.573 | 2176 | 2723 | 0 | 2176 | 478268 | 1644785 | 0.0 | 0.0 |
| C7-frozen | promotion-heavy | warm | 0.588 | 0.599 | 0.599 | 0 | 2723 | 2176 | 0 | 478268 | 1644785 | 0.0 | 0.0 |
| C7-frozen | independent-game | cold | 4.269 | 4.468 | 4.468 | 413 | 20722 | 17624 | 413 | 541300 | 1644785 | 0.0 | 0.0 |
| C7-frozen | independent-game | reference | 27.487 | 27.594 | 27.594 | 18037 | 20722 | 0 | 18037 | 541300 | 1644785 | 0.0 | 0.0 |
| C7-frozen | independent-game | warm | 2.986 | 3.127 | 3.127 | 0 | 20722 | 18037 | 0 | 541300 | 1644785 | 0.0 | 0.0 |
| C8-frozen | single-candidate | cold | 0.977 | 1.037 | 1.037 | 66 | 91 | 28 | 66 | 51264 | 1724429 | 0.0 | 0.0 |
| C8-frozen | single-candidate | reference | 1.047 | 1.053 | 1.053 | 94 | 91 | 0 | 94 | 51264 | 1724429 | 0.0 | 0.0 |
| C8-frozen | single-candidate | warm | 0.214 | 0.221 | 0.221 | 0 | 91 | 94 | 0 | 51264 | 1724429 | 0.0 | 0.0 |
| C8-frozen | full-214 | cold | 4.636 | 4.744 | 4.744 | 389 | 19309 | 16411 | 389 | 480436 | 1724429 | 0.0 | 0.0 |
| C8-frozen | full-214 | reference | 26.185 | 26.420 | 26.420 | 16800 | 19309 | 0 | 16800 | 480436 | 1724429 | 0.0 | 0.0 |
| C8-frozen | full-214 | warm | 3.300 | 3.376 | 3.376 | 0 | 19309 | 16800 | 0 | 480436 | 1724429 | 0.0 | 0.0 |
| C8-frozen | promotion-heavy | cold | 1.983 | 2.017 | 2.017 | 272 | 2723 | 1904 | 272 | 480436 | 1724429 | 0.0 | 0.0 |
| C8-frozen | promotion-heavy | reference | 4.635 | 4.681 | 4.681 | 2176 | 2723 | 0 | 2176 | 480436 | 1724429 | 0.0 | 0.0 |
| C8-frozen | promotion-heavy | warm | 0.741 | 0.751 | 0.751 | 0 | 2723 | 2176 | 0 | 480436 | 1724429 | 0.0 | 0.0 |
| C8-frozen | independent-game | cold | 4.861 | 5.028 | 5.028 | 413 | 20722 | 17624 | 413 | 547172 | 1724429 | 0.0 | 0.0 |
| C8-frozen | independent-game | reference | 28.279 | 28.354 | 28.354 | 18037 | 20722 | 0 | 18037 | 547172 | 1724429 | 0.0 | 0.0 |
| C8-frozen | independent-game | warm | 3.626 | 3.712 | 3.712 | 0 | 20722 | 18037 | 0 | 547172 | 1724429 | 0.0 | 0.0 |
| C8-promotion-relative | single-candidate | cold | 1.996 | 2.086 | 2.086 | 138 | 188 | 56 | 138 | 58612 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | single-candidate | reference | 2.033 | 2.116 | 2.116 | 194 | 188 | 0 | 194 | 58612 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | single-candidate | warm | 0.410 | 0.419 | 0.419 | 0 | 188 | 194 | 0 | 58612 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | full-214 | cold | 4.672 | 4.830 | 4.830 | 389 | 19309 | 16411 | 389 | 483868 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | full-214 | reference | 26.418 | 26.641 | 26.641 | 16800 | 19309 | 0 | 16800 | 483868 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | full-214 | warm | 3.334 | 3.534 | 3.534 | 0 | 19309 | 16800 | 0 | 483868 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | promotion-heavy | cold | 2.097 | 2.129 | 2.129 | 272 | 2723 | 1904 | 272 | 483868 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | promotion-heavy | reference | 4.671 | 4.736 | 4.736 | 2176 | 2723 | 0 | 2176 | 483868 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | promotion-heavy | warm | 0.821 | 0.831 | 0.831 | 0 | 2723 | 2176 | 0 | 483868 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | independent-game | cold | 6.429 | 6.588 | 6.588 | 497 | 20844 | 17669 | 497 | 546464 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | independent-game | reference | 29.913 | 29.986 | 29.986 | 18166 | 20844 | 0 | 18166 | 546464 | 2905103 | 0.0 | 0.0 |
| C8-promotion-relative | independent-game | warm | 4.279 | 4.457 | 4.457 | 0 | 20844 | 18166 | 0 | 546464 | 2905103 | 0.0 | 0.0 |
| C8-no-promotion-training | single-candidate | cold | 1.076 | 1.121 | 1.121 | 66 | 91 | 28 | 66 | 57016 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | single-candidate | reference | 1.098 | 1.119 | 1.119 | 94 | 91 | 0 | 94 | 57016 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | single-candidate | warm | 0.272 | 0.295 | 0.295 | 0 | 91 | 94 | 0 | 57016 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | full-214 | cold | 4.744 | 4.793 | 4.793 | 389 | 19309 | 16411 | 389 | 483472 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | full-214 | reference | 26.327 | 26.471 | 26.471 | 16800 | 19309 | 0 | 16800 | 483472 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | full-214 | warm | 3.345 | 3.412 | 3.412 | 0 | 19309 | 16800 | 0 | 483472 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | promotion-heavy | cold | 2.018 | 2.076 | 2.076 | 272 | 2723 | 1904 | 272 | 483472 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | promotion-heavy | reference | 4.674 | 4.710 | 4.710 | 2176 | 2723 | 0 | 2176 | 483472 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | promotion-heavy | warm | 0.801 | 0.816 | 0.816 | 0 | 2723 | 2176 | 0 | 483472 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | independent-game | cold | 6.534 | 6.570 | 6.570 | 497 | 20844 | 17669 | 497 | 545612 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | independent-game | reference | 29.779 | 29.887 | 29.887 | 18166 | 20844 | 0 | 18166 | 545612 | 2723013 | 0.0 | 0.0 |
| C8-no-promotion-training | independent-game | warm | 4.323 | 4.509 | 4.509 | 0 | 20844 | 18166 | 0 | 545612 | 2723013 | 0.0 | 0.0 |

Each fixture has five serial reference/cold/warm triplets. Cold uses a fresh session; warm reuses only that triplet's cold session. Every triplet requires identical whole-candidate exports, including native STVs, evidence IDs and proofs, and zero warm native invocations. Different models have different semantics; cross-model timing differences are not described as cache-equivalent optimizations.

Reported quantiles use nearest rank. With five observations p95 and p99 equal the sample maximum; they do not estimate population tails reliably. Timings are measured after concurrent study workers end on this shared host. Peak RSS is the Python process's cumulative high-water mark, not per-call allocation; native interpreter child RSS is not included. Native/proof counts shown in the table are from the first repetition; every sample, serialized proof size, model size and proof digest is retained in [benchmarks/](../../artifacts/cycle8/benchmarks).
