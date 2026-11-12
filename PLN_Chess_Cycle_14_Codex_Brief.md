# PLN Chess — Cycle 14 Consolidated Engineering Brief

## Reliable Preference Supervision, Temporal Generalization, and Compact Auditable Inference

**Repository:** https://github.com/machieke/pln-chess
**Starting commit:** `54353579e7921f9b47f43bbde1aa61cb887bc6e4`
**Accepted legal baseline:** Unchanged Cycle 12 promoted en-passant checkpoint
**Execution:** One consolidated autonomous engineering cycle
**Delivery:** Implementation, experiments, proofs, tests, reports, and local commits
**Authorization:** Local work only. No push, deployment, upstream changes, new PLN operators, or autonomous move selection.

---

## 1. Mission

Continue preference learning rather than introducing a chess-playing policy.

Cycle 13 established a working experimental preference pipeline, but independent evidence remains insufficient for reliable strategic move selection.

Cycle 14 must address four connected problems:

1. Unresolved or weakly specified reference preference labels.
2. Limited independent preference coverage.
3. Poorly established continuation-dependent preference learning.
4. Expensive inference responses containing duplicated proof material.

The central research question is:

> Can native PLN learn transferable, continuation-conditioned preferences from adequately characterized evidence, while preserving uncertainty, relative spatial knowledge, and complete auditability?

This is not authorization to implement a conventional chess evaluator, unrestricted search, or a new probabilistic calculus.

A successful cycle may improve engineering substantially without establishing reliable strategic preferences. Report those outcomes separately.

---

## 2. Source of Truth and Starting State

Read the actual Cycle 13 implementation and reports before editing.

Important starting documents:

- `docs/cycle13/engineering-report.md`
- `docs/cycle13/package-matrix.md`
- `docs/cycle13/research-registration.md`
- `docs/cycle13/preference-evidence.md`
- `docs/cycle13/preference-learning.md`
- `docs/cycle13/temporal-preferences.md`
- `docs/cycle13/calibration.md`
- `docs/cycle13/ablations.md`
- `docs/cycle13/performance.md`
- `docs/cycle13/reproduction.md`

Relevant existing implementation includes:

- `src/pln_chess/cycle13/`
- `training/cycle13_learning.py`
- Existing reference-label, evaluation, replay, and acceptance tools.

Discover additional paths from the checkout rather than assuming their names.

### Reported baseline

| Area | Cycle 13 result |
|---|---|
| Preference curriculum | 340 source-game pairs |
| Fixed immediate test | 56 pairs |
| Resolved test directions | 15 |
| Answered resolved directions | 6 |
| Correct answered directions | 5 |
| Answered directional accuracy | 83.3% |
| Coverage among resolved directions | 40% |
| Remaining test reference labels | 41 unresolved |
| Two-ply answered test results | 0/2 correct |
| Three-ply answered test results | 1/1 correct |
| Historical concept test | 306/306 correct |
| External concept panel | 28 correct, 68 abstentions, no wrong classifications |
| Final tests | 588 passed |
| Legal preservation | 206 shards, 584,112 candidate rows |
| Historical protection | 11,553 files unchanged |

These are repository-reported measurements. Reproduce them; do not present reading a report as independent execution.

The accepted legal model identity reported by Cycle 13 is:

`a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`

Verify this against the actual manifest and checkpoint.

### Legal baseline to preserve

| Cohort | Exact legal-move sets |
|---|---:|
| External FEN-only | 793/1,020 |
| External supplied history | 1,020/1,020 |
| C9 adversarial | 112/128 |
| C9 special moves | 71/80 |
| C10 synthetic adversarial | 98/112 |

The accepted legality checkpoint must remain byte-identical throughout this cycle.

---

## 3. Non-Negotiable Boundaries

### Native inference

- Use only the existing pinned and verified native PLN operators.
- Keep truth-value revision and inference inside the native runtime.
- Do not implement replacement strength/confidence formulas in Python.
- Do not introduce or enable a conjunction operator.
- Do not upgrade the native runtime silently.
- Do not describe host-assembled observations as native conjunction proofs.

### Relative knowledge

- Learned hypotheses must not contain absolute-square constants.
- Raw FEN, SAN/UCI strings, source IDs, game IDs, and proof IDs must not become predictive features.
- Coordinates remain permitted for environmental state, structural transitions, I/O, and visualization.
- Preserve owner-relative orientation and explicit boundary/history relations.
- Do not impose a short geometric radius that excludes relevant sliding-piece dependencies.

