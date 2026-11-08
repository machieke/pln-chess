# Clean reproduction and evidence manifest

Verified native study source: `4453b46217319fdbf22ac1d344c20111758798af`. Starting baseline: `c6ee658352395abe6e276cafdf1ddf59830a17a0`. Python 3.12.12; SWI-Prolog version 10.0.1 for x86_64-linux; PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`; PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`. PLN SHA-256 `cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`.

```bash
git clone /path/to/pln-chess /data/pln-chess-cycle8-reproduction
cd /data/pln-chess-cycle8-reproduction
git checkout --detach 4453b46217319fdbf22ac1d344c20111758798af
C8_OUT=/data/pln-chess-cycle8-output bash scripts/cycle8_reproduce.sh
```

The host must supply uv and audited SWI-Prolog 10.0.1 with Janus/PCRE. Bootstrap creates a fresh Python environment and pinned PeTTa checkout. The driver creates a separate original-C7 checkout and runs baseline imports from it; changed C8 code never silently regenerates the historical baseline. It then generates/trains deterministic C8 data/models, runs the entire test suite, laboratory, forensics, evaluation arms, controls, serial benchmarks, analysis, acceptance and actual application smoke checks. Independent subprocesses are bounded to three. No Python inference fallback exists.

The clean checkout bootstrapped at `40548ddef74680d4f623269957dcd9856754e8c0` and advanced while the isolated original-C7 workers ran to `4453b46217319fdbf22ac1d344c20111758798af` before any C8 execution. This committed change fixes explicit benchmark-mode routing and adds reports; dependency/native pins are unchanged. Every C8 test, training, inference, benchmark and acceptance subprocess executes the latter clean source. Both revisions and the clean transition are retained in `bootstrap-context.json`.

The original pre-edit baseline and development failures remain separately under `development/`. The clean baseline reruns all 38 evaluations using the freshly bootstrapped runtime. `configs/cycle8-replay.json` records pre-study dataset/model sentinels; verification requires exact replay. Commands, logs, bootstrap context, full tests and source hashes are recorded under `commands/`, `logs/`, `bootstrap-context.json`, `pytest.txt` and `verification.json`.

After the clean study completes, return to the delivery checkout (which contains the final reporting and browser helpers) and use the same newly reproduced output:

```bash
.venv/bin/python -m scripts.cycle8_supplement --out /data/pln-chess-cycle8-output
TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle8_ui_verify --out /data/pln-chess-cycle8-output --work /data/pln-chess-cycle8-ui-replay
cp /data/pln-chess-cycle8-ui-replay/owned-server.{py,json} /data/pln-chess-cycle8-output/ui/
# Refresh the repository delivery bundle while retaining its development evidence.
cp -a /data/pln-chess-cycle8-output/. artifacts/cycle8/
.venv/bin/python -m evaluation.cycle8_reporting --out artifacts/cycle8
```

The browser step requires ProofShot, agent-browser and Chromium. Its real form interactions, export Blob hash, video and screenshots are retained. The standalone native `.metta` witnesses contain the original library path; when moving them, replace only that import path with the pinned local `vendor/pln/lib_pln.metta`.

`manifest.json` hashes the delivered artifacts and reports; it excludes itself to avoid a circular hash. Lossless `.json.xz` reports use ordered proof references into interned native DAGs. Virtual environments, native caches, temporary query files and clean checkouts are generated but not committed. All Cycle 8 commits are local; this brief prohibits a push.
