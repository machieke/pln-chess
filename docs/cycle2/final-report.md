# Cycle 2 engineering delivery

Status: **native-partial**, with hierarchical relational transfer. No claim of complete compositional chess legality.

Baseline HEAD: `64754bb7ebbb17595293d0a1d23b5e012ee20f92`. The final delivery commit is available through `git log -1`; this report is generated before that commit. No Cycle 2 push or deployment is performed.

Dataset SHA-256: `54a54613957657e4e9180bcc06897314fb8d64e974eee05524290aaee43e6c26`; seed 271828. B2 model: `594465ad130be239d9063d1749ec83af7921c6e94d880c2023798ed312d3ab15`.

## Package status

| Package | Status | Evidence / scope |
|---|---|---|
| C2-01 | complete | Frozen baseline and fresh reproduction. `artifacts/cycle2/baseline/manifest.json; baseline/tests.txt` |
| C2-02 | partial | Executable native probes; conjunction unavailable; two alternate layouts not integrated. `artifacts/cycle2/native-probes.json; upstream-audit.json` |
| C2-03 | complete | Schema-2 tiers and versioned loading. `artifacts/cycle2/../../tests/test_cycle2.py; B1-model.json` |
| C2-04 | complete | Local-key independence in focused perturbation and transforms. `artifacts/cycle2/demonstrations.json` |
| C2-05 | complete | Distance-agnostic occupancy and destination conditionals. `artifacts/cycle2/demonstrations.json; dataset.json` |
| C2-06 | complete | Specificity, native choice and conflict abstention. `artifacts/cycle2/B2-model.json; ../../tests/test_cycle2.py` |
| C2-07 | partial | Integrated opt-in induction; curriculum marginal assumptions remain experimental. `artifacts/cycle2/B2-model.json; native-probes.json` |
| C2-08 | complete | Idempotency, dependence, replay, rollback and integrity. `artifacts/cycle2/pytest.txt; evidence.jsonl` |
| C2-09 | complete | Disjoint context families/games, paired splits separate. `artifacts/cycle2/dataset.json` |
| C2-10 | partial | Separate learned attacks and exposure bridges; full temporal composition unsupported. `artifacts/cycle2/demonstrations.json; B4-adversarial.json` |
| C2-11 | complete | Exact native calculation reuse with full proof parity. `artifacts/cycle2/benchmark.json` |
| C2-12 | complete | API schema dispatch, CLI selectors, inspector comparison. `artifacts/cycle2/ui-verification.json; pytest.txt` |
| C2-13 | complete | Identical-split B0–B7, calibration and uncertainty. `artifacts/cycle2/run-summary.json; calibration.json; B6-baselines.json` |
| C2-14 | complete | Local reproduction verified; clean copy status below. `artifacts/cycle2/clean-build.json; pytest.txt` |

## Identical independent held-out comparison

| Variant | Precision | Recall | F1 | Abstention | Exact sets | False legal |
|---|---:|---:|---:|---:|---:|---:|
| B0 | n/a | 0.0000 | 0.0000 | 0.7886 | 0.0000 | 0.0000 |
| B1 | 0.9725 | 0.9553 | 0.9638 | 0.1769 | 0.4250 | 0.0129 |
| B2 | 0.9725 | 0.9553 | 0.9638 | 0.1769 | 0.4250 | 0.0129 |
| B3 | 0.8499 | 0.8449 | 0.8474 | 0.1302 | 0.0250 | 0.0712 |
| B4 | 0.9033 | 0.9553 | 0.9286 | 0.1526 | 0.2000 | 0.0488 |
| B5 | 0.9725 | 0.9553 | 0.9638 | 0.1769 | 0.4250 | 0.0129 |
| B7 | 0.9725 | 0.9553 | 0.9638 | 0.1769 | 0.4250 | 0.0129 |

