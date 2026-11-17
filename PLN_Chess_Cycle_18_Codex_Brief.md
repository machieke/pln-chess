# PLN Chess — Cycle 18 Consolidated Engineering Brief

## Source-Bound Shared-Parameter Semantics and Evidence Contracts

**Repository:** https://github.com/machieke/pln-chess
**Starting commit:** `24f30ce8d4e0631f8937404929485dfdc0032f93`
**Starting branch:** `cycle17-shared-evidence-semantics`
**Delivery branch:** `cycle18-shared-parameter-contract`
**Operational baseline:** Unchanged accepted Cycle 12 legal checkpoint
**Execution:** One consolidated autonomous engineering assignment
**Delivery:** Source, executable contracts, reference experiments, native controls, tests, evidence, reports, commits, and a verified GitHub push

**Explicit authorization:**
Commit the completed work and push the dedicated delivery branch to the existing
`machieke/pln-chess` repository. Do not stop at local commits.

This does not authorize changing the native calculus, modifying the accepted
legal model, force-pushing, merging into master, publishing releases, uploading
bulk evidence, or deploying services.

---

## 1. Mission

Cycle 18 must turn the shared-evidence problem into an executable, source-bound
semantics contract.

Cycle 17 demonstrated that the native reasoner composes the learned clearance
and attack rules when their registered training ancestry is disjoint. Shared
training ancestry blocks the tested combinations, even when learned truth values
are identical.

Cycle 18 must not simply repeat that experiment or its illustrative probability
examples.

The new objective is:

> Define what the uncertain quantities in the actual two-rule learning experiment
> represent, which external observations update them, what an application reuses,
> and what can be concluded when dependence is specified or left unknown.

There are two distinct deliverables:

1. A typed evidence/application contract linked to real Cycle 17 records.
2. A small, isolated finite reference implementation that evaluates explicit
   semantic assumptions against those records.

Neither deliverable changes native inference.

A reference probability must never replace an unknown native answer.

The final architectural decision should identify whether a future isolated
native experiment can be specified precisely enough to request authorization.

---

## 2. Starting Findings and Source of Truth

Read these pinned files before implementation:

    docs/cycle17/engineering-report.md
    docs/cycle17/training-design.md
    docs/cycle17/composition-results.md
    docs/cycle17/reference-semantics.md
    docs/cycle17/evidence-policy-decision.md
    docs/cycle17/reproduction.md
    docs/cycle17/publication.md

    research/cycle17/provenance.py
    research/cycle17/reference_models.py
    research/cycle17/corpus.py
    research/cycle17/study.py

    artifacts/cycle17/witnesses/index.json

    knowledge/cycle16/finite_two.metta
    vendor/pln/lib_pln.metta
    configs/runtime-lock.json

Discover actual ledger, checkpoint, revision-receipt, and acceptance paths from
the repository rather than assuming filenames.

### Reported baseline to verify

- S-AA and S-BB derive clearance but not attack.
- D-AB and D-BA derive both clearance and attack.
- One overlapping training source is sufficient to block the tested matched pair.
- All six primary/sweep arms learn targeted parameters with:
  strength 1 and confidence 0.923076923076923.
- The two disjoint arms have attack confidence 0.8184960085207099 on the minimal
  fixture.
- Training preparation retains 48 admitted positive conditional observations
  and 384 dependent blocked/unknown exclusions.
- The held-out panel contains 96 dependent endpoints from 24 roots.
- Generic recursive reuse remains unresolved.

These are source-reported results, not universal guarantees.

The runtime remains pinned to:

- PLN: `4405956947c4b53c7ff01bd565aa3b114bc970a1`
- PeTTa: `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`

Verify actual hashes and identities from the lock and acceptance manifests.

---

## 3. Scope and Explicit Exclusions

### Authorized work

- Read-only inspection and restoration of existing research evidence.
- Source-bound observation and parameter-generation schemas.
- Immutable evidence registry and replay tests.
- Exact finite reference calculations for the registered two-parameter problem.
- Native baseline replay through the unchanged runtime.
- Mathematical assumptions, bounds, and identifiability analysis.
- An implementation-ready proposal for a future experiment.
- Tests, documentation, local commits, and the dedicated branch push.

### Not authorized

- Editing `StampDisjoint`, `PLN.Derive`, native truth formulas, or inference clauses.
- Introducing a new native inference operator.
- Removing, renaming, or manufacturing provenance to obtain a desired derivation.
- Treating a proof application as new training evidence.
- Feeding reference-model outputs into native checkpoints, inference, caches,
  classifications, or move selection.
