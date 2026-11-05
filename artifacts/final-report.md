# Engineering delivery report

Status: a tested **native-partial** research package. Full compositional chess learning is blocked by the audited runtime’s missing conjunction introduction. This is not a complete chess engine.

Runtime: PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`, PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`, SWI-Prolog version 10.0.1 for x86_64-linux, Python 3.12.12.

Dataset: 45 positions, 2128 candidates, seed 1729, chess 1.11.2, SHA-256 `67485e0eda18c05d6c74c1dbe7ccf00bd306e4ea5e2805e4a4a39111c2ce183a`.

## Measured results

| Split | Precision | Recall | F1 | Abstention | Exact move sets |
|---|---:|---:|---:|---:|---:|
| adversarial | 1.0000 | 0.2222 | 0.3636 | 0.5606 | 0.4000 |
| controlled-transfer | 1.0000 | 0.9474 | 0.9730 | 0.2632 | 0.0000 |
| heldout-transfer | n/a | 0.0000 | 0.0000 | 0.7403 | 0.0000 |
| train | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 |
| validation | n/a | 0.0000 | 0.0000 | 0.6871 | 0.0000 |

Abstentions count against recall. Out-of-board candidates are included; each JSON report also gives in-board metrics. Controlled-transfer is a paired demonstration, not independent structural generalization. Strict held-out families and games are disjoint from training.

## Actual native traces

| Scenario | Strength | Confidence | Display |
|---|---:|---:|---|
| rook-clear | 0.97500000 | 0.49500000 | supported |
| rook-blocked | 0.02500000 | 0.49500000 | contradicted |
| rook-enemy | 0.97500000 | 0.49500000 | supported |
| rook-friendly | 0.02500000 | 0.49500000 | contradicted |
| rook-pinned | 0.02500000 | 0.49500000 | contradicted |
| bishop-clear | 0.97500000 | 0.49500000 | supported |
| bishop-blocked | 0.02500000 | 0.49500000 | contradicted |
| queen-clear | 0.97500000 | 0.49500000 | supported |
| knight-jump | 0.97500000 | 0.49500000 | supported |
| knight-empty | 0.97500000 | 0.49500000 | supported |
| pawn-white | 0.97500000 | 0.49500000 | supported |
| pawn-blocked | 0.02500000 | 0.49500000 | contradicted |
| pawn-black | 0.97500000 | 0.49500000 | supported |
| pawn-capture | 0.97500000 | 0.49500000 | supported |
| pawn-empty-diagonal | 0.02500000 | 0.49500000 | contradicted |
| king-safe | 0.97500000 | 0.49500000 | supported |
| king-attacked | 0.02500000 | 0.49500000 | contradicted |
| king-adjacent | 0.02500000 | 0.49500000 | contradicted |
| castle-clear | 0.97500000 | 0.49500000 | supported |
| castle-no-right | 0.02500000 | 0.49500000 | contradicted |
| castle-through-attack | 0.02500000 | 0.49500000 | contradicted |
| castle-queenside | 0.97500000 | 0.49500000 | supported |
| castle-queenside-outer-blocked | 0.02500000 | 0.49500000 | contradicted |
| en-passant | 0.97500000 | 0.49500000 | supported |
| en-passant-no-target | 0.02500000 | 0.49500000 | contradicted |
| en-passant-opens-ray | 0.02500000 | 0.49500000 | contradicted |
| promotion | 0.97500000 | 0.49500000 | supported |
| promotion-friendly | 0.02500000 | 0.49500000 | contradicted |
| rook-long | 0.50000000 | 0.02475000 | unknown |
| bishop-capture | 0.50000000 | 0.02475000 | unknown |
| double-check | 0.00623636 | 0.04867474 | unknown |
| diagonal-pin | 0.50000000 | 0.02475000 | unknown |
| discovered-check | 0.50000000 | 0.02475000 | unknown |
| check-block | 0.50000000 | 0.02475000 | unknown |
| check-capture | 0.50000000 | 0.02475000 | unknown |
| mate | 0.50000000 | 0.02475000 | unknown |
| stalemate | 0.50000000 | 0.02475000 | unknown |
| edge-knight | 0.50000000 | 0.02475000 | unknown |
| castle-occupied | 0.50000000 | 0.02475000 | unknown |
| transfer-source | 0.97500000 | 0.49500000 | supported |
| transfer-target | 0.97500000 | 0.49500000 | supported |
| game-0 | 0.97500000 | 0.49500000 | supported |
| game-1 | 0.50000000 | 0.02475000 | unknown |
| game-2 | 0.50000000 | 0.02475000 | unknown |
| game-3 | 0.50000000 | 0.02475000 | unknown |

