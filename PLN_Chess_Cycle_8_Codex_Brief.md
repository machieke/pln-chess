# PLN Chess — Cycle 8 Engineering Implementation Brief

## Safe Generalization and Native PLN Composition Design

**Repository:** https://github.com/machieke/pln-chess  
**Starting commit:** `c6ee658352395abe6e276cafdf1ddf59830a17a0`  
**Execution:** Consolidated autonomous engineering cycle  
**Authorization:** Local implementation, experimentation, testing, documentation, and commits permitted. Do not push to GitHub. Do not enable new PLN inference operators.

---

# 1. Mission

Continue development of the existing PLN Chess research system.

Cycle 8 has two independent engineering objectives:

**Track A — Safe operational generalization**

Investigate and resolve the promotion-related classification errors that prevented the Cycle 7 experimental learner from replacing the accepted operational model.

Preserve the existing model's useful predictions, transferable relational knowledge, native PLN inference, and evidence provenance.

**Track B — Native PLN composition research**

Produce an implementation-ready mathematical and technical specification for the missing multi-premise PLN composition capability.

Do not implement an unapproved inference rule in production.

The two tracks must remain independent. Failure to establish a new PLN composition capability must not prevent delivery of operational improvements.

# 2. Starting State

Cycle 7 delivered:

- Accepted operational model: C7-frozen.
- Frozen transfer recall: 97.767%.
- New-game recall: 96.049%.
- Experimental candidate: 99.298% recall and 27/32 exact move sets on the new-game cohort.
- Experimental errors: four false-legal and four false-illegal promotion decisions.
- 287 verified negative evidence-removal controls.
- 318 passing tests.
- Native positive composition not demonstrated.
- Three existing-rule composition encodings investigated without success.

These are reported baselines. Verify them from repository artifacts before modifying implementation.

The accepted operational model must remain available and reproducible throughout Cycle 8.

# 3. Architectural Invariants

The following requirements are non-negotiable.

1. All learned chess knowledge must remain piece-relative and translation-independent.
2. Absolute coordinates may be used for board I/O, state reconstruction, and evaluation, but not as constants in learned movement rules.
3. Native PLN must remain responsible for truth-value inference and revision.
4. Do not substitute Python probability calculations for native PLN operators.
5. Do not introduce a deterministic chess-legality gate into production inference.
6. Keep the reference chess oracle restricted to training, testing, and evaluation.
7. Preserve evidence IDs, dependence groups, proof traces, model versions, and replay semantics.
8. Preserve operational, strict, and experimental inference modes.
9. Do not claim full compositional proofs when only conditional or partial evidence exists.
10. Unknown results must remain unknown when the available evidence cannot justify a conclusion.

# 4. Work Package C8-01 — Baseline Preservation

Before making changes:

- Verify the starting commit.
- Record repository status and dependencies.
- Reproduce Cycle 7 operational and experimental evaluations.
- Record dataset and model hashes.
- Preserve original checkpoints and proof artifacts.
- Establish frozen regression comparisons.

Create:

`artifacts/cycle8/baseline/`

Include machine-readable manifests containing:

- Commit SHA.
- Runtime versions.
- Dataset hashes.
- Model hashes.
- Evaluation metrics.
- Native operator versions.
- Reproduction commands.

Do not silently regenerate historical baselines using changed code.

# 5. Work Package C8-02 — Promotion Error Forensics

Investigate all eight incorrect promotion decisions from Cycle 7.

For every case, record:

- Original FEN.
- Proposed move.
- Promotion target.
- Color and ownership.
- Capture or non-capture.
- Relative geometry.
- Destination occupancy.
- King exposure.
- Relevant historical state.
- Matched learned hypotheses.
- Native PLN truth values.
- Evidence IDs.
- Dependence groups.
- Proof graph.
- Expected reference classification.
- Actual classification.

Identify the first inference or evidence-selection step responsible for each error.

Classify root causes into categories such as:

- Incorrect abstraction.
- Missing contextual distinction.
- Evidence contamination.
- Correlated evidence.
- Incorrect rule applicability.
- Promotion-choice confusion.
- Missing king-safety information.
- Confidence-selection behavior.
- Training distribution deficiency.

Do not assume that all eight errors share one cause.

Deliver:

`docs/cycle8/promotion-error-analysis.md`

and a structured JSON case inventory.

# 6. Work Package C8-03 — Promotion-Relative Ontology

Review the representation of pawn promotion.

The ontology must distinguish:

- Arrival at the promotion boundary.
- Pawn forward movement.
- Diagonal capture.
- Destination occupancy.
- Promotion choice.
- Resulting piece identity.
- Post-promotion king exposure.
- White and Black orientation.

Promotion should be represented as a relative state transition rather than a collection of absolute-square exceptions.

For example, the concept of reaching the final rank should be expressed through the pawn's owner-relative distance to the board boundary.

Avoid learning separate rules for a7, b7, c7, and so forth.

Implement reusable typed propositions where supported by the existing architecture.

Preserve explicit provenance for every observation and derived proposition.

# 7. Work Package C8-04 — Promotion Curriculum

