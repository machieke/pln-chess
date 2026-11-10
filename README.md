# PLN Chess

A piece-relative chess research package using **actual native MeTTa PLN** rules. It includes a pinned runtime audit, six-piece candidate grammar, structural special-move states, append-only evidence, native revision learning, inference/proof APIs, CLI, local inspector, datasets, tests, ablations and measured reports.

Cycle 12 adds eight typed experimental concept families, native conditional
proofs, dependency graphs, exact incremental fields, and replay of supplied
multi-move sequences. Start with the
[Cycle 12 engineering report](docs/cycle12/engineering-report.md),
[20-package matrix](docs/cycle12/package-matrix.md),
[legal promotion review](docs/cycle12/legal-promotion-review.md), and
[reproduction and interface guide](docs/cycle12/reproduction.md).
The legal default is gated by a source-bound acceptance receipt. Strategic
models remain experimental: structural packets and separate influence proofs
do not establish complete native pin, fork, overload or trapping theorems.
No strategic move selection or new native inference operator is introduced.

```bash
.venv/bin/python -m pln_chess serve --port 8765
.venv/bin/python -m pln_chess concept-inspect --input artifacts/cycle12/examples/concept-payload.json --output /tmp/pln-concept-proof.json
.venv/bin/python -m pln_chess field-evolution --input artifacts/cycle12/examples/sequence-payload.json --output /tmp/pln-sequence-proof.json
```

Open `http://127.0.0.1:8765/interactions` for concept, dependency and temporal
inspection. `/fields` and `/` retain the earlier field and legal inspectors.
Cycle 12's brief authorizes local commits only; no push or deployment is included.

Cycle 11 adds experimental learned attack, defense, ordinary mobility and
king-exposure relations, candidate successor fields, typed before/after
comparisons, and robust historical claim replay. Start with the
[engineering report](docs/cycle11/engineering-report.md),
[20-package matrix](docs/cycle11/package-matrix.md),
[relative ontology](docs/cycle11/potential-field-ontology.md), and
[reproduction and interface guide](docs/cycle11/reproduction.md).
Cycle 11 retained the accepted C8 legal checkpoint. Its isolated legal
experiment recovers both outstanding en-passant cases; original FEN-only
adversarial exact-set accuracy remains unchanged. Field conditionals have
native proofs, while field changes remain host diagnostics. No strategic
score, move selector or new native operator is introduced.

```bash
.venv/bin/python -m pln_chess field-inspect \
  --fen '7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1' \
  --piece a4 --family attack --move d4f5 --output /tmp/field-comparison.json
.venv/bin/python -m pln_chess history-claims --input supplied-claims.json --output /tmp/history-receipt.json
.venv/bin/python -m pln_chess serve --port 8765
```

Open `http://127.0.0.1:8765/fields` for the experimental inspector; the legal
inspector remains at `/`. Field and special-local checkpoints were experimental
and unpromoted in Cycle 11. Cycle 11 delivery includes local commits only, with no push or
deployment.

Cycle 10 evaluates the unchanged accepted C8 model on licensed external game
collections, transports supplied historical events, measures calibration under
distribution shift, and compares two experimental adaptations. Start with the
[Cycle 10 executive summary](docs/cycle10/executive-summary.md),
[engineering report](docs/cycle10/engineering-report.md),
[18-package matrix](docs/cycle10/package-matrix.md), and
[reproduction and interface guide](docs/cycle10/reproduction.md).
The default remains C8; new adaptation checkpoints are experimental. Native
positive composition remains incomplete; strategic fields were design work in Cycle 10.
Cycle 10 delivery uses local commits only, with no push or deployment.

```bash
.venv/bin/pln-chess external-report --section summary
.venv/bin/pln-chess external-report --section provenance
.venv/bin/pln-chess external-report --section calibration
.venv/bin/pln-chess serve --checkpoint artifacts/cycle10/model/C10-default.json
```

Cycle 9 retains the accepted C8 checkpoint and adds performance consolidation,
independent game and adversarial evaluation, empirical calibration diagnostics,
temporal provenance categories, and a formal composition decision. Start with the
[executive summary](docs/cycle9/executive-summary.md),
[engineering report](docs/cycle9/engineering-report.md),
[14-package matrix](docs/cycle9/package-matrix.md), and
[reproduction instructions](docs/cycle9/reproduction.md).
Calibration remains outside native inference; supported positive classifications
still carry partial proofs. The [architecture decision](docs/cycle9/architecture-decision.md)
does not authorize a new production operator. Cycle 9 delivery uses local commits
only, as required by its brief.

