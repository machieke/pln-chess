Cycle 8 development evidence, before the canonical clean study.

The baseline/ directory was completed against c6ee658 in an immutable checkout
before production edits. implementation-start.json records that sequencing.
Training model versions and the generated dataset are independently reproduced
by the clean study and bound by configs/cycle8-replay.json. Pilot raw controls
and test logs are retained; they do not replace the canonical acceptance matrix.

pilot-tests.txt: 26 passed, one zero-budget failure.
pilot-budget-retest.txt: the corrected budget regression passed.
pilot-tests-corrected.txt: all 28 focused tests passed.
pilot-benchmark-cli.txt: explicit benchmark mode routing passed after review.
composition-initial-signature-probe/: original unevaluated negation signature,
followed by the corrected native probe in the canonical composition results.

UI-pilot: the initial browser session and documented ProofShot output-config
issue. Final UI verification is independent and includes the actual accepted
checkpoint after acceptance.