### Operational separation

- Preference and concept experiments must not modify legal inference.
- No production reference-engine calls.
- No material-value table, piece-square table, handweighted utility, minimax, alpha-beta, or automatic move selection.
- Reference engines may generate offline supervision and evaluation evidence only.
- Maintain separate legality, field, concept, preference, and calibration identities.

### Scientific integrity

- Unknown supervision is not negative preference evidence.
- Missing observations are not false observations.
- Unknown mobility is not zero mobility.
- Repeated observations are not independent evidence.
- A preference conditioned on a supplied continuation is not a claim about optimal play.
- Finite zero-error results are not universal correctness guarantees.

Host-side parsing, indexing, descriptor construction, proof storage, evaluation statistics, and diagnostic calibration are allowed, but must be identified as such.

---

## 4. Execution Strategy

Complete the work as one assignment, not a sequence of approval requests.

Use this dependency order:

1. Preserve the baseline and register the study.
2. Audit reference-label semantics.
3. Implement compact proof storage and profiling early.
4. Register and acquire the expanded corpus.
5. Freeze partitions and labeling policies.
6. Fit bounded experimental model variants.
7. Freeze models and thresholds before final testing.
8. Run independent evaluations, regression gates, and clean reproduction.
9. Deliver the complete evidence-linked package.

Do not materialize a large new corpus of duplicated 50–174 MiB responses before addressing proof representation.

Register practical compute, storage, interpreter-call, and reference-search budgets. Use resumable jobs and deterministic scheduling. Record shortfalls rather than silently reducing the study.

If one research track fails, continue all independent work.

---

# Engineering Packages

## C14-01 — Baseline Lock and Reproduction

Verify the starting SHA and working-tree status.

Do not overwrite unrelated local changes. If the checkout differs, record ancestry and create an isolated local worktree where appropriate; do not destructively reset it.

Preserve:

- Legal, field, concept, and preference checkpoint identities.
- Native source and dependency hashes.
- Dataset and evidence-ledger identities.
- Descriptor versions.
- Labeling protocols.
- Thresholds and calibration mappings.
- Historical artifact manifests.

Reproduce the baseline preference, temporal, concept, and legal results.

Create:

`artifacts/cycle14/baseline/`

Historical outputs must remain immutable. New receipts belong under Cycle 14.

If a baseline discrepancy appears, diagnose it before using the result as a comparison. Continue independent preparation while the discrepancy is investigated.

**Deliverable:** Source-bound baseline manifest, discrepancy log, and reproduction receipt.

---

## C14-02 — Registered Study and Evaluation Contract

Write `docs/cycle14/research-registration.md` before fitting new models.

Register:

- Primary research questions.
- Source selection and candidate-pair construction.
- Dataset partitions and ancestry rules.
- Reference-label policy and escalation budgets.
- Descriptor variants and model-selection procedure.
- Temporal observation horizons and branch selection.
- Classification thresholds.
- Primary metrics and uncertainty methods.
- Performance workloads.
- Promotion and readiness criteria.

Separate four questions:

1. Did the reference process resolve a direction?
2. Did PLN answer?
3. Did the answer agree with the resolved reference?
4. Did the answer transfer to independent contexts?

Do not merge these into one accuracy figure.

Historical test sets are now regression/diagnostic sets. They must not be described as untouched final tests after their failures have informed development.

Freeze a new final test set. Any post-test refinement requires a new model version and a new final evaluation cohort.

**Deliverable:** Machine-readable registration, immutable partition manifest, and documented decision rules.

---

## C14-03 — Reference-Label Adapter Audit

Audit the offline engine adapter and raw Cycle 13 labeling output.

Record per analysis:

- Engine source, executable, and network hashes.
- Options, threads, hash memory, and reset policy.
- Search limits and termination status.
- Candidate root restrictions.
- Score type and perspective.
- Exact/unbounded versus lower-bound or upper-bound flags.
- Principal variation and candidate identity.
- Game history and root-state identity.
- Completed search iterations and raw transcript.

Test parsing and normalization for:

- White and Black actors.
- Odd and even continuation lengths.
- Mate scores and ordinary scores.
- Missing candidate results.
- Bound-only output.
- Interrupted searches.
- Different MultiPV ordering.
- Repeated analyses and engine resets.

