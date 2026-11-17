# Reproducing Cycle 16

Use the repository's Python 3.12 environment and pinned native runtime. Run from
the repository root with `.venv/bin/python`; no dependency upgrade or download
is required when the existing environment and historical evidence are present.
Choose a fresh output directory for each run: experiment records and checkpoints
refuse overwrite. The cycle introduces no operational CLI or model change.

## Small executable cases

```bash
.venv/bin/python -m research.cycle16 minimal --out /tmp/c16-minimal
.venv/bin/python -m research.cycle16 compare --out /tmp/c16-compare
.venv/bin/python -m research.cycle16 occupancy --out /tmp/c16-occupancy
.venv/bin/python -m research.cycle16 learned --out /tmp/c16-learned \
  --checkpoint artifacts/cycle16/learning/learned/model.json
```

These execute the native stamp failure, matched R/F/F-minus comparison, all nine
occupancy states for each of three slider kinds, and learned support. Full raw
native records are stored under each output's `raw/` directory; JSON results link
their hashes. `--proof-mode summary` reduces terminal display while retaining
the raw evidence. The direct operator witness is labeled separately from the
experimental derivation.

For an observed state JSON using the exact Cycle 15 raw schema:

```bash
.venv/bin/python -m research.cycle16 infer --state /path/to/state.json \
  --attacker attacker_id --target target_id --arm F \
  --steps 64 --tasks 128 --beliefs 256 --timeout 15 --out /tmp/c16-request
```

An optional `--move /path/to/move.json` accepts only a supplied displacement with
`id`, `piece`, and `destination`. It produces separately reasoned before/after
states; it does not choose or validate a move. `--arm L` requires a matching
`--checkpoint`. Missing entities remain invalid query domains, and unknown
occupancy is never converted to emptiness. Every request loads the whole arm.

Python callers use
`research.cycle16.experiments.infer(state, attacker, target, arm="F", ...)`.
The response includes target semantics, raw observations, scope identity,
knowledge/checkpoint identities, Clear/Attack/Exposure channels, native stamps,
classification, support/incomplete reasons, proof status and budget usage.
`proof_mode="summary"` omits bulky native transcripts from the returned value;
use the full mode to persist exact inputs and outputs. No strategic score or
best-move field exists.

## Learning and held-out evaluation

The committed [registration](../../artifacts/cycle16/corpus-registration.json)
contains the 42 selected game episodes, their frozen splits and source hash.
`research.cycle16.corpus.register(destination)` regenerates it from the existing
TCEC PGN using the registered first-compatible-pair selection, without attack
labels. Give a new destination; never rewrite the original registration.

```bash
TASK_OUT=/path/to/new/c16-evidence
.venv/bin/python -m training.cycle16_paths --out "$TASK_OUT/learning"
.venv/bin/python -m evaluation.cycle16_paths --out "$TASK_OUT/evaluation" \
  --learning "$TASK_OUT/learning" --workers 2
.venv/bin/python -m pytest -q tests/test_cycle16_*.py
```

Training generates learned, prior, shared-chain, duplicate-replay and leave-one-
source checkpoints. All use new structure identities; no historical checkpoint
is rehashed to impersonate compatibility. The exact declaration, stable rule
identity, admitted source ancestry and revision receipts are retained. Source
timestamps and receipt paths can change ledger/checkpoint versions on replay;
compare parameters, declarations and ancestry rather than timing-bearing hashes.

Additional executable controls are
`research.cycle16.evidence_audit.dependencies(out)`,
`research.cycle16.panel.interventions(out)`,
`research.cycle16.panel.structural(out)`, and
`research.cycle16.panel.budgets(out, learning_directory)`.
The shared-chain variable-bearing witness can be replayed after creating that
budget report with
`python -m scripts.cycle16_audit shared_witness --out "$TASK_OUT"`.
The separate bounded-controls command verifies Query compatibility, retention
pressure and an actual timeout.

## Full preservation and clean source scope

The source-bound implementation freeze is `86b7760d`. The exact historical
206-job manifest is reused; all candidate rows and canonical native proofs are
compared. Restore missing Cycle 14 evidence using its existing local manifest
before running this gate. The driver requires a clean Git checkout, verified
runtime/environment and historical evidence; it does not infer acceptance from
previous summaries.

```bash
.venv/bin/python -m research.cycle16 preservation \
  --source /path/to/clean/source-checkout \
  --out /path/to/new/c16-preservation --workers 4
```

The supplied delivery helper can link existing verified dependencies and missing
ignored Cycle 14 evidence into a fresh worktree:
`python -m scripts.cycle16_delivery prepare --path /path/to/clean/source-checkout`.
Tracked files always come from Git. The clean reproduction receipt separately
covers minimal native diagnostics, CLI comparison and an actual native refit.
It does not claim a fresh dependency installation or second full corpus run.

## Performance and local evidence

After competing preservation work stops:

```bash
.venv/bin/python -m evaluation.cycle16_performance \
  --checkpoint artifacts/cycle16/learning/learned/model.json \
  --out /path/to/new/c16-performance
```

The seven native workloads each use ten repetitions and three fresh native
processes per request, one for each stage. Cached retrieval and full proof
reconstruction are measured separately and execute no native inference.

Bulk evidence stays at `/home/purplezky/cycle16-evidence-20261117`. The Cycle 16
manifest uses the unchanged Cycle 15 transport schema, with Cycle 16 pack names.
It can be restored and checked using the existing tool:

```bash
.venv/bin/python -m scripts.cycle15_evidence restore \
  --root /path/to/restored-c16 --packs /path/to/c16-packs \
  --manifest publication/cycle16/manifest.json
.venv/bin/python -m scripts.cycle15_evidence verify \
  --root /path/to/restored-c16 --manifest publication/cycle16/manifest.json
```

Manifest paths and checksums are authoritative. Raw receipts retain original
source-bound paths; resolve them relative to `original_local_root` after moving
the pack set. Historical receipts are not rewritten for relocation. No pack,
release, branch or artifact is remotely published by this cycle.
