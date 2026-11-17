# Reproduction

The small native comparison uses checked-in fixtures, models and rules; it does
not require historical bulk evidence or the source PGN. The separate full legal
verification requires restored historical evidence. Both use the pinned runtime,
not an upgrade. Follow the repository's existing dependency/runtime setup first.

```bash
.venv/bin/python -m research.cycle17 minimal --out /tmp/c17-minimal
.venv/bin/python -m research.cycle17.reference_cli --out /tmp/c17-reference.json
.venv/bin/python -m pytest -q tests/test_cycle17_*.py
```

Use new output directories: evidence receipts and checkpoints are immutable.
`minimal` executes S-AA, S-BB, D-AB, D-BA, one/half-overlap, learned-clearance and
prior arms. Each Clear/Attack query starts from raw facts and the full registered
knowledge set in a fresh native process. It retains exact programs, stdout,
selected tasks, returned beliefs, stamps, process measurements and separate
guard/structural diagnostics. Diagnostic operator results never replace answers.

The [published witness index](../../artifacts/cycle17/witnesses/index.json) points
to exact native and guard outputs for decisive arms, including the historical
eleven-stamp case. Original programs contain their execution-root paths; use the
CLI to generate correct paths in a relocated checkout. Compact summaries retain
original local proof paths for bulk records, which are resolved through the
manifest described below rather than mistaken for remotely accessible files.

Actual native refitting and the complete new evaluation use the committed root
manifest. Training/reference label preparation uses the installed python-chess
dependency; native held-out inference cannot call that oracle.

```bash
C17_OUT=/path/to/new/c17-evidence
.venv/bin/python -m training.cycle17_shared_evidence --out "$C17_OUT/learning"
.venv/bin/python -m evaluation.cycle17_shared_evidence \
  --learning "$C17_OUT/learning" --out "$C17_OUT/evaluation" --workers 2
.venv/bin/python -m evaluation.cycle17_shared_evidence --historical \
  --learning "$C17_OUT/learning" --out "$C17_OUT/historical-evaluation" --workers 2
.venv/bin/python -c 'from research.cycle17.controls import run; import sys; run(sys.argv[1],sys.argv[2])' \
  "$C17_OUT/controls" "$C17_OUT/learning"
```

Refitting should preserve parameters, declarations and actual ancestry. Timing
and process paths can change ledger/checkpoint hashes; compare the scientific
content rather than claiming timing-bearing generations are byte-identical.
To regenerate the 54-root registration, call
`research.cycle17.corpus.register(new_destination)` against the existing licensed
TCEC PGN identified by the committed source hash. Never overwrite the frozen
registration. Historical evaluation is explicitly regression evidence.

The [clean reproduction receipt](../../artifacts/cycle17/reproduction/verified.json)
records a clean checkout, native minimal arms, an actual D-AB refit and the
separate reference command. An audit hook rejects reads of historical Cycle
14–16 artifact directories and PGN files during minimal inference/refit. Existing
verified runtime and Python dependencies are reused; this is not a fresh
dependency installation or a second full research-corpus run.

For full preservation, check out the frozen source commit recorded in
[source provenance](../../artifacts/cycle17/source-provenance.json), restore
historical Cycle 14 ignored evidence, and prepare the existing verified environment:

```bash
.venv/bin/python -m scripts.cycle16_delivery prepare --path /path/to/clean/source
.venv/bin/python -m scripts.cycle17_preservation \
  --source /path/to/clean/source --out /path/to/new/preservation --workers 6
```

The unchanged established driver executes the actual 206-job manifest, full
pytest suite, removal/history controls, recoveries and holdouts, then compares
all canonical native proofs. It requires a clean source checkout. Same-source
successful receipts can be resumed; failed or partial evidence must be retained
and explicitly accounted for. A smoke test does not substitute for this gate.

The initial execution sessions ended with reported status 143 (SIGTERM). The
first evaluation attempt completed no root; its partial raw requests are retained
in `evaluation-interrupted-001` and excluded from final endpoint metrics. The
first preservation attempt completed eight successful legal command receipts and
no completed failing receipt. Its partial logs and termination clarification are
retained under `preservation/interrupted-001`. Individual child exit statuses
were not captured. The detached resumed run reuses only those successful
same-source receipts and reruns unfinished jobs, including the full test suite.
Final acceptance requires the complete resumed population and proof comparison.

Run benchmarks separately from competing study jobs:

```bash
.venv/bin/python -m evaluation.cycle17_performance \
  --learning artifacts/cycle17/learning --out /path/to/new/performance
```

Bulk packs are local at `/home/purplezky/cycle17-evidence-20261117/packs`; they
are not uploaded. Obtain these files separately from the workspace owner for
full proof replay. Check all files against the committed manifest:

```bash
.venv/bin/python -m scripts.cycle15_evidence restore \
  --root /path/to/restored-c17 --packs /path/to/c17-packs \
  --manifest publication/cycle17/manifest.json
.venv/bin/python -m scripts.cycle15_evidence verify \
  --root /path/to/restored-c17 --manifest publication/cycle17/manifest.json
```

The transport schema is unchanged. Resolve original receipt paths relative to
the manifest's `original_local_root` after relocation; historical receipts are
not rewritten. Final acceptance binds compact evidence, source and reports;
remote publication is independently verified after the final commit.