Normalize every comparison to the original decision-maker's perspective.

When changing perspective, reverse bound orientation correctly. Do not merely negate a numeric value while leaving its bound type unchanged.

Never convert mate scores into arbitrary centipawn values for comparison convenience.

Distinguish:

- A score reported without a bound flag.
- A search bound.
- Stability across budgets.
- A proven game-theoretic result.

These are different evidential claims.

**Deliverable:** Adapter audit, raw fixtures, parser tests, and score-semantics specification.

---

## C14-04 — Resolve Reference Uncertainty Without Inventing Certainty

Investigate all 41 unresolved Cycle 13 test references and all unresolved temporal references.

Classify causes, including:

- Overlapping or one-sided bounds.
- Budget disagreement.
- Insufficient margin.
- Missing candidate analysis.
- Mate-order ambiguity.
- History or perspective mismatch.
- Genuine lack of demonstrated preference.
- Reference-source disagreement.

Preserve the original labels.

Create a new append-only label generation containing:

- Original observation ID.
- Original label and evidence.
- New analysis evidence.
- New label, if any.
- Supersession relationship.
- Protocol version.
- Resolution reason.

Repeated engine budgets for one pair are not independent training examples.

Use a preregistered escalation ladder: increase search effort or change the candidate-analysis method because the reference is unresolved, never because PLN answered incorrectly.

Investigate separately restricted root searches as an alternative to ambiguous MultiPV output. Record methodological differences.

For ordinary comparable scores, interval reasoning may be used in the offline labeling layer. For example, separation between a conservative lower estimate for A and upper estimate for B can support an operational reference direction under the registered protocol.

Do not describe such intervals as statistical confidence intervals or universal chess-value bounds.

Retain:

- `A`
- `B`
- `no-demonstrated-preference`
- `unknown`

The third means the protocol did not demonstrate a directional advantage. It does not prove equivalence.

Do not require every reference to resolve.

**Deliverable:** Complete resolution census, new label generation, and before/after supervision-quality analysis.

---

## C14-05 — Expanded Independent Preference Corpus

Register at least 750 source-grouped root comparisons, including at least 500 new pairs beyond the Cycle 13 corpus, subject to recorded resource limits.

Reserve at least 200 untouched final-test pairs. Aim for at least 100 resolved directional test references, but do not select the final test retrospectively to reach that number.

If ancestry merging reduces effective independence, report the reduced count.

Include:

- Tactical and quiet positions.
- Attack creation and attack disappearance.
- Defense preservation and defender removal.
- Mobility changes.
- Exposure and legal defensive responses.
- Pins, forks, discoveries, and threat removal.
- Promotion and history-sensitive cases.
- Ambiguous or near-equal alternatives.

Use at least three identifiable collection/provenance strata where available. Report publisher overlap and source-game overlap.

Separate:

- Training.
- Development/model selection.
- Diagnostic calibration.
- Final test.
- Source-held-out evaluation.
- Controlled demonstrations.

One source game should contribute at most one primary independent root pair. Additional branches, horizons, transformations, and counterfactuals inherit its ancestry.

Construct pairs before examining their reference scores. Balance displayed A/B order independently of labels.

Preserve uncertain and difficult examples. Report exclusions and reasons.

**Deliverable:** Corpus, licenses/provenance manifest, overlap audit, and effective-group counts.

---

## C14-06 — Relative Representation and Descriptor-Collision Analysis

Determine whether opposite reference directions collapse into the same relative descriptor.

For each hypothesis key, inspect:

- Number of independent evidence groups.
- Directional agreement and conflict.
- Unknown-field content.
- Role identity and allegiance.
- Temporal context.
- Relevant relationships lost by abstraction.

Investigate bounded descriptor refinements using training and development data only.

Candidate information includes:

- Which piece gained or lost influence.
- Which target changed protection.
- Whether two relations share the same attacker or defender.
- Whether an effect concerns the moving piece or another piece.
- Relative dependency paths.
- Influence persistence versus immediate cancellation.
- Unknown, unqueried, and incomplete relations.

Do not replace coarse descriptors with complete-position fingerprints.

Preserve relational identities while canonicalizing away incidental piece IDs and board locations.

Test:

- Translation where semantics are preserved.
- Owner-relative transformations.
- Piece-ID renaming.
- Irrelevant-piece changes.
- Relevant blocker or defender changes.

Report supplied abstractions separately from learned rule knowledge.