```bash
C9_OUT=/data/pln-chess-cycle9-output bash scripts/cycle9_reproduce.sh
.venv/bin/pln-chess research-report --section summary
.venv/bin/pln-chess calibration-export --output /tmp/cycle9-calibration.json
.venv/bin/pln-chess serve --port 8765
```

Cycle 8 adds learned relative promotion transitions, destination-aware evidence,
inspector comparisons of four checkpoints, and a separate mathematical proposal for
native multi-premise composition. Read the [engineering report](docs/cycle8/final-report.md),
[acceptance results](docs/cycle8/evaluation.md), [decision memo](docs/cycle8/decision-memo.md),
and [composition proposal](docs/cycle8/native-composition-proposal.md). No new native
operator is enabled; supported positive classifications still carry partial proofs.

```bash
C8_OUT=/data/pln-chess-cycle8-output bash scripts/cycle8_reproduce.sh
.venv/bin/pln-chess compare-generations --fen 'r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29' --move f7e8n
.venv/bin/pln-chess serve --port 8765
```

Use a fresh clone for clean Cycle 8 reproduction. The source-bound acceptance
receipt selects the operational default only after all registered gates pass.
[Reproduction instructions](docs/cycle8/reproduction.md) include the complete
evidence bundle, supplementary audits, real-browser verification and reporting
commands. [API details](docs/cycle8/architecture-and-api.md) describe schema 8,
proof status, modes and preserved historical checkpoints. Cycle 8 commits remain
local under its brief; no push is part of the delivery.

Cycle 7 is documented in the [engineering report](docs/cycle7/final-report.md), [bounded native feasibility result](docs/cycle7/native-feasibility.md), and [user decision memo](docs/cycle7/decision-memo.md). It adds versioned proof labels, a C6/C7 inspector comparison, offline active learning, bounded conditional backoff experiments, independent opening-family evaluation, and a source-bound operational-default receipt. Native positive composition remains unproved; rejected learning experiments remain separate from the accepted default.

```bash
C7_OUT=/data/pln-chess-cycle7-output bash scripts/cycle7_reproduce.sh
.venv/bin/pln-chess compare-cycles --fen '2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1' --move f6h5
.venv/bin/pln-chess inspect --checkpoint artifacts/cycle7/model/C7-default.json --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/python -m scripts.cycle7_witness 0
```

Use a fresh clone for the clean-bootstrap acceptance gate. The full Cycle 7 driver records commands and native transcripts, preserves prior-cycle artifacts, commits no generated runtime caches, and never pushes or publishes. [API migration](docs/cycle7/architecture-and-api.md) explains schema 7 and compatibility with earlier checkpoints.

**Coverage is native-partial.** The audited PLN core has no conjunction-introduction rule. This package learns conditional beliefs on typed relative observation categories and derives unary attack/exposure counterevidence. It does not claim a compositional proof of full chess legality. Read [the capability audit](docs/pln-compatibility-matrix.md), [coverage](docs/chess-coverage.md), and [measured final report](docs/final-report.md).

## Cycle 2: local relational transfer

Cycle 2 adds reusable ray/destination hypotheses, separate learned exposure evidence, guarded native induction, full B0–B7 comparisons, and native calculation caching with proof-parity checks. It remains **native-partial**; local conditional generalization is not a compositional legality theorem. See the [Cycle 2 report](docs/cycle2/final-report.md), [architecture](docs/cycle2/architecture.md), and [limitations](docs/cycle2/limitations.md), and [verification](docs/cycle2/verification.md).

```bash
bash scripts/cycle2_reproduce.sh
.venv/bin/pln-chess serve --port 8765 --checkpoint artifacts/cycle2/B1-model.json
```

This installs/verifies the same pinned dependencies and regenerates isolated Cycle 2 datasets, checkpoints, full-set evaluations, ablations, benchmarks, tests and reports. It preserves Cycle 1 artifacts and restores frozen inputs from checksummed repository archives when absent. Allow roughly 15–25 minutes for the full native baseline and comparisons. The inspector can compare B0, B1 and experimental B2 on one move and shows hierarchy, marginal premises, evidence overlap and abstention. B1 is the default Cycle 2 model; B2 induction is opt-in. Existing schema-1 checkpoints and commands remain supported.