- Assuming native strength/confidence is a Beta distribution or Bayesian posterior.
- Implementing a general probabilistic programming system.
- New path-length templates, broad preference training, or autonomous chess play.
- Changes to accepted operational source or legal defaults.
- Rewriting historical evidence.

Keep new work under an isolated research namespace.

The reference laboratory is executable specification work—not an alternative
chess inference backend.

---

## 4. Core Distinctions

The contract must distinguish:

| Entity | Meaning |
|---|---|
| Domain schema | The supplied logical structure of a rule |
| Parameter | A specifically defined uncertain quantity under a declared model |
| Parameter generation | A version produced from admitted evidence and assumptions |
| Observation event | An external observation with identity, content, and provenance |
| Source ancestry | Shared episode, game, instrument, or other recorded origin |
| Derived annotation | A label or feature computed from existing observations |
| Application | Use of existing knowledge for a particular binding/query |
| Prediction | An output conditional on the specified model and information |
| Native proof record | What the pinned runtime actually returned or exposed |
| Reference result | A result under an explicitly declared mathematical model |

Do not confuse:

- Same source game with the same observation.
- Same payload with the same event.
- Different identifiers with independent evidence.
- Multiple labels from one episode with automatically independent measurements.
- A new parameter generation with new observations.
- Posterior reuse with repeated likelihood application.

Typed provenance is necessary for clarity. It does not alone solve correlated
uncertainty propagation.

---

## 5. Execution Plan

Deliver eight packages:

1. Preserve the baseline and register the semantics study.
2. Bind the evidence contract to actual Cycle 17 records.
3. Specify the target and parameter meanings.
4. Implement the bounded finite reference models.
5. Verify application, replay, conflict, and cycle behavior.
6. Produce the native compatibility and future-change specification.
7. Complete preservation, reproducibility, and cost analysis.
8. Package, commit, push, and verify remote delivery.

Do not expand the experiment before the source-bound contract and target
definitions are settled.

Reuse existing fixtures rather than generating a large new corpus.

A negative or underidentified result is valid. Do not force a point estimate
merely to make the reference system appear decisive.

---

# C18-01 — Baseline Preservation and Registered Claims

## Objective

Establish the immutable experimental baseline and define what Cycle 18 can claim.

Verify:

- Starting SHA and branch ancestry.
- Working-tree state.
- Native source and dependency hashes.
- Accepted legal checkpoint identity and bytes.
- Cycle 17 model identities.
- Training groups and evidence manifests.
- Decisive native witnesses.

Do not destructively reset unrelated work.

### Targeted native reproduction

Rerun:

- D-AB and D-BA minimal success.
- S-AA and S-BB minimal shared-chain failure.
- The one-source overlap case.
- The original eleven-stamp witness.
- Recursive-rule reuse failure.
- Representative duplicate, diamond, and cycle controls.

Use exact native programs and preserve raw outputs.

Do not rerun the full corpus repeatedly merely to regenerate unchanged evidence.

### Registration

Create:

    docs/cycle18/research-registration.md

Freeze:

- The actual record population.
- Event identity and deduplication rules.
- Target quantities.
- Candidate parameter interpretations.
- At most three primary finite model families.
- Assumption-sensitive comparisons.
- Reference outputs and statuses.
- Resource limits.
- Native/control separation.
- Acceptance criteria.
- Publication plan.

Use separate success criteria for:

1. Engineering delivery.
2. Source mapping.
3. Semantic completeness.
4. Identifiability.
5. Native-extension readiness.

**Deliverables:** Baseline receipt, registration, and explicit claim boundaries.

---

# C18-02 — Source-Bound Observation and Parameter Contract

## Objective

Replace an illustrative provenance diagram with validated mappings to the actual
Cycle 17 training and application records.

## 2.1 Observation registry

Define a versioned record containing at least:

    event_id
    payload_hash
    source_artifact_path
    source_artifact_hash
    source_episode_id
    ancestry_groups
    observed_variables
    observation_kind
    measurement_or_label_method
    parent_event_ids
    admission_status
    exclusion_reason
    generation_or_supersession_identity

Classify observation kinds explicitly:

- Direct environmental observation.
- Evaluation-generated annotation.
- Deterministic derived annotation.
- Synthetic intervention.
- Unknown/missing observation.
- Superseded observation version.

A content hash binds payload integrity; it does not automatically define event
identity.

Two genuine events can have identical payloads.

Delivering the same event twice does not create two observations.

## 2.2 Audit the actual corpus