**Deliverable:** Collision census, bounded representation variants, and locality controls.

---

## C14-07 — Native Preference Learning and Model Isolation

Continue native revision and conditional inference.

Define the target explicitly:

`Preference(A, B | relative observations, supplied context, horizon)`

This is a conceptual predicate, not authorization for a new operator.

Keep native preference channels separate. Do not assume A, B, and no-demonstrated-preference form a normalized probability distribution merely because each has a truth value.

Unknown labels must not update directional channels as false evidence.

Audit how uncertain field beliefs enter the host-assembled observation packet. A derived uncertain field must not silently become a certain premise.

If the runtime cannot propagate joint uncertainty, retain the existing partial-conditional interpretation and expose the limitation.

Create separately versioned experimental models:

- Frozen C13 preference model.
- Revised-supervision model using the old representation.
- Refined-representation model using matched supervision.
- Continuation-conditioned model.

Select the primary candidate using development data, not final-test performance.

Do not change the accepted legal checkpoint or production defaults.

**Deliverable:** Model identities, native training traces, hypothesis inventory, and explicit proof-status contract.

---

## C14-08 — Evidence Dependence, Conflicts, and Label Revision

Extend the evidence ledger to support label generations without double counting.

Required behaviors:

- Idempotent ingestion.
- Atomic validation and durable append.
- Deterministic replay.
- Explicit active-label generation.
- Preserved superseded observations.
- Conflict reporting.
- Rollback to previous model generations.

Keep connected ancestry for:

- The same source game.
- The same root comparison.
- Reversed pair order.
- Multiple horizons.
- Counterfactual descendants.
- Translated or reflected copies.
- Repeated engine budgets.
- Multiple teachers evaluating the same position.

Different files or engines do not automatically create independent evidence.

Retain the conservative policy for internally contradictory dependent components unless an alternative is justified and evaluated separately.

Reproduce the Cycle 13 confidence-inflation control. Extend it to repeated label analyses and repeated continuation observations.

No unsafe dependence ablation may become the default.

**Deliverable:** Replay tests, conflict cases, dependence ablations, and counterfactual removal receipts.

---

## C14-09 — Controlled Temporal Preference Study

Separate two meanings of horizon:

1. How many supplied moves are included in the model's observations.
2. How the reference outcome is evaluated.

Do not confuse a two-ply supplied observation with an exhaustive two-ply strategic value.

Register at least 50 independent held-out root groups for two-ply comparisons and 50 for three-ply comparisons.

The same groups may appear at both horizons, but must not be counted as 100 independent groups.

Keep the original actor's perspective fixed.

Improve the Cycle 13 design by separating:

- Effects of adding continuation observations to a fixed checkpoint.
- Effects of adding temporal training evidence.
- Effects of changing the descriptor.
- Effects of changing reference labels.

Where schemas permit, compare the same checkpoint with continuation information present versus explicitly unknown.

Train an omission-robust study arm using training-only missing-context examples so that feature-removal controls are not merely invalid inputs.

Compare immediate and continuation-conditioned predictions against the same endpoint reference within each registered comparison.

A separate analysis may study root-reference versus endpoint-reference changes. Label that as a different target comparison.

**Deliverable:** Preregistered temporal factorial study, paired results, and all failures.

---

## C14-10 — Preference Reversal and Persistence Experiments

The principal experiment is transferable preference change under new relational evidence.

Construct development examples such as:

- An attack is created but can be neutralized.
- A defender moves and a previously protected target becomes exposed.
- A fork persists through one response but disappears through another.
- A mobility gain is followed by a loss of defensive coverage.

Do not hardcode the preferred direction.

For reversal claims, require:

- A resolved initial reference direction.
- A resolved continuation-conditioned direction.
- Consistent actor perspective.
- A disclosed change in information or target.
- Native preference outputs before and after.
- Evidence and premise-removal controls.

Distinguish preference revision from proof that the original move was objectively best.

Include non-reversal controls. A system that always flips after receiving a reply must fail.

Aim for at least ten preregistered held-out reversal opportunities and ten persistence controls. Report every registered case, not only successful illustrations.

Test transfer to unseen relative configurations and unrelated source games.

**Deliverable:** Reversal/persistence panel, transfer proofs, and failed-case analysis.

---

## C14-11 — Response Coverage and Branch Semantics

Continue bounded supplied-branch reasoning; do not introduce unrestricted search.

