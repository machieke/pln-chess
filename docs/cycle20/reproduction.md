# Reproduction

From a checkout of this branch, use the project's pinned Python 3.12.12 environment, PeTTa runtime and SWI-Prolog 10.0.1. The existing bootstrap entry point is `bash scripts/bootstrap.sh`. Publication verification reused installed dependencies and checked their hashes and executable versions. It did not perform a new dependency installation.

```bash
export PLN_CHESS_ROOT="$PWD"
export PYTHONPATH="$PWD/src:$PWD"
C20_RUN=$(mktemp -d)
.venv/bin/python -m research.cycle20 batch --out "$C20_RUN/batch" --meter "$C20_RUN/meter"
.venv/bin/python -m research.cycle20 combined --out "$C20_RUN/combined" --meter "$C20_RUN/meter"
.venv/bin/python -m research.cycle20 continuation --out "$C20_RUN/continuation" --meter "$C20_RUN/meter"
.venv/bin/python -m research.cycle20 correction --out "$C20_RUN/correction" --meter "$C20_RUN/meter"
.venv/bin/python -m research.cycle20 history --out "$C20_RUN/history" --meter "$C20_RUN/meter"
.venv/bin/python -m research.cycle20 residency --out "$C20_RUN/residency" --meter "$C20_RUN/meter"
```

Each command writes an immutable verified.json and its supporting state or wire records. These six examples use the published fixture constructor and compact Cycle 19 learned models. They need no private proof packs. The same entry point provides controls, refit, anchors, comparison-A, comparison-BC and benchmark. The complete archive comparison additionally needs the 2,512 original proofs and archived rows identified in the Cycle 19 local evidence manifest. The benchmark uses a fresh output generation and a quiet machine.

The full historical gate requires the project's historical inputs, including the restored Cycle 14 evidence in its expected layout, and a clean source checkout. The inherited driver runs the full pytest suite, legal shards, negative/history controls, recoveries and holdouts, then compares canonical proofs. Its historical scope string names the cycle that introduced the driver. Its source_head field identifies the actual checkout.

```bash
C20_GATE=$(mktemp -d)
C20_TEST_METER="$C20_GATE/meter" .venv/bin/python -m scripts.cycle15_preservation \
  --out "$C20_GATE/preservation" --source "$PWD" --workers 6
```

With the local packs available, restore and verify them in a new directory using the unchanged content-addressed transport.

```bash
.venv/bin/python -m scripts.cycle15_evidence restore --root "$C20_GATE/restored" \
  --packs "$C20_PACKS" --manifest publication/cycle20/manifest.json
```