Map all Cycle 17 preparation records to the contract.

Reconcile reported counts:

- 432 preparation records.
- 48 admitted conditional observations.
- 384 excluded blocked/unknown conditional records.

Reconcile the same admitted sources across S-AA, S-BB, D-AB, D-BA, and overlap
arms without counting reuse across experimental arms as additional experience.

Report missing fields rather than inventing historical information.

## 2.3 Shared episodes and two labels

For each episode contributing to both `clear-two` and `rook-attack`, determine:

- Which environmental facts were observed.
- Which labels were generated.
- Whether one label was derived using information also used by the other.
- Whether labels are distinct components of one vector observation.
- Which independence assumptions, if any, would be needed to factor their
  likelihood.

Do not automatically discard one label merely because both concern the same game.

Do not automatically multiply their contributions merely because they have
different label IDs.

## 2.4 Parameter generations

Define:

    schema_id
    parameter_generation_id
    admitted_event_ids
    excluded_event_ids
    training_source_groups
    learner_identity
    model_assumptions_id
    uncertainty_representation
    prior_generation_id
    native_checkpoint_reference
    generation_content_hash

Keep the original native generation and the reference-model generation separate.

Re-estimating from the same events is a new computation, not new evidence.

## 2.5 Application records

Define:

    application_id
    parameter_generation_refs
    entity_bindings
    environmental_event_refs
    state_and_history_identity
    query
    native_execution_reference
    observed_parent_refs
    parent_observability

Applications must not append training observations.

When the native runtime does not expose fired-rule parents, retain null or
explicitly unobserved parent fields. Do not fabricate a complete proof graph.

**Deliverables:** Schemas, source mapper, complete mapping audit, and small
checked-in examples tied to actual records.

---

# C18-03 — Define the Uncertain Quantities Before Calculating

## Objective

Specify exactly what the proposed parameters and queries mean.

## 3.1 Candidate interpretation

Use `theta_clear` and `theta_attack` only after defining their events, conditioning
contexts, and population.

For example, a parameter might describe the reliability of a recorded conclusion
label among a declared population of antecedent-qualified observations.

That is not automatically:

- The probability that the chess rule itself changes.
- The probability that an already observed cell is empty.
- The native rule's confidence.
- A calibrated error probability on arbitrary boards.

Document alternative interpretations and select one primary reference meaning.

## 3.2 Deterministic chess versus uncertain knowledge

The underlying chess relation can be deterministic for a fully specified state.

Uncertainty may instead concern:

- An imperfect observation.
- A supplied template's applicability.
- Representation limitations.
- A label-generation process.
- Generalization to a declared population.

Do not invent stochastic chess laws to justify a convenient probabilistic model.

A statement that the existing observations cannot identify the proposed
interpretation is an acceptable result.

## 3.3 Selection and admission

The Cycle 17 natural training rows were selected for antecedent satisfaction,
and all admitted labels were positive.

State whether selection depends on:

- Antecedent observations.
- The conclusion label.
- Reference-engine validation.
- Source ordering.
- Other availability conditions.

Model a conditional population or selection process honestly.

Do not extrapolate an admitted all-positive sample into a calibrated general
failure rate.

Blocked paths remain exclusions from an all-empty conditional, not fabricated
negative training outcomes.

## 3.4 Query definition

Define the reference query independently of the native result.

A general reference form is:

    predictive_quantity =
        expectation of q(theta_clear, theta_attack, context)
        under the declared reference model and admitted evidence

The function q must come from a fully stated event/conditional model.

Do not set q to a product merely because the logical proof has two rules.

A sequential conditional model may justify a product under its stated semantics.
That is a declared model, not a consequence of flat stamp disjointness.

Never use a natively derived `Clear` conclusion as an additional observed event
in the reference model. That would reuse the inference as evidence.

## 3.5 Confidence interpretation

Retain distinct fields for:

- Native strength.
- Native confidence.
- Reference predictive probability.
- Reference parameter uncertainty.
- Bounds caused by unspecified dependence.
- Empirical evaluation uncertainty.

Do not map posterior variance, sample count, or interval width into native
confidence without a separate justified specification.

“Confidence mapping unresolved” is preferable to an invented conversion.

**Deliverables:** Target semantics, parameter definitions, admission analysis,
and explicit unresolved interpretation obligations.

---

# C18-04 — Bounded Source-Bound Reference Models

## Objective

Implement a small reference laboratory connected to the mapped observations.

Do not create a general Bayesian-network or probabilistic-programming engine.

Use at most two rule parameters and a small registered finite support, initially
no more than 25 joint parameter states.