Every trace is saved under `artifacts/proofs/`, with premise/conclusion TVs, native expressions, rule IDs, evidence lineage, runtime/model versions, budgets, and an evaluation-only oracle comparison.

## Boundaries and limitations

- Native PLN: untouched upstream `|-` rules for modus ponens, negation and revision; native evidence choice. Deduction, inheritance and induction additionally have runnable audit tests.
- Host structural processing: FEN parsing, candidate geometry, raw occupancy categories, structural successor states, typed relational fingerprints, dependency bookkeeping, and native invocation scheduling.
- Oracle: only `training/` and `evaluation/` label and score moves/attacks. Production inference has no chess dependency; tests disable oracle imports at runtime.
- Learned legality is conditional on a joint categorical observation. It is not a proved conjunction of movement, context and safety. The explicit unary attack → exposure → negative-legality chain can add counterevidence; no absence-of-attacks safety theorem is asserted.
- All six piece grammars and structural castling/EP/promotion edits exist. Seen special-move examples have native conditional proofs, but full compositional/history semantics remain blocked. Standard castling boundary conventions appear only in structural state/I/O code.
- Induction executes natively in the audit, but automated chess induction/population marginal estimation is not integrated. Training generalization is explicit host grouping by a finite typed relative schema plus native revision.
- Dependence groups are conservative: only the first observation per hypothesis/group contributes. Correlated conflicts remain in the ledger and are excluded from confidence updates. Positive/negative channels share evidence and are selected, never revised together.
- Sensor TV `(1, 0.99)` is an explicit FEN-reading assumption, not a measured calibration claim. Calibration is post-hoc validation-bin mapping for evaluation, with small-sample limitations.
- Bounded observations intentionally lose information. Unseen relative combinations abstain, and selective accuracy must be read alongside coverage. No claim of chess parity or useful playing strength is made.
- SWI-Prolog 10.0.1 (including Janus/PCRE) is a checked system prerequisite. Bootstrap downloads the exact PeTTa commit and installs pinned Python packages. Missing or mismatched native runtime exits explicitly.

## Validation and commands

```bash
bash scripts/bootstrap.sh
.venv/bin/pytest -q
.venv/bin/pln-chess runtime-audit
.venv/bin/pln-chess inspect --fen "7k/8/8/8/8/8/2R5/2K5 w - - 0 1" --move c2e2
.venv/bin/pln-chess invariance --fixture transfer-source --transform translate
.venv/bin/pln-chess evaluate --split heldout-transfer
.venv/bin/pln-chess benchmark --config configs/benchmark.json
.venv/bin/pln-chess serve --port 8765
```

Test suite: **61 passed in 24.54s**. Native audit passed: `True`. Invariance passed: `True`. Test output: `artifacts/pytest.txt`. Timing/peak memory/checkpoint size: `artifacts/benchmark.json`. Calibration: `artifacts/calibration.json`. Ablations: `artifacts/ablations.json`. Evidence replay demonstration: `artifacts/proofs/evidence-revision.json`.

## Files and next work

The exact authored-file inventory is `artifacts/file-manifest.json`. The user-provided plan is preserved. No commits, pushes, or deployment were performed.

1. Verify a native conjunction/generalized multi-premise rule in an appropriate upstream runtime before replacing categorical legality with compositional proofs.
2. Add native population-based induction with explicit marginal estimation and stronger dependence semantics.
3. Expand independent structural families and calibration data; quantify and reduce the observed abstention and false-legal rates.
4. Extend full-history and adversarial successor-state modeling; preserve unknown history.
5. Profile and optimize native batching/grounding while preserving proof/evidence identity.