## Reproduce the package

System prerequisites: Linux x86-64, Git, `uv`, and **SWI-Prolog 10.0.1 with Janus and PCRE** available as `swipl`. Python 3.12.12 is selected/downloaded by uv. No paid services or remote writes are needed. The bootstrap refuses missing/mismatched native dependencies with an explicit diagnostic; it never substitutes Python inference.

```bash
bash scripts/bootstrap.sh
```

This installs pinned Python packages, checks out the pinned PeTTa runtime locally, runs the native audit, regenerates fixtures, trains/replays evidence, writes native proof demonstrations, evaluates held-out move sets, runs ablations and benchmarks, runs tests, and produces reports. It can take several minutes. Native PLN is vendored verbatim under `vendor/pln/` with its license. PeTTa is fetched into ignored `.runtime/` and hash-checked.

## Inspect actual beliefs

```bash
.venv/bin/pln-chess runtime-audit
.venv/bin/pln-chess inspect --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/pln-chess infer --fen '2r4k/8/8/8/8/8/2R5/2K5 w - - 0 1' --format json
.venv/bin/pln-chess invariance --fixture transfer-source --transform translate
.venv/bin/pln-chess train --config configs/training.json
.venv/bin/pln-chess evaluate --split heldout-transfer
.venv/bin/pln-chess benchmark --config configs/benchmark.json
.venv/bin/pln-chess report --output artifacts/final-report.md
.venv/bin/pln-chess serve --port 8765
```

The inspector is available at `http://127.0.0.1:8765` while the last command runs. Select a move to see the board, raw TVs, relative observations, native proof graph, evidence IDs, runtime and budget. Leave the move empty to inspect the complete bounded candidate set. Stop it with Ctrl-C.

```python
from pln_chess.api import explain_move, infer_moves, compare_transforms

proof = explain_move(
    '7k/8/8/8/8/8/2R5/2K5 w - - 0 1',
    'c2e2', checkpoint='artifacts/model.json',
)
print(proof['candidate']['legal_move_truth_value'])
print(proof['candidate']['proof_trace'])
```

For learning, use `observe_example(..., source=..., dependence_group=..., ledger_path=...)` followed by `train(Ledger(path))`. Re-ingestion is idempotent. Checkpoints preserve native TVs and evidence lineage. `pln-chess replay --ledger artifacts/evidence.jsonl --through 10 --output artifacts/rollback.json` creates an earlier model without deleting evidence. Public contracts are in `src/pln_chess/api/`.

The delivered package also passed a [clean-copy bootstrap verification](docs/verification.md).

## Verify and read the results

```bash
.venv/bin/pytest -q
```

[Architecture](docs/architecture.md), [spatial semantics](docs/spatial-semantics.md), [learning semantics](docs/learning-semantics.md), [experiments](docs/experiments.md), [decisions](docs/decisions.md), and [model card](docs/model-card.md) explain the boundaries. `artifacts/` contains exact native traces, evidence/checkpoints, dataset/runtime manifests, complete-set metrics, calibration, ablations, timing/memory results, and test output. [Browser verification](docs/ui-verification.md) includes recorded desktop/mobile interactions and error handling. Tests distinguish trained demonstrations from held-out performance and prevent oracle calls in production inference.

A checkout is the supported distribution: install it editable, or set `PLN_CHESS_ROOT` to the checkout containing configs/vendor/runtime/artifacts. The Python package deliberately does not bundle system native interpreters into a wheel.
# Cycle 3

Cycle 3 adds separate condition beliefs, learned post-move and castling-transit exposure, a new contact curriculum, independent adversaries, and explicit history uncertainty. It remains a **native-partial** learner: the pinned runtime does not prove conjunction of movement and king safety.

```bash
bash scripts/cycle3_reproduce.sh
.venv/bin/pln-chess cycle3 --action audit
.venv/bin/pln-chess serve --port 8765 --checkpoint artifacts/cycle3/C3-full-model.json
.venv/bin/pln-chess counterfactual --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2 --operation add-blocker --square d2
```