Register branch selection before observing PLN success.

Separate:

- Published game continuations.
- Controlled constructed continuations.
- Offline engine-supplied continuations.
- Reproducibly sampled continuations.

Engine-supplied branches are teacher-assisted evidence and must be labeled accordingly.

Use a small configurable response budget, initially at most three supplied responses per candidate.

Record:

- Responses examined.
- Selection policy.
- Known response count when available from evaluation.
- Unexamined-response gap.
- Unknown branch legality.
- Endpoint incompleteness.

Do not average branch strengths, take their product, or select their minimum and call the result a native robust preference.

When branches disagree, expose branch-conditioned results. Do not invent a global preference.

Do not use an illegal king-exposing move as an ordinary valid strategic alternative. Keep illegal and unknown branches in diagnostic panels with their status explicit.

Test identical board layouts with different histories to prevent unsafe state or cache merging.

**Deliverable:** Branch-coverage contract, contradictory-branch tests, and bounded-response report.

---

## C14-12 — External Concept Generalization

Preserve the historical 306/306 concept result and rerun the 96-case external panel.

Investigate all 68 external abstentions by cause:

- Missing learned conditional.
- Missing query scope.
- Descriptor mismatch.
- Unsupported conjunction.
- Incomplete field evidence.
- Overly specific piece or role abstraction.
- Insufficient independent evidence.

The historical panel is diagnostic/regression data, not a new untouched test.

Create a separate source-grouped concept holdout before refinement.

Prioritize concept evidence that could improve preference discrimination, rather than maximizing isolated concept counts.

Preserve the distinction between:

- Structural fork candidate and strategically useful fork.
- Geometric protection and legal recapture.
- Competing defensive obligations and demonstrated overload.
- Ordinary-exit restriction and strategic trapping.

Measure preferences with and without concept evidence on matched data.

**Deliverable:** External concept census, independent transfer panel, and contribution analysis.

---

## C14-13 — Evaluation and Diagnostic Calibration

Report explicit counts before percentages.

For each cohort define:

- `N_all`: registered comparisons.
- `N_directional`: resolved A/B references.
- `N_nondirectional`: no-demonstrated-preference references.
- `N_reference_unknown`: unresolved references.
- `N_answered`: directional model answers on resolved directions.
- `N_correct` and `N_wrong`.
- Model abstentions, contradictions, and incomplete requests.

Primary directional metrics:

- Answered accuracy = `N_correct / N_answered`.
- Directional coverage = `N_answered / N_directional`.
- Correct-answer yield = `N_correct / N_directional`.

Report reference-resolution rate and model answer rate across all registered pairs separately.

Do not score predictions on unknown references as correct or incorrect.

Evaluate no-demonstrated-preference as a separate target. Do not call it strategic equivalence.

For calibration:

- Freeze mappings on calibration data only.
- Define exactly which event each probability estimates.
- Keep native channel TVs separate.
- Do not assume independent channel strengths sum to one.
- Report raw and calibrated diagnostics separately.
- Include Brier score, log loss with disclosed numerical handling, reliability, selective risk, and uncertainty.
- Cluster resampling by source-game/ancestry component.
- Report source-held-out and temporal results separately.

Tiny denominators must remain visibly tiny.

**Deliverable:** Metric schema, count tables, clustered intervals, and calibration diagnostics.

---

## C14-14 — Factorial Ablations and Causal Restraint

Run a bounded, preregistered ablation matrix.

At minimum separate:

1. Old versus revised supervision with the same descriptor.
2. Old versus refined descriptors with the same supervision.
3. New independent evidence versus repeated dependent copies.
4. Immediate versus supplied-continuation observations.
5. Temporal training absent versus present.
6. Concept evidence absent versus present.
7. Correct dependence versus explicitly unsafe counting.
8. Primary model versus simple evaluation-only reference baselines.

Where possible, hold all other factors fixed.

Use identical final cohorts and frozen thresholds.

A majority-class or frequency baseline may exist in evaluation only. It must not become a hidden production decision mechanism.

Register a bounded representation search rather than brute-force hypothesis enumeration.

Report coverage as well as answered accuracy. A variant that answers nothing is not an equally accurate strategic model.

Do not attribute gains to temporal information when labels, training evidence, and descriptors all changed simultaneously.

**Deliverable:** Matched ablation matrix, effect estimates, and negative findings.

---

