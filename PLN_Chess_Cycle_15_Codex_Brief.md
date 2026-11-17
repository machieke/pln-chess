# PLN Chess — Cycle 15 Consolidated Engineering Brief

## Native Relational Inference and Local Consequence Learning

**Repository:** https://github.com/machieke/pln-chess
**Publication baseline:** `d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d`
**Original Cycle 14 delivery:** `4a603722a73f9f0280e5034186ee4dc26b0f1bbc`
**Accepted legal model:** Unchanged Cycle 12 promoted en-passant checkpoint
**Execution:** One consolidated autonomous engineering assignment
**Delivery:** Implementation, executable experiments, native evidence, tests, reports, and local commits
**Authorization:** No push, remote publication, deployment, upstream modification, new PLN inference operators, or autonomous move selection

---

## 1. Mission

Cycle 15 must test the reasoning architecture originally intended for PLN Chess.

The central objective is:

> Python supplies relative observations and a query. Reusable declarative knowledge is supplied to native PLN. Native inference determines which supported derivations apply and produces the answer.

This differs from:

> Python constructs a configuration descriptor, looks up its corresponding conditional, and calls a native truth-value function for the already selected conclusion.

The current implementation remains a valuable baseline. Do not remove or misrepresent it.

Build an isolated experimental path that uses the existing native derivation machinery, then determine what it can actually infer.

The primary chess experiment is deliberately narrow:

> How does moving an intervening piece change a specified sliding piece's attack relationship to a target?

Do not conduct another broad strategic preference campaign during this cycle.

Do not implement move selection.

---

## 2. Required Outcomes

The cycle must distinguish four outcomes.

### A. Native execution

The existing reasoner applies supplied declarative knowledge without Python prescribing the inference sequence.

### B. Relational applicability

Rules reuse shared roles and relative relationships across unfamiliar entities and positions.

### C. Evidence-based learning

Native revision updates rule beliefs from independent evidence. Learned truth values contribute to held-out predictions.

### D. Chess-consequence inference

The system derives a limited attack or exposure consequence from the permitted observations.

These outcomes are separate.

A successful symbolic smoke test does not establish chess competence.

Learning a truth value does not establish discovery of a rule's structure.

A conclusion derived from an imported attack fact does not establish derivation of that attack from occupancy.

Engineering delivery can succeed while a research outcome remains negative. Report both statuses.

---

## 3. Starting Point and Source References

Inspect the pinned publication checkout before editing.

Relevant files include:

- `vendor/pln/lib_pln.metta`
- `configs/runtime-lock.json`
- `src/pln_chess/pln/`
- `src/pln_chess/cycle14/ontology.py`
- `src/pln_chess/cycle14/inference.py`
- `src/pln_chess/cycle14/graph.py`
- `src/pln_chess/cycle14/proofs.py`
- `training/cycle14_learning.py`
- `docs/cycle14/engineering-report.md`
- `docs/cycle14/relative-representation.md`
- `docs/cycle14/preference-learning.md`
- `docs/cycle14/ablations.md`
- `docs/cycle14/performance.md`
- `docs/cycle14/proof-storage.md`
- `docs/cycle14/publication.md`
- `artifacts/cycle14/representation/census.json`

Discover additional paths from the repository. Do not assume a proposed filename already exists.

### Verified source-level starting facts

The vendored library exposes these full signatures:

    (PLN.Derive
        $Tasks $Beliefs $steps $maxsteps
        $taskqueuesize $beliefqueuesize)

    (PLN.Query
        $Tasks $Beliefs $term $maxsteps
        $taskqueuesize $beliefqueuesize)

It also exposes shorter overloads.

The native sentence representation is:

    (Sentence
        (<proposition> (stv <strength> <confidence>))
        (<evidence-stamp-items>))

The existing derivation procedure selects tasks by confidence, attempts native statement-level inference against beliefs, checks stamp overlap, and bounds task/belief collections.

The query procedure invokes derivation and selects a matching answer from the returned beliefs.

These are source observations, not a guarantee that the proposed chess encodings will execute correctly.

### Runtime lock

Preserve the existing runtime manifest, including:

- PLN commit: `4405956947c4b53c7ff01bd565aa3b114bc970a1`
- PeTTa commit: `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`

Verify the actual checked-in hashes and prerequisites.

Do not update dependencies to make an experiment pass.

---

## 4. Research Boundaries

### Allowed

