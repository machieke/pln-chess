# PLN Chess — Cycle 19 Codex Implementation Brief

## Measured Chess Consequences, Native Learning, and Evidence Correction

**Repository:** https://github.com/machieke/pln-chess  
**Required baseline:** `4691c9cc7bf3aebe89c87fb5956852622be3eeb5`  
**Baseline branch:** `cycle18-shared-parameter-contract`  
**Target branch:** `cycle19-measured-chess-consequences`

---

## 1. Execution mandate

Implement and deliver the complete Cycle 19 package described below.

This is an implementation, research, verification, and publication assignment. Continue through the experiments, analysis, documentation, commits, push, and independent publication verification. Do not stop after producing a plan or a partial implementation.

The user explicitly authorizes:

- Local implementation and meaningful tests.
- Reading the existing repository and its preserved evidence.
- Acquiring additional public, appropriately licensed source material where needed within the registered scope.
- Creating an isolated worktree or dedicated feature branch.
- Creating local commits.
- Pushing the completed feature branch to `machieke/pln-chess`.
- Verifying the remote commit and reproducing compact examples from the published checkout.

No additional confirmation is needed for those actions.

The assignment does not authorize changes to the native inference calculus, weakening evidence-disjointness checks, changing the accepted operational chess model, updating the default branch, force-pushing, publishing releases, or uploading bulk evidence packs.

Resolve routine engineering choices autonomously. If a research hypothesis fails, preserve the negative result and complete the remaining work. A missing empirical probability interpretation must not prevent completion of the native learning and consequence evaluation.

Read applicable repository instructions before implementation. Preserve unrelated local work. Use an isolated worktree if the current checkout is dirty or belongs to another task.

If the target branch already exists, inspect its ancestry and contents. Continue from a compatible tip or use a clearly named new branch and document the reason. Never overwrite a diverged branch.

---

## 2. Purpose

The project’s purpose is a probabilistic logic network whose declarative rules and truth-valued relational beliefs perform the core reasoning about chess.

Python may import positions, construct permitted observations, manage evidence, schedule native queries, and display results. It must not quietly compute the chess consequence that the native reasoning system is supposed to derive.

The representation must remain local and relative:

- Rules bind pieces, cells, targets, and states through relational roles.
- Learned conditions describe relative geometry and occupancy.
- Knowledge should transfer across board locations and unfamiliar entity identifiers.
- Absolute coordinates are permitted in source records, board reconstruction, audit data, and visualization.
- Absolute square names must not become learned rule conditions or exact-position lookup keys.

Cycle 19 should answer:

> Given the permitted relative observations of one current position, what does the existing native PLN system derive about clearance and rook influence, and how does that result depend on the actual evidence used to learn its rules?

The primary deliverable is a measured native consequence study with defensible observation provenance.

A calibrated probability interpretation may remain unresolved. Native strength and confidence must retain their existing meaning and remain separately labeled.

---

## 3. Starting evidence and required reading

Inspect the following at the required baseline:

- `docs/cycle18/engineering-report.md`
- `docs/cycle18/package-matrix.md`
- `docs/cycle18/architecture-decision.md`
- `docs/cycle18/parameter-semantics.md`
- `docs/cycle18/source-evidence-contract.md`
- `docs/cycle18/source-bound-reference.md`
- `docs/cycle18/native-compatibility.md`
- `docs/cycle18/reproduction.md`
- `docs/cycle18/publication.md`
- `research/cycle18/contracts.py`
- `research/cycle18/source_mapping.py`
- `research/cycle18/applications.py`
- `research/cycle18/reference_joint.py`
- `research/cycle18/reference_bounds.py`
- `training/cycle17_shared_evidence.py`
- The Cycle 15–17 native adapters, knowledge declarations, and decisive witnesses used by Cycle 18.
- `configs/runtime-lock.json`

Authoritative published entry points:

- [Cycle 18 report](https://github.com/machieke/pln-chess/blob/4691c9cc7bf3aebe89c87fb5956852622be3eeb5/docs/cycle18/engineering-report.md)
- [Cycle 18 architecture decision](https://github.com/machieke/pln-chess/blob/4691c9cc7bf3aebe89c87fb5956852622be3eeb5/docs/cycle18/architecture-decision.md)
- [Cycle 18 parameter semantics](https://github.com/machieke/pln-chess/blob/4691c9cc7bf3aebe89c87fb5956852622be3eeb5/docs/cycle18/parameter-semantics.md)

Carry forward these findings accurately:

1. The 48 admitted Cycle 17 annotations copy 24 underlying evaluation vectors.
2. The original 144 revision receipts represent reuse across arms, not 144 independent observations.
3. Shared and overlapping native chains remain blocked.
4. Disjoint native chains compose under the demonstrated conditions.
5. Generic recursive reuse remains unresolved.
6. Cycle 18’s reference query concerns two distinct future label-channel trials.
7. Its application journal preserves evidence identity but does not evaluate a new context-dependent chess consequence.
8. No conversion from reference probability, posterior variance, or sample count to native confidence has been established.

Verify baseline identities rather than relying only on this brief.

Expected runtime pins:

- PLN: `4405956947c4b53c7ff01bd565aa3b114bc970a1`
- PeTTa: `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`
- Python: `3.12.12`
- SWI-Prolog: `10.0.1`

Expected accepted legal checkpoint identities:

- File SHA-256: `5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8`
- Semantic identity: `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`

The baseline operational source identity is:

`e88ff7969885be101af2ceedbbdf5d5499f4253b361a8cee18ff1814f055282c`

Any mismatch must be investigated and reported before it is treated as an accepted baseline.

---

## 4. Nonnegotiable boundaries

### 4.1 Native inference

Use only the verified operators and execution paths in the pinned runtime.

Preserve:

- `StampDisjoint`.
- Existing native truth-value formulas.
- Genuine rule and training-source stamps.
- The distinction between observations and applications.
- The accepted operational checkpoint and behavior.

Do not:

- Mint new evidence stamps for repeated uses of the same rule.
- Remove shared training ancestry to make composition succeed.
- Treat distinct identifiers as proof of statistical independence.
- Inject audited `Clear` or `Attack` conclusions into inference inputs.
- Replace native derivation with Python evaluation or host-side truth arithmetic.
- Select a successful grounded rule in Python and present that selection as native binding.
- Convert a reference probability into a native truth value.
- Introduce a general correlated-inference engine.
- Promote an experimental checkpoint into the operational default.

Supplied domain templates remain supplied. Parameter learning through native revision must not be described as rule-structure discovery.

### 4.2 Evaluation and reference calculations

Chess evaluators and direct domain checks may be used for offline measurement, training-label preparation, and evaluation.

Their results must not enter native inference through facts, cached conclusions, feature names, or hidden selection logic.

Keep separately typed outputs for:

- Native strength/confidence.
- Empirical measurement results.
- Observed prediction errors.
- Reference probabilities under declared models.
- Bounds or unidentified quantities.
- Execution completeness.

### 4.3 Historical preservation

Place new scientific work in Cycle 19 namespaces.

Preserve the frozen Cycle 18 implementation, historical artifacts, accepted model, runtime, and protected evidence. Use wrappers or new modules for the new lifecycle policy.

Inventory the actual protected files at the Cycle 19 baseline. Do not reuse Cycle 18’s protected-file count as though it were the new inventory.

---

## 5. Primary task and uncertainty contract

### 5.1 Domain targets

Retain the existing finite setting:

- A rook attacker.
- A distinct target at the supported relative distance.
- Exactly two intervening cells.
- A shared state identity.
- The existing relative ray representation.

Define these targets separately:

| Target | Meaning |
| --- | --- |
| `Clear` | Both intervening cells are unoccupied in the specified state |
| `Attack` | The registered sliding-influence relation from the rook to the target |
| `NoAttack` | The explicit contrary relation supported by the existing native encoding |
| Unknown | No adequate supported answer under the recorded inference conditions |
| Conflict | Supported incompatible channels under the frozen conflict policy |
| Incomplete | An execution or resource obligation was not completed |

Influence is not move legality, legal recapture, or universal king safety. Preserve the registered treatment of friendly occupied destinations.

A negative `Attack` result must not automatically become negative `Clear`, and absence of an attack proof must not become king safety.

### 5.2 Three separate layers

The study must distinguish:

1. **Domain truth:** the relation in the fully specified reference state.
2. **Available observations:** the information actually supplied to native inference.
3. **Native support:** the strength/confidence derived from the supplied templates, admitted training evidence, and native inference.

The primary interpretation of layer three is native conditional support.

Do not claim that native confidence equals:

- Calibrated correctness probability.
- A Beta posterior.
- An effective number of independent games.
- Posterior precision.
- A probability that a schema is universally valid.

A correct conditional may have only positive antecedent-qualified training outcomes. That is an acceptable result. It does not identify a stochastic failure process.

---

## 6. Registration, cohort size, and resource discipline

Perform an outcome-blind feasibility census before finalizing the study registration.

Default natural-data target:

- 48 training roots, divided into two source groups.
- 24 development roots.
- 72 final test roots.
- One primary natural root per source game.

These are research targets, not grounds for silently selecting favorable outcomes.

Use existing licensed collections first. Bound the initial acquisition/search effort to approximately 240 candidate games and 200 eligible natural roots. Record acquisition hashes, licenses, source identities, and selection counts.

If the target is infeasible:

- Preserve the selection rule.
- Register the actual achievable cohort before final inference.
- Record the shortfall and its implications.
- Continue the study without recycling test games into training or selecting successful predictions.

Separate the conditional training curriculum from the natural evaluation sampling frame:

- Training admissions may require the conditional’s raw antecedent.
- Record this qualification explicitly.
- Do not interpret an antecedent-qualified all-positive curriculum as an unbiased sample of arbitrary positions.
- Select natural evaluation roots using registered structural eligibility, without filtering on oracle conclusions, successful native predictions, or desired error rates.

Register before final evaluation:

- Target definitions.
- Sampling and admission rules.
- Source and structural exclusions.
- Training groups and model arms.
- Thresholds and observation trust.
- Native execution budgets.
- Diagnostic subset selection.
- Transformation and correction controls.
- Resource ceilings.
- Statistical reporting methods.

Commit the registration before new outcome-dependent analysis.

Estimate the complete native workload before launching it. Include fitting, all targets, arms, controls, refits, tests, and compact reproduction.

Use a default ceiling of 4,000 Cycle 19 research native invocations. Count historical preservation separately. If a larger budget becomes necessary, publish a reasoned amendment before consuming it; do not expand a search merely to obtain a desired result.

Do not repeat the full historical preservation campaign during routine iteration. Run focused checks, freeze executable source and data, then run the required complete final gate.

---

## 7. Work packages

## C19-01 — Baseline isolation and study registration

### Implement

1. Verify the required starting commit and branch ancestry.
2. Create the dedicated worktree/branch without disturbing unrelated work.
3. Record runtime, accepted checkpoint, operational source, historical manifests, and protected files.
4. Reproduce the compact decisive native anchors:
   - Shared chain.
   - Reciprocal disjoint chains.
   - One-source overlap.
   - Historical eleven-stamp witness.
   - Recursive reuse counterexample.
   - Supplied finite and removed-rule controls.
5. Run the outcome-blind corpus feasibility census.
6. Commit the study registration.

### Acceptance

- Baseline identities are verified.
- Unexpected mismatches are resolved or explicitly block the affected comparison.
- Historical and experimental results have separate namespaces.
- Registration precedes outcome-dependent selection and final inference.

Do not rerun every prior research matrix merely to restate the known shared-evidence limitation.

---

## C19-02 — Current-position targets and independent measurement

### Implement

Create a measurement record for every registered episode containing:

- Source collection, game, root, and ancestry identifiers.
- The fully specified reference state.
- The observations permitted at inference time.
- Attacker, target, intervening-cell, and state bindings.
- A clearance measurement.
- An influence measurement.
- Measurement method and implementation identities.
- Input hashes and parent-event references.
- Conditional eligibility and exclusion reasons.
- Measurement disagreement or unresolved status.

Measure clearance through an explicit occupancy/path audit.

Measure influence through a separately implemented influence check using the registered definition.

Do not create the clearance label by copying the influence label.

Include hand-inspectable fixtures capable of exposing mistakes shared by automated checks, including:

- Both intervening cells empty.
- A blocker at either intervening cell.
- Both cells occupied.
- Friendly and opposing target occupancy.
- Reversed relative directions.
- A state or role mismatch.

“Separately checked” does not mean statistically independent. Preserve common state ancestry and shared implementation dependencies.

### Required distinctions

Record separately:

- Antecedent true, false, or unknown.
- Conclusion true, false, or unresolved.
- Measurement agreement or disagreement.
- Training admission or exclusion.

A blocked path is not a failed observation of an implication whose antecedent requires an empty path.

### Acceptance

- Every admitted annotation has a concrete measurement lineage.
- Clearance and influence have distinct measurement procedures.
- Evaluation disagreements remain visible.
- No historical label is silently overwritten.
- Measurement code cannot be called by the native inference path.

---

## C19-03 — Corpus, holdouts, and relative transfer

### Implement

Freeze source groups and splits before fitting.

Exclude previously used Cycle 15–18 source games from the new cohort where available. Audit any unavoidable overlap and distinguish:

- New to this cycle.
- New to the native learner.
- New to the project.
- Shared through upstream representations or supplied templates.

Do not describe a source as globally unseen merely because it was excluded from the current preference or consequence fit.

For each split, report novelty along these axes:

- Source-game ancestry.
- Absolute endpoint location pair.
- Relative direction.
- Canonical local geometry.
- Occupancy pattern.
- Surrounding relational context.
- Source collection.

Where feasible, preregister a relative-direction or source-collection holdout. If unavailable, report that limitation.

The fixed two-intervening-cell task cannot establish unseen path-length generalization. Translated copies and renamed entities do not establish new structural knowledge.

### Separate populations

Maintain separate identifiers and metrics for:

1. Natural training roots.
2. Natural development roots.
3. Natural final test roots.
4. Historical diagnostic anchors.
5. Dependent occupancy interventions.
6. Deliberately withheld observations.
7. Optional synthetic corruption controls.

Use a preregistered subset of approximately 12–16 roots for the full nine-case E/O/U occupancy matrix.

Distinguish withholding an observation from changing the underlying state. A hidden true occupancy may remain available to the evaluator while being unavailable to inference.

### Acceptance

- Every root and variant has inspectable lineage.
- Transformations do not inflate the independent-game count.
- Final test selection is unaffected by model success.
- Absolute locations do not enter learned rule conditions.
- Claimed transfer matches the recorded novelty audit.

---

## C19-04 — Native learning from audited evidence

### Implement

Fit new experimental generations using the existing supplied templates and verified native revision.

Use the newly measured outcomes for the intended target of each conditional.

Preserve:

- Actual event and component identities.
- Common source ancestry.
- Genuine copied or derived relationships.
- Frozen rule structures.
- Registered observation trust.
- Native revision expressions and raw receipts.

If observation confidence remains a supplied constant, state that explicitly. Do not call it measured reliability.

Include these comparison arms:

| Arm | Purpose |
| --- | --- |
| H | Frozen historical model |
| F | Supplied finite-rule control |
| D-AB | New clearance fit from group A, terminal fit from group B |
| D-BA | Reciprocal disjoint assignment |
| S-AA | Both fits from group A |
| S-BB | Both fits from group B |
| P | Prior/untrained control |

Register the exact evidence selection before fitting.

Do not force equal learned truth values by overriding native results. If qualified counts or measured outcomes differ between groups, report those differences.

Use source matching or deterministic subsampling only when registered before observing model outcomes.

### Controls

Execute:

- Duplicate training delivery.
- Reversed delivery order where applicable.
- Removal of all support for a targeted learned rule.
- Leave-one-source-out through an actual refit.
- Rule removal.
- Required-premise removal.
- Wrong-state and wrong-role bindings.

### Acceptance

- Native revision is demonstrated by executable receipts.
- Learning effects are separated from supplied rule structure.
- Duplicated evidence does not increase support.
- Source-removal controls rebuild the model from the remaining evidence.
- No evidence identities are changed to manufacture disjointness.

Zero natural conditional errors is an acceptable scientific result. Do not introduce synthetic failures into the natural training set.

---

## C19-05 — Connected native consequence evaluation

### Implement

Evaluate `Clear` and `Attack` from the permitted low-level observations.

The decisive path must contain native derivation of the intermediate relation and terminal consequence. Do not feed an externally calculated `Clear` into the attack query.

If separate native invocations are needed for inspection, use the same registered raw facts and rules. Do not bridge the invocations by importing an audited or host-computed answer.

For each query retain:

- Canonical input facts and rules.
- Model and runtime identities.
- Query and entity bindings.
- Native answer and contrary channels.
- Strength/confidence.
- Evidence stamps.
- Selected and retained statements exposed by the runtime.
- Process status and resource limits.
- The scope of observable proof information.

Fired-rule parents remain unknown when the runtime does not expose them. Host dependency links must not be represented as native firing traces.

Freeze thresholds and inference budgets before final evaluation.

Do not tune thresholds against final test errors.

### Interpretation

A shared arm may remain unknown. That does not prevent completion of the study.

Distinguish:

- A completed bounded execution with no supported answer.
- An observed execution failure.
- A resource limit.
- A semantic conflict.
- A supported positive or contrary conclusion.

A completed bounded search does not prove that no derivation exists under every larger budget.

### Acceptance

- The model’s current-position answer comes from native inference.
- No evaluator or reference-model output crosses into inference.
- State and role binding are preserved.
- All intended final evaluations complete or retain explicit incomplete status.
- The historical shared/disjoint capability boundary remains accurately reported.

---

## C19-06 — Query meaning and bounded reference analysis

### Required deliverable

Write an explicit mapping between the current-position query and its evidence.

A useful notation is:

`Attack(attacker, target, state) given available observations and learned evidence`.

Do not reuse Cycle 18’s two-future-trial probability as the probability of this current attack.

Identify which uncertainty, if any, is relevant:

- Missing or imperfect occupancy observations.
- Representation error.
- Conditional applicability.
- Uncertainty about a reusable schema.
- Computational incompleteness.

The native empirical study must proceed even if none of these has a defensible probability model.

### Conditional reference work

Implement a new numerical reference calculation only if:

1. The current-position event is explicitly defined.
2. Its observation and uncertainty assumptions are written down.
3. The calculation answers that event.
4. It has a clear role in interpreting the measured chess experiment.

Otherwise deliver a structured `not_identified` result explaining the missing information.

If a reference calculation is justified:

- Reuse the small exact laboratory.
- Keep it isolated from native inference, training checkpoints, caches, and operational classification.
- Use at most two uncertain parameters and 25 total enumerated states, counting any added latent states.
- Use only a small preregistered set of current-position cases and assumptions.
- Enforce resource limits and retain inconsistency/incomplete outcomes.
- Justify parameter support and priors.
- Do not exclude perfect reliability and then interpret subunit predictions as measured failure.
- Distinguish shared uncertainty from independent repeated trials.
- Label synthetic noise or corruption as a separate known-generative control.

No general Bayesian engine, large grid search, or new native bridge is authorized.

### Acceptance

The package must conclude either:

- A relevant current-position reference interpretation is implemented and bounded; or
- The intended probability remains unidentified, with a precise explanation.

An honest unidentified result is complete research reporting, not an engineering failure.

---

## C19-07 — Dependency-aware correction and active evidence

### Implement

Add a new Cycle 19 active-evidence policy around immutable historical records.

When an environmental observation is superseded:

1. Retain the old observation and all historical descendants.
2. Follow explicit parent references to identify affected measurements and annotations.
3. Mark affected descendants stale for current use.
4. Identify parameter generations that admitted those stale records.
5. Prevent those generations from silently serving as current generations.
6. Identify affected applications and cached results.
7. Recompute measurements and refit generations explicitly where required.
8. Publish the new active view only after the rebuild succeeds.

Historical generations remain reproducible for their original evidence snapshots.

Do not automatically invalidate unrelated records merely because they share a publisher or source-game group. Direct dependency and statistical dependence are different relationships.

### Required safeguards

- Current fitting rejects stale annotations.
- Current inference rejects stale environmental references.
- A new annotation cannot claim freshness while depending on an invalid parent.
- A correction is not counted as an additional independent measurement of the same event.
- Unknown corrected occupancy remains unknown.
- Failed rebuilding cannot expose a mixture of old and new active generations.
- Component masks, payloads, assumptions, learner identity, and relevant evidence versions remain bound to generation identity.
- Historical replay explicitly selects the historical snapshot.

### Required controls

1. Same event delivered again.
2. New event with identical payload.
3. Changed payload under the same ID rejected.
4. Explicit supersession.
5. Empty occupancy corrected to occupied.
6. Empty occupancy corrected to unknown.
7. Attacker or target identity corrected.
8. Training-source correction followed by actual refit.
9. Branched dependencies with two affected descendants.
10. An unaffected disconnected branch.
11. Failed or interrupted rebuild.
12. Historical snapshot replay.
13. Incremental affected-set handling compared with full reconstruction.

Use a small existing cache or research-only cache where needed to demonstrate stale-result rejection. Do not redesign the project’s caching system without a concrete requirement.

Cache identities must bind all relevant inputs, including state/history, evidence versions, model generation, query/bindings, runtime, policy, and applicable budgets.

### Acceptance

- Stale data are rejected, not merely flagged.
- Incremental and full reconstruction agree.
- Historical results remain reproducible.
- Native stamps and calculus remain unchanged.
- Reports describe this as host-managed evidence lifecycle handling, not native automatic belief propagation.

---

## C19-08 — Evaluation, uncertainty, and decisive demonstrations

### Implement

Report `Clear` and `Attack` separately.

For each arm and cohort provide:

- Roots and source games.
- Queries and dependent variants.
- Reference-positive, reference-negative, and unresolved measurements.
- Supported positive, supported contrary, unknown, conflict, and incomplete counts.
- False-positive and false-negative classifications.
- Precision, recall, coverage, and applicable uncertainty intervals.
- Native truth-value distributions.
- Evidence and proof references.

If a metric has a zero denominator, report it as undefined. Do not replace undefined precision with 100%.

Keep natural, transformed, missing-observation, and synthetic-corruption results separate.

Report evaluator disagreements and exclusions in the original cohort denominator accounting. Do not silently remove difficult cases from the final report.

Use source/root-aware uncertainty analysis. State the assumptions of any resampling or interval method. Distinct games do not prove statistical independence, especially when openings, engines, publishers, or upstream checkpoints are shared.

### Demonstrations

Deliver at least eight compact, inspectable cases selected by registered criteria:

- A native positive clearance and attack.
- A blocked influence case.
- A missing-observation case.
- Transfer to a new endpoint location.
- A relative-direction transfer where available.
- A shared-source composition limitation.
- A genuine source-removal/refit effect.
- An environmental correction with dependent invalidation and rebuild.

Include failures and unknowns when those are the actual outcomes.

For each case show:

- The source episode.
- Relative observations.
- Audited outcomes.
- Admitted training evidence.
- Native inputs and outputs.
- What changed under the intervention.
- What the case does and does not establish.

### Acceptance

The final analysis must answer:

1. Are the two domain targets separately supported by the measurement pipeline?
2. Does native revision affect the intended consequence model?
3. What transfer was actually demonstrated?
4. What remains blocked by shared evidence or repeated rule stamps?
5. Is any empirical probability interpretation identified?
6. What remains assumption-dependent or unidentified?

No accuracy improvement or confidence conversion is required for engineering acceptance.

---

## C19-09 — Isolation, preservation, resources, and reproduction

### Implement

Extend meaningful checks for:

- Measurement-to-inference isolation.
- Reference-to-native isolation.
- Frozen rule/template integrity.
- Duplicate and supersession semantics.
- State and role separation.
- Unknown, conflict, and incomplete handling.
- Cache invalidation and proof parity.
- Historical snapshot reproduction.

Use the repository’s established preservation machinery.

At the final executable-source freeze, run the complete required historical gate, including:

- The full test suite.
- All 206 legal shards and 584,112 candidate rows.
- Exact canonical native proof parity.
- The 287 evidence-removal controls.
- The 27 history controls.
- Both historical en-passant recoveries.
- The 76 controlled legal holdouts.
- Protected historical files and evidence manifests.
- Accepted checkpoint and runtime identities.

The Cycle 18 test count is a baseline receipt, not a fixed expected count for the extended suite.

If executable code, data, or configuration changes after the freeze, create a new freeze and rerun the gates needed to establish final acceptance. Do not combine old-source and new-source receipts into a claimed single completed campaign.

### Resources

Separate:

- Corpus preparation.
- Measurement.
- Native training.
- Native inference.
- Lifecycle/refit controls.
- Optional reference calculations.
- Historical preservation.
- Proof comparison.
- Published-checkout reproduction.

Record wall time, CPU time, peak memory, native calls, output size, and incomplete runs.

Use a small preregistered benchmark panel for:

- Cold native query.
- Warm cached query where applicable.
- Corrected-input query.
- Source-removal refit.
- Incremental lifecycle update.
- Full lifecycle reconstruction.

Require correctness and proof parity before reporting performance gains. Do not describe a cache lookup as faster native reasoning.

### Reproduction levels

Provide distinct commands for:

1. One compact measured episode.
2. The new measurement and native-learning study.
3. Correction/invalidation controls.
4. Decisive native historical anchors.
5. Full historical preservation.

Distinguish a fresh checkout using verified dependencies from a fresh dependency installation.

---

## C19-10 — Interfaces, architectural decision, and delivery

### Implementation layout

Prefer new modules under `research/cycle19/`, with focused tests and delivery helpers following existing repository conventions.

Expose a documented research CLI covering:

- Measurement.
- Fitting.
- Evaluation.
- Evidence lifecycle controls.
- Compact reproduction.
- Optional reference diagnostics.

Use explicit output schemas and new generation directories. Refuse silent overwriting of evidence generations.

Keep operational APIs and defaults unchanged. A new production endpoint or inspector redesign is not required.

### Required documentation

Deliver:

1. `engineering-report.md`
2. `package-matrix.md`
3. `research-registration.md`
4. `targets-and-measurements.md`
5. `corpus-and-transfer.md`
6. `native-results.md`
7. `evidence-lifecycle.md`
8. `architecture-decision.md`
9. `reproduction.md`
10. `publication.md`

Use compact machine-readable artifacts for detailed counts, resources, provenance, and acceptance.

The package matrix must separate:

- Implementation delivered.
- Experiments executed.
- Research finding.
- Unmet target or limitation.
- Supporting evidence.

### Architectural decision

Conclude explicitly which outcomes apply:

**A — Domain measurement established.**  
The current-position targets and their measurement lineage are defensible.

**B — Native learning and bounded transfer demonstrated.**  
The existing runtime learns support and derives consequences within the measured scope.

**C — Probability interpretation unresolved.**  
The available measurements do not identify the intended uncertainty model or confidence conversion.

**D — Native extension still required for the requested capability.**  
Shared evidence or repeated rule stamps prevent the desired composition under the pinned runtime.

These outcomes may coexist.

If proposing future native work, name the smallest required capability and its unresolved semantics. A proposal is not authorization to implement it.

Do not begin a new runtime-extension cycle under this brief.

---

## 8. Mandatory acceptance gates

Engineering acceptance requires:

1. Verified baseline and registered study.
2. Traceable, separately checked target measurements.
3. Honest sampling, admission, and overlap accounting.
4. Native learning and inference through the pinned supported path.
5. No evaluator/reference leakage into inference.
6. No evidence laundering or stamp manipulation.
7. Correct stale-evidence rejection and immutable historical replay.
8. Incremental lifecycle parity with full reconstruction.
9. Explicit handling of unknown, conflict, and incomplete results.
10. Complete required historical preservation.
11. Compact reproduction from the final published source.
12. Successful commit, push, and independent remote verification.

Research acceptance does not require:

- Improved chess accuracy.
- Nonzero natural error rates.
- A calibrated probability model.
- A repaired shared-source chain.
- Generic recursion.
- A confidence conversion.
- Promotion of an operational model.

Report an engineering failure as an engineering failure. Report a negative research result as a research result. Do not conflate them.

---

## 9. Artifact and Git size discipline

Commit enough material to reproduce and inspect the principal results without access to private local paths:

- Source and tests.
- Registration and corpus manifests.
- Appropriately licensed compact input records.
- Measurement examples.
- Experimental checkpoint identities.
- Decisive native inputs, outputs, and observable traces.
- Correction and refit witnesses.
- Reports and reproduction commands.

Keep large historical proof exports, dependency caches, and bulk evidence outside ordinary Git.

Use the existing evidence-pack conventions, with checksums and an actual restore-and-verify test.

Retain these project budgets:

- Maximum new blob: 10 MiB.
- Target total new unique blob content: 100 MiB.

These are project budgets, not statements about GitHub limits.

Inventory every new reachable blob across the entire baseline-to-HEAD range, including superseded versions. A tip-only check is insufficient.

Scan both current and superseded new content for accidental secrets.

If unpublished commits contain excessive bulk:

- Preserve a backup and provenance record.
- Repackage only the unpublished range.
- Retain compact decisive evidence.
- Never rewrite already published history to reduce size.

Do not upload bulk packs, create a release, publish tags, or deploy anything under this assignment.

---

## 10. Explicit commit and push requirements

Committing and pushing are mandatory deliverables.

### 10.1 Commit sequence

Create meaningful commits for:

- Registration.
- Implementation and tests.
- Any substantive correction.
- Final reports and compact evidence.

No particular commit count is required.

Stage reviewed paths explicitly. Do not blindly add the entire working directory.

Before final publication:

- Confirm the branch descends from the required baseline.
- Confirm the executable-source freeze and final evidence correspond.
- Complete the size and secret checks.
- Confirm the protected baseline remains intact.
- Confirm the working tree is clean after the final commit.

### 10.2 Verify the destination

Inspect:

- The fetch URL.
- Every configured push URL.
- Relevant URL rewriting.
- The effective repository.
- The exact destination ref.

Do not print or commit credential-bearing URLs.

The only authorized repository is `machieke/pln-chess`.

The push must update only the dedicated Cycle 19 branch. Do not update `main`, `master`, tags, or unrelated branches.

### 10.3 Push

After the checks above, use an explicit refspec.

For the default branch name:

```bash
set -euo pipefail

C19_BASE=4691c9cc7bf3aebe89c87fb5956852622be3eeb5
C19_BRANCH=cycle19-measured-chess-consequences

test "$(git branch --show-current)" = "$C19_BRANCH"
git merge-base --is-ancestor "$C19_BASE" HEAD
test "$(git rev-list --count "${C19_BASE}..HEAD")" -gt 0
test -z "$(git status --porcelain)"

C19_LOCAL_SHA="$(git rev-parse HEAD)"

git -c push.followTags=false -c push.recurseSubmodules=no \
  push --set-upstream origin \
  "HEAD:refs/heads/${C19_BRANCH}"

C19_REMOTE_SHA="$(
  git ls-remote --exit-code origin "refs/heads/${C19_BRANCH}" |
  awk 'NR == 1 {print $1}'
)"

test -n "$C19_REMOTE_SHA"
test "$C19_LOCAL_SHA" = "$C19_REMOTE_SHA"
```

If a different dedicated branch name was required, use the registered name consistently.

Do not use any force option.

### 10.4 Independent publication verification

A successful `git push` and local remote-tracking reference are insufficient.

After pushing:

1. Query the branch freshly from the remote.
2. Query the canonical GitHub repository independently through the GitHub API, connector, or an equivalent direct read.
3. Require exact equality with local `HEAD`.
4. Retrieve the engineering report, source, compact inputs, and reproduction guide at that exact SHA.
5. Create a fresh checkout of the published commit.
6. Execute the compact measurement, native consequence, and lifecycle reproduction using verified dependencies.
7. Confirm the original working tree remains clean.

Account for Git URL rewriting when deciding whether a check is independent. Two Git commands using the same rewritten destination are not two independent destination checks.

Keep the final publication receipt outside the tracked checkout, or in an existing separately managed receipt location, to avoid self-referential final-SHA commits.

### 10.5 Failure handling

If push or verification fails:

- Preserve all work and local commits.
- Record the exact failure.
- Report the final local SHA.
- State whether the branch was pushed, partially verified, or not pushed.
- Do not claim synchronization without verification.
- Do not bypass authentication, access controls, or repository protections.
- Do not force-push to resolve a rejection.

A negative research finding does not prevent publishing the completed, correctly labeled engineering package.

---

## 11. Final response requirements

The final response must include:

1. Starting SHA.
2. Final local SHA.
3. Independently verified remote SHA.
4. Branch.
5. Commit list.
6. Working-tree status.
7. Engineering package matrix.
8. Research outcome.
9. Natural roots, games, measurements, annotations, and dependent-variant counts.
10. Training admissions and exclusions by target.
11. Native results by arm and cohort.
12. Actual learning and transfer findings.
13. Correction/invalidation and refit results.
14. Reference interpretation or explicit unidentified result.
15. Historical preservation and proof-parity results.
16. Resource use and incomplete or interrupted runs.
17. Git size inventory and evidence-pack restoration.
18. Published-checkout reproduction result.
19. Links to the published report and decisive evidence.
20. The exact remaining native capability limitation.

Use precise conclusions.

A successful Cycle 19 should make it possible to inspect a current chess position, identify the relative observations, examine separately checked outcomes, trace the learned native support, and see what changes after new evidence, correction, source removal, or transfer.

It must also make clear which parts are native inference, which are host-managed evidence operations, and which remain unresolved research.