B0 is the frozen Cycle 1 checkpoint scored on this same new dataset. B6 evaluation-only geometry/absolute baselines are in `artifacts/cycle2/B6-baselines.json`. Full reports contain in-board/per-piece metrics, uncertainty, self-check errors and proof-tier coverage. The 40 held-out positions comprise 36 long-ray/clutter cases and four independent source games; these results do not establish all-chess competence.

### Split detail and regressions

| Variant | Split | Precision | Recall | Abstention | Self-check false legal |
|---|---|---:|---:|---:|---:|
| B0 | adversarial | 1.0000 | 0.0529 | 0.6921 | 0 |
| B0 | controlled-translation | 1.0000 | 0.9737 | 0.1316 | 0 |
| B0 | heldout-transfer | n/a | 0.0000 | 0.7886 | 0 |
| B0 | irrelevant-context | n/a | 0.0000 | 0.6053 | 0 |
| B0 | train | 1.0000 | 0.3337 | 0.5492 | 0 |
| B0 | validation | n/a | 0.0000 | 0.7271 | 0 |
| B1 | adversarial | 0.8939 | 0.9648 | 0.2608 | 26 |
| B1 | controlled-translation | 1.0000 | 1.0000 | 0.1053 | 0 |
| B1 | heldout-transfer | 0.9725 | 0.9553 | 0.1769 | 23 |
| B1 | irrelevant-context | 1.0000 | 1.0000 | 0.1053 | 0 |
| B1 | train | 1.0000 | 0.9989 | 0.1114 | 0 |
| B1 | validation | 1.0000 | 0.9950 | 0.1729 | 0 |
| B2 | adversarial | 0.8939 | 0.9648 | 0.2608 | 26 |
| B2 | controlled-translation | 1.0000 | 1.0000 | 0.1053 | 0 |
| B2 | heldout-transfer | 0.9725 | 0.9553 | 0.1769 | 23 |
| B2 | irrelevant-context | 1.0000 | 1.0000 | 0.1053 | 0 |
| B2 | train | 1.0000 | 0.9989 | 0.1114 | 0 |
| B2 | validation | 1.0000 | 0.9950 | 0.1729 | 0 |

Induction alternatives are retained with their native premises and population counts, even when direct revised evidence wins native confidence choice. Equal B1/B2 metrics are a null result for induction selection, not evidence of improvement from induction. Calibration is fit on validation only; confidence is not a calibrated outcome probability.

## New reusable motifs

- **Rook / contradicted**: unseen `8/1K6/R2N4/8/1n6/8/8/bk6 w - - 0 1`, move `a6e6`. Rule `c2:627ff68a8ee2d7b98f76ed6a` (tier 4), native TV `{'confidence': 0.8777616279069769, 'strength': 0.0032679738562090277}`. Local descriptor `{'destination': 'Empty', 'destination_kind': None, 'effect': 'ordinary', 'motion': 'orthogonal', 'piece': 'Rook', 'promotion': None, 'ray_contents': ['Friendly']}`. Training evidence: `{'dependence_group': 'historical-rook-east', 'evidence_id': 'b02eb241e7ed0d8d9fdbcf659a825c9b31d146261ecf863738a4f70c66e86347', 'input': {'fen': '7k/8/8/8/8/8/2RP4/2K5 w - - 0 1', 'move': 'c2e2'}, 'label': False}`. Held-out generative family, longer ray, mixed opponent context, no exact-context rule; tier 4 distance-agnostic occupancy/destination relation.
- **Bishop / supported**: unseen `8/8/1n6/8/8/4K3/kB6/5b2 w - - 0 1`, move `b2f6`. Rule `c2:6cbd9dae6a4a5983b4178856` (tier 4), native TV `{'confidence': 0.9121572580645162, 'strength': 0.9978165938864629}`. Local descriptor `{'destination': 'Empty', 'destination_kind': None, 'effect': 'ordinary', 'motion': 'diagonal', 'piece': 'Bishop', 'promotion': None, 'ray_contents': []}`. Training evidence: `{'dependence_group': 'historical-bishop-main', 'evidence_id': '5d6e1474ae9fce5abb0feb21f8380a378ee62037788f4d45ff123f4874f1365c', 'input': {'fen': '8/7k/8/8/8/2B5/8/K7 w - - 0 1', 'move': 'c3d4'}, 'label': True}`. Held-out generative family, longer ray, mixed opponent context, no exact-context rule; tier 4 distance-agnostic occupancy/destination relation.
- **Queen / supported**: unseen `8/Q7/8/4n3/7k/8/1b3K2/8 w - - 0 1`, move `a7e7`. Rule `c2:c4cea81dd58b6238c493f95a` (tier 4), native TV `{'confidence': 0.9121572580645162, 'strength': 0.9978165938864629}`. Local descriptor `{'destination': 'Empty', 'destination_kind': None, 'effect': 'ordinary', 'motion': 'orthogonal', 'piece': 'Queen', 'promotion': None, 'ray_contents': []}`. Training evidence: `{'dependence_group': 'historical-queen-main', 'evidence_id': 'e55a248f84bef3a38b00b555cff5036e570de42ed86b7a4bdffee71a27ff374b', 'input': {'fen': '7k/8/8/8/2Q5/8/8/K7 w - - 0 1', 'move': 'c4c5'}, 'label': True}`. Held-out generative family, longer ray, mixed opponent context, no exact-context rule; tier 4 distance-agnostic occupancy/destination relation.