Construct a balanced, reproducible promotion curriculum.

Include:

- White promotions.
- Black promotions.
- Queen promotions.
- Rook promotions.
- Bishop promotions.
- Knight promotions.
- Forward promotions.
- Capture promotions.
- Friendly-occupied destinations.
- Blocked pawn advances.
- Promotions that expose the king.
- Promotions that resolve check.
- Promotions involving pinned pawns.
- Underpromotion examples.
- Incomplete observations.

Partition the dataset by structural families and independent games.

Avoid leakage through translated or reflected versions of training positions.

Maintain separate:

1. Training examples.
2. Validation examples.
3. Independent combination holdouts.
4. Adversarial examples.
5. Independent-game holdouts.

The same structural family must not appear in both training and strict held-out evaluation.

# 8. Work Package C8-05 — Safe Generalization Improvements

Improve the experimental learner without introducing hardcoded legality decisions.

Prioritize correcting the underlying relational abstractions and evidence relationships.

Candidate improvements may include:

- Promotion-choice-specific evidence attribution.
- Better distinction between movement and resulting-piece transitions.
- Local context refinement.
- More conservative dependence-group handling.
- Separating attack evidence from promotion eligibility.
- Improved native confidence selection.
- Better treatment of missing evidence.

Every proposed improvement must include an ablation.

Compare the new model with:

- Cycle 7 operational.
- Cycle 7 experimental.
- Cycle 8 experimental candidate.

Do not promote a candidate merely because recall improves.

False-legal and false-illegal regressions are release blockers.

# 9. Work Package C8-06 — Independent Generalization

Evaluate whether learned promotion knowledge transfers across:

- Board translations.
- File reflections where semantics are preserved.
- Color-relative transformations.
- Different pawn files.
- Different opponent configurations.
- Different resulting-piece choices.
- Unseen capture configurations.

Require at least five inspectable transfer demonstrations.

Each demonstration must include:

- Training evidence.
- Held-out position.
- Relative descriptor.
- Native inference expression.
- Raw truth value.
- Matched rule IDs.
- Proof graph.
- Evidence-removal control.

A successful transfer must not depend on an exact-context match.

# 10. Work Package C8-07 — Native PLN Composition Specification

Produce a formal proposal for a native multi-premise composition capability.

The proposal must define the intended inference problem independently of chess.

Consider premises A and B, and a conclusion C that depends jointly on A and B.

Specify:

- Logical syntax.
- Premise truth-value types.
- Conclusion truth-value type.
- Strength semantics.
- Confidence semantics.
- Required independence assumptions.
- Evidence overlap handling.
- Correlation and dependence behavior.
- Unknown evidence.
- Contradictory evidence.
- Boundary conditions.
- Revision interactions.

Investigate how this capability relates to the existing native PLN operators:

- Modus ponens.
- Deduction.
- Induction.
- Revision.
- Negation.
- Inheritance.
- Evidence selection.

Do not assume that multiplying premise strengths is a valid general conjunction formula.

Do not assume independence merely because evidence comes from different files or observations.

Explicitly distinguish:

1. Logical conjunction.
2. Probabilistic dependence.
3. Conditional implication.
4. Evidence aggregation.
5. Confidence estimation.

Deliver:

`docs/cycle8/native-composition-proposal.md`

# 11. Work Package C8-08 — Mathematical Validation

The proposed operator must include a rigorous mathematical analysis.

At minimum, investigate:

- Probability bounds.
- Normalization.
- Confidence behavior.
- Zero-evidence cases.
- Contradictory premises.
- Correlated observations.
- Duplicate evidence.
- Associativity, if applicable.
- Commutativity, if applicable.
- Order sensitivity.
- Interaction with native revision.
- Potential double counting.

Provide explicit counterexamples where naive formulas fail.

If the proposed rule requires assumptions that cannot be established from the available evidence, identify those assumptions as unresolved proof obligations.

Do not claim mathematical soundness based solely on successful chess examples.

# 12. Work Package C8-09 — Isolated Composition Laboratory

Create an isolated research environment for evaluating the proposed semantics.

The laboratory may include mathematical reference calculations and prototype experiments, but these must not become production PLN inference.

Separate:

- Existing native PLN behavior.
- Proposed mathematical semantics.
- Experimental prototype behavior.

Use independently acquired premises.

Demonstrate both successful and unsuccessful cases.

Required examples:

1. Two independent positive premises.
2. One positive and one negative premise.
3. Unknown premise.
4. Correlated evidence.
5. Duplicate evidence.
6. Contradictory evidence.
7. Held-out conclusion.
8. Chess-relative application.

Produce exact expressions, numerical results, and counterexamples.

No new operator may be enabled in the operational learner.

# 13. Work Package C8-10 — Proof and Provenance Integrity

All experimental conclusions must retain:

- Premise IDs.
- Rule IDs.
- Evidence IDs.
- Dependence groups.
- Native runtime version.
- Model version.
- Truth values.
- Derivation order.
- Proof status.
- Inference budget.

Differentiate:

- Native complete proof.
- Native partial proof.
- Proposed-rule experimental result.
- Unsupported inference.
- Unknown conclusion.

