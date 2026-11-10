# Cycle 11 reproduction

Starting source: `fe9e28edc03184fee02ec535399768fd9d5883fa`. The original accepted checkpoint, runtime locks, datasets and historical artifacts remain byte-identical. The unchanged-source baseline executes the original 399 tests, 287 negative controls, 26 historical suites, 48 Cycle 9 shards and 132 frozen/history Cycle 10 shards. [baseline/reproduction-receipt.json](../../artifacts/cycle11/baseline/reproduction-receipt.json).

The current implementation was bootstrapped into `/data/pln-chess-cycle11-verified` with fresh dependencies and the pinned native runtime. It passed 463 tests and the same complete native acceptance replay; every candidate's proof, value, rule/evidence lineage and predicted set matches the original. [current/verified.json](../../artifacts/cycle11/current/verified.json); [current/proof-parity.json](../../artifacts/cycle11/current/proof-parity.json).

The new research stages also executed independently in the fresh checkout: data regeneration, native field/legal learning, held-out field evaluation, all transformations/transfers/examples and temporal controls. Model bytes, datasets, every frozen field metric/proof row and worked native relations matched exactly. [clean-research/verified.json](../../artifacts/cycle11/clean-research/verified.json). This reuses the already executed unchanged-source baseline by its receipt; it is not a second full end-to-end baseline run.

To inspect a field with the delivered checkpoint:

```bash
.venv/bin/python -m pln_chess field-inspect \
  --fen '7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1' \
  --piece a4 --family attack --move d4f5 --output /tmp/field-comparison.json
.venv/bin/python -m pln_chess history-claims --input supplied-claims.json --output /tmp/history-receipt.json
.venv/bin/python -m pln_chess serve --port 8765
```

The local browser route is `http://127.0.0.1:8765/fields`; the existing legal inspector remains at `/`. Public Python callers use `pln_chess.api.inspect_fields` and `replay_history_claims`. A candidate comparison returns separate legal status, before/after relations and diagnostic differences. The field checkpoint remains experimental even when the separate candidate is supported legal.

The staged reproduction entry point is `scripts/cycle11_reproduce.py`. Use a new output, checkout, baseline-snapshot and browser-work directory. The driver preserves command logs, return codes and source identities; it reuses the exact bundled licensed source bytes rather than reacquiring games. Timings and capture metadata may differ. Dataset/model/native proof identities are the reproducible scientific objects.

```bash
.venv/bin/python -m scripts.cycle11_reproduce \
  --out /data/pln-chess-cycle11-replay-output \
  --checkout /data/pln-chess-cycle11-replay-checkout \
  --baseline /data/pln-chess-cycle11-replay-baseline \
  --browser-work /data/pln-chess-cycle11-replay-browser
```

The required system tools are the pinned SWI-Prolog runtime prerequisites, Python/bootstrap dependencies, `zstd` for bundled PGN data, and ProofShot/browser tooling for the UI phase. Plotting uses the explicitly selected plotting interpreter. No GitHub push, external deployment, new operator or upstream modification is part of reproduction.

Executed stage receipts, their source hashes and any retained failed development attempts are distinguished in [delivery status](../../artifacts/cycle11/delivery.json). A supplied driver is not by itself evidence of a second complete end-to-end run. The delivery receipt states exactly which clean-checkout stages actually executed.
