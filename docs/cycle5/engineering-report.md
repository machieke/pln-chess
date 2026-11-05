# Cycle 5 engineering report

Starting reference `d5cfcb126acc9c3e5da669744d661e6895fb9303`. Build source `f8b7834cc79ce495d3cf2c67019a91d7b5d08b8e`. Final delivery is the local commit containing this report and its manifest; no push is authorized for this cycle.

Cycle 5 produces stricter, inspectable proof gaps and reusable native negative transfer. It does **not** complete positive compositional chess legality. All default positive claims abstain, so recall is zero and precision is undefined. This is a substantial coverage loss relative to C4's conditional local projection. Aspirational positive-recall and exact-set targets are not achieved.

All 49 historical false-legal cases retain supported-illegal proofs. Across the declared splits, 238 additional C4 unknowns receive C5 negative proofs; decisive-family removal changes classification in 238 cases. Observed false-illegal among those changes: 0. Every new negative retains the complete native proof and removal result; alternative witnesses are not hidden.

## Package matrix

| Package | Status | Actual outcome | Evidence |
|---|---|---|---|
| C5-01 | complete | Four exact C4 baseline reruns, versioned snapshots and provenance lock | [baseline.json](../../artifacts/cycle5/baseline.json) |
| C5-02 | complete | Executable native capability matrix, including negative conjunction results | [native-probes/audit.json](../../artifacts/cycle5/native-probes/audit.json) |
| C5-03 | complete | Versioned typed premises, raw pre/post frames and disclosed host abstractions | [model/C5-full.json](../../artifacts/cycle5/model/C5-full.json) |
| C5-04 | partial | Clean local combination holdout; exposure and temporal tests remain structural controls rather than fully independent factorial curricula | [factorial.json.xz](../../artifacts/cycle5/factorial.json.xz) |
| C5-05 | complete | Strict proof planner and negative feasibility result; no defensible new positive legality theorem | [proofs/before-after.json.xz](../../artifacts/cycle5/proofs/before-after.json.xz) |
| C5-06 | complete | Original 49 negative proofs retained; every newly resolved negative has family-removal evidence | [proofs/new-negative-counterfactuals.json.xz](../../artifacts/cycle5/proofs/new-negative-counterfactuals.json.xz) |
| C5-07 | partial | Three temporal trust modes and scoped observations; no learned theorem of complete historical legality | [temporal.json](../../artifacts/cycle5/temporal.json) |
| C5-08 | partial | Causal activation/disabled/sham study executed; host-proposed descriptors, no native abstraction discovery or production gain | [induction.json](../../artifacts/cycle5/induction.json) |
| C5-09 | complete | Source/ancestor exclusion, replay, rollback, corruption and family counterfactuals | [proofs/family-counterfactuals.json.xz](../../artifacts/cycle5/proofs/family-counterfactuals.json.xz) |
| C5-10 | complete | Whole candidate sets, new games, calibration and two representation ablations; positive research targets fail | [comparison.json](../../artifacts/cycle5/comparison.json) |
| C5-11 | partial | Shared typed calculations, exported DAG references and full cache parity; inherited C4 proof occurrences still repeat | [benchmarks/C5.json](../../artifacts/cycle5/benchmarks/C5.json) |
| C5-12 | complete | Compatible schema dispatch, CLI modes and inspector proof gaps | [ui-verification.json](../../artifacts/cycle5/ui-verification.json) |
| C5-13 | complete | Tests and locked clean reproduction with explicit native failures | [verification.json](../../artifacts/cycle5/verification.json) |
| C5-14 | complete | Versioned reports, exact changed-file list, manifest and local delivery | [manifest.json](../../artifacts/cycle5/manifest.json) |

## Results and evidence

