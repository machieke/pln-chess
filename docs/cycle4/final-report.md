# Cycle 4 final engineering report

Starting HEAD `38cd26b97c3cf2ffe33eac526006c9820f8c3f82`. Full clean build source HEAD `373b9da9fc757b93b36aa1a7537a6728b386e218`. Final source HEAD `47ccd08f4ac916492b842c9b151c617fb832b619` adds only a diagnostic interpretation/assertion correction, verified by rerunning the native audit and its targeted test. Production source is identical to the full clean build. Final delivery commit is the local commit containing this report; nothing was pushed. [Verification details](verification.md) state the exact scope.

Native unary constraint chains resolve supported-illegal conclusions without treating local movement support as a global safety theorem. Pooled local observations transfer beyond capture-piece identity and unnecessary context. General conjunction remains unavailable; positive conclusions remain native-partial.

| Model / split | Precision | Recall | F1 | Abstention | Exact sets | False legal | False illegal | Self-check FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C3 / frozen-heldout-transfer | 100.00% | 95.53% | 97.72% | 18.14% | 67.50% | 0 | 0 | 0 |
| C3 / frozen-adversarial | 100.00% | 97.36% | 98.66% | 28.23% | 75.00% | 0 | 0 | 0 |
| C3 / cycle3-independent-games | 100.00% | 88.64% | 93.98% | 29.82% | 0.00% | 0 | 0 | 0 |
| C3 / cycle4-independent-games | 100.00% | 92.24% | 95.96% | 25.05% | 29.17% | 0 | 0 | 0 |
| C4-full / frozen-heldout-transfer | 100.00% | 97.77% | 98.87% | 3.15% | 75.00% | 0 | 0 | 0 |
| C4-full / frozen-adversarial | 100.00% | 99.12% | 99.56% | 2.32% | 91.67% | 0 | 0 | 0 |
| C4-full / cycle3-independent-games | 100.00% | 95.24% | 97.56% | 3.89% | 0.00% | 0 | 0 | 0 |
| C4-full / cycle4-independent-games | 100.00% | 95.37% | 97.63% | 3.27% | 41.67% | 0 | 0 | 0 |

## Before/after proof cases

| Family / candidate | Before | After | Native final TV | Resolved |
|---|---|---|---|---|
| attacked-destination / heldout-transfer-ray-0 g3f4 | unknown | contradicted | {'confidence': 0.6596954320891415, 'strength': 0.010526982630077453} | True |
| castling-history-transit / heldout-transfer-ray-1 e3c3 | unknown | contradicted | {'confidence': 0.6596954320891415, 'strength': 0.010526982630077453} | True |
| geometry-abstraction-mismatch / heldout-transfer-ray-3 a6a1 | unknown | supported | {'confidence': 0.7392857142857144, 'strength': 0.9913793103448276} | True |
| board-boundary / heldout-transfer-ray-3 a6(0,-1) | unknown | contradicted | {'confidence': 0.9097761277262921, 'strength': 0.002186085559935824} | True |
| blocker-composition / heldout-transfer-ray-5 c2h7 | unknown | contradicted | {'confidence': 0.6508810656055903, 'strength': 0.01153814935064923} | True |
| pin-exposure / heldout-transfer-ray-9 a5a6 | unknown | contradicted | {'confidence': 0.763578600786819, 'strength': 0.006594865631307956} | True |
| geometry-abstraction-mismatch / heldout-transfer-ray-4 f6h5 | unknown | unknown | {'confidence': 0.0, 'strength': 0.5} | False |

All 49 original Cycle 2 false legal cases: `{'supported -> unknown -> contradicted': 49}`. Complete proofs and losing evidence are in proofs/original-49-errors.json.xz.

## Native composition and induction

Native MP, negation, revision and confidence choice are production operators. Conjunction negative probes remain empty. Induction TV `{'confidence': 0.46972477064220186, 'strength': 1.0}` activates five distance controls but is redundant with the host-provided coarse abstraction. All 28 legacy induction formulas reproduce; production induction stays experimental and disabled.

The tested inheritance-to-predicate wrapper also returns no derivation. Three disjoint learned families contribute through native unary MP chains; this is not independent-premise conjunction. The castling-tagged example above is an off-home candidate without rights, resolved by learned exposure, not a complete temporal legality proof. Positive capture transfer remains a pooled, explicitly non-compositional local category.

## Performance and verification

The 214-candidate run: reference 23.878s / 16636 calls; cold 2.135s / 259; warm 1.275s / 0. All 482 candidates across the benchmark corpus have complete reference/cached proof parity. Checkpoint 760,719 bytes. Fresh-process peak RSS 217,772 KiB, comparable C3 208,212 KiB. Research-process peak is separately reported.

