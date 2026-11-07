# Reproduction and evidence manifest

Verified implementation: `a94b7816f0a97e253adc319acb4a8cb2f0e27996`. Python `3.12.12`; `SWI-Prolog version 10.0.1 for x86_64-linux`; PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`; PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`. PLN library SHA-256: `cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`.

The first clean study at `0eab14ca5dd6926549d9772dc73d9cfd668de526` completed all native evaluations, controls and benchmarks, then stopped on a report-only bootstrap-cluster sort involving mixed integer/string game IDs. The corrected source was checked in a second fresh checkout: pinned bootstrap, the full test suite, complete report analysis, acceptance and application smoke checks were rerun. Completed native studies were reused only after confirming identical production source, registration and model inputs. Original failure logs and command receipts are preserved under `development/clean-analysis-first-failure/`; `execution-lineage.json` records both source revisions. This was a recovered clean-copy study, not a claim of an uninterrupted first run.

```bash
git clone /path/to/pln-chess /data/pln-chess-cycle7-reproduction
cd /data/pln-chess-cycle7-reproduction
git checkout --detach a94b7816f0a97e253adc319acb4a8cb2f0e27996
C7_OUT=/data/pln-chess-cycle7-output bash scripts/cycle7_reproduce.sh
```

The clean-copy driver bootstraps pinned dependencies, runs the complete test suite, reexecutes all 33 C6 mode/split baselines, generates the deterministic game manifest, trains all independent-group budgets, executes the evaluation matrix and ablations, preserves negative/temporal controls, measures reference/cold/warm parity, verifies acceptance and runs actual API/CLI/inspector default smoke checks. Independent subprocesses are bounded to three; final timing runs are serial. The current host must provide SWI-Prolog 10.0.1 with Janus/PCRE and uv. Bootstrap records exact failures rather than substituting a Python inference engine.

`commands/*.json`, `logs/`, `bootstrap-context.json`, `pytest.txt`, and `verification.json` preserve actual execution outcomes. `manifest.json` hashes the committed evidence and reports. Runtime caches, virtual environments, temporary native query files and clean-clone working directories are generated and not committed. Each compressed report is lossless JSON, with ordered proof references into an interned native DAG.

Known limits: synthetic games are not external human-game validation; small sample intervals are exploratory; coarse backoff can generalize incorrectly; conditional positives do not prove global king safety; historical replay is structural; the native inventory is scoped to pinned signatures; no native joint introduction or distributional confidence extension is shipped.