| Model / split | Positions | Candidates | Supported legal | Supported illegal | Unknown | False legal / illegal | Precision | Recall | F1 | Exact sets |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C4 / cycle3-independent-games | 8 | 1697 | 260 | 1371 | 66 | 0 / 0 | 100.00% | 95.24% | 97.56% | 0.00% |
| C4 / cycle4-independent-games | 24 | 4650 | 762 | 3736 | 152 | 0 / 0 | 100.00% | 95.37% | 97.63% | 41.67% |
| C4 / cycle5-combination-holdout | 14 | 516 | 183 | 319 | 14 | 0 / 0 | 100.00% | 98.39% | 99.19% | 78.57% |
| C4 / cycle5-independent-games | 32 | 6427 | 855 | 5375 | 197 | 0 / 0 | 100.00% | 95.32% | 97.60% | 31.25% |
| C4 / cycle5-structural-holdout | 6 | 176 | 60 | 109 | 7 | 0 / 0 | 100.00% | 96.77% | 98.36% | 66.67% |
| C4 / cycle5-validation | 8 | 1543 | 257 | 1236 | 50 | 0 / 0 | 100.00% | 95.54% | 97.72% | 37.50% |
| C4 / frozen-adversarial | 24 | 1208 | 225 | 955 | 28 | 0 / 0 | 100.00% | 99.12% | 99.56% | 91.67% |
| C4 / frozen-heldout-transfer | 40 | 2635 | 832 | 1720 | 83 | 0 / 0 | 100.00% | 97.77% | 98.87% | 75.00% |
| C5-abstract-only / cycle3-independent-games | 8 | 1697 | 0 | 1371 | 326 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-abstract-only / cycle4-independent-games | 24 | 4650 | 0 | 3736 | 914 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-abstract-only / cycle5-combination-holdout | 14 | 516 | 0 | 319 | 197 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-abstract-only / cycle5-independent-games | 32 | 6427 | 0 | 5375 | 1052 | 0 / 0 | undefined | 0.00% | 0.00% | 3.12% |
| C5-abstract-only / cycle5-structural-holdout | 6 | 176 | 0 | 109 | 67 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-abstract-only / cycle5-validation | 8 | 1543 | 0 | 1236 | 307 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-abstract-only / frozen-adversarial | 24 | 1208 | 0 | 955 | 253 | 0 / 0 | undefined | 0.00% | 0.00% | 8.33% |
| C5-abstract-only / frozen-heldout-transfer | 40 | 2635 | 0 | 1720 | 915 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-full / cycle3-independent-games | 8 | 1697 | 0 | 1398 | 299 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-full / cycle4-independent-games | 24 | 4650 | 0 | 3808 | 842 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-full / cycle5-combination-holdout | 14 | 516 | 0 | 327 | 189 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-full / cycle5-independent-games | 32 | 6427 | 0 | 5450 | 977 | 0 / 0 | undefined | 0.00% | 0.00% | 3.12% |
| C5-full / cycle5-structural-holdout | 6 | 176 | 0 | 109 | 67 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-full / cycle5-validation | 8 | 1543 | 0 | 1251 | 292 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-full / frozen-adversarial | 24 | 1208 | 0 | 964 | 244 | 0 / 0 | undefined | 0.00% | 0.00% | 8.33% |
| C5-full / frozen-heldout-transfer | 40 | 2635 | 0 | 1752 | 883 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-no-new-negatives / cycle3-independent-games | 8 | 1697 | 0 | 1371 | 326 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-no-new-negatives / cycle4-independent-games | 24 | 4650 | 0 | 3736 | 914 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-no-new-negatives / cycle5-combination-holdout | 14 | 516 | 0 | 319 | 197 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-no-new-negatives / cycle5-independent-games | 32 | 6427 | 0 | 5375 | 1052 | 0 / 0 | undefined | 0.00% | 0.00% | 3.12% |
| C5-no-new-negatives / cycle5-structural-holdout | 6 | 176 | 0 | 109 | 67 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-no-new-negatives / cycle5-validation | 8 | 1543 | 0 | 1236 | 307 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |
| C5-no-new-negatives / frozen-adversarial | 24 | 1208 | 0 | 955 | 253 | 0 / 0 | undefined | 0.00% | 0.00% | 8.33% |
| C5-no-new-negatives / frozen-heldout-transfer | 40 | 2635 | 0 | 1720 | 915 | 0 / 0 | undefined | 0.00% | 0.00% | 0.00% |