- Relative geometry and raw occupancy observations.
- Structural successor-state construction without legality adjudication.
- Typed, connected relational facts.
- Declarative domain knowledge using existing supported PLN statement forms.
- Native derivation, query, and revision.
- Small, disclosed rule-template grammars.
- Host-side indexing, serialization, budgeting, storage, and evaluation.
- Evaluation-only chess references.
- Existing compact proof storage.
- Local implementation and commits.

### Not allowed

- New `|-` inference clauses or altered native truth formulas.
- A new conjunction, negation, quantification, or aggregation calculus.
- A replacement Python rule engine that decides the chess conclusion.
- Moving deterministic chess adjudication into a custom MeTTa function and calling it PLN.
- Configuration-specific answer rules keyed by full board descriptors.
- Production oracle calls.
- Absolute-square constants in learned knowledge.
- Handweighted strategic utility.
- Autonomous search or move selection.
- Modifying the accepted legality checkpoint.
- Pushing or publishing remotely.

### Domain knowledge versus inference calculus

Adding a domain implication as knowledge is permitted.

Adding a new generic inference mechanism is not.

For every new declaration, classify it as:

1. Environmental observation.
2. Supplied domain-rule template.
3. Learned rule truth value.
4. Native inference result.
5. Host diagnostic.

Do not hide an unsupported logical operation inside an observation constructor or a domain helper.

---

## 5. Scope and Execution Order

Deliver eight engineering packages.

Work in this order:

1. Baseline isolation and study registration.
2. Native derivation capability experiments.
3. Connected relative observations.
4. The blocker-move consequence experiment.
5. Native learning and independent transfer.
6. Matched comparisons.
7. Proof, budget, and performance analysis.
8. Integration, preservation, and decision report.

The native capability work is an early decision gate.

If a required capability fails, produce a minimal reproducible counterexample and continue independent work. Do not spend the rest of the cycle disguising the failure behind a categorical fallback.

Use bounded research:

- At most three materially distinct native representations for any failed capability.
- Reuse prior negative experiments where applicable.
- Register compute and storage budgets.
- Stop repeating an approach once its failure is reproduced and localized.

No new large external preference corpus is required.

No new inspector redesign is required.

No full evidence-history download is required merely to inspect source.

---

# C15-01 — Preserve the Baseline and Register the Experiment

## Objective

Create a safe experimental branch and define the claims before implementation.

## Tasks

Verify:

- Checkout commit and ancestry.
- Working-tree state.
- Native source hashes.
- Runtime dependencies.
- Accepted legal checkpoint identity and file hash.
- Relevant field/concept checkpoint identities.
- Existing evidence and publication manifests.

Do not destructively reset an unfamiliar checkout.

If the starting checkout is newer than the publication baseline, record the difference and isolate the experiment in a worktree or branch without discarding user work.

Read the publication documentation before restoring externalized evidence.

Use the existing checksum-verifying restoration tools where evidence is required.

Do not rewrite original scientific receipts to reference the repackaged commit.

### Study registration

Create:

    docs/cycle15/research-registration.md

Register:

- Questions and outcomes.
- Permitted observations.
- Native representations to test.
- Rule-template grammar.
- Fact/rule truth-value policies.
- Evidence-stamp policy.
- Inference budgets.
- Training/development/test partitions.
- Counterfactual interventions.
- Baseline comparison arms.
- Evaluation metrics.
- Research targets and stopping rules.

### Baseline scope

Run a targeted starting smoke suite immediately.

Reserve the expensive complete preservation suite for the final source-bound acceptance run rather than rerunning it after every documentation change.

Historical evidence remains immutable.

**Deliverables:** Baseline manifest, source-bound smoke receipt, registration, and explicit experimental boundaries.

---

# C15-02 — Integrate and Audit Native Derivation

## Objective

Establish what the pinned `PLN.Derive` and `PLN.Query` actually support.

Do this before attempting complete chess inference.

## 2.1 Dedicated adapter

Implement an experimental adapter that accepts:

- Initial fact sentences.
- Domain-rule sentences.
- Evidence stamps.
- A ground query or registered query form.
- Explicit derivation budgets.
- Runtime identity.

The adapter must serialize a knowledge base and invoke native derivation.

It must not:

- Look up a board-descriptor-specific answer conditional.
- Build a predetermined list of chess-specific modus-ponens calls.
- Compute the expected conclusion before invoking PLN.
- Fall back to direct truth-function calls when derivation fails.

Direct native operator calls remain permitted for audit comparisons and training, but they do not satisfy the derivation objective.

Use local pinned imports. Do not execute an example's unpinned `git-import!` unchanged.

## 2.2 Compatibility smoke

Reproduce at least one suitable example from the pinned upstream source.

The pinned `examples/Smokes.metta` is a starting reference.