A small finite nuisance variable is permitted only when essential to a registered
shared-observation example and explicitly included in the resource bound.

Use rational arithmetic for primary examples where feasible.

## 4.1 Three model families

### M-F — Explicitly factorized reference model

State:

- The joint prior.
- The observation model.
- The assumptions permitting factorization.
- The conditional-independence assumptions between source groups.
- The query event.

Different native stamps do not establish these assumptions.

Shared source records may still admit a factorized model, but only if that
factorization is explicitly imposed and justified as a reference hypothesis.

### M-J — Explicit finite joint model

Retain a non-factorized joint distribution over the two parameters.

Specify the complete prior and observation likelihoods.

Use shared observations as joint evidence rather than independently applying the
same fact to each parameter.

Compare at least two registered joint assumptions that are compatible with the
same recorded marginal information.

Do not choose the dependence model because it best reproduces a desired native
answer.

### M-B — Partially identified model

When dependence information is insufficient, return identified bounds or
`not_identified`.

State exactly what information is fixed:

- Parameter marginals.
- Event marginals.
- A finite family of joint models.
- Additional constraints.
- A complete posterior.

These are different bounding problems.

## 4.2 Source-group likelihood contract

A reference update may take the form:

    posterior(theta | D, M)
        proportional to
    prior_M(theta) × product over source groups g of L_g(D_g | theta, M)

Use that product only when conditional factorization across those groups is an
explicit assumption.

Within a source group, use a joint likelihood for all relevant observations
unless a further factorization is explicitly specified.

Each real observation must enter with the intended multiplicity.

A single observation can inform multiple parameters through one joint likelihood.
It must not acquire extra likelihood factors solely because several rules use it.

## 4.3 Source-bound execution

Run the registered reference families using mapped Cycle 17 event sets.

For every result expose:

- Exact event IDs.
- Exact source-group IDs.
- Model family.
- Prior and likelihood specification.
- Assumptions.
- Query definition.
- Posterior or feasible-set identity.
- Numerical result or bounds.
- Identifiability status.

No automatic prior selection from native `(strength, confidence)` is allowed.

Any finite grid is a supplied approximation/design choice. Report grid sensitivity
within a small preregistered panel.

Do not claim a grid-based answer is an exact continuous-parameter result.

## 4.4 Bounds and witnesses

For small marginal-coupling problems, provide feasible extremal joint distributions
that attain reported endpoints when claiming sharp bounds.

An envelope over several chosen model examples is not automatically a sharp bound
over every joint distribution compatible with the data.

Distinguish:

- Bounds for supplied posterior marginals.
- Bounds after conditioning an incompletely specified prior.
- Sensitivity ranges across selected assumptions.

If the stronger problem is not solved, label the weaker result precisely.

## 4.5 Avoid repeating Cycle 17

Keep the earlier fair-bit, shared-parameter, diamond, and cycle examples as
regression fixtures.

The new contribution must be:

- Validated actual-event mappings.
- Source-bound likelihood construction.
- Explicit parameter-generation semantics.
- Application without re-learning.
- Assumption-sensitive results for the actual admitted evidence.

A larger collection of unrelated toy examples does not satisfy this package.

## 4.6 Output boundary

Use a distinct result schema, for example:

    reference-semantics-v18

Include statuses such as:

    point_under_declared_model
    bounded_under_declared_constraints
    not_identified
    inconsistent_evidence
    resource_incomplete

Do not emit native `stv` objects or production `supported-positive`
classifications from this reference module.

**Deliverables:** Exact finite implementation, source-bound runs, extremal
witnesses where justified, and assumption-sensitivity report.

---

# C18-05 — Learning, Application, Replay, and Conflict Controls

## Objective

Make the evidence contract falsifiable through executable controls.

## 5.1 Required controls

| Control | Required contract behavior |
|---|---|
| Same event delivered repeatedly | No additional likelihood or evidential weight |
| Same payload from a genuinely different event | Distinct event retained; dependence still requires a model |
| Same event ID with changed payload | Reject or explicitly supersede; never silently overwrite |
| One event produces two dependent annotations | Retain dependency; no automatic independent counting |
| One vector event informs two parameters | Use the registered joint observation model |
| Parameter generation applied repeatedly | Prediction reuse does not update the posterior |
| New external observation | Creates a new admitted update and generation |
| Source group removed | Recompute from remaining evidence, not subtract confidence heuristically |
| Shared-ancestor diamond | Preserve the common event/parameter identity |
| Cycle without new observations | No increase in evidence or posterior concentration merely from cycling |
| Conflicting observations | Apply a declared noise/conflict policy or return inconsistency |
| Missing dependence | Bounds or unresolved result, not silent independence |
| Inference outcome reintroduced as observation | Reject unapproved self-training |
| State/history changes | New contextual identity; no stale prediction reuse |

