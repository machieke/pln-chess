# Cycle 3 final engineering report

This is a native-partial conditional learner. Frozen Cycle 2 performance is a retrospective regression comparison; the new challenge and independent games provide additional evaluation. No strategic search or engine legality gate was added.

| Model / split | Candidates | Precision | Recall | F1 | Abstention | Exact sets | Self-check FP |
|---|---:|---:|---:|---:|---:|---:|---:|
| B0 / frozen-heldout-transfer | 2635 | — | 0.00% | 0.00% | 78.86% | 0.00% | 0 |
| B0 / frozen-adversarial | 1208 | 100.00% | 5.29% | 10.04% | 69.21% | 8.33% | 0 |
| B0 / new-challenge | 736 | 100.00% | 2.98% | 5.78% | 73.91% | 0.00% | 0 |
| B0 / new-independent-games | 1697 | — | 0.00% | 0.00% | 75.07% | 0.00% | 0 |
| B1 / frozen-heldout-transfer | 2635 | 97.25% | 95.53% | 96.38% | 17.69% | 42.50% | 23 |
| B1 / frozen-adversarial | 1208 | 89.39% | 96.48% | 92.80% | 26.08% | 45.83% | 26 |
| B1 / new-challenge | 736 | 75.24% | 94.05% | 83.60% | 21.74% | 47.83% | 50 |
| B1 / new-independent-games | 1697 | 96.79% | 88.28% | 92.34% | 29.11% | 0.00% | 8 |
| B2 / frozen-heldout-transfer | 2635 | 97.25% | 95.53% | 96.38% | 17.69% | 42.50% | 23 |
| B2 / frozen-adversarial | 1208 | 89.39% | 96.48% | 92.80% | 26.08% | 45.83% | 26 |
| B2 / new-challenge | 736 | 75.24% | 94.05% | 83.60% | 21.74% | 47.83% | 50 |
| B2 / new-independent-games | 1697 | 96.79% | 88.28% | 92.34% | 29.11% | 0.00% | 8 |
| C3-local / frozen-heldout-transfer | 2635 | 90.33% | 95.53% | 92.86% | 14.84% | 20.00% | 87 |
| C3-local / frozen-adversarial | 1208 | 56.96% | 97.36% | 71.87% | 14.40% | 16.67% | 167 |
| C3-local / new-challenge | 736 | 50.80% | 94.05% | 65.97% | 8.70% | 13.04% | 151 |
| C3-local / new-independent-games | 1697 | 95.65% | 88.64% | 92.02% | 29.17% | 0.00% | 11 |
| C3-exposure / frozen-heldout-transfer | 2635 | 100.00% | 95.53% | 97.72% | 18.14% | 67.50% | 0 |
| C3-exposure / frozen-adversarial | 1208 | 100.00% | 97.36% | 98.66% | 28.23% | 75.00% | 0 |
| C3-exposure / new-challenge | 736 | 100.00% | 94.05% | 96.93% | 29.48% | 69.57% | 0 |
| C3-exposure / new-independent-games | 1697 | 100.00% | 88.64% | 93.98% | 29.82% | 0.00% | 0 |
| C3-induction / frozen-heldout-transfer | 2635 | 100.00% | 95.53% | 97.72% | 18.14% | 67.50% | 0 |
| C3-induction / frozen-adversarial | 1208 | 100.00% | 97.36% | 98.66% | 28.23% | 75.00% | 0 |
| C3-induction / new-challenge | 736 | 100.00% | 94.05% | 96.93% | 29.48% | 69.57% | 0 |
| C3-induction / new-independent-games | 1697 | 100.00% | 88.64% | 93.98% | 29.82% | 0.00% | 0 |
| C3-full / frozen-heldout-transfer | 2635 | 100.00% | 95.53% | 97.72% | 18.14% | 67.50% | 0 |
| C3-full / frozen-adversarial | 1208 | 100.00% | 97.36% | 98.66% | 28.23% | 75.00% | 0 |
| C3-full / new-challenge | 736 | 100.00% | 94.05% | 96.93% | 29.48% | 69.57% | 0 |
| C3-full / new-independent-games | 1697 | 100.00% | 88.64% | 93.98% | 29.82% | 0.00% | 0 |
| no-obstruction / frozen-heldout-transfer | 2635 | 87.36% | 84.49% | 85.90% | 13.70% | 10.00% | 0 |
| no-obstruction / frozen-adversarial | 1208 | 89.45% | 85.90% | 87.64% | 24.92% | 58.33% | 0 |
| no-obstruction / new-challenge | 736 | 92.07% | 89.88% | 90.96% | 24.59% | 56.52% | 0 |
| no-obstruction / new-independent-games | 1697 | 57.18% | 74.36% | 64.65% | 14.32% | 0.00% | 0 |
| no-exposure / frozen-heldout-transfer | 2635 | 90.33% | 95.53% | 92.86% | 14.84% | 20.00% | 87 |
| no-exposure / frozen-adversarial | 1208 | 56.96% | 97.36% | 71.87% | 14.40% | 16.67% | 167 |
| no-exposure / new-challenge | 736 | 50.80% | 94.05% | 65.97% | 8.70% | 13.04% | 151 |
| no-exposure / new-independent-games | 1697 | 95.65% | 88.64% | 92.02% | 29.17% | 0.00% | 11 |
| no-induction / frozen-heldout-transfer | 2635 | 100.00% | 95.53% | 97.72% | 18.14% | 67.50% | 0 |
| no-induction / frozen-adversarial | 1208 | 100.00% | 97.36% | 98.66% | 28.23% | 75.00% | 0 |
| no-induction / new-challenge | 736 | 100.00% | 94.05% | 96.93% | 29.48% | 69.57% | 0 |
| no-induction / new-independent-games | 1697 | 100.00% | 88.64% | 93.98% | 29.82% | 0.00% | 0 |
| no-arbitration / frozen-heldout-transfer | 2635 | 90.33% | 95.53% | 92.86% | 14.84% | 20.00% | 87 |
| no-arbitration / frozen-adversarial | 1208 | 57.25% | 97.36% | 72.10% | 14.40% | 16.67% | 165 |
| no-arbitration / new-challenge | 736 | 51.80% | 94.05% | 66.81% | 8.70% | 17.39% | 147 |
| no-arbitration / new-independent-games | 1697 | 95.65% | 88.64% | 92.02% | 29.17% | 0.00% | 11 |
| no-dependence / frozen-heldout-transfer | 2635 | 100.00% | 85.19% | 92.01% | 20.49% | 2.50% | 0 |
| no-dependence / frozen-adversarial | 1208 | 100.00% | 78.85% | 88.18% | 30.22% | 20.83% | 0 |
| no-dependence / new-challenge | 736 | 100.00% | 69.64% | 82.11% | 34.24% | 0.00% | 0 |
| no-dependence / new-independent-games | 1697 | 100.00% | 84.98% | 91.88% | 30.11% | 0.00% | 0 |
| exact-context-only / frozen-heldout-transfer | 2635 | — | 0.00% | 0.00% | 89.03% | 0.00% | 0 |
| exact-context-only / frozen-adversarial | 1208 | 100.00% | 3.08% | 5.98% | 86.75% | 8.33% | 0 |
| exact-context-only / new-challenge | 736 | 100.00% | 2.98% | 5.78% | 86.14% | 0.00% | 0 |
| exact-context-only / new-independent-games | 1697 | — | 0.00% | 0.00% | 88.86% | 0.00% | 0 |