Record the original file hash and any import-path-only adaptation.

Do not infer that every construct in an example was exercised merely because its final assertion passed.

## 2.3 Required micro-experiments

Build a small capability matrix.

| Probe | Question |
|---|---|
| Stored fact retrieval | Does the query return a fact already in the supplied knowledge base? |
| One-rule inference | Does a conclusion absent from the inputs derive through an implication? |
| Multi-step inference | Can two or more reusable implications support an absent conclusion? |
| Irrelevant facts/rules | Does the result remain supported when bounded distractors are added? |
| Parameterized role binding | Can one native schema bind different entities without host substitution? |
| Shared-variable binding | Does a repeated role refer to the same entity across premises/conclusion? |
| Renaming | Do incidental entity names affect the result? |
| Missing premise | Is the dependent derivation unavailable when its sole support is removed? |
| Rule removal/change | Does changing declarative knowledge change the result without Python edits? |
| Duplicate/shared evidence | How do stamps affect revision and chained derivations? |
| Opposing support | What happens when positive and contrary support coexist? |
| Budget/order sensitivity | Can eviction, input order, or step limits alter the retained answer? |

Run each with raw native inputs and outputs retained.

## 2.4 Grounding classification

Report the strongest demonstrated level:

- `ground-instance-native-inference`
- `uniform-grounding-plus-native-inference`
- `native-schema-binding`
- `unsupported`

Uniform grounding is a diagnostic fallback, not equivalent to native schema binding.

If used, it must enumerate all type-compatible instances within a registered bounded domain, independently of labels and predicted outcomes.

Do not allow Python to instantiate only the rule whose chess conclusion it has already selected.

The strongest architectural target requires native binding of reusable knowledge.

## 2.5 Native semantics to test explicitly

Do not assume:

- `PLN.Query` performs backward chaining.
- A query variable is handled like a variable inside a rule.
- Queue capacities are inclusive exactly as named.
- Missing marginal truth values have a valid default.
- Equal-confidence answers have order-independent selection.
- More derivation steps always preserve the previously selected answer.
- An empty native result means logical falsity.
- A native evidence stamp is a complete probability-dependence model.

Test exact boundary behavior.

Provide required marginal `STV` declarations only with a disclosed source or explicit modeling assumption. Do not invent marginals silently to make deduction or induction run.

## 2.6 Proof reporting

Retain the exact native program, tasks, beliefs, budgets, stdout, stderr, and final output.

The current native output may expose selected tasks and evidence stamps without a complete fired-rule proof tree.

Do not fabricate a detailed execution trace.

Distinguish:

- Directly observed execution trace.
- Native-returned evidence stamp.
- Post-hoc native-revalidated proof witness.

A reconstructed witness may use only supplied or natively observed statements and supported operators. It must not decide the production answer.

No vendor-source modification is authorized to improve tracing.

**Gate A:** Demonstrate a conclusion absent from the input, supported through native inference, with rule and premise interventions.

**Gate B:** Demonstrate reusable native role binding, or report its exact limitation.

**Deliverables:** Adapter, executable microcases, capability matrix, raw transcripts, and minimal failing examples.

---

# C15-03 — Connected Piece-Relative Facts

## Objective

Retain the relationships needed for reasoning without turning the whole position into an opaque categorical key.

## 3.1 Environmental facts

Define a typed observation contract.

Candidate conceptual relations include:

    PieceKind(piece, kind)
    Owner(piece, side)
    RelativeOffset(piece_a, piece_b, dx, dy)
    Occupies(piece, cell, state)
    Empty(cell, state)
    UnknownOccupancy(cell, state)
    OrderedRayCell(ray, index, cell)
    CandidateTransition(move, before_state, after_state)
    OriginalActor(state, side)

These are conceptual signatures. Use the concrete native encoding established by C15-02.

Relative displacement and ordered ray membership may be structural geometry observations.

They must not already adjudicate chess attack or legality.

## 3.2 Shared identities

Preserve the fact that two relations concern the same target, defender, attacker, cell, or state.

Example:

    influences(A, T, S)
    protects(D, T, S)
    moved(D, M)

The shared `T` must survive representation.

Do not replace this structure solely with counts such as:

    attack increased
    defense decreased

Use episode-local entity identities. Rule schemas must not contain those identities as learned constants.

## 3.3 State and role isolation

Every state-dependent relation must carry an explicit state or context.

Before-state occupancy must not silently become after-state occupancy.

A hypothetical successor must not be treated as an observed real game event.

Ownership and original-actor perspective must survive state transitions.

Test identical local geometry with different:

- Allegiance.
- Target role.
- State identity.
- Relevant history.
- Unknown observations.

## 3.4 Observation exclusions

The raw-observation arm must not receive:

- `ClearRay`
- `Attacks`
- `Pinned`
- `KingExposed`
- `MoveLegal`
- `MoveIllegal`
- Reference labels or reference-engine scores

Such statements may appear only as explicitly imported Stage A premises or as derived outputs, with their origin recorded.

Do not hide these answers in a feature name, hash, special case, or MeTTa helper.

## 3.5 Bounded locality

Use a dependency-connected query neighborhood.

For the primary experiment, include the attacker, target, relevant intervening cells, moved piece, and necessary state/ownership observations.

Do not exclude a distant rook or bishop interaction merely because it exceeds a short radius.

Scope selection must use disclosed structural relationships, not the oracle result or a precomputed successful proof.

Retain distractor tests to expose overly selective input construction.

**Deliverables:** Ontology, serializer, scope manifest, fact-origin audit, and invariance/sensitivity tests.

---

# C15-04 — Blocker-Move Consequence Experiment

## Objective

Determine whether native PLN can explain changes in a specified attack relationship after a supplied move.

Use a sliding attacker, an intervening piece, and a target.

The supplied move is an experimental input. The subsystem is not selecting it.

## 4.1 Separate the two inference stages

### Stage A — Consequence chaining from supplied support

Supply an explicitly labeled attack-related premise.

Investigate native consequences such as an exposure implication when the premise's roles and ownership justify it.

This tests native inference execution and role binding.

It does not demonstrate attack derivation from geometry or occupancy.

Do not use a generic implication from any attack to own-king exposure. Target identity, side, and state must be correct.

### Stage B — Attack support from lower-level observations

Remove the imported attack premise.

Supply only the permitted raw observations and declarative domain knowledge.

Investigate whether the native system can derive the attack relation itself.

Start with a minimal one-intermediate-cell problem, then test longer paths.

Do not claim arbitrary-ray generalization from a one-cell demonstration.

## 4.2 Required scenario families

| Case | Required distinction |
|---|---|
| The sole intervening piece leaves the ray | Attack support may change if other conditions are justified |
| The piece moves along the ray and remains between attacker and target | Occupancy is not equivalent to clearance |
| One blocker leaves but a second remains | Removing one obstruction does not establish a clear path |
| A relevant ray cell is unknown | Missing observation is not empty occupancy |
| An unrelated piece moves | The relevant relation should remain invariant when its dependencies are unchanged |
| The attacker is removed | Do not retain an attack from a nonexistent source |
| The target is removed or replaced | Preserve target identity, role, and query-domain changes |
| Equivalent geometry uses different entities or locations | Reusable knowledge should transfer |
| The target is the original actor's king | Keep attack/exposure semantics separate from ordinary target influence |
| Competing observations or stale state facts are supplied | Expose conflict or reject invalid framing |

Reference expectations must be generated and checked outside production inference.

## 4.3 Definition of the target

Define exactly what `Attack` means for the experiment.

Separate:

- Geometric influence.
- Occupancy-constrained attack.
- Legal capture eligibility.
- Own-king exposure.
- Full move legality.

Use reference predicates matching the chosen definition.

Do not score a geometric attack query against legal-capture labels.

## 4.4 Native composition boundary

Audit every intermediate predicate.

If a step requires combining independent facts, determine whether the pinned native rules support the required binding and semantics.

Nested implications may be tested as supplied domain knowledge, but do not call them a verified general conjunction.

A rule supplied specifically to bridge a missing semantic step must be labeled supplied knowledge. It is not evidence that the bridge was discovered or that arbitrary multi-premise reasoning now works.

If complete positive path-clearance reasoning remains unsupported:

- Preserve the unresolved premises.
- Report any valid negative or partial derivations.
- Deliver the minimal unsupported query.
- Do not substitute a host clearance test.

## 4.5 Before/after reporting

Infer each state's target separately.

A host comparison of endpoint truth values is allowed as a diagnostic.

It is not automatically a native truth value for “the attack was created.”

Only report a native change proposition if the native derivation actually produced it.

**Deliverables:** Scenario library, Stage A and B results, native evidence, and explicit capability boundaries.

---

# C15-05 — Native Learning and Independent Transfer

## Objective

Learn support for reusable rules, not a separate answer for each complete configuration.

## 5.1 Bounded template grammar

Register a small domain grammar before final evaluation.

Aim for at most twelve substantive templates in the primary experiment.

Templates may express relevant movement, obstruction, attack, or exposure relationships using the verified encoding.