## 5.2 Application-repeat test

Apply the same parameter generation to the same query 1, 10, and 100 times.

Verify:

- Admitted event set unchanged.
- Parameter-generation scientific identity unchanged.
- Posterior/reference bounds unchanged.
- Only execution/application records increase.

Do not require execution timestamps or request identifiers to remain identical.

## 5.3 Distinct measurement versus duplicate label

Test:

1. Two labels computed deterministically from one underlying observed variable.
2. Two measurements with a declared joint noise model.
3. Two conditionally independent measurements under an explicit assumption.

These must not be collapsed into the same evidence treatment.

## 5.4 Contradiction and zero-likelihood cases

A noise-free model may assign zero probability to the supplied evidence.

Return an explicit inconsistent-model/evidence state.

Do not normalize by zero, add an undisclosed epsilon, or silently replace the
noise model.

A noisy alternative is a separate registered model with separate outputs.

Synthetic corruptions and deliberately false hypotheses must remain quarantined
from real native training ledgers.

## 5.5 Full recomputation parity

Compare incremental event ingestion with rebuilding the reference result from
the same active event set.

Test order independence where the declared model requires it.

Replay and supersession histories remain inspectable even when active scientific
state is equivalent.

**Deliverables:** Executable control matrix, property tests, and exact replay/
recomputation receipts.

---

# C18-06 — Native Correspondence and Future Change Specification

## Objective

Explain what a future native mechanism would require without implementing it.

## 6.1 Side-by-side correspondence

For the actual shared and disjoint two-rule cases, produce a record containing:

- Native input facts/rules.
- Native answer channels.
- Native stamp overlap.
- Observed trace scope.
- Mapped external event set.
- Parameter definitions.
- Reference assumptions.
- Reference result.
- Whether the native and reference quantities have comparable meanings.

The comparison is explanatory, not a numerical accuracy competition.

Do not describe a reference-model positive probability as having “fixed” the
native shared-chain failure.

The native result must remain unchanged.

## 6.2 Representation-gap analysis

Determine which required information is currently:

- Present in native truth values.
- Present in native stamps.
- Present only in host provenance.
- Recoverable from the original ledger.
- Supplied as a model assumption.
- Missing or not identifiable.

For a proposed bridge, state what new data would be needed.

Do not imply that typed provenance supplies a joint distribution.

## 6.3 Proposed future interface

Specify, but do not activate, a versioned future contract for:

    Observation registration
    Parameter estimation/revision
    Knowledge application
    Dependence declaration
    Query evaluation
    Conflict handling
    Proof provenance
    Resource limits

The proposal must state whether it would require:

- Richer truth values.
- A joint-parameter object.
- Retained sufficient statistics.
- An explicitly constrained factorization.
- Interval-valued support.
- A different distinction between rule identity and evidence identity.
- A different native admissibility or propagation policy.

A generic recommendation to “ignore rule stamps” is insufficient.

## 6.4 Mathematical obligations

State which obligations are demonstrated and which remain open:

- Probability interpretation.
- Confidence interpretation.
- Duplicate-evidence behavior.
- Shared-parameter reuse.
- Shared-observation updates.
- Cyclic derivation behavior.
- Conflict/noise semantics.
- Conservative treatment of unidentified dependence.
- Backward compatibility.
- Termination and resource growth.
- Approximation guarantees, if proposed.

Do not claim a sound replacement policy if only the probability portion is
specified and native confidence remains unmapped.

## 6.5 Decision

Choose:

A. Existing information is sufficient only under explicit restricted assumptions.

B. Source-bound joint semantics are specified, but a native bridge still has
   unresolved obligations.

C. A sufficiently precise isolated native prototype can be proposed for separate
   authorization.

D. The intended parameter meaning or evidence model remains unidentifiable, and
   additional measurements/specification are required.

No outcome authorizes implementing a native policy change during Cycle 18.

**Deliverables:** Correspondence report, representation-gap matrix, future
interface specification, and explicit decision.

---

# C18-07 — Isolation, Preservation, and Reproduction

## Objective

Keep the reference laboratory from becoming an accidental inference backend.

## 7.1 Import and dataflow isolation

Place the reference implementation in a dedicated namespace.

