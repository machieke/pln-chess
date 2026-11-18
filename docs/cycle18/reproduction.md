# Reproduction levels

The first three levels use compact checked-in records and the pinned runtime.
They do not require historical bulk evidence or the TCEC PGN. Complete historical
preservation is a separate level. The clean reproduction receipt distinguishes
reuse of verified Python/native dependencies from a fresh dependency installation.

Start from the delivered branch, optionally using a sparse partial clone to
avoid large historical artifacts:

```bash
git clone --depth 1 --filter=blob:none --no-checkout \
  --branch cycle18-shared-parameter-contract \
  ssh://git@github.com/machieke/pln-chess /path/to/c18
git -C /path/to/c18 sparse-checkout init --cone
git -C /path/to/c18 sparse-checkout set \
  src research training evaluation knowledge configs vendor scripts tests \
  artifacts/cycle17 artifacts/cycle18 docs/cycle18
git -C /path/to/c18 checkout cycle18-shared-parameter-contract
```

Follow the existing repository dependency/runtime setup, retaining the runtime
lock: PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1` and PeTTa
`ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`. When reusing a verified environment
from another checkout, bind imports and resources to this checkout explicitly:

```bash
export PLN_CHESS_ROOT="$PWD"
export PYTHONPATH="$PWD/src:$PWD"
```

**1. Source-bound contract example.** Inspect
[the decisive example](../../artifacts/cycle18/contract/mappings/decisive-example.json)
and run the mapping tests. The example gives actual original artifact hashes and
locators, an environment, one evaluation vector and its two conditional aliases.

```bash
.venv/bin/python -m pytest -q tests/test_cycle18_contracts.py
```

**2. Complete finite reference/control suite.** Use a new output directory; the
CLI refuses to overwrite an existing generation or write into operational paths.
This maps all 432 rows, validates all six checkpoint/ledger memberships and 144
revision receipts, runs 72 grid/arm/model fits with sharp marginal-coupling
witnesses, and executes replay/application/conflict controls. It launches no
native processes. Original revision receipts are read, never reestimated.

```bash
.venv/bin/python -m research.cycle18 contract --out /tmp/c18-contract-new
.venv/bin/python -m pytest -q tests/test_cycle18_reference.py \
  tests/test_cycle18_replay.py tests/test_cycle18_isolation.py
```

**3. Decisive native replay.** This reexecutes exact original inputs for six
primary/overlap arms and the eleven-stamp witness, then recursive, duplicate,
diamond, cycle and dependence controls. Evaluation-oracle access is disabled.
Exact programs, stdout/stderr, process receipts, selections, retained statements
and stamps are retained. Fired-rule parents remain unobserved.

```bash
.venv/bin/python -m research.cycle18 native --out /tmp/c18-native-new
.venv/bin/python -m pytest -q tests/test_cycle18_native.py
```

The [clean reproduction receipt](../../artifacts/cycle18/reproduction/verified.json)
executes the full contract and native commands in a clean checkout at the
[frozen executable source](../../artifacts/cycle18/source-provenance.json),
`66a0ff66fa9dbb0e133421aeb4686e885e2aba45`. Its audit hook denies PGN and Cycle
14–16 artifact reads. The historical eleven-stamp input is already preserved as
a compact Cycle 17 witness. Existing verified dependencies are reused; this
is not a fresh dependency install or a second full historical campaign.

**4. Complete historical preservation.** Use a nonsparse checkout at the frozen
source and restore the registered historical evidence. The existing preparation
helper can link already verified ignored Cycle 14 evidence from this workspace:

```bash
.venv/bin/python -m scripts.cycle16_delivery prepare --path /path/to/clean/source
.venv/bin/python -m scripts.cycle18_preservation \
  --source /path/to/clean/source --out /path/to/new/preservation --workers 6