Record for every template:

- Supplied logical structure.
- Learned parameters.
- Required premises.
- Intended conclusion.
- Evidence source.
- Known dependence assumptions.
- Supported and unsupported scope.

Do not claim rule-structure discovery unless it is actually implemented and measured.

Do not perform brute-force enumeration of arbitrary chess programs.

## 5.2 Native revision

Use native revision to update rule truth values from training evidence.

Offline labels may support or contradict a declared conditional hypothesis.

They must never be inserted as the queried answer during held-out inference.

Preserve:

- Positive and negative observations.
- Unknown observations.
- Dependence ancestry.
- Native revision expressions.
- Rule identities.
- Pre/post training truth values.

Do not let an unrelated reason for move illegality globally discredit a movement or attack rule.

Train against the exact conditional target being studied.

## 5.3 Evidence stamps and dependence

Audit two distinct mechanisms:

1. Native stamp overlap used during inference.
2. Dependence groups used during evidence admission and revision.

A disjoint stamp set is not proof of statistical independence.

Do not create fresh evidence IDs merely to bypass overlap rejection.

Do not assign a reused learned rule a different evidential identity each time it fires.

Do not revise a prediction into its own training support.

If conservative stamp handling prevents a desired derivation, expose the limitation rather than manufacturing independence.

Test a chain and a diamond-shaped support pattern where evidence can be reused.

Repeated proof replay must not increase confidence.

## 5.4 Independent corpus

Use a focused corpus rather than another large preference collection.

Target:

- At least 24 training root families.
- At least 12 development root families.
- At least 48 held-out root families.

Each root may have before/after states and counterfactual variants.

Those descendants remain dependent observations, not additional independent roots.

Partition by structural family and source ancestry before training.

Include held-out changes in:

- Ray length.
- Relative direction.
- Blocker position.
- Piece identity.
- Board location where boundary semantics permit.
- Relevant versus irrelevant occupancy changes.

Translations, reflections, color transformations, and renamings inherit their parent's split.

A direction or boundary transformation is valid only when the semantics remain preserved.

## 5.5 Transfer criteria

Distinguish:

- Exact categorical reuse.
- Role-binding reuse.
- Native rule-schema reuse.
- New supported composition.
- Unsupported combination.

For the main claim, show that a previously learned rule contributes to an unfamiliar binding without creating a new configuration-specific rule.

Record which facts and rule beliefs were sufficient.

**Deliverables:** Registered grammar, evidence ledger, native training traces, frozen checkpoint, and independent transfer study.

---

# C15-06 — Matched Comparisons and Interventions

## Objective

Separate changes in representation, execution, and learning.

Do not credit the native reasoner with improvements caused only by a different dataset or supplied answers.

## 6.1 Comparison arms

| Arm | Purpose |
|---|---|
| A — Existing field/conditional implementation | Frozen operational reference for semantically compatible attack queries |
| B — Same conditional knowledge through native derivation | Isolate the execution-path change |
| C — Connected relative facts and reusable rules through native derivation | Test the intended architecture |
| D — Learning and rule/premise interventions | Determine what evidence and knowledge actually contribute |

The Cycle 14 preference result may be included as context, but do not compare preference accuracy directly with attack-consequence accuracy.

Only compare arms on targets they actually represent.

Unsupported targets remain explicitly unsupported; do not convert them into false predictions.

## 6.2 Architecture interventions

Require tests for:

- Removing the sole supporting rule.
- Removing an essential fact.
- Changing one learned rule's truth value.
- Renaming entities.
- Translating a semantics-preserving local configuration.
- Adding an irrelevant fact.
- Adding a relevant second blocker.
- Swapping a shared role so that two relations no longer concern the same target.
- Supplying equal aggregate counts with different connected structures.
- Replaying identical evidence.
- Removing a training ancestry group and refitting.

Do not require a classification to flip when a rule is removed if an independent valid derivation remains.

In that situation, report the removed derivation and surviving support.

## 6.3 Information-loss challenge

Construct a diagnostic panel where aggregate field counts are identical but relevant connectivity differs.

First verify that the reference consequence differs.

Then determine whether the connected representation distinguishes the cases.

This is a diagnostic challenge set, not a representative estimate of general chess accuracy.

Keep final statistical evaluation separate.

## 6.4 Metrics

Report:

- Registered roots and dependent observations.
- Supported positive, supported negative, unknown, conflicting, and incomplete outcomes.
- Correct and incorrect classified outcomes.
- Positive recall including abstention.
- Negative coverage.
- Native-schema transfer coverage.
- Rule-removal and premise-removal outcomes.
- Budget failures.
- Proof/evidence validation status.