Permit it to be imported by:

- Its research CLI.
- Its tests.
- Clearly labeled research-report generation.

Prohibit imports or output consumption from:

- Operational inference.
- Native consequence adapters.
- Native training.
- Model/checkpoint construction.
- Production cache lookup.
- Legal or preference classification.

Test static imports, known dynamic-import entry points, and runtime output paths.

No reference result may be serialized into a native checkpoint.

## 7.2 Native invariance

Replay the decisive Cycle 17 cases.

Confirm that shared arms remain blocked and disjoint arms retain their recorded
behavior under the unchanged native inputs.

Do not let source-bound reference analysis modify original evidence stamps or
training admissions.

## 7.3 Operational preservation

Preserve:

- Accepted legal checkpoint bytes and semantic identity.
- Native runtime and vendor hashes.
- Operational source identity.
- Historical files and scientific receipts.
- Existing public APIs.
- 206 legal shards and 584,112 candidate-row classifications/proofs.
- 287 negative evidence-removal controls.
- 27 history controls.
- Both known en-passant recoveries.
- 76 controlled legal holdouts.

Use the actual registered acceptance manifests.

Run targeted checks during development and one complete source-bound acceptance
run after executable changes are frozen.

Do not rerun every historical research campaign merely to produce more logs.

If a required gate cannot run, report the exact missing dependency/evidence.
Do not describe targeted checks as complete preservation.

## 7.4 Reproduction levels

Provide:

1. Small source-bound contract example from a clean checkout.
2. Exact finite reference/control suite.
3. Decisive native shared/disjoint replay.
4. Complete historical preservation requiring restored evidence.

The first three should use compact checked-in fixtures wherever possible.

Distinguish reused verified dependencies from fresh dependency installation.

## 7.5 Resource accounting

Record:

- Reference state-space size.
- Number of likelihood evaluations.
- Rational-arithmetic growth.
- Native invocations separately.
- Wall time and memory.
- Output and retained artifact sizes.
- Budget failures.

Do not benchmark a small finite reference calculation as proof that a future
general correlated-inference system would scale.

**Deliverables:** Isolation tests, invariance receipts, preservation results,
resource report, and clean reproduction commands.

---

# C18-08 — Consolidated Delivery

## Suggested layout

Adapt to existing repository conventions:

    research/cycle18/
        contracts.py
        source_mapping.py
        reference_joint.py
        reference_bounds.py
        applications.py
        native_comparison.py
        cli.py

    tests/test_cycle18_contracts.py
    tests/test_cycle18_reference.py
    tests/test_cycle18_replay.py
    tests/test_cycle18_isolation.py

    artifacts/cycle18/
        registration/
        mappings/
        reference_cases/
        native_controls/
        summaries/
        publication/

Do not build an unrelated general inference framework.

## Required reports

Produce:

    docs/cycle18/engineering-report.md
    docs/cycle18/package-matrix.md
    docs/cycle18/research-registration.md
    docs/cycle18/source-evidence-contract.md
    docs/cycle18/parameter-semantics.md
    docs/cycle18/source-bound-reference.md
    docs/cycle18/replay-and-conflict-controls.md
    docs/cycle18/native-compatibility.md
    docs/cycle18/architecture-decision.md
    docs/cycle18/reproduction.md
    docs/cycle18/publication.md

Each package must distinguish:

- Implementation delivered.
- Experiments executed.
- Research finding.
- Remaining limitation.
- Evidence location.

Include compact decisive records in Git.

The principal result must be inspectable without access to the development
machine's absolute local paths.

No required report should consist only of an assertion that another unavailable
archive passed.

---

## 6. Acceptance Criteria

### Mandatory engineering gates

1. Native runtime and policy unchanged.
2. Accepted operational learner unchanged.
3. Real source records mapped without fabricated fields.
4. Event identity distinct from payload equality and source grouping.
5. Application does not create learning evidence.
6. Reference models cannot feed native outputs or checkpoints.
7. Unknown dependence is explicit.
8. Inconsistent evidence is not silently repaired.
9. Replay and recomputation satisfy the declared contract.
10. Compact reproduction works from the published branch.
11. Claims are tied to their actual evidence and assumptions.
12. Commit and push are verified.

### Research targets

| Area | Required investigation |
|---|---|
| Source binding | All Cycle 17 preparation records accounted for |
| Shared observation | Actual clearance/attack label relationships mapped |
| Parameter semantics | A precise primary interpretation or an explicit nonidentifiability finding |
| Reference families | Factorized, joint, and partially identified cases |
| New contribution | Actual event-to-likelihood mapping, not repeated toy arithmetic |
| Replay | Duplicate delivery and repeated application separated |
| Dependence | Source-bound sensitivity and identified-information analysis |
| Native bridge | Implementable specification or explicit missing obligations |

