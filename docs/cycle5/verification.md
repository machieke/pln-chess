# Reproduction and verification scope

The delivery receipt at [verification.json](../../artifacts/cycle5/verification.json) records the exact final source, clean run, test count, runtime, model/dataset hashes, protected-file checks and UI sessions. [Manifest](../../artifacts/cycle5/manifest.json) hashes the delivered source, artifacts and documentation, excluding itself to avoid a circular hash. The final delivery commit is the commit containing that manifest.

From a fresh checkout, with the audited SWI-Prolog 10.0.1 installation available:

```bash
TMPDIR=/dev/shm bash scripts/cycle5_reproduce.sh
```

The script recreates pinned Python dependencies through `uv`, clones the pinned PeTTa revision when absent, verifies native library/backend hashes, reruns C4 baselines and native probes, generates the registered data, reconstructs the evidence/checkpoints, evaluates all splits/ablations, runs causal and counterfactual experiments, benchmarks reference/cold/warm execution, runs the complete test suite and generates the final reports. No `--resume` is used for the clean delivery. Missing native dependencies fail explicitly; SWI-Prolog is a checked system prerequisite rather than a silently substituted interpreter.

The original 194 tests were run before implementation and remain unchanged. Cycle 5 adds proof-gap, generated translation/color/renaming, replay/retraction/idempotency, checkpoint corruption, temporal trust/conflict/truncation, no-oracle, cache identity, combined-budget, runtime-error and inspector contracts. Full native candidate/proof parity is measured separately from aggregate metrics.

UI verification uses the ProofShot skill at `/home/purplezky/.codex/skills/proofshot/SKILL.md`. Completed sessions include C4/C5 raw comparison, unresolved knight premises, trusted metadata, event-backed EP scope, exhausted budget, malformed input clearing, exported JSON and a 390-pixel viewport. The runtime-error rendering is exercised with an explicitly identified browser response harness; the automated suite independently injects a real `NativeError` at the runtime boundary. The native library is not altered to manufacture a browser failure. One initial browser-start timeout is retained as a failed verification attempt, followed by successful isolated browser sessions.

The root filesystem had little free space. Large generated development/clean experiment outputs use `/dev/shm`; completed earlier disposable checkouts were relocated there with their original paths preserved. Earlier committed artifacts remain ordinary files and are hash-checked for immutability. Operational recordings/logs are kept separate from scientific native outputs.

Exact changed paths are listed in [changed-files.json](../../artifacts/cycle5/changed-files.json). No push, deployment, upstream modification or external-system change is part of this cycle.

## Executed delivery receipt

The final clean checkout at `/dev/shm/pln-chess-cycle5-clean-twosoy6q` ran source `f8b7834cc79ce495d3cf2c67019a91d7b5d08b8e` without resume, recreated its virtual environment and native checkout, and passed **227 tests**. The original 194 tests were unchanged. All **438 protected files** match the startup hashes. All 32 evaluation reports reproduce the development candidate rows, raw truth values, rule/evidence IDs, retained native proofs and complete move sets; models and dataset also match byte for byte. Timings and memory are fresh measurements.

The initial development full suite found three legacy inspector failures; the backend now accepts both file paths and in-memory models. Four targeted compatibility tests passed, then the clean experiment was restarted from the corrected commit. The interrupted first clean attempt and failed development log are retained; none of its outputs were reused for final delivery. The induction study also gained explicit native disabled/enabled/sham controls after its development run, so no byte equality is claimed for those two research artifacts.

Two completed ProofShot sessions retain eight screenshots and recordings. The failed initial browser-start attempt is retained separately. The final HTML matches the recorded source; the later backend compatibility change is covered by the clean suite. See the machine-readable [UI scope](../../artifacts/cycle5/ui-verification.json), [acceptance checklist](../../artifacts/cycle5/acceptance.json), and [chess coverage](chess-coverage.md).

The 1,974 reconstructed evidence events match after excluding their wall-clock `timestamp` field; every other event field is identical. Model and dataset bytes match exactly. Delivered XZ artifacts are losslessly repacked to reduce disk use; [artifact-encoding.json](../../artifacts/cycle5/artifact-encoding.json) records original/delivery sizes and the exact decompressed payload hash. Compression bytes can differ from a reproduction without changing any scientific result.
