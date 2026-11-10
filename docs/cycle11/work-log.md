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

## Evaluation orchestration prepared during baseline replay

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

## Contract tests and trace-storage preparation

Added executable specifications for native learned/empty field behavior,
typed domains, unknown observations, model/provenance edits, long-ray blockers,
special structural effects, cache mutation, disabled caches and zero budgets.
Separate claim tests cover ordering, duplication, missing events, conflicting
metadata, late contradictions and receipt/model/runtime tampering. API tests
require the accepted legal learner to remain independent of field imports.
These tests have passed syntax compilation; execution waits for the production
modules after the baseline receipt. They are not counted as passing tests yet.

The field ledger driver now stores an exact lossless XZ copy of its complete
JSONL evidence bytes and restores that copy before a resumed run. A post-freeze
audit will quantify raw relative-context versus pooled-key sharing. The
experimental legal regression panel was selected without model predictions:
128 C9 adversarial, 80 C9 special, 112 C10 synthetic and 28 applicable external
test positions. Every candidate in those 28 positions is scheduled under both
FEN-only and actual-history conditions. The full accepted-model regression
remains separate and exhaustive over its registered cohorts.

## Baseline completed and implementation opened

The unchanged-source receipt passed at `fe9e28edc03184fee02ec535399768fd9d5883fa`: 399 tests, 287 negative controls, 26 historical suites, 48 Cycle 9 and 132 Cycle 10 shards, all 180 exact native proof comparisons, and 4,586 protected historical files unchanged. Production implementation began only after this receipt. Final comparison hashes each already native-verified DAG node once and checks every ordered row reference; redundant sequential rehash attempts and their logs remain archived.

Before legal learning, structural replay exposed 20 color-reflected curriculum histories with an initial fullmove-counter mismatch. The original files and failed pre-training validation are retained under `development/pre-training-history-counter-fix/`. The correction changes only the mirrored initial counter. All positions, labels, splits and relative hypotheses remain fixed; all corrected histories now replay exactly. No native learning preceded the correction.

Implemented independent field ontology, model validation, native conditional inference, dependency-bound cache reuse, hypothetical successor comparison, robust claim transport, public API/CLI and browser inspector. Field model `d38e6c3c26e8d1f2e38a62d288394cb920038649041ec8d2cc5f9eb9d0a314f3` learned 1,764 conditionals from 18,003 training queries, with 23,590 logical native revision nodes. Pure arithmetic reuse executed 32 distinct operators; each revision and evidence dependency remains in its trace. The eight public interface tests and 55 initial field/temporal tests passed.

All 38 registered transformations, eight dedicated unseen-displacement transfers, 15 before/after examples, and five dependence checks passed. All 27 temporal controls passed; 12 supply eligible observations and 15 withhold them. Frozen field evaluation retains nine mobility false negatives. Post-freeze diagnosis identifies king-to-rook castling aliases accepted by the offline reference API but missed by the ordinary-mobility label adapter's two-cell castle exclusion. These errors, original labels and denominators are preserved; neither model nor thresholds are retuned. The native boundary audit passed after rewriting list concatenation in the conservative confidence selector to avoid the AST audit's arithmetic false positive; no numerical policy changed.

The first full implementation test run passed 462 tests. Browser preflight exercised all 15 examples, four families, native proof inspection, empty/incomplete controls, actual 7.6 MB export and mobile/desktop layouts. A detected mobile control-grid overflow was fixed and the rerun passed with zero console/server errors. The actual board and proof captures were visually inspected.

Final review found that the temporal selector unnecessarily capped explicitly supplied confidence above 0.99 at its empty-history default. Selection now uses the minimum supplied value, with 0.99 only when no value was supplied. The added regression passes. The pre-correction current/research replay drivers were stopped; their partial logs and outputs remain under `development/pre-confidence-default-correction/`. Final fresh-checkout verification restarts against the corrected source. Registered study claims are at or below 0.99, so their frozen results are unchanged.

Fresh research reproduction passed at production-source commit `6d7c37d2036a6602a1fe78bcb589b840c0f5b740`: regenerated datasets and all three experimental/empty model bytes match; all held-out field proof/metric rows, 38 transformations, eight transfer proofs, 15 worked native relation/difference sets and temporal summaries match. The separately completed unchanged-source baseline is reused by its exact receipt, not claimed as a second end-to-end run.

Legal completion produced both published EP recoveries and 76/76 exact independent controlled holdout move sets, recovering 16 previously unknown legal candidates without false-legal or false-illegal results. All 39 explicitly synthetic historical interventions became exact under supplied interventions; they remain separate from original FEN-only fixtures. EP geometry/destination/ray/boundary/temporal removals abstain; exposure removal still permits inherited operational support, and strict/experimental modes remain unknown. This limitation is retained in the legal report. Full experimental adversarial/applicability-panel regression and the unchanged-model mandatory replay remain separate gates.

The isolated experimental regression completed all 39 shards and 287 negative controls. FEN-only exact sets remain 112/128 C9 adversarial, 71/80 C9 special and 98/112 C10 synthetic, with no false-legal or false-illegal classifications. On the preselected 28-position external applicability panel, FEN-only exact sets are 12/28 and actual supplied-history exact sets are 28/28. The model remains unpromoted: this is a selected panel, not a fresh complete 1,020-position experimental evaluation. All 287 negative controls retain exact native parity and abstain on evidence removal.

An early current-source operational adversarial shard comparison matched all 1,198 candidate records and every ordered native DAG node against the unchanged-source baseline. This is a development integration check, not a substitute for the required final 180-shard comparison.
