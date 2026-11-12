# Compact proof contract

The Cycle 14 inspection API is opt-in and requires an explicit `ProofStore`. It builds one endpoint at a time, interns the native traces and observations, and retains only the projections needed for later comparisons. The response root contains typed references to endpoint objects. It does not first construct the full duplicated legacy response.

Each object is canonical JSON with a versioned SHA-256 domain. Dictionary keys are sorted; list order and repeated occurrences remain intact. Distinct evidence bindings produce distinct objects even when their native arithmetic and truth values agree. This is host storage and indexing, not a persistent native reasoning graph.

The `summary` view exposes separate legality and preference conclusions, uncertainty, model/runtime identities and durable proof handles. `proof_graph` returns bounded pages of objects and dependencies. `full_archive` returns the complete standalone object set, its manifest hash and the exact canonical expanded-response hash. `canonical_chunks` streams the legacy JSON when that representation is explicitly requested. Import verifies every object, dependency and reconstructed hash atomically. Missing and corrupt objects are errors, including after a previously successful read.

For equivalence to Cycle 13, comparisons exclude only `execution` and `incremental` telemetry. Every native expression, ordered premise, evidence occurrence, conclusion, graph identity and provenance binding remains in the comparison. Individual archives retain their execution metadata and support exact reconstruction without exclusions.

Request identities bind full observed state, supplied history, candidates, branches and horizons, source provenance, all checkpoint identities, runtime manifest, source code and inference options including budgets. A cache hit reuses the immutable proof request and reports delivery telemetry separately. It does not claim a faster native interpreter. Incomplete requests have their own bound options and cannot satisfy a request with different budgets.

SQLite transactions batch object insertion, commit durably and support retrieval after process restart. Standalone archives permit reconstruction in another empty store. The retained decoded cache is bounded; integrity is checked from durable bytes once per distinct object within each expansion operation. Summary retrieval checks its root and immutable request binding; full graph/archive retrieval checks all reached objects.

Immediate and temporal native integration tests compare reconstructed Cycle 14 output with independent Cycle 13 execution. Storage tests exercise repeated evidence, literal reference-looking user objects, tampering, missing objects, failed atomic import, restart retrieval and request invalidation. Performance targets remain unclaimed until the registered isolated benchmark has run.

## Requests and responses

Run `.venv/bin/python -m pln_chess serve --port 8765` and open `/compact-preferences`. `C14_OUT` selects the research artifact directory; `C14_PROOF_STORE` selects the durable SQLite file. Defaults are `artifacts/cycle14` and `.runtime/cycle14/proofs.sqlite` under the repository root. The trained aliases require the delivered model registry.

Use the direct URL `http://127.0.0.1:8765/compact-preferences`: the legacy legal homepage does not render the intended navigation link. This known entry-navigation limitation is recorded in the [browser note](../../artifacts/cycle14/ui/final-trained/navigation-note.json); direct access and the compact inspector's functional workflows are verified separately.

| Request field | Contract |
| --- | --- |
| `fen` | Required observed position; coordinates identify the environment, not a learned preference key |
| `move_a`, `move_b` | Required explicit UCI candidates for immediate comparison |
| `branches` | For continuations, an object with `A` and `B`; each holds one to three supplied move lists including the candidate as the first move |
| `horizons` | Supplied endpoint horizons, normally `[2, 3]`; missing endpoints remain incomplete |
| `history` | Optional supplied structural history, bound into request identity |
| `unknown_squares` | Optional list of explicitly unobserved squares |
| `preference_model` | `frozen-c13` (default), `empty`, `primary-immediate`, or `primary-temporal` |
| `mode` | Separate legal mode: `operational`, `strict`, or `experimental` |
| `max_invocations`, `timeout` | Native work and wall-time limits; unfinished work is exposed in execution status |
| `sensor_confidence`, `max_candidates`, `incremental` | Explicit observation/query options included in cache identity |
| `selection_provenance` | Continuation-source description; it does not assert an optimal response |
| `view` | `summary` (default), `proof_graph`, or `full_archive` |