## C14-15 — Compact Content-Addressed Proof Representation

Replace repeated proof nesting in new experimental responses with a versioned, content-addressed proof graph.

Store reusable objects such as:

- Ground propositions and native truth values.
- Native rule applications.
- Premise references.
- Evidence references.
- Runtime/model identities.
- State and branch provenance.
- Dependency edges.
- Observation-construction records.

Separate:

- Proof identity.
- Cached numerical computation identity.
- Request identity.
- Human-readable presentation.

Identical native arithmetic may be memoized without merging distinct evidence occurrences.

Do not merge two derivations merely because they produce the same truth value.

Provide three views:

1. `summary`: decision, uncertainty, identities, and proof handles.
2. `proof_graph`: requested graph nodes and dependencies.
3. `full_archive`: complete reconstructable audit package.

Require:

`expand(compact_proof) == canonical_legacy_proof`

under a documented comparison excluding only genuinely nonsemantic execution metadata.

Preserve evidence multiplicity, ordering where meaningful, premise identity, and native expressions.

Missing or corrupted referenced objects must produce an explicit error.

Compression alone is insufficient: avoid constructing the entire duplicated object merely to discard it before returning a summary.

**Deliverable:** Proof-store schema, migration adapter, reconstruction tests, and size measurements.

---

## C14-16 — Inference Architecture, Caching, and Performance

Profile before optimizing.

Measure separately:

- Model loading.
- Observation construction.
- Query-domain construction.
- Native execution.
- Interpreter startup.
- Proof construction.
- Serialization.
- Compression.
- Archive retrieval.
- Browser transfer and rendering where measured.

Cycle 13 warm requests did not eliminate native work in every workload. Investigate cache capacity, invalidation, repeated graph construction, and interpreter launches rather than assuming all remaining time is serialization.

Implement dependency-safe reuse keyed by relevant:

- Model and runtime versions.
- Descriptor schema.
- State and history.
- Actor and horizon.
- Query scope.
- Supplied continuation.
- Observation completeness.
- Evidence generation.

Return a graph/data-access census:

- Persistent learned hypotheses.
- Stored facts.
- Native-resident atoms, if any.
- Host-indexed records.
- Per-request materialized atoms.
- Derived proof nodes.
- Cache entries and invalidations.

Do not describe a host proof index as a persistent native PLN reasoning graph.

Keep interpreter reuse optional until cross-request state isolation and exact parity are verified.

**Research goals:** At least 2× lower warm summary-response latency and at least 90% smaller interactive payloads, with complete proof reconstruction.

Measure equivalent workloads. Separately label faster summaries and faster complete-audit execution.

**Deliverable:** Profile, optimized implementation, data-access map, and matched benchmarks.

---

## C14-17 — API, CLI, and Inspector

Extend the experimental comparison interface without changing legal defaults.

Conceptual interface:

    compare_moves(
        position,
        move_a,
        move_b,
        history=...,
        continuations=...,
        model=...,
        proof_mode="summary",
    )

Return:

- Legality beliefs for both candidates.
- Preference channels and classification.
- Actor and observation horizon.
- Continuation scope and coverage.
- Unknown/conflicting premises.
- Proof status.
- Model/runtime/evidence identities.
- Proof handles.
- Budget and incompleteness status.

Provide paginated proof retrieval and full archive export.

A reference label belongs in a research/evaluation view, not in the production inference input.

The inspector must distinguish:

- Unresolved reference.
- Model abstention.
- Contradictory supported channels.
- Incomplete execution.
- Partial conditional proof.

Add before/after continuation comparison and evidence-removal inspection.

Keep proofs available after process restart when durable storage is configured.

Verify desktop/mobile behavior and actual archive reconstruction, not merely screenshot appearance.

**Deliverable:** Compatible interfaces, examples, schema documentation, and browser evidence.

---

## C14-18 — Preservation, Isolation, and Regression Gates

Mandatory gates:

1. Accepted legal checkpoint remains byte-identical.
2. Established legal cohorts retain exact classifications and native proof parity.
3. No new legal false positives, false negatives, or self-check errors.
4. All 287 negative controls pass.
5. All 27 history controls, both known recoveries, and 76 controlled holdouts pass.
6. Historical concept behavior remains reproducible.
7. No production oracle access.
8. No new native operator or truth-value formula.
9. No hidden score, label, source-ID, or PV leakage into descriptors.
10. Evidence replay and rollback remain deterministic.
11. Compact proofs reconstruct their complete audit representation.
12. Cache invalidation handles state, history, branch, and model changes.
13. Protected historical files remain unchanged.
14. Experimental preferences remain opt-in.
15. No autonomous move-selection interface is introduced.

