# PLN Chess — Cycle 20 Codex Implementation Brief

## Reusable Native Belief States and Multiple Queries

**Repository:** https://github.com/machieke/pln-chess  
**Required baseline:** `7c06d8e15972e5db2e0932160102dda329c304ab`  
**Baseline branch:** `cycle19-measured-chess-consequences`  
**Target branch:** `cycle20-native-belief-workspaces`

---

## 1. Execution mandate

Implement and deliver the complete Cycle 20 package.

This assignment includes implementation, bounded capability experiments, evaluation, preservation, documentation, commits, push, and independent publication verification.

Continue through delivery. Do not stop after proposing an architecture or implementing only the first successful optimization.

The user explicitly authorizes:

- Reading the repository and its existing evidence.
- Implementing the research modules, adapters, tests, and documentation described here.
- Creating a dedicated feature branch or isolated worktree.
- Running the registered experiments and required preservation checks.
- Creating local commits.
- Pushing the completed feature branch to `machieke/pln-chess`.
- Independently verifying the remote SHA.
- Reproducing compact examples from the published checkout.

No additional confirmation is needed for these actions.

This assignment does not authorize:

- Modifying the native truth-value calculus.
- Weakening `StampDisjoint`.
- Replacing native inference with host inference.
- Changing the accepted operational model.
- Updating the default branch.
- Force-pushing or rewriting published history.
- Publishing tags, releases, deployments, or bulk evidence uploads.

Resolve routine implementation choices autonomously. If a capability is unsupported, preserve the decisive evidence, implement the permitted fallback, and complete the remaining packages.

Read applicable repository instructions first. Preserve unrelated local work. If the requested branch already exists, inspect its ancestry and continue only from a compatible tip. Otherwise use a new dedicated branch and record the reason.

---

## 2. Purpose

The project’s purpose is a truth-valued relational network in which native PLN rules perform the core reasoning about chess.

Python may:

- Import and validate positions.
- Construct permitted observations.
- Manage evidence identities and generations.
- Schedule native execution.
- Transport native state.
- Assemble reports and visual projections.
- Cache already established results.

The native runtime must continue to perform:

- Rule application and binding.
- Truth-value computation.
- Derivation of intermediate and terminal consequences.
- Selection of answers from native retained beliefs.

Cycle 20 should move from repeatedly reconstructing an isolated inference request toward a reusable native belief state.

The central demonstration is:

> Load one consistent relational state, derive native consequences once, answer several questions from the resulting beliefs, then replace the state after a relevant correction and verify the replacement against fresh computation.

This is a systems and representation cycle. It does not need new chess accuracy, new rule structures, probability calibration, or a repaired shared-evidence calculus.

---

## 3. Baseline findings and required reading

Inspect these files at the required baseline:

- `docs/cycle19/engineering-report.md`
- `docs/cycle19/native-results.md`
- `docs/cycle19/targets-and-measurements.md`
- `docs/cycle19/corpus-and-transfer.md`
- `docs/cycle19/evidence-lifecycle.md`
- `docs/cycle19/architecture-decision.md`
- `docs/cycle19/reproduction.md`
- `docs/cycle19/publication.md`
- `research/cycle19/native.py`
- `research/cycle19/lifecycle.py`
- `research/cycle19/learning.py`
- `research/cycle19/measurements.py`
- `research/cycle15/native_reasoner.py`
- `research/cycle15/observations.py`
- `research/cycle16/experiments.py`
- `knowledge/cycle16/finite_two.metta`
- `vendor/pln/lib_pln.metta`
- `configs/runtime-lock.json`

Published entry points:

- [Cycle 19 report](https://github.com/machieke/pln-chess/blob/7c06d8e15972e5db2e0932160102dda329c304ab/docs/cycle19/engineering-report.md)
- [Current native adapter](https://github.com/machieke/pln-chess/blob/7c06d8e15972e5db2e0932160102dda329c304ab/research/cycle15/native_reasoner.py)
- [Current observation constructor](https://github.com/machieke/pln-chess/blob/7c06d8e15972e5db2e0932160102dda329c304ab/research/cycle15/observations.py)
- [Pinned native library](https://github.com/machieke/pln-chess/blob/7c06d8e15972e5db2e0932160102dda329c304ab/vendor/pln/lib_pln.metta)

Carry forward these distinctions accurately:

1. Cycle 19 demonstrated native parameter learning and bounded consequence inference.
2. Positive terminal composition succeeded for disjoint training assignments.
3. Shared training ancestry still blocked the positive terminal chain.
4. Negative influence results came from the supplied obstruction rule.
5. Direction invariance was supported by the relative representation and supplied templates.
6. Clearance and influence were measured separately.
7. Native confidence remains uncalibrated.
8. Each current consequence request still makes separate native derivations for Clear and Attack.
9. The existing journal and cache are host-managed.
10. Generic recursive rule reuse remains unresolved.

Verify the pinned runtime and accepted-model identities rather than assuming them.

Expected runtime:

- PLN: `4405956947c4b53c7ff01bd565aa3b114bc970a1`
- PeTTa: `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`
- Python: `3.12.12`
- SWI-Prolog: `10.0.1`

Expected accepted legal checkpoint:

- File SHA-256: `5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8`
- Semantic identity: `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`

Investigate unexpected mismatches before treating them as a valid baseline.

---

## 4. Native execution opportunity

In the existing derive-mode adapter, `PLN.Derive` operates on facts and rules without receiving the requested query.

The adapter subsequently selects an answer from the returned beliefs using the existing native confidence-selection expression.

Cycle 19 repeats that derivation separately for Clear and Attack over identical inputs.

The first implementation must therefore:

1. Construct the same ordered facts, rules, and initial tasks.
2. Execute native derivation once.
3. Materialize the returned task and belief tuples.
4. Perform several native selections over that same result.
5. Return a shared derivation receipt and individual readout records.

A Clear/Attack request normally needs three native selections:

- Clear.
- Attack.
- NoAttack.

It does not need three derivations.

One process does not by itself prove one derivation. Deferred evaluation may recompute an expression. Verify actual native work through selected-task traces and execution counters.

---

## 5. Nonnegotiable boundaries

### 5.1 Preserve native semantics

Do not modify:

- Native truth formulas.
- `StampDisjoint`.
- Native rule matching.
- Native answer-selection semantics.
- The supplied domain rule structures.
- The accepted operational checkpoint or default behavior.

Do not:

- Create fresh evidence stamps per query, ray, batch, or rule application.
- Strip shared ancestry.
- Reinterpret retained derived beliefs as new observations.
- Insert audited Clear or Attack values into inference.
- Implement a Python equivalent of native inference or answer selection.
- Convert reference probabilities into native truth values.
- Promote a new operational model.

Thin transport helpers may invoke existing native functions and perform the existing native readout expression. They must not introduce a replacement inference policy.

### 5.2 Preserve relative representation

Use opaque state-local identities for cells and pieces.

Absolute coordinates may define the import mapping and appear in audit or display records. Learned rules must continue to bind relative relationships and entity roles.

A cell identity must not encode a learned absolute-square condition.

Assigning an identity to a cell does not assert that its occupancy is known or empty.

### 5.3 Preserve historical evidence

Create new Cycle 20 modules and schemas.

Keep frozen Cycle 19 adapters, artifacts, models, and historical evidence intact. Do not rewrite previous proofs to make new comparisons pass.

Inventory the actual protected baseline. Do not reuse the previous protected-file count as the new inventory.

---

## 6. Define the capabilities separately

Use these terms consistently:

| Capability | Required evidence |
| --- | --- |
| Native batching | One derivation followed by several native readouts |
| Native continuation | Further native derivation using the actual returned tasks and beliefs |
| Serialized state restoration | Validated native state transported and restored in another execution |
| Host result caching | A previously established result returned without native work |
| Native residency | Native state retained in a live process across separately delivered host requests |
| Historical replay | Explicit reconstruction or restoration of an older immutable generation |

A single batch program does not establish native residency.

A Python dictionary or serialized proof archive does not establish native resident memory.

A cache hit does not demonstrate faster native inference.

The report must state which capabilities were demonstrated.

---

## 7. Comparison contracts

Define the comparators before implementing the optimization.

### Comparison A — Identical Cycle 19 inputs

Compare the frozen separate-query implementation with one derivation and multiple native readouts using identical:

- Facts and their ordering.
- Rule declarations and their ordering.
- Truth values and stamps.
- Initial tasks.
- Runtime.
- Budgets.
- Native selector and classification thresholds.

Require exact canonical parity for:

- Answers and contrary answers.
- Truth values.
- Evidence stamps.
- Classifications.
- Selected task sequence.
- Retained belief tuple.
- Remaining task tuple.
- Completion status.

Whole process receipts will differ because program text, markers, timing, and process count change. Do not require identical receipt hashes.

Define a scientific projection that reconstructs each legacy query result from the shared derivation and its readout.

Do not normalize away meaningful differences. Preserve raw outputs. If justified native variable renaming requires an existing alpha-equivalence comparator, document it and distinguish that comparison from byte equality.

### Comparison B — Identical combined Cycle 20 inputs

Compare:

- Separate fresh queries over the combined knowledge base.
- One derivation with multiple readouts over that same knowledge base.

Use the same canonical identities, input ordering, runtime, and budgets.

This is the main equivalence gate for multiple rays.

### Comparison C — Combined state versus legacy local neighborhoods

Measure the difference between:

- The old per-ray inputs.
- A larger combined native state.

Exact equality is not assumed. Additional beliefs can change bounded scheduling and resource competition.

Report differences without silently increasing budgets or changing query order until they disappear.

### Comparison D — Continuation

Compare uninterrupted and chunked derivation with:

- Matched total step allowance.
- Identical queue capacities.
- Exact returned state between chunks.
- Preserved tuple order.

Require parity within the registered supported cases. Retain counterexamples if a runtime property prevents it.

---

## 8. Work packages

## C20-01 — Baseline, registration, and capability inventory

### Implement

1. Verify the starting commit, runtime, accepted model, and historical manifests.
2. Create the dedicated branch/worktree.
3. Record the actual current data-access path.
4. Reproduce compact shared/disjoint and recursive limitation anchors.
5. Define the four comparison contracts.
6. Register datasets, workloads, budgets, controls, and performance methods.
7. Commit registration before outcome-dependent selection or benchmarking.

The inventory must distinguish:

- Source observations.
- Rule schemas.
- Native sentence records.
- Unique propositions.
- Retained alternatives for the same proposition.
- Requested queries.
- Native process starts.
- Derivation calls.
- Host cache entries.

Do not use “nodes,” “rules,” and “queries” interchangeably.

### Acceptance

- Baseline identities are verified.
- Registration and comparators are committed.
- Existing capability limits are documented without assuming persistence or retraction.

---

## C20-02 — One native derivation with multiple readouts

### Implement

Add a research adapter that:

- Validates a collection of ground queries.
- Uses one ordered input knowledge base.
- Evaluates `PLN.Derive` once.
- Binds the returned tasks and beliefs once.
- Executes the existing native selector for every requested proposition.
- Emits a common derivation receipt and query-specific results.

Do not use `PLN.Query` in a way that silently reruns derivation for every readout.

If a zero-step native query is used for selection, prove that it adds no selected tasks or derivations and preserves the existing selection behavior.

### Required controls

- Clear, Attack, and NoAttack from the same derivation.
- Duplicate query.
- Reversed query order.
- Missing proposition.
- Equal-confidence alternatives.
- A retained zero-confidence statement.
- Positive and contrary support.
- A newly requested term already present in retained beliefs.
- A query outside the loaded observation scope.
- Empty or malformed query collection handling.

Readouts must not change:

- Training evidence.
- Parameter generations.
- Tasks or beliefs.
- Native support.
- Observation identities.

### Acceptance

Comparison A passes on the registered cohort.

Adding readouts does not multiply derivation work.

Preserve the native zero-confidence and tie behavior. Do not “fix” those semantics inside the new adapter.

---

## C20-03 — Immutable native state format

### Implement

Define a versioned native-state object containing at least:

- State and evidence-generation identities.
- Learned-model generation.
- Runtime and policy identities.
- Observation identity-map version.
- Ordered initial-input identities.
- Exact remaining-task tuple.
- Exact retained-belief tuple.
- Cumulative selected-step accounting.
- Queue capacities.
- Completion and resource status.
- Native derivation receipt references.
- Transport mode.
- Snapshot content hash.
- Parent-generation or continuation references.

Retain native term structure, truth values, stamps, and ordering without lossy conversion.

Keep native returned state separate from fresh environmental input.

The existing adapter limits fresh facts/rules and initial tasks to 256. A native queue with capacity 512 may return more than 256 entries. The continuation format must validate returned state against its recorded native capacities rather than pretending that it is fresh input.

Do not globally relax the frozen adapter’s bounds.

### Integrity controls

Reject:

- Changed payload under an existing snapshot identity.
- Wrong runtime or model generation.
- Missing tasks or beliefs.
- Unsupported schema versions.
- Malformed terms or invalid truth values.
- Untrusted executable expressions in transported data.
- Truncated or incomplete snapshots presented as complete.
- Changed ordering without a new identity.

Preserve variable bindings and scope in partially derived native conditionals. Test transport using more than ground terminal statements.

### Acceptance

Lossless serialization and restoration preserve the native state and registered readouts.

Historical snapshots remain immutable and independently inspectable.

---

## C20-04 — Consistent state-local identities

### Implement

Introduce a new Cycle 20 observation constructor for several rays in one state.

The existing per-ray `cell_i` names are assigned from each local neighborhood. They cannot safely be concatenated.

Create one state-wide identity mapping before selecting or adding rays.

Require:

- One identity for the same physical cell within the state.
- Different identities for different cells.
- Stable identities when query order changes.
- Stable identities when another ray is requested.
- Explicit separation between state generations.
- A reversible source-coordinate mapping for audit and display.

The mapping may cover the entire board while emitted facts remain limited to the registered observation scope.

### Observation evidence

The same recorded occupancy observation reused by two rays must retain one evidence identity.

Do not include query ID, batch number, application count, or wall-clock time in that observation’s identity.

Do not collapse genuinely different observations merely because their proposition text is equal.

Preserve the existing source policy:

- Common state ancestry does not require every fact to share one stamp.
- Different stamps do not prove statistical independence.
- Duplicate delivery must not create additional support.

Record explicit lineage when migrating legacy local names into the new representation.

### Required controls

- Two rays whose legacy `cell_0` names refer to different cells.
- Two rays sharing an empty cell.
- Two rays sharing a blocker.
- Crossing rays.
- Reversed attacker/target roles.
- Renamed entities.
- Similar local identifiers in different states.
- Added rays and permuted ray lists.
- Unknown occupancy.
- Duplicate delivery of the same observation.

### Acceptance

There are no cell aliases or new evidence created by query-set expansion.

Do not claim byte-identical legacy proofs after changing names or stamps. Use the declared representation comparison and preserve the frozen legacy path.

---

## C20-05 — Several local relations in one native state

### Implement

Construct a combined native knowledge base for registered local rays.

Use:

- The consistent state-local identity map.
- Raw occupancy and piece observations.
- Relative geometry.
- Complete frozen rule templates.
- One explicit learned-model generation.

The host may enumerate eligible relations using the registered structural geometry. It must not choose rays or rules based on whether they produce favorable inferred answers.

Define deterministic initial fact and rule ordering independent of query-list order.

Deduplicate repeated delivery of the same observation before native execution. Do not deduplicate distinct evidence merely because the statements are textually equal.

### Study panel

Use approximately 8–12 existing measured positions.

Test ray-set sizes of:

- 1.
- 2.
- 4.
- 8, where available within the registered scope and limits.

Use:

- Supplied F.
- Learned disjoint D-AB.
- Shared S-AA as a limitation control.

Select rays structurally before inspecting native outcomes.

If a natural position lacks the requested number of eligible rays, report the actual maximum. Use separately labeled constructed fixtures for required aliasing or high-density cases.

Reusing Cycle 19 positions is appropriate for engineering equivalence. Do not present this as a new independent accuracy cohort.

### Acceptance

Comparison B passes.

Comparison C is measured and explained.

Deliver at least one inspectable combined-state example containing multiple distinct rays and useful supported consequences. Include an open-path consequence and an obstruction consequence where the fixture permits them.

Shared-source positive composition must retain its actual behavior. No stamp changes may be used to manufacture success.

---

## C20-06 — Bounded native continuation

### Implement

Continue native reasoning from the actual returned:

- Remaining tasks.
- Retained beliefs.

Preserve both tuples exactly, including order.

Do not:

- Requeue all retained beliefs.
- Restart from the original task list.
- Sort or independently deduplicate returned native tuples.
- Round truth values.
- Rename stamps.
- Treat derived statements as new environmental evidence.

Register the step accounting convention.

Test matched schedules such as:

- 64 uninterrupted steps.
- 16 + 16 + 32 steps.
- A second registered total for a larger workspace.

Use identical queue capacities across compared schedules.

### Required controls

- Empty remaining-task queue.
- Zero additional derivation steps.
- Equal-confidence tasks.
- Near-capacity tasks and beliefs.
- Readouts between continuation chunks.
- Serialization and restoration between chunks.
- A rejected mismatched model or runtime.
- A failed or interrupted continuation.

The pinned `LimitSize` implementation retains strictly fewer entries than its capacity once applied. Record actual tuple sizes rather than assuming a capacity of N retains N entries.

Keep zero queue capacities prohibited.

### Acceptance

Comparison D passes where claimed.

A failed continuation cannot replace a previously valid generation with partial state.

If only serialized continuation is demonstrated, call it serialized continuation. Do not call it native residency.

---

## C20-07 — Native residency feasibility and bounded integration

### Investigate

Inspect the pinned PeTTa interfaces and existing project transport facilities.

Determine whether an existing supported interface can retain native state across separately delivered host requests without modifying the pinned runtime.

Bound this investigation. Use at most 24 focused native capability programs before making the capability decision.

### Required residency witness

To claim native residency, demonstrate:

1. A native process/session is created.
2. A belief generation is loaded and derived.
3. The host subsequently sends a new query not included in the original request.
4. The same native session selects the answer from retained native state.
5. The full knowledge base is not retransmitted or rederived.
6. Native execution counters and session identity are inspectable.
7. Continuation, stale-generation rejection, and shutdown behave correctly.

A host cache returning an old answer does not pass.

A single program with all queries written in advance does not pass.

### Permitted implementation

A thin research transport may call existing native functions through supported interfaces.

It may handle framing, validation, timeouts, generation references, and process lifetime.

It must not reimplement inference, answer selection, evidence arithmetic, or rule application.

### If unsupported

Deliver:

- Single-invocation batching.
- Lossless native-state transport.
- Demonstrated bounded continuation.
- The concrete residency blocker.
- A precise future interface requirement.

Do not patch vendor files or create a new runtime service merely to force a positive residency claim.

### Acceptance

The capability is classified accurately as:

- Demonstrated native residency.
- Demonstrated batching/continuation with residency unestablished.
- A specific bounded failure requiring separate work.

Complete the rest of Cycle 20 in every case.

---

## C20-08 — Corrections, model replacement, and historical replay

### Implement

Extend the Cycle 19 lifecycle policy to native state generations.

A native generation must identify every input generation that can affect its bounded execution.

When an observation changes:

1. Mark the native generation that consumed it unavailable for current use.
2. Reject its current cached answers.
3. Construct replacement raw inputs.
4. Derive a fresh native generation.
5. Compare it with fresh reconstruction.
6. Publish the replacement atomically.
7. Retain explicit historical replay.

When a learned-model generation changes, invalidate every native generation using that model.

Do not assume that an apparently irrelevant fact can be changed inside one combined knowledge base while preserving its old answers. It may affect scheduling and queue competition.

Unchanged separate workspaces may remain valid.

### Safe default

Rebuild an affected native generation from valid raw inputs.

Do not delete a raw fact while retaining its derived descendants.

No native retraction capability may be claimed without a separate supported demonstration.

### Required controls

- Empty cell corrected to occupied.
- Empty cell corrected to unknown.
- Attacker or target identity corrected.
- An added ray introducing new observations.
- A new readout introducing no new observations.
- Model replacement after an actual source-removal refit.
- Two workspaces using the same model generation.
- An unrelated workspace using unchanged inputs.
- Failed or interrupted replacement.
- Historical replay.
- Restored serialized state with validated identities.
- Stale or wrong-generation session request.

Every answer must identify its exact state, evidence, model, runtime, and native generation.

An in-flight result from an old generation must not masquerade as a current answer.

### Acceptance

Replacement results match fresh reconstruction for the same replacement inputs.

Historical results remain reproducible.

No mixed old/new generation is published.

Keep this a bounded research lifecycle. Do not expand into a general concurrent transaction or distributed recovery system.

---

## C20-09 — Capacity and performance

### Register before benchmarking

Use a small paired benchmark panel with the same hardware, inputs, runtime, and budgets.

Benchmark separately:

- Legacy separate derivations.
- One derivation with multiple readouts.
- Combined-state separate queries.
- Combined-state batched queries.
- Chunked continuation.
- Serialized restoration.
- Native residency, only if demonstrated.
- Host cache lookup.
- Corrected-state rebuilding.

Use serial paired runs or explicitly controlled scheduling. Do not compare a busy concurrent reference run with an idle optimized run.

Use approximately 7–10 repetitions on a small representative subset. Report the raw samples and median/range. Do not present sparse p99 values as reliable tail estimates.

### Count actual work

At each workload size report:

- Unique input facts.
- Observation events and stamps.
- Rule schemas.
- Unique retained propositions.
- Retained native sentence records.
- Remaining tasks.
- Selected tasks.
- Native process starts.
- Derivation calls.
- Native readouts.
- Semantic target queries.
- Repeated queries.
- Host cache lookups.
- Input/output bytes.
- Serialization/parsing time where measurable.
- Wall time, CPU time, and memory.
- Positive, contrary, unknown, conflict, and incomplete counts.

Clear and Attack are two semantic targets; selecting Attack and NoAttack separately creates two native readouts for that target. Keep these counts distinct.

Describe the actual data-access path. A retained tuple scanned by the native selector is not automatically an indexed graph database.

### Limits

Preserve the frozen fresh-input bounds.

Use registered queue capacities within the existing adapter/runtime limits. A continuation object may transport a larger native-returned tuple only through its distinct validated state contract.

Use a default total research ceiling of 6,000 native process starts, covering probes, tests, comparisons, refits, and published compact reproduction. Count historical preservation separately and disclose any overlapping counters.

Retain per-operation timeouts and process cleanup.

Before launching the full matrix, calculate its expected work. Reduce only preregistered secondary panels if necessary; do not drop failures or change the primary comparator after seeing results.

### Interpretation

No speedup is mandatory.

Require correctness before performance claims.

Report capacity refusal as a resource outcome. Do not convert an oversized or failed workspace into a collection of semantic unknown answers.

Larger knowledge bases need not preserve coverage under bounded queues. Record that behavior honestly.

---

## C20-10 — Compatibility, preservation, and reproduction

### Cycle 19 compatibility

Use the complete registered Cycle 19 episode/model pairs for artifact-based input and identity checks.

Where original native evidence is available, run the new legacy-compatible batch path across the complete 1,256 episode/model pairs and compare the reconstructed scientific outputs with the recorded baseline.

Freshly reexecute the old path on a preregistered representative subset covering:

- All relevant model classes.
- Positive and blocked cases.
- Missing observations.
- Representation controls.
- Shared-source limitations.

Freshly investigate every mismatch.

Do not rerun the entire old study merely to generate duplicate receipts if recorded baseline integrity is already established.

If required baseline evidence is unavailable, report the missing material and the exact reduced verification scope. Do not describe an unperformed full comparison as complete.

### Historical preservation

After executable source, data, schemas, and configurations are frozen, run the established complete preservation gate:

- Full test suite.
- All 206 legal shards.
- All 584,112 legal candidate rows.
- Exact canonical native proof parity.
- 287 evidence-removal controls.
- 27 history controls.
- Both historical en-passant recoveries.
- 76 controlled legal holdouts.
- Accepted checkpoint and runtime identities.
- Protected historical files and evidence manifests.

The 799 Cycle 19 tests are a baseline receipt, not the fixed expected count of the extended suite.

If executable inputs change after the freeze, establish a new freeze and rerun the necessary final gates. Do not merge incompatible-source receipts into one claimed successful campaign.

### Compact reproduction

Provide separate reproducible commands for:

1. One derivation with several native readouts.
2. A combined state with multiple rays.
3. Chunked continuation.
4. Correction and replacement.
5. Historical replay.
6. Native residency, if demonstrated.
7. The full preservation campaign.

Compact examples must work from the published checkout without private bulk paths.

Distinguish verified dependency reuse from a fresh dependency installation.

---

## C20-11 — Interfaces, evidence, and documentation

### Implementation layout

Prefer new modules under `research/cycle20/`, focused tests, and new delivery helpers following repository conventions.

Expose a research interface for:

- Creating a native workspace generation.
- Deriving it.
- Reading several queries.
- Continuing it.
- Exporting and restoring state.
- Replacing a generation after correction.
- Replaying history.
- Reporting residency capability.

Do not expose a production endpoint or change operational defaults.

An inspector view is optional. If added, it must clearly distinguish native retained statements from host dependency edges.

### Evidence representation

Store one common derivation receipt per native generation and small query-specific records referencing it.

Avoid copying the complete native trace into every query export.

Provide a lossless scientific projection for compatibility checks.

Never fabricate fired-rule parents. The existing runtime exposes selected tasks and returned statements; that remains the proof-observability boundary unless a supported capability demonstrates more.

### Required documentation

Deliver:

1. `engineering-report.md`
2. `package-matrix.md`
3. `research-registration.md`
4. `native-state-contract.md`
5. `identity-and-observations.md`
6. `batching-and-parity.md`
7. `continuation-and-residency.md`
8. `correction-and-replay.md`
9. `capacity-and-performance.md`
10. `architecture-decision.md`
11. `reproduction.md`
12. `publication.md`

Use machine-readable manifests for detailed results and counts.

The package matrix must distinguish implementation status, executed experiments, research outcomes, limitations, and evidence.

---

## C20-12 — Publication and architectural conclusion

### Required conclusion

State independently whether Cycle 20 demonstrated:

- Exact identical-input batching parity.
- Consistent shared identities for multiple rays.
- Exact batching parity on a combined knowledge base.
- Bounded native continuation.
- Lossless serialized restoration.
- Native residency across separate requests.
- Corrected-generation replacement.
- Historical replay.
- Performance improvement.
- A measured capacity boundary.

Do not collapse these into a single “persistent graph complete” claim.

### Preserved limitations

Reexecute the compact shared-training and recursive-reuse witnesses.

The report must retain the distinction between:

1. Shared training observations across different learned rules.
2. Repeated use of the same rule in a recursive derivation.

Neither is repaired by batching, caching, or persistence.

No confidence calibration, new probability interpretation, operational promotion, or native evidence-policy extension is part of this cycle.

Any proposal for such work must specify the capability and unresolved semantics separately. Do not begin that implementation under this brief.

---

## 9. Mandatory acceptance gates

Engineering acceptance requires:

1. Verified baseline and committed registration.
2. Correct native batching without host answer substitution.
3. Exact Comparison A parity where claimed.
4. Consistent state-local identities and observation reuse.
5. Exact Comparison B parity where claimed.
6. Honest reporting of Comparison C differences.
7. Lossless state transport and validated continuation.
8. Correct generation invalidation, replacement, and historical replay.
9. Explicit distinction between batching, restoration, caching, and residency.
10. No evaluator or reference-model leakage into inference.
11. Preserved native calculus, stamps, runtime, and accepted model.
12. Complete required historical preservation.
13. Compact reproduction from published source.
14. Commit, push, and independent remote verification.

The core functional demonstration must show several queries sharing native derivation work.

Cross-request native residency is a bounded capability outcome. A documented unsupported result does not invalidate correctly delivered batching and continuation.

Research acceptance does not require improved accuracy, a speedup, generic recursion, shared-source positive composition, or calibrated confidence.

Do not label a failed parity gate as an acceptable negative research result. Parity failures must be fixed, isolated from the delivered working path, or reported as an incomplete engineering capability.

---

## 10. Artifact and Git discipline

Commit the material needed to inspect and reproduce the principal results:

- Source and tests.
- Registration.
- Compact input states.
- Identity maps and observation lineage.
- Native state schemas.
- Decisive native inputs and outputs.
- Common derivation receipts.
- Query readouts.
- Continuation witnesses.
- Correction and replay examples.
- Benchmarks and capacity summaries.
- Reports and reproduction commands.

Keep large historical proof exports, dependency caches, and bulk native transcripts outside ordinary Git.

Use checksummed local evidence packs and perform an actual restore-and-verify test.

Project budgets:

- Maximum new blob: 10 MiB.
- Target total new unique blob content: 100 MiB.

These are project budgets, not GitHub platform-limit claims.

Inventory every new reachable blob across the complete baseline-to-HEAD range, including superseded versions.

Deleting a large file in a later commit does not remove it from earlier reachable commits.

Scan current and superseded newly reachable content for secrets.

If unpublished commits contain excessive bulk, preserve a backup and provenance record and repackage only the unpublished range. Do not rewrite already published history.

No release upload, external bulk hosting, tag publication, or deployment is authorized.

---

## 11. Explicit instructions to commit and push

Committing and pushing are mandatory deliverables.

### 11.1 Commits

Create meaningful commits for:

- Registration.
- Implementation and tests.
- Any substantive correction.
- Final reports and compact evidence.

No particular commit count is required.

Stage reviewed paths explicitly. Preserve unrelated local work.

Before final publication, verify:

- The branch descends from the required baseline.
- The final executable-source freeze matches the evidence.
- Required acceptance gates have passed.
- Historical files and accepted model remain protected.
- Git size and secret checks cover the entire new range.
- The working tree is clean after the final commit.

### 11.2 Destination checks

Inspect:

- Fetch URL.
- Every push URL.
- Relevant URL rewrite rules.
- Effective repository identity.
- Exact destination branch.

Do not print or commit credential-bearing URLs.

The only authorized repository is `machieke/pln-chess`.

Update only the dedicated Cycle 20 branch. Do not update the default branch, tags, or unrelated refs.

### 11.3 Push command

For the default target branch:

```bash
set -euo pipefail

C20_BASE=7c06d8e15972e5db2e0932160102dda329c304ab
C20_BRANCH=cycle20-native-belief-workspaces

test "$(git branch --show-current)" = "$C20_BRANCH"
git merge-base --is-ancestor "$C20_BASE" HEAD
test "$(git rev-list --count "${C20_BASE}..HEAD")" -gt 0
test -z "$(git status --porcelain)"

C20_LOCAL_SHA="$(git rev-parse HEAD)"

git -c push.followTags=false -c push.recurseSubmodules=no \
  push --set-upstream origin \
  "HEAD:refs/heads/${C20_BRANCH}"

C20_REMOTE_SHA="$(
  git ls-remote --exit-code origin "refs/heads/${C20_BRANCH}" |
  awk 'NR == 1 {print $1}'
)"

test -n "$C20_REMOTE_SHA"
test "$C20_LOCAL_SHA" = "$C20_REMOTE_SHA"
```

If another dedicated branch name was necessary, substitute the registered name consistently.

Do not use a force option.

### 11.4 Independent verification

After pushing:

1. Query the branch freshly from the remote.
2. Verify the branch through an independently addressed canonical GitHub API or connector read.
3. Require exact equality with local `HEAD`.
4. Retrieve the report, source, compact inputs, and reproduction guide at that exact SHA.
5. Create a fresh checkout of the published commit.
6. Run compact batching, combined-state, continuation, and correction examples.
7. Run the residency example only if residency is claimed.
8. Verify the original working tree remains clean.

Two local remote-tracking references are not independent verification.

Account for Git URL rewriting when checking the canonical destination.

Keep the final publication receipt outside the tracked checkout, or in an existing separately managed receipt location, to avoid self-referential final-SHA commits.

### 11.5 Publication failures

If push or verification fails:

- Preserve the implementation, evidence, and commits.
- Record the exact failure.
- Report the final local SHA.
- State precisely whether publication or verification remains incomplete.
- Do not claim synchronization without verification.
- Do not bypass authentication or repository protections.
- Do not force-push to resolve a rejection.

A correctly documented unsupported residency result or absent speedup does not prevent publication of the completed engineering package.

---

## 12. Final response requirements

The final response must contain:

1. Starting SHA.
2. Final local SHA.
3. Independently verified remote SHA.
4. Branch and commit list.
5. Working-tree status.
6. Package matrix.
7. Exact capability status for batching, continuation, restoration, residency, caching, and replay.
8. Comparison A, B, C, and D results.
9. Identity and shared-observation controls.
10. Combined-state workloads and capacity limits.
11. Native statement, task, query, and process counts.
12. Correction and learned-generation replacement results.
13. Historical preservation and proof parity.
14. Performance results with raw-sample scope and limitations.
15. Failed, incomplete, or interrupted experiments.
16. Remaining shared-evidence and recursive-reuse limitations.
17. Git size inventory and pack-restoration evidence.
18. Published-checkout reproduction.
19. Links to the engineering report and decisive native witnesses.
20. The next architectural decision supported by the evidence.

A successful Cycle 20 should make shared native work visible:

- One consistent relational state.
- One derivation supporting several native readouts.
- Explicit retained tasks and beliefs.
- Controlled continuation.
- Correct replacement after changed evidence.
- Reproducible historical generations.

Describe the implementation according to what it actually does, including which state lives in native execution and which operations remain host-managed.