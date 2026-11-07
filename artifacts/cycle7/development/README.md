# Development evidence (noncanonical)

These are actual intermediate runs retained for audit. The canonical clean-copy outputs are in the parent directory. Development results do not authorize the default.

- `logs/test-cycle7.txt` records the initial incorrect typed-inheritance expectation; the pinned native wrapper returned empty. The corrected suite passed, followed by all 317 development tests.
- `logs/pilot.txt` records all learning budgets, including an incomplete full-budget candidate at the 20,000-node production cap. The offline registration was raised to 100,000 nodes; production is unchanged. `development/evaluation-budget-check.json` records completion at 20,186 nodes.
- `development/first-backoff/` preserves the earlier backoff experiment before frozen-first selection prevented coarse evidence from displacing supported classifications.
- `development/temporal-source-validation-failure.txt` records a rejected missing-source input. The corrected temporal harness retains explicit invalid-input tests.
- `native/` and `native-final/` are preliminary inventories; the canonical native laboratory contains the final exact source metadata, native scheduler controls, and standalone witnesses.
- `proofshot-development/` records the first browser launcher timeout. The isolated `pln-chess-cycle7` session in `proofshot-development-verified/` completed with no captured console or server errors. The early `strict.png` still shows the previous operational result; `strict-verified.png` records the actual strict response. Later accepted-default browser verification is separate.
- `benchmarks/C6-before-cache.json` was measured under concurrent development load; do not infer a statistical speedup from it.

A manual budget check initially failed with `OSError: [Errno 28] No space left on device` when using the full root-volume temporary directory. Repeating with `TMPDIR=/dev/shm` succeeded. The reproducibility script already uses that location and `/data` outputs. One attempted reproduction launch preceded completion of the local clone and reported `scripts/cycle7_reproduce.sh: No such file or directory`; no bootstrap began until the clone completed.

The pre-change 33-evaluation baseline is preserved under `../preflight/`; its source hashes precede Cycle 7 semantic integration. Old Cycle 6 artifacts remain unchanged.

ProofShot produced its report but left its owned browser, recorder, and server processes alive. They were stopped explicitly after bundling; no unrelated browser session was stopped. The captured WebM was checked with ffprobe.

The supplementary reproduction check initially required raw compressed-byte equality for training examples. The XZ encodings differ, but decoded bytes are identical; `../reproducibility-parity.json` records both facts.