Use both static boundary checks and runtime tests with reference-engine access disabled.

Preference errors are research findings, not permission to change legality semantics or suppress difficult examples.

Passing these engineering gates does not establish strategic accuracy.

**Deliverable:** Complete gate matrix with machine-readable receipts.

---

## C14-19 — Clean Reproduction and Resource-Accounted Verification

Perform clean-checkout reproduction using pinned dependencies.

Rebuild or replay:

- Reference-label fixtures and selected raw analyses.
- Dataset partitions and ancestry.
- Native feature extraction.
- Evidence ledgers.
- Preference checkpoints.
- Native training/inference traces.
- Evaluations and ablations.
- Compact/full proof equivalence.
- Legal preservation suites.
- Browser and API workflows.

Separate stochastic or execution metadata from scientific identities explicitly. Do not exclude failed classifications or changed evidence from comparisons.

Run benchmarks without concurrent study jobs under your control.

Use at least 20 repetitions for headline latency workloads where practical. Report distributions and uncertainty; do not treat a small-sample p99 as a stable service guarantee.

Measure per-process memory and avoid adding unrelated lifetime maxima into a fictitious simultaneous working set.

Record compute time, reference-search work, interpreter launches, generated bytes, and retained artifact sizes.

Use resumable stages and avoid overwriting delivered evidence during reproduction.

**Deliverable:** Clean reproduction receipt, final test results, benchmark suite, and resource ledger.

---

## C14-20 — Consolidated Delivery and Readiness Decision

Write:

    docs/cycle14/engineering-report.md
    docs/cycle14/package-matrix.md
    docs/cycle14/research-registration.md
    docs/cycle14/reference-label-audit.md
    docs/cycle14/dataset-provenance.md
    docs/cycle14/relative-representation.md
    docs/cycle14/preference-learning.md
    docs/cycle14/evidence-dependence.md
    docs/cycle14/temporal-study.md
    docs/cycle14/preference-reversals.md
    docs/cycle14/response-coverage.md
    docs/cycle14/concept-generalization.md
    docs/cycle14/evaluation-calibration.md
    docs/cycle14/ablations.md
    docs/cycle14/proof-storage.md
    docs/cycle14/performance.md
    docs/cycle14/reproduction.md
    docs/cycle14/readiness-decision.md

Include machine-readable:

- Source/model/runtime manifests.
- Label generations and raw-reference hashes.
- Partition and overlap audits.
- Evidence ledgers.
- Model checkpoints.
- Proof graphs and archive manifests.
- All registered evaluation outcomes.
- Counterfactual/removal controls.
- Performance and resource measurements.
- Test and reproduction receipts.

Every package must have two separate status fields:

- Engineering delivery status.
- Research outcome.

“Implemented and evaluated” must not be reported as “hypothesis demonstrated” when results are negative.

The readiness memo must choose between:

- Continue preference research.
- Propose a separately authorized bounded selection experiment.
- Investigate a materially new native-PLN capability question.

No option authorizes implementation of move selection during this cycle.

---

## 5. Research Targets and Decision Criteria

These targets guide the investigation. They are not permission to weaken mandatory gates.

| Area | Target |
|---|---|
| Corpus | At least 750 registered root groups, including 500 new pairs |
| Final immediate test | At least 200 untouched pairs |
| Resolved directional test support | Aim for at least 100 independent references |
| Temporal test | At least 50 independent root groups at each horizon |
| Reversal evaluation | At least 10 registered opportunities plus persistence controls |
| Preference transfer | Independent structural and source-held-out measurements |
| Immediate preference quality | Aim for at least 80% answered accuracy at at least 50% directional coverage |
| Temporal utility | Improve on the immediate baseline against matched endpoint references |
| Interactive payload | At least 90% reduction |
| Warm summary latency | At least 2× improvement on matched workloads |
| Proof integrity | Exact reconstruction and native/evidence parity |
| Legal preservation | All mandatory gates pass |

Report all numerators, denominators, effective groups, and uncertainty intervals.

Do not claim the immediate preference-quality target on six or ten answers.

Do not expand or filter the final test after seeing model results. If label resolution is insufficient, report the shortfall and reserve new data for a subsequent registered evaluation.