Dataset `7285584bfd3b06b0829620d66d4c9522eb28b96e10025b48db97dda8a6f5ffaa`; model `f76d02067c40ed2dfe73287581cbacf61339dcbe8cae166a4480f41db4aa9b5f`. Tests: `194 passed in 121.41s (0:02:01)`. Preservation: 317 files. Read clean-build.json and verification.json for the fresh-copy receipt and hashes.

All 44 clean evaluation reports match the independent development run on every candidate classification, TV and full proof digest. Model and dataset bytes match exactly. Three completed UI sessions supply nine screenshots and videos with zero captured console/server errors. The full diagnostic research parent peaks at 2,367,052 KiB (2.26 GiB), materially above the earlier approximately 660 MiB research process; isolated inference costs must not be confused with this reporting overhead. C4 cold inference is slower than the matched C3 1.711-second run, although within the three-second goal.

One legal castle changes from supported to unknown because FEN rights do not establish scoped history; its full before/after evidence is in [coverage-regressions.json](../../artifacts/cycle4/coverage-regressions.json). The older eight-game set still has zero exact move sets. Conservative-threshold ablations introduce two adversarial and one validation self-check false positives. Default C4 retains zero observed false legal/false illegal/incomplete results on these splits; all remaining abstentions count against recall. [In-board-only metrics](../../artifacts/cycle4/in-board-metrics.json) and [verification](verification.md) supplement the full reports.

## Acceptance criteria

| Criterion | Status | Actual result | Evidence |
|---|---|---|---|
| H1 verified native calculus | pass | No vendor changes; all production truth arithmetic native | [native-probes/audit.json](../../artifacts/cycle4/native-probes/audit.json) |
| H2 no production oracle | pass | Import-blocked production execution and full suite | [pytest.txt](../../artifacts/cycle4/pytest.txt); [tests/test_cycle4.py](../../tests/test_cycle4.py) |
| H3 three-way output | pass | Supported / contradicted / unknown, plus explicit incomplete status | [evaluation/](../../artifacts/cycle4/evaluation/); [tests/test_cycle4.py](../../tests/test_cycle4.py) |
| H4 dependence, replay, hashes and invariance | pass | Explicit lineage, scoped cache and parity tests | [pytest.txt](../../artifacts/cycle4/pytest.txt); [preservation.json](../../artifacts/cycle4/preservation.json) |
| H5 no universal abstention | pass | Independent recall 95.37%; coverage 96.73% | [comparison.json](../../artifacts/cycle4/comparison.json) |
| H6 compatibility and old artifact immutability | pass | 317 frozen files unchanged; schemas 1–4 supported | [preservation.json](../../artifacts/cycle4/preservation.json); [pytest.txt](../../artifacts/cycle4/pytest.txt) |
| H7 local only | pass | No push, deployment, account mutation or destructive reset performed | final local git history |
| A1 native proof lineage and oracle boundary | pass | Native source locked; explicit antecedent/bridge groups checked | [native-probes/audit.json](../../artifacts/cycle4/native-probes/audit.json); [pytest.txt](../../artifacts/cycle4/pytest.txt) |
| A2 no regression in prior proof/invariance/replay tests | pass | Original tests retained; all five C3 split proofs exactly reproduced | [baseline.json](../../artifacts/cycle4/baseline.json); [pytest.txt](../../artifacts/cycle4/pytest.txt) |
| A3 zero observed self-check errors without coverage collapse | pass | Frozen 0, adversarial 0; coverage 96.85% / 97.68% | [comparison.json](../../artifacts/cycle4/comparison.json) |
| A4 independent exact ≥25%, recall ≥90%, precision ≥98% | pass | 41.67%, 95.37%, 100.00% | [evaluation/C4-full-cycle4-independent-games.json.xz](../../artifacts/cycle4/evaluation/C4-full-cycle4-independent-games.json.xz) |
| A5 three independently trained premise families | scoped alternative | Attack, exposure and illegality in a disjoint native unary chain. General multi-condition conjunction remains unproved. | [proofs/before-after-examples.json.xz](../../artifacts/cycle4/proofs/before-after-examples.json.xz); [native-probes/audit.json](../../artifacts/cycle4/native-probes/audit.json) |
| A6 five newly resolved structural families | pass | 6 represented resolved primary families, plus unsuccessful case | [proof-examples-summary.json](../../artifacts/cycle4/proof-examples-summary.json) |
| A7 cold ≤3 seconds, memory ≤2× comparable C3 | pass | Cold 2.135s; fresh-process RSS 217772 / C3 208212 KiB | [benchmarks/inference.json](../../artifacts/cycle4/benchmarks/inference.json); [benchmarks/C3-reference.json](../../artifacts/cycle4/benchmarks/C3-reference.json) |

