# Generalization results

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

C5 strict positive recall is zero and precision is undefined because no positive legality theorem is established. Zero false-legal observations therefore do not demonstrate useful positive prediction. Any exact empty move sets are terminal-position matches. C4 conditional local projections are a different claim and remain reported as the prior baseline.

All reports use the unchanged candidate grammar and include unknowns in recall. Every report includes in-board-only and per-family/per-piece/special-move metrics, raw TVs, model/dataset hashes, bootstrap intervals and incomplete counts. Boundary negatives do not establish chess competence. New games have 16 independent source games with two sampled positions each, plus four validation games. The full trajectories are retained.

The factorial-only model omits C4 observation hypotheses and retains only independently trained bridge conditionals. Fine and abstract combinations, declared structural families, symmetry and source ancestry are disjoint. Full C4 prior overlap is separately disclosed; it cannot be called novel transfer. Repeated synthetic training rows share dependence groups. Sample-efficiency results report the first success among measured prefixes, not a minimal-context theorem.

Calibration uses only the new validation games. Confidence is not treated as probability. Risk curves only suppress already-admitted negative witnesses as display confidence increases; the detection floor remains 0.25. See [calibration](../../artifacts/cycle5/calibration.json), [risk curves](../../artifacts/cycle5/selective-risk.json), [factorial evidence](../../artifacts/cycle5/factorial.json.xz), and [dataset audit](../../artifacts/cycle5/datasets/dataset.json).

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