Irrelevant-context movement ID/TV checks: `{'movement_hypothesis_id': True, 'movement_truth_value': True}`. Complete proofs and training references: `artifacts/cycle2/demonstrations.json`.

## Native execution and performance

Production uses untouched upstream `Truth_Revision`, `Truth_ModusPonens`, `Truth_Negation` and `BestConfidenceCandidate`. Opt-in induction additionally uses `Truth_w2c` and `Truth_Induction`. Exact source lines, expressions and outputs: `artifacts/cycle2/native-probes.json`. The inheritance wrapper marginal-order issue and conjunction boundary are documented in `docs/cycle2/native-pln-feasibility.md`.

| Schedule | Native calls | Logical nodes | Seconds |
|---|---:|---:|---:|
| reference | 13742 | 13742 | 20.5807 |
| cold | 158 | 13742 | 1.5024 |
| warm | 0 | 13742 | 0.9392 |

On 214 candidates: cold speedup 13.70×; call reduction 86.97×. Exact proof/TV/rule/lineage parity: **True**. Warm results reuse raw native computations; no persistent PeTTa process. This scheduler comparison uses the same Cycle 2 model on both sides. The reproduced Cycle 1 timings are separately archived in `artifacts/cycle2/baseline/benchmark.json`.

## Verification and reproduction

Tests: **91 passed in 64.13s (0:01:04)**. Clean-copy status: **passed**. Browser verification: **passed**.

```bash
bash scripts/cycle2_reproduce.sh
.venv/bin/pln-chess cycle2 --action audit
.venv/bin/pln-chess inspect --checkpoint artifacts/cycle2/B1-model.json --fen "8/6k1/8/8/8/2R5/2K5/8 w - - 0 1" --move c3f3
.venv/bin/pln-chess serve --port 8765 --checkpoint artifacts/cycle2/B1-model.json
```

Prerequisites remain SWI-Prolog 10.0.1 with Janus/PCRE and uv. Bootstrap verifies native hashes and installs pinned Python 3.12.12 dependencies. The reproduction archive restores the frozen baseline if outputs are absent; it never regenerates over Cycle 1 originals. `--resume` reuses compatible evaluation outputs, while the default regenerates all Cycle 2 experiments.

## Remaining work

Native conjunction remains unsupported. Priorities are a maintained multi-premise rule with dependence semantics, statistically justified induction populations, broader independent games/special moves and perturbations, stronger temporal constraints, and bounded cache retention. See `limitations.md` for every host-derived/non-compositional step and measurement limitation.
