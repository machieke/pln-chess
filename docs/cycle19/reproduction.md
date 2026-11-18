# Reproduction

Use Python 3.12.12 and the pinned runtime in `configs/runtime-lock.json`: PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`, PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`, SWI-Prolog 10.0.1. The recorded clean-checkout verification reuses verified dependencies. It is not evidence of a fresh dependency installation; `scripts/bootstrap.sh` documents that separate path.

Run from a checkout of the published Cycle 19 branch. Set the source explicitly if reusing an editable virtual environment. Choose a new external output directory for every command; never target a source checkout or sealed historical evidence. A shared meter counts research invocations and refuses the 4,001st reservation.

```bash
export PLN_CHESS_ROOT="$PWD"
export PYTHONPATH="$PWD/src:$PWD"
C19_RUN="$(mktemp -d /tmp/pln-cycle19.XXXXXX)"

# Compact measured episodes, native learning/consequences, actual refits/lifecycle.
.venv/bin/python -m research.cycle19 compact --out "$C19_RUN/compact" --meter "$C19_RUN/meter"

# Complete registered measurement, learning, evaluation and correction study.
.venv/bin/python -m research.cycle19 study --out "$C19_RUN/study" --meter "$C19_RUN/meter" --workers 4

# Measurement alone; no native inference is needed.
.venv/bin/python -m research.cycle19 measure --out "$C19_RUN/measurement" --meter "$C19_RUN/meter"

# Repeat lifecycle controls using a completed study's frozen measurements/models.
.venv/bin/python -m research.cycle19 lifecycle --input "$C19_RUN/study" --out "$C19_RUN/lifecycle" --meter "$C19_RUN/meter"

# Compact historical native anchors, including shared/disjoint/overlap/recursion.
.venv/bin/python -m research.cycle19 anchors --out "$C19_RUN/anchors" --meter "$C19_RUN/meter"

# Explicit current-position probability interpretation.
.venv/bin/python -m research.cycle19 reference --out "$C19_RUN/meaning" --meter "$C19_RUN/meter"
```

The `fit` and `evaluate` commands also accept `--input` naming a study-shaped generation with `measurement/` and, for evaluation, `learning/`. They emit fresh generations. Do not run every full control repetition blindly against one meter: repeated full fits consume its registered budget. The compact run needs neither the source PGN nor historical bulk proofs; the full census reproduction requires the licensed archive already present in the repository.

Full historical preservation is separate and much more expensive. Use a clean source checkout with the existing Cycle 14 evidence restored or verified dependency links prepared, then run:

```bash
.venv/bin/python -m scripts.cycle19_preservation --source "$PLN_CHESS_ROOT" --out "$C19_RUN/preservation" --workers 6
```

That command runs the full test suite, 206 legal shards, removal/history/recovery/holdout controls and exact proof comparison. Historical evidence-pack restoration uses the unchanged `scripts/cycle15_evidence.py` transport and the relevant `publication/cycle*/manifest.json`; bulk packs were not uploaded. For the final package's read-only hash/gate check, run `.venv/bin/python -m scripts.cycle19_acceptance` after all tracked compact evidence is present.

Schemas distinguish native strength/confidence, offline measurements, classification errors, unidentified probabilities and execution completeness. No CLI command changes operational defaults or promotes an experimental model.
