# Cycle 2 delivery verification

The complete `bash scripts/cycle2_reproduce.sh` command finished in a fresh temporary source copy with no Python environment, native runtime checkout, or generated outputs. All dependencies were installed and verified again. An empty memory-backed artifact directory and temporary directory avoided an earlier workspace disk-full failure; no preexisting model outputs were supplied. The frozen Cycle 1 input archive was restored by the reproduction script.

The run regenerated the masked curriculum, trained all models, scored every full candidate set, ran B0–B7 comparisons, calibration and uncertainty, verified full schedule parity, and passed **91 tests** in 64.13 seconds. All 51 code/config/lock files matched the checked source at collection. Subsequent reporting corrections fixed two test-evidence paths and completed B6 empirical-baseline diagnostics for self-check errors, exact move sets, per-piece/in-board results and uncertainty. The B6 scorer was executed again and all original classification metrics were asserted unchanged; [its verification receipt](../../artifacts/cycle2/B6-verification.json) and before/after source hashes distinguish this follow-up from the clean run. No native inference, learning, model, or B0–B5/B7 evaluation behavior changed.

- [Clean execution receipt](../../artifacts/cycle2/clean-build.json)
- [Complete bootstrap log](../../artifacts/cycle2/clean-bootstrap.log)
- [Tests](../../artifacts/cycle2/pytest.txt)
- [Preserved Cycle 1 evidence](../../artifacts/cycle2/cycle1-preservation.json)
- [Browser recordings and checks](ui-verification.md)
- [Measured final report](final-report.md)

The 61 Cycle 1 tests remain unchanged. Ninety-three original evidence, dataset and vendored-source files retain their exact original hashes. Earlier interrupted development attempts are explicitly recorded separately; final metrics and checkpoints come from the successful clean run.
