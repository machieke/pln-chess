# Verified Cycle 4 baseline

Starting HEAD: `38cd26b97c3cf2ffe33eac526006c9820f8c3f82`. Initial branch was master; the only user addition was the Cycle 4 brief. Native lock verification ran before evaluation. The baseline receipt records actual status, hashes, runtime, platform and invocation.

All five Cycle 3 datasets reproduced exact candidate classifications, native TVs and proof hashes. The original 214-candidate reference/cold/warm candidates also matched in full. The original 141 tests remain part of the expanded suite.

| Baseline mode | Seconds | Native calls |
|---|---:|---:|
| cold | 2.049 | 179 |
| reference | 24.651 | 17318 |
| warm | 1.634 | 0 |

317 pre-existing artifact, fixture, vendor, configuration and lock files were verified unchanged. Source/API extensions are mapped in architecture.md.

Frozen C2/C3 tests are retrospective regressions; they were not added to training. The independent C4 game seeds, sample plies, thresholds and induction task are registered in configs/cycle4.json. Translation controls intentionally share training lineage. The dataset records the full game trajectories and all split identities.

Exact startup and clean reproduction commands are retained in the baseline and clean-build receipts. Reproduce with `TMPDIR=/dev/shm bash scripts/cycle4_reproduce.sh`. Use `C4_OUT=/path/to/fresh/output` to isolate new output.
