# Architecture and API migration

Schema 7 wraps the frozen schema-6 checkpoint without relabeling its learned rules. The source model first evaluates every candidate. Optional backoff applies only to its unknown candidates and never replaces an existing specific local hypothesis, including low-confidence or disputed ones. It tries exact, ray-contents-masked, then destination-and-ray-masked relative categories. A second native C6 inference pass evaluates those selected candidates; the combined budgets remain bounded. All TV revision, implication and negation still run in the pinned native library.

This backoff is a learned conditional over a host projection. It is not independent-premise composition or a Boolean chess legality test. Coarse hypotheses cannot displace any supported frozen positive or negative. Strict and experimental modes do not execute the optional backoff pass. Their positive-proof behavior remains frozen. If operational backoff has not been evaluated in a strict request, its cross-mode comparison is explicitly null with `evaluated: false`.

| `proof_status` | Meaning |
|---|---|
| `native-compositional` | Reserved; no current candidate receives this label. |
| `native-unary/partial` | Used as `premise_proof_status` for independently executed partial premises, not a complete move conclusion. |
| `learned-conditional` | Operational positive with an actual LocalAdmissibility derivation; global safety remains unproved. |
| `negative-supported` | A supported negative with its native constraint proof. |
| `unknown` | The candidate conclusion is not accepted; diagnostic native TVs remain available. |
| `incomplete` | Budget/runtime failure, distinct from an epistemic abstention. |

Schema 6 keeps its original proof labels. Schema 7 declares `proof_status_schema: proof-status-v7`, retains `legacy_proof_status`, and preserves raw TVs and full native trace fields. Every candidate includes selected backoff level, learned/grounded rule IDs and evidence lineage. Decision nodes are explicitly host policy. Their metadata is separate from the native DAG. A native confidence is not a calibrated legality probability.

API `explain_move`, `infer_moves` and `analyze_batch` accept both schemas. `pln_chess.cycle7.api.compare_cycles` returns actual C6/C7 results in the selected mode, with complete native proofs, supporting/contradicting premises, evidence groups and abstention reasons. The inspector uses the same application contract; its export retains both comparison results.

The default remains operational only through a matching acceptance receipt bound to the production source hash, runtime, registration, model versions and executed checks. The C7 receipt can separately attest the preserved C6 model without altering the immutable C6 acceptance artifact. An explicit C6_OUT override remains isolated. Missing, incomplete or mismatched receipts fail closed to strict.

```bash
.venv/bin/python -m pln_chess inspect --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/python -m pln_chess inspect --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2 --mode strict --format json
.venv/bin/python -m pln_chess compare-cycles --fen '2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1' --move f6h5
.venv/bin/python -m pln_chess serve --port 8765
```

Absolute coordinates remain at the input/environment boundary. Model projections contain relative motion, occupancy, ray content and existing temporal/boundary observations. No chess oracle is imported by production inference. Oracle labels occur only in training/evaluation. The seeded geometric candidate grammar remains an inductive bias rather than a discovered rule set.