Do not label proposed-rule calculations as native PLN proofs.

Verify that removing essential evidence changes the corresponding conclusion or its support as expected.

Preserve the 287 established negative controls.

# 14. Work Package C8-11 — Performance and Caching

Preserve Cycle 7's proof-preserving cache behavior.

Benchmark:

- Single-candidate inference.
- Full-position inference.
- Promotion-heavy positions.
- Independent-game positions.
- Cold execution.
- Warm execution.
- Reference uncached execution.

Report:

- p50, p95, and p99 latency.
- Native invocation counts.
- Grounded atoms.
- Cache hits and misses.
- Peak RSS.
- Checkpoint size.
- Proof equivalence.
- Truncation and timeout rates.

Optimization must not alter truth values, classifications, evidence IDs, or proof semantics.

# 15. Work Package C8-12 — API, CLI, and Inspector

Extend the existing developer interfaces.

The inspector should allow comparison of:

- Cycle 7 operational.
- Cycle 7 experimental.
- Cycle 8 experimental.
- Accepted Cycle 8 operational, if promoted.

Display promotion-specific evidence and proof differences.

Expose whether a conclusion is:

- Supported.
- Contradicted.
- Unknown.
- Incomplete.

Also expose proof completeness separately from classification.

Provide machine-readable exports for every comparison.

Avoid duplicating inference logic inside the UI.

# 16. Work Package C8-13 — Evaluation and Acceptance

Run all established regression datasets and new Cycle 8 datasets.

Report:

- Precision.
- Recall.
- F1.
- Abstention rate.
- False-legal count.
- False-illegal count.
- False-positive self-check count.
- Exact legal-move-set accuracy.
- Per-piece results.
- Promotion-specific results.
- Independent-game results.
- Calibration diagnostics.

## Mandatory acceptance gates

1. Existing operational behavior remains reproducible.
2. Zero observed false-legal and false-illegal regressions across established acceptance datasets.
3. All 287 negative evidence-removal controls pass.
4. No production oracle dependency.
5. No new unapproved PLN operator.
6. Native proof and cache parity remain valid.
7. Full clean-checkout reproduction succeeds.
8. All tests pass.
9. Failed experiments are documented.
10. The accepted model is promoted only after passing every mandatory gate.

## Research targets

Aim to:

- Resolve all eight original promotion errors.
- Preserve at least 27/32 exact move sets on the Cycle 7 new-game cohort.
- Improve independent-game exact-set accuracy.
- Preserve or improve legal-move recall.
- Demonstrate at least five new promotion-related transfers.

These targets are not permission to weaken the mandatory gates.

If the experimental learner fails acceptance, retain the previous operational model and deliver the experimental findings separately.

# 17. Work Package C8-14 — Consolidated Delivery

Produce:

- Engineering report.
- Work-package status matrix.
- Baseline comparison.
- Promotion-error analysis.
- Dataset and model manifests.
- Native proof traces.
- Evidence-removal results.
- Generalization experiments.
- Ablation reports.
- Performance benchmarks.
- Formal PLN composition proposal.
- Mathematical validation report.
- Reproduction instructions.
- One-page architectural decision memo.

The decision memo must answer:

1. Did Cycle 8 resolve the promotion errors?
2. Was the improved learner accepted?
3. What independent generalization was demonstrated?
4. What exact PLN capability is missing?
5. Is a native PLN extension technically justified?
6. What are the mathematical risks?
7. What implementation and verification work would authorization entail?
8. What should Cycle 9 prioritize?

# 18. Execution Contract

Work autonomously through all feasible packages.

Do not stop after each milestone for approval.

Make ordinary local engineering decisions independently.

Preserve the existing architecture unless a change is justified by reproducible evidence.

Do not silently weaken acceptance criteria.

Do not replace PLN inference with a conventional chess engine.

Do not invent a new native PLN operator.

Do not push to GitHub.

Commit completed work locally with clear commit messages.

Stop only when an essential dependency is unavailable, a genuinely blocking technical incompatibility prevents further independent work, or external authorization is required.

# 19. Final Reporting Format

The final Codex response must include:

1. Starting and ending commit hashes.
2. Clean working-tree status.
3. Commit list.
4. Work-package completion matrix.
5. Baseline versus Cycle 8 metrics.
6. Promotion-error outcomes.
7. Generalization results.
8. Native PLN composition findings.
9. Test and reproduction results.
10. Performance comparisons.
11. Known limitations.
12. Architectural decision recommendation.

Every performance or correctness claim must be supported by reproducible artifacts.

Distinguish independently verified results from experimental hypotheses.

---

# Final Objective

Cycle 8 must deliver two independently valuable outcomes:

**Operational:** A safer, more generalizable probabilistic chess-rule learner that preserves existing native PLN inference guarantees.

**Research:** A rigorous, implementation-ready proposal for the missing multi-premise PLN composition capability.

The project must not sacrifice operational correctness merely to satisfy an unsupported proof requirement.

The long-term objective remains a probabilistic chess intelligence that learns transferable, local relational rules rather than memorizing absolute board configurations.