There is no required chess-accuracy improvement.

Shared native answers are expected to remain unchanged because the policy is not
being modified.

Do not interpret that preservation as a research failure or force a native
positive answer to satisfy an artificial target.

---

## 7. Commit and Push — Required Delivery

### Authorization

You are explicitly instructed to:

1. Commit the implementation, tests, reports, and compact evidence.
2. Push the delivery branch to `machieke/pln-chess`.
3. Verify that the remote branch points to the final local commit.
4. Confirm that the principal report and minimal reproducer are retrievable.

Do not finish with “committed locally” when publication is possible.

A negative research result must still be committed and pushed with its
limitations accurately documented.

### Branch safety

Use:

    cycle18-shared-parameter-contract

Verify descent from:

    24f30ce8d4e0631f8937404929485dfdc0032f93

Do not destructively reset existing branches.

If the intended branch already contains unrelated work, create a documented
new branch name with a suffix.

Never use force-push, mirror push, push-all, or a master/main update.

Do not merge or create a release.

### Remote verification before pushing

Inspect the actual fetch and push URLs and any URL rewriting.

The authorized repository is exactly:

    machieke/pln-chess

Do not assume a remote named `origin` necessarily points there.

Do not expose tokens or credential-bearing URLs in reports.

Resolve multiple push URLs before publication so that the push cannot write to
an unintended repository.

---

## 8. Publication Size and Evidence Discipline

Retain the smaller-publication approach.

### Track in ordinary Git

- Source, tests, and schema definitions.
- Small source-bound fixtures.
- Compact experimental checkpoints/manifests where applicable.
- Reports and result summaries.
- Exact decisive reference cases.
- Representative native witnesses.
- Reproduction scripts and hashes.

### Keep outside ordinary Git

- Native environments and dependency caches.
- Repeated complete historical proof exports.
- Large databases and bulk transcript collections.
- Temporary profiles and generated caches.
- Large local evidence packs.

Use project budgets:

- No new blob larger than 10 MiB.
- Aim for at most 100 MiB of new unique Git blob content across the whole
  Cycle 18 commit range.

These are project publication budgets, not platform-limit claims.

Audit every new reachable blob, including files added and later deleted.

Do not blanket-ignore the evidence directory: decisive small evidence must
remain reviewable.

If publication size fails, preserve local evidence and repackage only unpublished
Cycle 18 work with a backup and recorded mapping.

Do not rewrite already published history.

No release upload or external artifact hosting is authorized. Clearly identify
bulk evidence that remains local.

---

## 9. Required Git Delivery Procedure

Create meaningful implementation and reporting commits.

Stage explicit reviewed paths rather than blindly adding the entire working
directory.

A suggested final packaging message is:

    Deliver Cycle 18 source-bound shared-parameter evidence contract

The number of commits is not an acceptance target.

After final commits and publication preflight, use a verified procedure equivalent
to:

```bash
set -euo pipefail

BASE="24f30ce8d4e0631f8937404929485dfdc0032f93"
BRANCH="cycle18-shared-parameter-contract"
CANONICAL="https://github.com/machieke/pln-chess.git"

test "$(git branch --show-current)" = "$BRANCH"
git merge-base --is-ancestor "$BASE" HEAD
test "$(git rev-list --count "${BASE}..HEAD")" -gt 0
test -z "$(git status --porcelain)"

# Remote identity, push URLs, URL rewrites, secrets, and new-blob sizes
# must already have passed the documented preflight.
LOCAL_SHA="$(git rev-parse HEAD)"

git -c push.followTags=false -c push.recurseSubmodules=no \
    push --set-upstream origin "HEAD:refs/heads/${BRANCH}"

REMOTE_SHA="$(
    git ls-remote --exit-code origin "refs/heads/${BRANCH}" |
    awk 'NR == 1 { print $1 }'
)"

CANONICAL_SHA="$(
    git ls-remote --exit-code "$CANONICAL" "refs/heads/${BRANCH}" |
    awk 'NR == 1 { print $1 }'
)"

test -n "$REMOTE_SHA"
test -n "$CANONICAL_SHA"
test "$LOCAL_SHA" = "$REMOTE_SHA"
test "$LOCAL_SHA" = "$CANONICAL_SHA"

printf 'Verified branch: %s\nVerified commit: %s\n' \
    "$BRANCH" "$LOCAL_SHA"
```

