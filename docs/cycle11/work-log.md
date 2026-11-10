# Cycle 11 work log

- Read the complete Cycle 11 brief and confirmed clean starting commit `fe9e28edc03184fee02ec535399768fd9d5883fa`; the brief was the sole untracked user input.
- Started a detached unchanged-source baseline in `/data/pln-chess-cycle11-baseline`. The first orchestration attempt incorrectly resolved the portable Cycle 10 manifest relative to the repository root. It stopped before any native replay; the original log is retained under `artifacts/cycle11/baseline/logs/attempt-1-manifest-path.txt`. The driver now uses the manifest's artifact-directory base.
- Registered the two-track study before production changes or new model experiments. Baseline execution uses the unchanged source, checkpoint, native runtime and thresholds. All new files so far are offline orchestration, registration and documentation.
- The unchanged starting checkout passed all 399 tests in 308.6 seconds and all 287 negative-evidence controls in 617.5 seconds. Historical and external native replays continue separately.
- Reconstructed both published en-passant games, their complete event sequences and supplied prefixes. The rightward conditional retained an inherited positive observation with confidence zero; the leftward exact conditional is absent. Both temporal eligibility channels are recognized at native strength 1/confidence 0.99. Archived and newly queried native classifications/values agree.
- Archived a complete 5,462-row unknown/incomplete inventory across the registered adversarial, special-move and external final cohorts, including unresolved negative candidates. Original full-position proofs and source artifact hashes are retained.
- Registered 96 new controlled special-move training rows and 76 holdout rows, 15 worked successor examples, 38 transformation/observation controls, eight dedicated long-range transfers and 27 temporal claim perturbations.
- Generated 45,424 field queries: 18,003 training, 11,864 calibration and 15,557 test. The first generated panel was archived before training because its external training queries included long sliding distances reserved for transfer. The corrected label-blind sampler filters those training displacements. No model was trained or evaluated on the superseded panel.
- The all-dihedral/translation audit found no train/calibration/test full-position, group or ancestry overlap; all eight dedicated transfer configurations and positions are absent from training. New controlled contexts and special-move training have no whole-position overlap with historical datasets. External panels deliberately reuse the original Cycle 10 game partitions.
- A worked-example generator initially used the reference library's legality-validating `push_uci` on an intentionally contradicted candidate. Its failed log is retained. It now uses structural `push` after separately recording the reference legal label; production legality behavior is unchanged.
- Offline native-training drivers are prepared with an explicit completed-baseline guard. No production source or original tests have changed and no new field or legal-completion model has been trained yet.
# Evaluation orchestration prepared during baseline replay

Prepared separate native field-learning, held-out relation evaluation,
transformation/removal, dependence, temporal-claim, legal-completion and
experimental legal-regression drivers. These require the unchanged-source
baseline receipt before inference experiments begin. The independent
regression driver replays every original accepted cohort in a fresh checkout.
Performance measurements run only after native regression workers finish and
compare exact full, warm and incremental proof identities. The browser driver
uses the ProofShot skill with an owned local server, screenshots, video,
desktop/mobile assertions and an actual exported proof payload.

No production source has changed at this stage. Experiment drivers and
assertions describe expected contracts; their existence does not establish
that the experiments have passed.
