# Compact proof contract

The Cycle 14 inspection API is opt-in and requires an explicit `ProofStore`. It builds one endpoint at a time, interns the native traces and observations, and retains only the projections needed for later comparisons. The response root contains typed references to endpoint objects. It does not first construct the full duplicated legacy response.

Each object is canonical JSON with a versioned SHA-256 domain. Dictionary keys are sorted; list order and repeated occurrences remain intact. Distinct evidence bindings produce distinct objects even when their native arithmetic and truth values agree. This is host storage and indexing, not a persistent native reasoning graph.

The `summary` view exposes separate legality and preference conclusions, uncertainty, model/runtime identities and durable proof handles. `proof_graph` returns bounded pages of objects and dependencies. `full_archive` returns the complete standalone object set, its manifest hash and the exact canonical expanded-response hash. `canonical_chunks` streams the legacy JSON when that representation is explicitly requested. Import verifies every object, dependency and reconstructed hash atomically. Missing and corrupt objects are errors, including after a previously successful read.

For equivalence to Cycle 13, comparisons exclude only `execution` and `incremental` telemetry. Every native expression, ordered premise, evidence occurrence, conclusion, graph identity and provenance binding remains in the comparison. Individual archives retain their execution metadata and support exact reconstruction without exclusions.

Request identities bind full observed state, supplied history, candidates, branches and horizons, source provenance, all checkpoint identities, runtime manifest, source code and inference options including budgets. A cache hit reuses the immutable proof request and reports delivery telemetry separately. It does not claim a faster native interpreter. Incomplete requests have their own bound options and cannot satisfy a request with different budgets.

SQLite transactions batch object insertion, commit durably and support retrieval after process restart. Standalone archives permit reconstruction in another empty store. The retained decoded cache is bounded; integrity is checked from durable bytes once per distinct object within each expansion operation. Summary retrieval checks its root and immutable request binding; full graph/archive retrieval checks all reached objects.

Immediate and temporal native integration tests compare reconstructed Cycle 14 output with independent Cycle 13 execution. Storage tests exercise repeated evidence, literal reference-looking user objects, tampering, missing objects, failed atomic import, restart retrieval and request invalidation. Performance targets remain unclaimed until the registered isolated benchmark has run.