Use the actual documented alternate branch name if a suffix was required.

A fresh canonical GitHub API read is an acceptable additional remote check.

Confirm that `docs/cycle18/engineering-report.md` and the minimal reproducer are
accessible at the final commit.

Do not rely solely on a local remote-tracking reference.

### Publication failures

If authentication, network access, branch protection, or size prevents pushing:

- Preserve all local work.
- Record the exact error.
- State “committed locally; push blocked.”
- Do not claim successful publication.
- Do not bypass repository protections or credentials.

Keep the final push-verification receipt outside the tracked checkout or in the
delivery response. Avoid creating endless commits to record each commit's own
final SHA.

---

## 10. Final Codex Response

Return:

1. Starting and ending commit hashes.
2. Actual branch and working-tree state.
3. Commit list.
4. Verified remote SHA and publication status.
5. Eight-package matrix.
6. Native baseline reproduction result.
7. Source-record mapping and admission counts.
8. Chosen parameter and query meanings.
9. Factorized/joint/bounded reference results with assumptions.
10. What is identified and what remains unidentified.
11. Duplicate/application/revision distinctions.
12. Conflict, diamond, and cycle controls.
13. Native/reference separation tests.
14. Representation gaps and confidence-semantics obligations.
15. Legal preservation and exact test scope.
16. Reproduction and resource accounting.
17. Public versus local evidence.
18. Known limitations.
19. Native-extension readiness decision.
20. Recommended next experiment.

Link the published engineering report, architecture decision, reproduction guide,
and decisive source-bound examples.

Do not claim:

- A shared native inference failure was repaired.
- Reference probabilities are native PLN truth values.
- A posterior is empirically calibrated from the all-positive selected corpus.
- Typed provenance alone solves dependence.
- Generic recursion was established.
- A push succeeded without remote verification.

---

## 11. Next-Cycle Decision

### Contract and parameter meaning remain unresolved

Continue with the smallest missing semantic question or necessary measurement.

Do not implement a native policy based on an ambiguous target.

### Source-bound reference semantics are complete, but confidence or mapping is unresolved

Publish the executable specification and identify the exact remaining bridge
obligations.

Do not compress a richer joint model into an unsupported scalar truth value.

### A precise isolated native prototype can be proposed

Provide a separate authorization request naming:

- The exact native change.
- The new data representation.
- The unchanged baseline.
- Required regression counterexamples.
- Probability and confidence interpretations.
- Resource bounds.
- Migration/replay plan.

Do not implement that change during Cycle 18.

### Existing native behavior remains the appropriate conservative default

Retain it and document which supported disjoint arrangements remain usable,
without presenting separate training partitions as a universal solution.

---

## 12. Reference Sources

Pinned scientific sources:

[R1] Cycle 17 evidence-policy decision:
https://github.com/machieke/pln-chess/blob/24f30ce8d4e0631f8937404929485dfdc0032f93/docs/cycle17/evidence-policy-decision.md

[R2] Cycle 17 training design:
https://github.com/machieke/pln-chess/blob/24f30ce8d4e0631f8937404929485dfdc0032f93/docs/cycle17/training-design.md

[R3] Cycle 17 exact reference semantics:
https://github.com/machieke/pln-chess/blob/24f30ce8d4e0631f8937404929485dfdc0032f93/docs/cycle17/reference-semantics.md

[R4] Cycle 17 provenance implementation:
https://github.com/machieke/pln-chess/blob/24f30ce8d4e0631f8937404929485dfdc0032f93/research/cycle17/provenance.py

Publication references:

[R5] https://git-scm.com/docs/git-push
[R6] https://git-scm.com/docs/git-ls-remote

Use the pinned repository and runtime as the executable baseline.

---

## Final Objective

Cycle 18 must connect evidence semantics to the actual learning experiment.

The deliverable is not another collection of illustrative probability examples,
nor a replacement chess evaluator.

It is an executable contract explaining:

- What was observed.
- Which uncertain quantity was updated.
- Which observations were counted.
- What is reused when a rule is applied.
- Which dependence assumptions are supplied.
- Which predictions or bounds those assumptions identify.
- What the native runtime currently represents.
- What a future native change would need to preserve.

**Reusing knowledge is not receiving new evidence. A shared source is not a
complete dependence model. An unresolved joint distribution must not be replaced
by an undisclosed independence assumption.**

Complete the consolidated package, commit it, push the dedicated branch, and
verify that the final commit and decisive evidence are accessible remotely.