```

The unchanged driver runs the entire test suite, all 206 legal shards/584,112
candidate rows, 287 removal controls, 27 history controls, both en-passant
recoveries and 76 legal holdouts, then compares every canonical native proof.
It requires a clean source checkout and the actual registered acceptance panels.
Successful same-source receipts can be resumed; incomplete/failed receipts
must remain visible. Targeted tests do not substitute for this gate.

After the full test suite and negative/history controls completed, one spare
worker ran distant, unstarted tail shards with the unchanged
`scripts.cycle16_tail_workers` helper. It uses the same frozen source, standard
worker commands and receipt format. The six-worker main driver remains
responsible for all 206 comparisons, reusing successful same-source tail receipts.
During overlap with recovery, at most eight top-level commands were active.
This scheduling change alters neither inference nor acceptance criteria.
Timed job totals include tail work; the separate sampled main-process tree
excludes that independently launched worker and must not be added to job totals.
The worker completed 12 distant shards successfully; its
[scheduling receipt](../../artifacts/cycle18/preservation/tail-scheduling.json),
[launch](../../artifacts/cycle18/execution/tail-launch.json) and
[completion](../../artifacts/cycle18/execution/tail-finished.json) retain the
exact jobs and frozen source identity.

Local bulk evidence is retained under
`/home/purplezky/cycle18-evidence-20261117`, with checksummed packs and a verified
restore. Packs are not downloadable from GitHub and must be obtained separately
from the workspace owner for full receipt/proof inspection. Existing transport
commands use the committed manifest:

```bash
.venv/bin/python -m scripts.cycle15_evidence restore \
  --root /path/to/restored-c18 --packs /path/to/c18-packs \
  --manifest publication/cycle18/manifest.json
.venv/bin/python -m scripts.cycle15_evidence verify \
  --root /path/to/restored-c18 --manifest publication/cycle18/manifest.json
```

Original local execution paths are provenance, not download links. Resolve bulk
paths relative to the manifest's original root after relocation. All decisive
reference cases and native raw records are also in ordinary Git at relative
paths, so the principal result is inspectable without that local directory.

One development native replay stopped after two successful stage executions
because the reporting loop selected the last JSON-key-ordered stage (Clear)
instead of Attack for the diagnostic. The original inputs/results were retained;
the stage lookup was corrected **before source freeze**, and the complete
development, frozen and clean-reproduction replays were then run. This was a
reporting error, not a native policy or outcome change. No failed development
run is counted as complete acceptance.

A subsequent identity review found that equal posteriors could conceal different
admitted component masks. The corrected generation includes those masks and
payload hashes, with a regression test. No model, grid, query or numeric result
changed. The initial full preservation run at `9dc9159d` was explicitly stopped
after nine successful job receipts; one nonzero interrupted receipt and all
partial outputs are retained. None of those jobs is reused at the final source.
The complete acceptance restarts at `66a0ff66`. The registered replay ceiling
was transparently amended from 200 to 300 before the required reruns; finite
model, CPU and publication limits did not change.

Initial outputs are retained under `source-correction-001` in the local evidence
root. Its `relocation.json` explains how to resolve old receipt paths to that
archive rather than to the newer generation now occupying the original output
prefixes. Original receipts are not rewritten. Interrupted CPU is reported as
completed-job measurements and separately sampled lower bounds, not silently
counted as a successful full run.

The [final preservation receipt](../../artifacts/cycle18/preservation/cycle18-verification.json)
records 771 passing tests, all 206 shards/584,112 rows with unchanged classifications
and exact canonical proofs, 287 removal controls, 27 history controls, both
recoveries and 76 holdouts. The post-run historical recheck also passed. The
[resource receipt](../../artifacts/cycle18/resources.json) separates 222 retained
research native invocations from preservation commands and comparison sampling;
the [engineering report](engineering-report.md) states measured costs and coverage
limits. All 1,956 files in the local evidence manifest were actually restored and
verified. A separate post-push compact reproduction adds 44 native invocations
outside that sealed census, for an expected combined 266 under the amended 300
ceiling; its actual result is recorded in the external publication receipt.