See [Cycle 3 report](docs/cycle3-final-report.md), [architecture](docs/cycle3-architecture.md), [native audit](docs/cycle3-native-pln-audit.md), [learning semantics](docs/cycle3-learning-semantics.md), and [experiment protocol](docs/cycle3-experiments.md). Machine-readable results and per-candidate error ledgers are under `artifacts/cycle3/`. Earlier checkpoints, fixtures and artifacts remain supported and preserved. FEN alone does not establish en passant history; explicit predecessor handling is documented in the architecture.


## Cycle 5: strict premise proofs

Cycle 5 preserves native negative constraint proofs and makes positive composition gaps explicit. Default C5 emits **supported illegal or unknown** until a defensible global positive theorem exists. C4's supported local projections remain available for comparison; C5's zero legal recall is an explicit research failure, not improved precision.

Read the [engineering report](docs/cycle5/engineering-report.md), [native capability matrix](docs/cycle5/native-composition-matrix.md), [temporal trust modes](docs/cycle5/temporal-semantics.md), [model card](docs/cycle5/model-card.md), [API/CLI reference](docs/cycle5/api-cli.md), and [verification](docs/cycle5/verification.md). The new dataset separates clean local combination holdouts from comparisons containing the frozen C4 prior.

Reproduce with `TMPDIR=/dev/shm bash scripts/cycle5_reproduce.sh`. Inspect with `.venv/bin/pln-chess serve --checkpoint artifacts/cycle5/model/C5-full.json`. The Cycle 5 brief authorizes local commits only; no push is part of this delivery.

## Cycle 6: explicit proof modes

Cycle 6 restores useful C4 predictions while keeping their partial proof status visible. `operational` accepts learned conditional evidence and verified negative chains. `strict` abstains on positive moves without a complete native derivation. `experimental` isolates the existing-native composition investigation; no successful independent-premise conjunction is claimed.

```bash
bash scripts/cycle6_reproduce.sh
.venv/bin/pln-chess inspect --checkpoint artifacts/cycle6/model/C6-full.json --mode operational --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/pln-chess inspect --checkpoint artifacts/cycle6/model/C6-full.json --mode strict --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/pln-chess inspect --checkpoint artifacts/cycle6/model/C6-full.json --mode experimental --fen '2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1' --move f6h5
.venv/bin/pln-chess evaluate --checkpoint artifacts/cycle6/model/C6-full.json --mode operational --dataset artifacts/cycle6/datasets/dataset.json --split independent-games --output /tmp/c6-games.json.xz
.venv/bin/pln-chess benchmark --checkpoint artifacts/cycle6/model/C6-full.json --mode operational --positions artifacts/cycle5/benchmarks/positions.json --output /tmp/c6-benchmark.json
.venv/bin/pln-chess serve --checkpoint artifacts/cycle6/model/C6-full.json
```

All three modes retain the same raw native evidence channels. An unknown strict classification can carry strong local evidence: strength, confidence, and proof acceptance are different quantities. Public labels are `supported-legal`, `supported-illegal`, `unknown`, and `incomplete`; `legacy_classification` supports older metric consumers. Python accepts `explain_move(..., mode='operational')`, `infer_moves(..., mode='strict')`, and per-request batch modes. The inspector compares C4/C5/C6 and exports full diagnostic JSON.

A matching acceptance receipt enables operational as the C6 default only after the recorded gates pass. Missing or stale receipts retain strict. Earlier checkpoints keep their original semantics. Migrate a C5 checkpoint with `pln-chess migrate-model --checkpoint artifacts/cycle5/model/C5-full.json --output /tmp/c6.json`.

See [the Cycle 6 report](docs/cycle6/final-report.md), [mode contracts](docs/cycle6/architecture.md), and [native capability audit](docs/cycle6/native-capability-audit.md). Reproduction writes versioned output and never pushes. A fully fresh clone is required to independently satisfy the clean-bootstrap promotion gate.

For a subsequent Cycle 6-only change, `C6_BASELINE_FROM=/path/to/previous/output bash scripts/cycle6_reproduce.sh` can reuse the exact executed C4/C5 baselines. This is fail-closed: runtime, protected inputs, and all frozen inference/evaluation sources must match byte for byte. The receipt explicitly records reuse and the original execution commit; the default command reruns the baselines.