Separate absence of support from contradicted support.

If both a proposition and its contrary have support, expose the conflict. Do not hide it by displaying only the highest-confidence channel.

Use group-aware uncertainty estimates where sample sizes permit.

Do not describe fixture variants as independent samples.

**Deliverables:** Matched evaluation, intervention receipts, information-loss panel, and failure census.

---

# C15-07 — Budgets, Proof Integrity, and Cost

## Objective

Measure the real reasoning workload while preserving evidence.

## 7.1 Budget sensitivity

Register step and queue budgets before final testing.

For small capability fixtures, include a sufficiently generous diagnostic run and smaller operational budgets.

Measure:

- Initial and retained tasks.
- Initial and retained beliefs.
- Selected tasks.
- Derived statements.
- Grounded role instances.
- Native invocation counts.
- Duplicate derivations.
- Wall time.
- Peak memory.
- Output and proof bytes.

Audit eviction and stopping behavior.

A completed bounded run with no matching answer means:

    no support found under the reported budget

It does not prove the queried proposition false.

An error or timeout means incomplete execution.

Do not claim complete saturation unless the actual termination conditions justify it.

Input-order sensitivity under bounded queues must be reported. Do not silently reorder inputs based on expected answers.

## 7.2 Data-access census

For each arm, report:

- Persistent learned rule count.
- Supplied fact count.
- Native tasks and beliefs.
- Host-side indexes.
- Native-resident state, if any.
- Per-request materialization.
- Stored proof objects.
- Cache entries and invalidations.

Do not count a JSON proof object as a native belief.

Do not call a host Merkle store a native reasoning graph.

A fresh native knowledge base per request is acceptable for this cycle.

Persistent interpreter state is optional and may be investigated only after correctness and isolation are established.

## 7.3 Compact proof reuse

Reuse Cycle 14 content-addressed proof storage where practical.

Retain:

- Exact input program.
- Rule and fact manifests.
- Native runtime hashes.
- Budgets.
- Native output.
- Evidence stamps.
- Proof-witness origin.
- Learning provenance.
- Query identity.
- State/history identity.

Do not collapse distinct evidence occurrences merely because their truth values are equal.

If proof reconstruction is post-hoc, label it accordingly.

## 7.4 Benchmark categories

Separate:

1. Uncached native derivation.
2. Repeated inference with permissible computation caches.
3. Retrieval of a previously stored answer.
4. Full proof retrieval/reconstruction.

A cached-answer retrieval speedup is not a native-inference speedup.

Benchmark new states, not only exact repeated requests.

Include matched full-scope and scoped runs. Scope reduction must preserve relevant facts and must not select a known proof.

Use at least ten repetitions for the small headline workloads, subject to recorded resource limits.

No absolute speed target overrides correctness.

## 7.5 Artifact discipline

Avoid repeating the oversized-publication problem.

Store ordinary source, tests, compact fixtures, summaries, manifests, and small representative proofs in Git.

Keep large generated archives in an external local output directory with content hashes and restoration instructions.

Do not place generated dependency caches or full native environments in Git.

Use the existing publication pattern, but do not create a release or upload assets without separate authorization.

**Deliverables:** Budget study, graph/data-access census, proof audit, benchmarks, and artifact-size manifest.

---

# C15-08 — Integration, Preservation, and Decision Report

## Objective

Deliver a usable isolated experiment and an evidence-based architectural decision.

## 8.1 Proposed implementation layout

Adapt to existing repository conventions.

A suitable layout may be:

    src/pln_chess/cycle15/
        native_reasoner.py
        knowledge.py
        observations.py
        queries.py
        provenance.py

    knowledge/cycle15/
        domain_rules.metta
        schemas.json

    training/cycle15_consequences.py
    evaluation/cycle15_consequences.py

    tests/test_cycle15_native_reasoner.py
    tests/test_cycle15_observations.py
    tests/test_cycle15_consequences.py
    tests/test_cycle15_transfer.py

Do not duplicate existing modules without justification.

Domain knowledge must be separable from host orchestration.

Changing a domain rule file must not require editing the inference adapter.

## 8.2 Interface contract

Provide an experimental API conceptually equivalent to:

    infer_consequence(
        observed_state,
        supplied_candidate,
        target_relation,
        knowledge_checkpoint,
        budgets,
        proof_mode,
    )

Return:

- Query and target semantics.
- Observation scope.
- Supplied fact/rule counts.
- Grounding mode.
- Native answer and contrary support.
- Strength and confidence.
- Classification and incompleteness.
- Evidence stamps and ancestry references.
- Native execution receipt.
- Proof or proof-witness status.
- Budget usage.
- Model/runtime identities.