Machine-readable results include denominator, model version, dataset hash, confidence policy, per-piece and in-board metrics. [Generalization and overlap policy](generalization-results.md), [native boundary](composition-feasibility.md), [temporal semantics](temporal-semantics.md), [induction study](induction-results.md), [performance](performance.md), and [verification](verification.md) describe limitations. [All changed paths](../../artifacts/cycle5/changed-files.json) and the [artifact manifest](../../artifacts/cycle5/manifest.json) define the delivery.

## Reproduce

```bash
TMPDIR=/dev/shm bash scripts/cycle5_reproduce.sh
.venv/bin/pln-chess composition-audit
.venv/bin/pln-chess evaluate --checkpoint artifacts/cycle5/model/C5-full.json --split independent-games
```

## Ranked next questions

1. Can a separately validated native operator establish a positive conjunction with explicit dependence semantics? Require a previously unseen positive combination and adverse controls before changing C5's default.
2. Can a native safety theorem summarize independent opponent frames without treating absent threats as safety? Measure recovery of legal recall, not just zero false positives.
3. Can independently sourced temporal premises establish special-move eligibility and survive truncation/conflict tests? Keep event consistency separate from legal history.
4. Can induction propose a useful relation absent from host abstractions? Require enabled/disabled/sham classification differences on a fresh holdout.
5. Can inherited C4 proof occurrences be interned while preserving bindings, lineage and complete proof parity? Measure fresh-process memory and total serialized proof cost.

## Metric provenance

The registered decision policy uses confidence 0.25, positive strength 0.8 and negative strength 0.2. C5 additionally requires a complete native positive proof, which is never established in these runs. All 32 default comparison reports have zero incomplete, false-legal and false-illegal classifications. C4 precision is 100% in these observed samples; C5 precision is undefined and recall/F1 are zero. These finite results do not prove universal correctness.

| Model | Semantic model version |
|---|---|
| C4 | `f76d02067c40ed2dfe73287581cbacf61339dcbe8cae166a4480f41db4aa9b5f` |
| C5-abstract-only | `3b47e3e6bdc7f607a8921371a512aa78ec06d022426a4bb03b805140d296b6e3` |
| C5-full | `f1893f11340954d8af675a1738d98cdcc01bf818294e0e8448b1f6a4ca5defb2` |
| C5-no-new-negatives | `661ba280ee0c680c9977b58c968746ae557c91a35abf591f572b17d117f1e502` |

| Split | Oracle legal candidates (recall denominator) | Dataset semantic hash |
|---|---:|---|
| cycle3-independent-games | 273 | `6a190f64fd6ba9eaccc3a2c0f393f185b720cf4f30b300c2b0b7fdd29b392068` |
| cycle4-independent-games | 799 | `7285584bfd3b06b0829620d66d4c9522eb28b96e10025b48db97dda8a6f5ffaa` |
| cycle5-combination-holdout | 186 | `8568a37be74da40a2c05691299147b13ad064c239d915dceb9a4dbe5b49f91a0` |
| cycle5-independent-games | 897 | `8568a37be74da40a2c05691299147b13ad064c239d915dceb9a4dbe5b49f91a0` |
| cycle5-structural-holdout | 62 | `8568a37be74da40a2c05691299147b13ad064c239d915dceb9a4dbe5b49f91a0` |
| cycle5-validation | 269 | `8568a37be74da40a2c05691299147b13ad064c239d915dceb9a4dbe5b49f91a0` |
| frozen-adversarial | 227 | `54a54613957657e4e9180bcc06897314fb8d64e974eee05524290aaee43e6c26` |
| frozen-heldout-transfer | 851 | `54a54613957657e4e9180bcc06897314fb8d64e974eee05524290aaee43e6c26` |

In-board-only new-game evaluation contains 3,197 candidates: 897 legal, 2,220 supported-illegal and 977 unknown under C5. The other 3,230 candidates are out of board. The full-model comparison is distinct from the clean factorial-only experiment; seven prior C4 combination overlaps are disclosed in the leakage audit.

[Machine-readable comparison](../../artifacts/cycle5/comparison.json) includes all ablations, in-board results, per-piece/special-move metrics, calibration and policy details.