A successful reversal demonstration is not an unbiased reversal success rate unless all registered opportunities are included.

A performance improvement from returning less data is a useful interface improvement, but not automatically a native inference speedup.

---

## 6. Authorization and Change-Control Contract

Authorized:

- Local source changes.
- Read-only acquisition of public, suitably licensed research data.
- Existing native PLN experiments.
- Offline reference-engine supervision.
- Experimental model training.
- Tests, benchmarks, documentation, and local commits.
- New experimental proof-storage and inspection interfaces.

Not authorized:

- GitHub push or remote write.
- External deployment.
- Paid services or new private credentials.
- Upstream PLN modification.
- New inference operators.
- Production reference-engine access.
- Conventional strategic evaluation functions.
- Autonomous move selection.
- Changes to the accepted legal checkpoint.
- Deletion or mutation of historical evidence.
- Relaxation of mandatory acceptance criteria.

Previous cycles having been pushed does not authorize a push now.

Do not execute `git push`, create remote pull requests, or publish artifacts remotely.

Complete local work and report remaining authorization needs without performing those actions.

---

## 7. Final Codex Response

Return a concise evidence-linked completion report containing:

1. Starting and ending commit hashes.
2. Working-tree status and local commit list.
3. Explicit confirmation that no push or deployment occurred.
4. Twenty-package delivery matrix.
5. Legal preservation and historical-file verification.
6. Reference-label resolution counts by cause.
7. Dataset sizes, partitions, and effective independent groups.
8. Immediate preference counts, accuracy, coverage, and uncertainty.
9. Two-ply and three-ply results on matched targets.
10. Reversal and persistence outcomes, including failures.
11. Source-held-out and concept results.
12. Dependence, calibration, and ablation findings.
13. Compact/full proof integrity.
14. Latency, memory, payload, and archive comparisons.
15. Tests and clean reproduction.
16. Explicit unresolved limitations.
17. Readiness recommendation.

Distinguish:

- Source-inspected claims.
- Reproduced baseline results.
- New measurements.
- Native conditional derivations.
- Host-side observations and comparisons.
- Diagnostic calibration.
- Unsupported joint conclusions.

Do not claim strategic playing strength from preference agreement alone.

---

## 8. Source References

These documents inform the brief. Verify the implementation against the pinned checkout.

[R1] Cycle 13 engineering report:
https://github.com/machieke/pln-chess/blob/54353579e7921f9b47f43bbde1aa61cb887bc6e4/docs/cycle13/engineering-report.md

[R2] Cycle 13 research registration:
https://github.com/machieke/pln-chess/blob/54353579e7921f9b47f43bbde1aa61cb887bc6e4/docs/cycle13/research-registration.md

[R3] Cycle 13 evidence contract:
https://github.com/machieke/pln-chess/blob/54353579e7921f9b47f43bbde1aa61cb887bc6e4/docs/cycle13/preference-evidence.md

[R4] Cycle 13 temporal study:
https://github.com/machieke/pln-chess/blob/54353579e7921f9b47f43bbde1aa61cb887bc6e4/docs/cycle13/temporal-preferences.md

[R5] Cycle 13 performance report:
https://github.com/machieke/pln-chess/blob/54353579e7921f9b47f43bbde1aa61cb887bc6e4/docs/cycle13/performance.md

[R6] Official Stockfish UCI documentation:
https://official-stockfish.github.io/docs/stockfish-wiki/UCI-%26-Commands.html

[R7] python-chess engine communication documentation:
https://python-chess.readthedocs.io/en/stable/engine.html

Use the repository's pinned engine and library versions. Current online documentation is a reference, not permission to change dependencies.

---

## Final Objective

Cycle 14 should make the preference research more trustworthy and the implementation more usable.

The system should learn from better-characterized evidence, distinguish relevant relational contexts, and represent how supplied responses change a preference without assuming that every future has been examined.

Its outputs should become smaller and faster to inspect without losing the native proofs and evidence needed to audit them.

The decisive result is not a larger number of generated comparisons.

It is a reproducible demonstration that a learned relational preference—or a justified change in that preference—transfers to independent situations at meaningful coverage.

Preserve the central principle:

**The chessboard is the environment. Transferable local relationships are the knowledge. Native PLN performs the supported inference. Uncertainty remains explicit wherever the evidence or calculus is insufficient.**