## Every original self-check error

{'abstention': 23, 'correct-negative': 0, 'remaining-false-positive': 0}. Correct negative classifications and abstentions are counted separately. Full before/after evidence is in `artifacts/cycle3/self-check-errors.json.xz`.

## Native semantics and induction

Native MP, revision, negation and confidence choice produce the displayed TVs. Independent conditionals are not conjoined. Explicit joint-sensor inference and unary implication chains execute; native conjunction introduction/elimination does not. No safe-king belief follows from absent attack evidence.

Induction classification changes: {'frozen-adversarial': 0, 'frozen-heldout-transfer': 0, 'new-challenge': 0, 'new-independent-games': 0}. All 14 original native formulas are independently re-executed. Direct parents and induced hypotheses share evidence and are alternatives, never independently fused.

## Same-model optimization parity

| Fixture | Candidates | Reference s / calls | Cold s / calls | Warm s / calls | Full proof parity |
|---|---:|---:|---:|---:|---|
| game-0 | 214 | 24.867 / 17318 | 1.975 / 179 | 1.952 / 0 | True |
| challenge-double-check | 38 | 2.817 / 1900 | 0.619 / 134 | 0.192 / 0 | True |
| challenge-castle-transit | 38 | 2.674 / 1656 | 0.658 / 111 | 0.164 / 0 | True |
| independent-games-0 | 226 | 26.083 / 18165 | 2.090 / 196 | 1.683 / 0 | True |

