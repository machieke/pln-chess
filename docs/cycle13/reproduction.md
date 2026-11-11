# Reproducing the frozen Cycle 13 package

The starting commit is `b000898a0a1f46e556f161982f2c0e6d3944c322`. Production source was frozen at `3e5aae6b6e4989cc8f0a5ad4eafcbd7df352f9dc`, with code hash `7ac9cac3ef48d9c48c48681d03cd56a472b12d3cbc861865afc9df3d3dbdec8b`. Later commits add only offline orchestration, evidence and documentation. This report was generated from local content commit `200e22f4a4d15e60bad4d4e1832992d5489917c3`; the final delivery commit is available with `git rev-parse HEAD` and is stated in the delivery message.

Starting reproduction passed 534 tests, 206 legal shards and 584,112 ordered candidate proofs. The current fresh checkout passes 584 tests, every shard, 287 negative controls, 27 history controls, two recoveries and 76 holdouts with exact native proof parity. The final post-acceptance test run passes 588 tests. The accepted legal checkpoint remains byte-identical to Cycle 12.

The final full suite is partitioned by complete modules across 4 isolated pytest processes, each with its own temporary and cache directories. Collection identities, command logs and JUnit reports verify that every collected item executes exactly once, with no failures, errors or skips.

A second fresh checkout regenerated all 340 pair labels, 120 endpoint labels, 400 complete native feature artifacts, fork learning, all preference fits, ablations, controls and concept results. 527 artifacts compare exactly under the documented semantics; model checkpoints are byte-identical. The pinned offline reference engine rebuilt to the exact registered executable hash. The source checkout remained clean.

Execution counters and incremental flags, and wall-clock timestamps on ledger records, are the only exclusions from research semantic comparison. Raw telemetry remains archived. No ordered native expression, premise, truth value, graph, label, rule or evidence identity is excluded. Bootstrap pins Python dependencies, native runtime and PLN source; no upstream source was edited.

For a new run, use a new output directory and checkout path. The commands below are offline orchestration from an already bootstrapped package checkout; replace paths and `<local-commit>` explicitly. Never overwrite prior evidence generations.

```bash
bash scripts/bootstrap.sh --dependencies-only
.venv/bin/python -m scripts.cycle13_clean_research run --out artifacts/cycle13 --generation /data/c13-research-new-output --checkout /data/c13-research-new-source --commit <local-commit> --workers 4
.venv/bin/python -m scripts.cycle13_clean_research compare --out artifacts/cycle13 --generation /data/c13-research-new-output
.venv/bin/python -m evaluation.cycle13_cli --out /data/c13-research-new-output/run
.venv/bin/python -m evaluation.cycle13_performance --out /data/c13-research-new-output/run
.venv/bin/python -m pytest -q
```

The delivered output is the comparison reference. `--generation` names a new replay directory, so the reproduction driver creates its fresh source checkout, copies only its six explicitly listed source/baseline inputs into the new run and regenerates every research output. CLI and performance outputs above also go into that new generation. Run the commands sequentially, and start performance only after other native jobs finish; the driver refuses reused benchmark receipts.

The complete command receipts include actual arguments, checkout identities and logs. The baseline/current legal replay drivers are `scripts.cycle13_baseline` and `scripts.cycle13_regression`; both use the unchanged 206-job panel. Boundary, legal acceptance and complete-delivery drivers require their complete prerequisite receipts in a new package output root. Do not rerun those writing commands against the delivered reference directory. The executed command records and linked receipts document the complete delivery sequence.

Browser verification uses the [ProofShot skill](/home/purplezky/.codex/skills/proofshot/SKILL.md), with a dedicated agent-browser session and `--run` server capture. Its screenshots, video, logs and exact downloaded response are retained. The download instrumentation merely grants the recording context permission to save the actual UI export; it does not alter application data.

Evidence: [baseline/reproduction-receipt.json](../../artifacts/cycle13/baseline/reproduction-receipt.json), [current/verified.json](../../artifacts/cycle13/current/verified.json), [clean-research/verified.json](../../artifacts/cycle13/clean-research/verified.json), [clean-research/comparison.json](../../artifacts/cycle13/clean-research/comparison.json), [final-checks/verified.json](../../artifacts/cycle13/final-checks/verified.json), [ui/verification.json](../../artifacts/cycle13/ui/verification.json).