Unknown request fields, including reference labels and engine scores, are rejected. Immediate requests reject continuation fields. [Immediate example](../../artifacts/cycle14/examples/compare.json) and [continuation example](../../artifacts/cycle14/examples/continuations.json) are controlled input examples, not held-out successes.

The immediate response schema is `compact-pairwise-inspection-v14`. It contains separate `legality.A` and `legality.B` beliefs, `preference.channels`, `actor`, `horizon`, model/runtime identities, `execution`, `proof_handle`, `proof_root` and `delivery`. Preference statuses are `A-preferred`, `B-preferred`, `indeterminate` or `incomplete`; supported contradictions are flagged separately. `conditional_proof_complete` does not imply `joint_proof_complete`. The continuation response retains its immediate comparison, each branch/horizon comparison, branch coverage and unexamined responses; `global_robust_preference` is null and `automatic_move_selection` is false. A preference is never permission to play an unknown or illegal move.

| HTTP route | Operation |
| --- | --- |
| `GET /cycle14-catalog` | Experimental model aliases and registered non-final observations |
| `POST /cycle14-compare` | Immediate JSON request |
| `POST /cycle14-continuations` | Supplied-branch JSON request |
| `GET /cycle14-proof?handle=…&view=…&offset=0&limit=64` | Durable summary, paginated objects or standalone archive |
| `POST /cycle14-expand` | Upload an archive or full response; validate and return exact reconstructed JSON |
| `GET /cycle14-research-reference?id=…` | Separate offline research display; never an inference input |

Reconstruction returns exact `Content-Length`, `X-Proof-Legacy-SHA256` and `X-Proof-Root` headers after verification. Upload the original archive bytes; JavaScript parse/stringify can change floating-point lexemes. Missing or corrupt proof content produces an explicit error. Full-archive HTTP uploads are bounded at 128 MiB.

## Python and CLI examples

The lower-level `pln_chess.cycle14.api.compare_moves` takes explicit legal, field, concept, fork and preference checkpoints plus a `ProofStore`. `pln_chess.cycle14.temporal.analyze_continuations` takes the same model dependencies and supplied branches. The inspector wrapper resolves the versioned experimental aliases while retaining the unchanged accepted legal model:

```python
from pln_chess.cycle14.inspector import inspect, proof
from pln_chess.cycle14.proofs import ProofStore

payload = {
    "fen": "4k3/8/8/8/8/8/8/R3K3 w - - 0 1",
    "move_a": "a1a2", "move_b": "a1b1",
    "preference_model": "primary-immediate", "max_candidates": 2,
}
with ProofStore("/tmp/pln-c14-proofs.sqlite") as store:
    summary = inspect(payload, store=store)
handle = summary["proof_handle"]
with ProofStore("/tmp/pln-c14-proofs.sqlite") as reopened:
    page = proof(handle, store=reopened, view="proof_graph", offset=16, limit=16)
    archive = proof(handle, store=reopened, view="full_archive")
```

The CLI accepts the same JSON payloads and performs each operation in a separate process. Replace `HANDLE_FROM_SUMMARY` with the returned durable handle:

```bash
.venv/bin/python -m pln_chess compact-compare --input artifacts/cycle14/examples/compare.json --store /tmp/pln-c14-proofs.sqlite --output /tmp/pln-c14-summary.json
.venv/bin/python -m pln_chess proof-view --handle HANDLE_FROM_SUMMARY --store /tmp/pln-c14-proofs.sqlite --view proof_graph --offset 16 --limit 16
.venv/bin/python -m pln_chess proof-view --handle HANDLE_FROM_SUMMARY --store /tmp/pln-c14-proofs.sqlite --view full_archive --output /tmp/pln-c14-archive.json
.venv/bin/python -m pln_chess proof-expand --input /tmp/pln-c14-archive.json --output /tmp/pln-c14-reconstructed.json
```

[Executed CLI receipts](../../artifacts/cycle14/interfaces/verified.json) and [browser receipts](../../artifacts/cycle14/ui/verified.json) bind the delivered source and models. Existing Cycle 13 comparison commands remain available.
