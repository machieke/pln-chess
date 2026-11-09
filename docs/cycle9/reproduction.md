# Reproducing Cycle 9

Verified native-study source: `d26228d6064b52d8b769e3253c02793d264ebf7d`. Qualified application source: `898e17856fc2b15d1dd0b378c8d7239be5dc9cff`. Starting baseline: `36b5ea10395c0f41de4c03824ba6f8ee1c5dbad1`. Runtime: Python 3.12.12, SWI-Prolog 10.0.1, PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`, PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`. Dependencies and native file hashes are pinned and verified. The host must supply uv and the audited SWI-Prolog build; no Python inference fallback exists.

```bash
git clone /path/to/pln-chess /data/pln-chess-cycle9-replay
cd /data/pln-chess-cycle9-replay
git checkout --detach d26228d6064b52d8b769e3253c02793d264ebf7d
C9_OUT=/data/pln-chess-cycle9-replay-output bash scripts/cycle9_reproduce.sh
```

Use a fresh checkout without `.venv` or `.runtime` and a fresh output directory outside the checkout. From scratch, the driver executes the original C8 snapshot, regenerates data exactly, runs all tests/controls, historical regressions, new evaluation shards, serial paired benchmarks, analysis, source-bound acceptance and actual API/CLI smoke checks. Command receipts and logs retain source identities, parameters, exit status and duration. Interrupted shards resume only with matching production/driver/data/model identities and artifact hashes.

The delivered run bootstrapped at `682237b5a0aacf8495eb56fd1393150f05e0d3d4`, then advanced cleanly to `d26228d6064b52d8b769e3253c02793d264ebf7d` before any new native study execution. The exact dataset-replay gate exposed a checkout-name-dependent path filter; its correction changed only the offline generator and its test. The production hash did not change. The failed dataset and logs are preserved under `development/clean-path-audit-failure`. [Bootstrap transition](../../artifacts/cycle9/bootstrap-context.json).

A second fresh checkout at the exact corrected study commit independently passed dependency bootstrap, identical runtime/production hashes, and exact registered dataset replay. Both its initial and final working trees were clean. This closes the bootstrap-source distinction without pretending the first failed invocation succeeded. [Fresh corrected-source receipt](../../artifacts/cycle9/fresh-source-bootstrap/verified.json), [commands](../../artifacts/cycle9/fresh-source-bootstrap/commands.json). The full native study is the main recorded run; this supplemental check does not claim a second execution of all native evaluations.

For this delivery, the original baseline replay and original serial benchmark were completed before source edits in an isolated original checkout, then copied into the fresh study output with their original source/command receipts. The optimized regressions, new cohorts, controls and tests ran against the fresh pinned runtime. Its complete runtime manifest matches the pre-edit runtime. The from-scratch command above reruns both sides when no preexisting receipts are supplied.

The final mobile check exposed overflow from the 64-character report hash. Source `898e17856fc2b15d1dd0b378c8d7239be5dc9cff` adds one CSS wrapping attribute. Every other production byte, including native inference, acceptance and JavaScript, is identical to the executed native study. The original verifier rechecked every native gate; all 365 tests and actual API/CLI smoke were rerun on the corrected source before browser verification. Native evaluations and timings were reused only after that exact one-attribute equivalence check. [Source equivalence](../../artifacts/cycle9/presentation/source-equivalence.json), [qualification](../../artifacts/cycle9/presentation/verified.json), [original receipts](../../artifacts/cycle9/presentation/native-study/), [current test log](../../artifacts/cycle9/presentation/pytest.txt).

After the study, use the delivery checkout (with its dependencies installed using `bash scripts/bootstrap.sh --dependencies-only` if necessary), the reproduced output, and an environment with matplotlib 3.7.5 for figures. The supplemental bootstrap uses another fresh checkout. The presentation qualification rejects any production change beyond the exact CSS attribute and reruns the full tests before restoring the source-bound operational default:

```bash
.venv/bin/python -m scripts.cycle9_bootstrap_check --source "$PWD" --checkout /data/pln-chess-cycle9-bootstrap-replay --out /data/pln-chess-cycle9-replay-output
.venv/bin/python -m scripts.cycle9_presentation --out /data/pln-chess-cycle9-replay-output --study-checkout /data/pln-chess-cycle9-replay
python3 evaluation/cycle9_plots.py --out /data/pln-chess-cycle9-replay-output
C9_OUT=/data/pln-chess-cycle9-replay-output TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle9_ui_verify --out /data/pln-chess-cycle9-replay-output --work /data/pln-chess-cycle9-browser
cp -a /data/pln-chess-cycle9-replay-output/. artifacts/cycle9/
.venv/bin/python -m evaluation.cycle9_reporting --out artifacts/cycle9
```

Browser verification requires ProofShot, agent-browser and Chromium. It records real requests, screenshots, video, actual JSON export hashes and owned-server cleanup; it publishes nothing. The report renderer hashes artifacts and documents, excluding the manifest itself. Wall times, timestamps and videos are naturally run-specific; dataset/model identities and semantic proof equality are the deterministic reproduction gates.