Do not add a `best_move` field.

Provide a CLI capable of reproducing a microcase and a blocker-move experiment.

Document actual commands after implementation. Do not list nonexistent commands as delivered.

Reuse an existing inspector view or provide a compact CLI/HTML report. A new interactive application is out of scope.

## 8.3 Mandatory preservation

Preserve:

- Accepted legal checkpoint bytes.
- Established legal classifications and native proof parity.
- All 287 negative controls.
- All 27 history controls.
- Both known en-passant recoveries.
- All 76 controlled legal holdouts.
- Historical field and concept behavior.
- Protected historical files.
- Runtime and operator hashes.
- Existing public APIs unless a migration is explicitly documented.

Run the complete source-bound legal preservation suite at final acceptance.

If required evidence or dependencies are unavailable, report the exact blocked checks. Do not claim complete preservation from a targeted smoke test.

Preference and consequence checkpoints remain opt-in.

## 8.4 Production-boundary tests

Test with evaluation-oracle access disabled.

Verify that:

- Labels and engine outputs cannot enter inference inputs.
- Test labels cannot update learned rules.
- Raw coordinates do not enter learned rule constants.
- No descriptor-key fallback produces the experimental answer.
- No Python or custom MeTTa chess adjudicator supplies the queried conclusion.
- Native failure does not trigger an undisclosed fallback.
- State and evidence from one request cannot leak into another.

## 8.5 Required documents

Produce:

    docs/cycle15/engineering-report.md
    docs/cycle15/package-matrix.md
    docs/cycle15/research-registration.md
    docs/cycle15/native-capabilities.md
    docs/cycle15/relative-knowledge.md
    docs/cycle15/blocker-consequences.md
    docs/cycle15/learning-and-transfer.md
    docs/cycle15/performance-and-proofs.md
    docs/cycle15/reproduction.md
    docs/cycle15/architecture-decision.md

Reports should link to compact reproducible evidence rather than duplicate large proof dumps.

The package matrix must separate implementation status from research outcome.

---

## 6. Acceptance Gates

### Mandatory engineering gates

1. Experimental subsystem is isolated.
2. Runtime and native calculus remain unchanged.
3. No production oracle.
4. No hidden descriptor-to-answer fallback.
5. Exact input/output provenance is retained.
6. Unknown, conflicting, and incomplete outcomes remain distinguishable.
7. Evidence replay does not manufacture confidence.
8. Historical checkpoint and regression protections pass.
9. Clean reproduction instructions work within their stated scope.
10. No push, publication, or deployment occurs.

### Native-execution research gate

Demonstrate an absent conclusion through the native reasoner, with rule and premise interventions.

Retrieving an input fact does not pass this gate.

Directly scheduling a truth-function call does not pass this gate.

### Relational-binding research gate

Demonstrate a reusable schema binding unfamiliar entities while preserving shared roles.

Uniform host grounding is reported separately and does not satisfy the strongest binding claim.

### Learning research gate

Demonstrate native evidence revision of reusable knowledge and a measurable effect on held-out inference.

Supplied high-confidence rules alone do not pass this gate.

### Chess-consequence research gate

Demonstrate at least one nontrivial target derived from lower-level permitted observations.

Stage A imported-attack chains do not substitute for Stage B.

State the exact supported scope: for example, a single intervening cell, a fixed ray family, or a broader held-out range.

Do not claim general chess legality from a local consequence result.

---

## 7. Research Targets

These are investigation targets, not permission to fabricate results.

| Area | Target |
|---|---|
| Capability probes | All registered native micro-experiments executed |
| Native chaining | At least one multi-rule absent conclusion with interventions |
| Shared-role binding | At least one schema applied to unfamiliar entity bindings |
| Blocker cases | All required scenario families represented |
| Learning | Native revision over a disclosed bounded template grammar |
| Independent evaluation | At least 48 held-out root families |
| Transfer | Held-out locations, roles, and ray geometry within declared scope |
| Representation | Distinguish equal-count cases with different relevant connectivity |
| Preservation | All mandatory operational gates pass |
| Publication size | No large generated evidence accidentally added to ordinary Git |

Report actual positive/negative accuracy, coverage, uncertainty, and errors.

Do not use zero answers as evidence of perfect accuracy.

Do not conceal an unsupported research outcome behind a complete work-package count.

---

## 8. Decision Paths

The final report must choose the appropriate outcome.

### Outcome 1 — Native execution works; relational binding does not