## Work packages

| Package | Status | Outcome | Evidence |
|---|---|---|---|
| C4-01 | complete | Inventory, exact Cycle 3 proof/TV baseline, locks, partitions and preservation | [baseline.json](../../artifacts/cycle4/baseline.json); [preservation.json](../../artifacts/cycle4/preservation.json); [docs/cycle4/architecture.md](../../docs/cycle4/architecture.md) |
| C4-02 | complete | Complete mutually reviewable taxonomy and native proof references | [error-taxonomy.json](../../artifacts/cycle4/error-taxonomy.json); [proofs/error-case-ledger.json.xz](../../artifacts/cycle4/proofs/error-case-ledger.json.xz) |
| C4-03 | complete | Executed capability laboratory and scoped strategy decision; general AND unavailable | [native-probes/audit.json](../../artifacts/cycle4/native-probes/audit.json); [docs/cycle4/native-composition-feasibility.md](../../docs/cycle4/native-composition-feasibility.md) |
| C4-04 | complete | Versioned typed relative ontology and explicit non-compositional baseline | [src/pln_chess/cycle4/ontology.py](../../src/pln_chess/cycle4/ontology.py); [tests/test_cycle4.py](../../tests/test_cycle4.py) |
| C4-05 | complete | Reusable cell obstruction, destination and boundary chains; causal blocker/jump controls | [model/C4-full.json](../../artifacts/cycle4/model/C4-full.json); [proofs/before-after-examples.json.xz](../../artifacts/cycle4/proofs/before-after-examples.json.xz); [tests/test_cycle4.py](../../tests/test_cycle4.py) |
| C4-06 | complete | Learned exposure chains and all 49 historical false-legal regressions | [proofs/original-49-errors.json.xz](../../artifacts/cycle4/proofs/original-49-errors.json.xz); [original-errors-summary.json](../../artifacts/cycle4/original-errors-summary.json) |
| C4-07 | partial | Structured uncertain history and successor operations; no full historical-legality proof | [src/pln_chess/cycle4/history.py](../../src/pln_chess/cycle4/history.py); [tests/test_cycle4.py](../../tests/test_cycle4.py); [docs/cycle4/limitations.md](../../docs/cycle4/limitations.md) |
| C4-08 | complete | Measured induction activation and redundancy; no production benefit claimed | [ablations/induction.json](../../artifacts/cycle4/ablations/induction.json) |
| C4-09 | complete | Source-group/ancestor exclusion, disjoint chains, conflict retention, retraction and replay | [src/pln_chess/cycle4/model.py](../../src/pln_chess/cycle4/model.py); [tests/test_cycle4.py](../../tests/test_cycle4.py) |
| C4-10 | partial | Bounded indexed matching, exact calculation cache, parity/cost counters; exported logical occurrences still repeated | [benchmarks/inference.json](../../artifacts/cycle4/benchmarks/inference.json); [src/pln_chess/cycle4/inference.py](../../src/pln_chess/cycle4/inference.py) |
| C4-11 | complete | Translation, structural and game tiers; locked seeds and symmetry/source audit | [datasets/dataset.json](../../artifacts/cycle4/datasets/dataset.json) |
| C4-12 | complete | All declared ablations, validation calibration, risk/coverage and clustered variability | [comparison.json](../../artifacts/cycle4/comparison.json); [calibration.json](../../artifacts/cycle4/calibration.json); [ablations/](../../artifacts/cycle4/ablations/) |
| C4-13 | complete | Compatible schema dispatch, CLI, batch export, temporal input and factored inspector | [src/pln_chess/api/__init__.py](../../src/pln_chess/api/__init__.py); [src/pln_chess/cli/](../../src/pln_chess/cli/); [ui-verification.json](../../artifacts/cycle4/ui-verification.json) |
| C4-14 | complete | Locked clean reproduction, tests, proof parity, local delivery and explicit limits | [run.json](../../artifacts/cycle4/run.json); [pytest.txt](../../artifacts/cycle4/pytest.txt); [clean-build.json](../../artifacts/cycle4/clean-build.json); [verification.json](../../artifacts/cycle4/verification.json) |

C4-07 and C4-10 remain partial. General conjunction remains a demonstrated native limitation. No package is waiting for an external approval. All negative experiment results are retained.

Reproduce: `TMPDIR=/dev/shm bash scripts/cycle4_reproduce.sh`. Diagnostics: `pln-chess cycle4 --action diagnose --split independent-games`; production-only batch: `pln-chess analyze-batch --input requests.json --output diagnostics.json`.

Next work is prioritized in NEXT_CYCLE.md. Claims are limited to measured candidate grammar, declared observations and source groups; this is not a complete chess engine.
