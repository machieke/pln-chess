# Clean reproduction and inspection

The starting f4 checkout was independently bootstrapped with a fresh environment/runtime and fully replayed.
It reproduced 463 tests, 26 historical suites, 48 Cycle 9 shards, 132 Cycle 10 shards,
287 negative controls and the Cycle 11 research package. The implementation was then independently bootstrapped
at `ae7411b2bd697015e5d675043a7be6ded2ad9b43` in `/data/pln-chess-cycle12-current-v2`. Its final source remained clean throughout the recorded runs.

The current-source run passes 534 tests and all the same native legal cohorts with exact proof parity.
A separate clean research replay regenerates data, trains both concept models and reruns all concept, counterfactual,
dependence, interaction and sequence experiments: 55 model/artifact comparisons pass.
Both concept checkpoint files are byte-identical. Research equality excludes execution/cache metadata and the legacy
`legal_candidates.peak_process_rss_kib` resource measurement in trapping diagnostics. Both raw memory measurements are retained;
their initial 40 KiB difference and the narrowed comparison correction are recorded separately. All proof and inference fields remain compared.
The research replay reuses the already passed baseline receipt; it does not claim a second baseline execution within that replay.
The complete command below is supplied for future fresh replay; the delivered execution used its separately logged stages.

From a committed clean final checkout, choose new absolute paths on a disk with sufficient room for native proof artifacts:

```bash
TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle12_reproduce \
  --out /data/new-cycle12-output \
  --checkout /data/new-cycle12-source \
  --baseline /data/new-cycle12-baseline \
  --browser-work /data/new-cycle12-browser
```

This performs a fresh locked bootstrap, starting baseline, registered training/evaluation, complete legal review,
recovery/history/removal controls, current-source regression, native boundary checks, clean research replay,
source-bound promotion, accepted-default tests, isolated performance and browser verification.
`--skip-browser` explicitly records an incomplete delivery. Do not run benchmarks alongside native study workers.
The requirements and runtime lock hashes are recorded in each bootstrap receipt. PLN is pinned to
`4405956947c4b53c7ff01bd565aa3b114bc970a1`, PeTTa to `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`.
The authoritative dependency and runtime file hashes are in the bootstrap manifest.

To use the inspector after acceptance:

```bash
.venv/bin/python -m pln_chess serve --port 18782
# Open http://127.0.0.1:18782/interactions
.venv/bin/python -m pln_chess concept-inspect --input artifacts/cycle12/examples/concept-payload.json --output /tmp/pln-concept-proof.json
.venv/bin/python -m pln_chess field-evolution --input artifacts/cycle12/examples/sequence-payload.json --output /tmp/pln-sequence-proof.json
```

`GET /cycle12-catalog` provides bounded examples. `POST /cycle12-fields` accepts a position, selected source,
field family, candidate edit and explicit roles or bounded candidate enumeration. `POST /cycle12-evolution`
accepts a `sequence` object with an initial FEN and explicit ordered events. Unknown inputs and exhausted proof budgets
remain visible. The existing legal and Cycle 11 field APIs remain available; their explicit checkpoint contracts are unchanged.
Python exports are `pln_chess.api.inspect_interactions` and `pln_chess.api.replay_field_evolution`.
Candidate enumeration is bounded and structural; absence from that set is not a negative concept conclusion.
The example payloads contain only supplied inputs. Both new CLI commands were executed and their native output packages are retained
in [cli-smoke/verified.json](../../artifacts/cycle12/cli-smoke/verified.json); the reproduction runner regenerates these examples under its output directory.

Final browser verification uses ProofShot with an owned local server, actual browser interaction, screenshots/video,
zero console/server errors and a captured export whose bytes match the server result. The owned server and recorder are stopped.
On phones the compact graph scrolls horizontally inside its panel; selecting an edge opens its full record in the proof pane.
The initial interrupted/low-contrast development capture is retained, followed by the corrected passing development and final captures.
Historical artifacts are immutable: all 7959 protected files retain their starting hashes.

Evidence: [baseline/reproduction-receipt.json](../../artifacts/cycle12/baseline/reproduction-receipt.json), [current/verified.json](../../artifacts/cycle12/current/verified.json),
[current-bootstrap-v2/verified.json](../../artifacts/cycle12/current-bootstrap-v2/verified.json), [clean-research/verified.json](../../artifacts/cycle12/clean-research/verified.json),
[final-tests/verified.json](../../artifacts/cycle12/final-tests/verified.json), [ui/verification.json](../../artifacts/cycle12/ui/verification.json), [manifest.json](../../artifacts/cycle12/manifest.json).

Starting commit: `f4a9fd5536d001fa8830773012dcd578443b0b61`. Validated production freeze: `ae7411b2bd697015e5d675043a7be6ded2ad9b43`.
Production hash: `76b645e833a27c711d1b6ee503ff7382cbffc44b431669c38dcabd7acd1dc359`. Later commits contain reports/artifacts/driver improvements without changing production source.
The final delivery commit is necessarily recorded by the repository's history and final response rather than self-embedded in this file.
All commits are local; no GitHub push, external deployment or upstream edit is performed.

```text
eaa847f Register Cycle 12 studies and fresh Cycle 11 baseline replay
23839bf Register Cycle 12 concept families, sequence references and full legal review
443eee9 Specify Cycle 12 proof, temporal and incremental regression contracts
9ae1c59 Implement typed concept packets, dependency graphs and supplied field evolution
e666ad9 Add complete Cycle 12 studies, promotion gates and browser verification drivers
9051c69 Bind delivery acceptance to executed evidence and expose graph edge provenance
9f999f4 Complete replay entry point and clarify control and measurement accounting
32a0f3b Measure legal inference separately in each realistic performance workload
f953eb7 Withhold edit-legality diagnostics on incomplete motif boards before fitting
e5f2ec0 Record complete fresh Cycle 11 baseline and locked Cycle 12 bootstrap
50c989c Validate Cycle 12 learned concepts, dependency parity and temporal studies
ae7411b Verify Cycle 12 inspector graph contrast and mobile interactions
cff2f29 Add consolidated delivery reporting and verify Cycle 12 CLI contracts
691cf60 Tighten default identity checks and document measured research limits
e0a0c57 Compare research semantics independently of measured process memory
f4e7f1a Reproduce Cycle 12 research and frozen en-passant recovery gates
c822858 Verify frozen candidate history and negative evidence controls
408b329 Report explicit error and abstention rates across Cycle 12 panels
a03124c Verify final package hashes and avoid mutating the reproduction manifest
c8281ae Preserve complete current-source legal regressions and exact native proof parity
18fd0d0 Verify frozen legal candidate across all 206 regression jobs
8cc8202 Promote verified en-passant checkpoint and validate the accepted default
8c442fb Clarify the scope of child-process memory measurements
98b54cf Record all 42 isolated Cycle 12 benchmark workers
f7e9612 Verify final inspector workflows and desktop and mobile layouts
57ddeed Verify benchmark completeness against an independent native temporal replay
```