Deliver the adapter and minimal binding failure.

Do not claim the original architecture is achieved.

Recommend the smallest remaining compatibility question or separately authorized change.

### Outcome 2 — Native binding works; raw chess consequence remains partial

Preserve the demonstrated rule-driven architecture.

Identify the exact semantic/composition gap, such as path clearance or shared-evidence restrictions.

Recommend a focused follow-up, not another broad preference study.

### Outcome 3 — Local consequences learn and transfer

Recommend extending to one additional consequence family, such as protection lost after a defender moves.

Only then propose a matched experiment testing whether those consequences improve preference learning.

### Outcome 4 — Native reasoning is correct but too expensive

Keep the semantic result.

Prioritize scope, caching, or execution-control improvements without changing the calculus or relabeling incomplete searches as negative answers.

A persistent native knowledge base may be investigated later. It is not required for the core architecture result.

---

## 9. Autonomous Execution Contract

Authorized:

- Local inspection and implementation.
- Read-only retrieval of pinned public reference sources.
- Existing evidence restoration where required.
- Native reasoning experiments.
- Training and evaluation in isolated modules.
- Tests, profiling, reports, and local commits.

Not authorized:

- `git push`.
- Remote releases, pull requests, or artifact uploads.
- Deployment.
- Paid services or new credentials.
- Runtime upgrades or upstream edits.
- New native inference operators.
- Operational legality changes.
- Autonomous chess move selection.
- Deleting or rewriting historical evidence.
- Weakening acceptance criteria.

The earlier successful smaller publication does not authorize publication of Cycle 15.

Complete all feasible packages in one consolidated run.

Do not request approval after every milestone.

If one capability is unavailable, preserve the counterexample, continue independent work, and report the architectural boundary.

Do not spend the remaining budget recreating the old conditional pipeline under a new name.

---

## 10. Final Codex Response

Return:

1. Starting and ending commits.
2. Working-tree state and local commit list.
3. Confirmation that no remote write occurred.
4. Eight-package delivery matrix.
5. Separate native-execution, binding, learning, and chess-consequence outcomes.
6. Exact native API forms and runtime identities used.
7. Grounding classification.
8. Stage A versus Stage B results.
9. Held-out transfer counts, errors, and abstentions.
10. Rule/premise/ancestry intervention results.
11. Matched baseline comparisons.
12. Evidence-dependence findings.
13. Budget and input-order sensitivity.
14. Proof-capture versus reconstructed-witness scope.
15. Cold inference and cached-retrieval costs separately.
16. Legal preservation and historical-file verification.
17. Clean reproduction status.
18. Known limitations.
19. Architecture decision.
20. Recommended next experiment.

Every major claim must link to executable evidence.

Do not describe a host proof graph as a native knowledge graph.

Do not describe native truth-value calculation alone as native relational rule selection.

Do not describe supplied rule structure as learned structure.

---

## 11. Reference Sources

[S1] Pinned vendored native implementation:
https://github.com/machieke/pln-chess/blob/d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d/vendor/pln/lib_pln.metta

[S2] Runtime lock:
https://github.com/machieke/pln-chess/blob/d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d/configs/runtime-lock.json

[S3] Pinned upstream example:
https://github.com/trueagi-io/PLN/blob/4405956947c4b53c7ff01bd565aa3b114bc970a1/examples/Smokes.metta

[S4] Cycle 14 inference:
https://github.com/machieke/pln-chess/blob/d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d/src/pln_chess/cycle14/inference.py

[S5] Cycle 14 relative representation:
https://github.com/machieke/pln-chess/blob/d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d/docs/cycle14/relative-representation.md

[S6] Cycle 14 publication and evidence restoration:
https://github.com/machieke/pln-chess/blob/d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d/docs/cycle14/publication.md

Use the pinned implementation as the executable source of truth.

Online documentation does not authorize changing the runtime.

---

## Final Objective

Cycle 15 should establish whether the existing native PLN reasoner can apply reusable relative knowledge to infer a local chess consequence without Python prescribing the conclusion.

The flagship result is not a larger preference dataset or a better-looking graph.

It is an inspectable derivation in which:

- Relative observations enter the knowledge base.
- Shared entities and dependencies remain represented.
- Native inference applies the relevant declarative knowledge.
- Evidence changes the learned rule beliefs.
- The same knowledge transfers to an unfamiliar configuration.
- Missing premises and unsupported composition remain explicit.

Preserve the central principle:

**Python provides the environment and infrastructure. Declarative relational knowledge expresses the chess hypotheses. Native PLN performs the supported reasoning.**