Peak process RSS: 675452 KiB. Checkpoint: 1247402 bytes. Evidence records: 1906. RSS is process-wide; the memory budget limits estimated proof payload and cache entries, not OS RSS.

## Work packages

| Package | Status | Evidence |
|---|---|---|
| C3-01 | complete | `baseline.json` — Frozen B1/B2 candidate TVs/classes and optimization reproduced; B0 also measured. |
| C3-02 | complete | `native-probes.json` — Executed composition boundary and source signatures; no unsupported operator adopted. |
| C3-03 | complete | `../../docs/cycle3-architecture.md` — Versioned descriptors, explicit schema replay and separate observations. |
| C3-04 | partial | `transfer-proofs.json.xz` — Reusable local and obstruction motifs transfer; true native conjunction unavailable. |
| C3-05 | complete | `self-check-resolution.json` — Every frozen self-check false positive tracked; independent attack curriculum and temporal frames evaluated. |
| C3-06 | partial | `../../tests/test_cycle3.py` — Castling phases, promotion and explicit predecessor tests; FEN-only EP remains unknown, historical legality not proved. |
| C3-07 | partial | `induction.json` — Original 14 formulas reproduced and controlled integration measured; no claimed novel cross-piece induction or forced benefit. |
| C3-08 | complete | `../../docs/cycle3-learning-semantics.md` — Disjoint chain evidence pools, replay/rollback, conflicts, low confidence and calibration; supplied dependence identities remain assumptions. |
| C3-09 | complete | `dataset.json` — Independent challenge/game sets, paired transforms, full candidate sets, sparse curves and overlap audit. |
| C3-10 | complete | `comparison.json` — All named baselines and ablations scored with errors and abstention visible. |
| C3-11 | complete | `benchmark.json` — Full candidate/proof parity, cold/warm measurements, bounded cache and estimated proof-memory budget; RSS limit is not OS-enforced. |
| C3-12 | complete | `ui-verification.json` — Existing API/CLI extended, independent condition panels, comparisons and structural counterfactuals. |
| C3-13 | complete | `clean-build.json` — Full suite and clean reproduction receipt; exact final status in linked evidence. |
| C3-14 | complete | `manifest.json` — Documentation, machine-readable artifacts and local delivery; no push. |

## Reproduction and integrity

Tests: 141 passed in 98.89s (0:01:38)
Dataset: `6a190f64fd6ba9eaccc3a2c0f393f185b720cf4f30b300c2b0b7fdd29b392068`.
C3-full model: `60479e1a92d81e974f5bc635a2407047b81efb4e4da0382b016fef14d5b4a473`.
Runtime PLN: `4405956947c4b53c7ff01bd565aa3b114bc970a1`; source SHA256 `cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`.

```bash
bash scripts/cycle3_reproduce.sh
.venv/bin/pln-chess cycle3 --action audit
.venv/bin/pln-chess serve --port 8765 --checkpoint artifacts/cycle3/C3-full-model.json
```

Use `pln-chess inspect --fen "..." --move c2e2 --checkpoint artifacts/cycle3/C3-full-model.json` for a candidate. `counterfactual` accepts `--operation add-blocker|remove-piece|move-piece|color-flip|remove-right`, `--square` and `--target`. See `docs/cycle3-architecture.md` for trusted predecessor observations and explicit inference budgets.

Starting commit: `f80b27dc41e591c90ed7456f3730fb5c0ea5d28e`. Final delivery commit is available from `git log -1`; a file cannot contain the hash of its own committing tree. Local commits only; no push, deployment or remote mutation.

## Remaining research priorities

1. Verified native conjunction and justified closed-world safety evidence.
2. Independently sampled induction populations that can add useful hypotheses beyond direct parents.
3. More unseen pawn/history and castling contexts, with explicit predecessor evidence.
4. Broader independent game evaluation and confidence/coverage tradeoffs.
5. Persistent native execution or shared immutable observation scheduling with full proof parity.
