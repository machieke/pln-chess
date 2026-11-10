# PLN Chess — Cycle 12 Engineering Implementation Brief

## Relational Field Dynamics, Strategic Concept Formation, and Temporal Evolution

**Repository:** https://github.com/machieke/pln-chess  
**Starting commit:** `f4a9fd5536d001fa8830773012dcd578443b0b61`  
**Accepted operational baseline:** C8-promotion-relative with Cycle 10 temporal evidence  
**Execution:** Consolidated autonomous engineering cycle  
**Delivery:** Source code, experiments, native proofs, tests, benchmarks, documentation, and local commits  
**Authorization:** No GitHub push, no external deployment, no upstream PLN modifications, and no unapproved inference operators.

---

# 1. Mission

Cycle 12 must investigate whether reusable local probabilistic relationships can produce higher-level strategic concepts and temporal field dynamics.

The system already represents:

- Relative movement relationships.
- Attack potential.
- Defense potential.
- Mobility potential.
- King-exposure potential.
- Candidate successor-state fields.
- Before/after relational field differences.

Cycle 12 must build on these capabilities.

The central research question is:

> Can independently learned, piece-relative probabilistic relationships support the recognition and evolution of strategic chess concepts without memorizing absolute board configurations or introducing conventional handcoded chess evaluation heuristics?

The project must remain grounded in native SingularityNET/OpenCog PLN inference.

The objective is not to build a competitive chess engine.

The objective is to establish an explainable probabilistic representation of strategic relationships.

---

# 2. Engineering Tracks

Cycle 12 consists of four coordinated tracks.

## Track A — Legal-Move Completion

Evaluate the unpromoted Cycle 11 en-passant improvements and determine whether they can safely be incorporated into the operational learner.

Preserve all existing regression guarantees.

## Track B — Relational Field Dynamics

Develop interactions between attack, defense, mobility, and king-exposure fields.

Investigate how local changes propagate through relational dependencies.

## Track C — Strategic Concept Formation

Investigate reusable representations of:

- Pins.
- Forks.
- Discovered attacks.
- Overloaded defenders.
- Trapped pieces.
- Discovered defenses.
- Multiple attackers.
- Threat removal.

## Track D — Temporal Field Evolution

Track probabilistic relational fields across actual move sequences.

Investigate the appearance, persistence, transformation, and disappearance of strategic relationships.

All four tracks must remain independently testable.

Failure of an experimental track must not degrade the accepted operational learner.

---

# 3. Starting Baseline

Cycle 11 reported:

- 20/20 engineering packages delivered.
- 11/12 research targets achieved.
- Both outstanding en-passant cases recovered experimentally.
- 76/76 independent controlled legal holdouts passed.
- 27/27 temporal evidence controls passed.
- 38/38 spatial transformation controls passed.
- Eight dedicated field-learning transfers passed.
- Four experimental field families implemented.
- Fifteen before/after field demonstrations.
- Accepted legal-move model unchanged.

The established operational baseline includes:

| Cohort | Exact legal-move sets |
|---|---:|
| External FEN-only | 793/1,020 |
| External history-assisted | 1,018/1,020 |
| C9 adversarial | 112/128 |
| C9 special moves | 71/80 |
| C10 synthetic adversarial | 98/112 |

Reported external recall:

- FEN-only: 99.2645%.
- History-assisted: 99.9939%.

These are historical reported measurements.

Codex must reproduce their provenance before implementation.

---

# 4. Architectural Invariants

The following constraints are mandatory.

1. Learned chess knowledge must remain piece-relative.
2. Absolute coordinates may be used for board I/O, state reconstruction, and visualization, but not as learned rule constants.
3. Native PLN must perform probabilistic inference and truth-value revision.
4. Do not replace native PLN truth-value formulas with custom host-language calculations.
5. Do not introduce deterministic legality gates into production inference.
6. Reference chess engines remain restricted to training, testing, and evaluation.
7. Preserve operational, strict, and experimental inference modes.
8. Preserve evidence IDs, dependence groups, rule IDs, native expressions, and proof graphs.
9. Distinguish raw PLN strength, PLN confidence, and empirically calibrated diagnostic probabilities.
10. Preserve unknown and incomplete inference states.
11. Do not claim complete positive legality proofs where only partial conditional evidence exists.
12. Do not introduce new native PLN inference operators.
13. Do not enable the previously proposed multi-premise composition extension.
14. Do not implement conventional chess-engine evaluation functions or piece-square tables.
15. Preserve all historical datasets, checkpoints, and proof artifacts.
16. Experimental strategic reasoning must not change operational legality classifications.
17. Avoid hidden deterministic strategic-pattern detectors presented as learned PLN concepts.
18. Every strategic conclusion must disclose whether it is learned, derived, structurally observed, or supplied as a hypothesis.

---

# 5. Core Research Principle

Strategic concepts should emerge from relationships between pieces rather than from memorized chessboard configurations.

For example, a pin is not fundamentally a particular arrangement on the e-file.

It is a relational structure involving:

- A potential attacker.
- An intervening piece.
- A protected target behind that piece.
- An aligned relative ray.
- A change in exposure if the intervening piece moves.

The same structure can occur on different files, ranks, and diagonals.

Similarly, a fork is not a knight occupying a particular square.

It is a relationship in which one piece simultaneously influences multiple valuable targets.

Cycle 12 must investigate how these concepts can be expressed through existing native PLN inference and reusable local relationships.

Do not silently assume that the system can perform arbitrary conjunction.

The missing native multi-premise composition capability remains an explicit limitation.

---

# 6. Work Package C12-01 — Baseline Preservation

Verify the starting repository state.

Record:

- Git commit.
- Working-tree status.
- Native PLN version.
- PeTTa runtime version.
- Dependency hashes.
- Accepted legal model hash.
- Experimental field model hashes.
- Dataset hashes.
- Inference thresholds.

Reproduce Cycle 11 results.

Preserve historical artifacts.

Create:

    artifacts/cycle12/baseline/

Deliver:

- Baseline manifest.
- Reproduction receipt.
- Proof parity report.
- Model identity report.
- Dataset identity report.

Do not overwrite previous-cycle evidence.

---

# 7. Work Package C12-02 — En-Passant Promotion Review

Review the experimental Cycle 11 en-passant improvements.

Reproduce:

- Both recovered external en-passant cases.
- All 76 independent controlled holdouts.
- All 27 temporal evidence controls.
- Established legal-move regression cohorts.

Investigate whether the experimental model can be safely promoted.

Requirements:

- No new false-legal classifications.
- No new false-illegal classifications.
- No new self-check false positives.
- Preserved native proof provenance.
- Preserved evidence-removal controls.
- No deterministic legality gate.
- No absolute-coordinate rule specialization.

If all mandatory acceptance gates pass, promote the improvement.

Otherwise preserve it as an experimental checkpoint.

Document the decision.

---

# 8. Work Package C12-03 — Relational Field Interaction Ontology

Extend the Cycle 11 field ontology.

Represent interactions among:

- Attack potential.
- Defense potential.
- Mobility potential.
- King exposure.
- Obstruction.
- Relative alignment.
- Candidate successor states.
- Temporal evidence.

Introduce conceptual relations such as:

    Influences
    Supports
    Obstructs
    Exposes
    RestrictsMobility
    RemovesDefense
    OpensAttack
    ChangesInfluence
    PersistsAcrossMove
    ContradictsInfluence

These names are ontology candidates, not new PLN inference operators.

Specify:

- Predicate signatures.
- Argument types.
- Evidence semantics.
- Truth-value provenance.
- Relative spatial interpretation.
- Temporal interpretation.
- Unknown-state handling.

Avoid opaque full-position context keys.

Prefer reusable typed relational propositions.

Deliver:

    docs/cycle12/field-interaction-ontology.md

---

# 9. Work Package C12-04 — Relational Dependency Graph

Implement a dependency graph connecting field relationships.

For example:

    Piece movement
         |
         v
    Occupancy change
         |
         v
    Ray obstruction change
         |
         v
    Attack influence change
         |
         v
    Defense relationship change

The graph must preserve:

- Source propositions.
- Dependent propositions.
- Native rule IDs.
- Evidence IDs.
- Dependence groups.
- Model versions.
- Proof status.

Do not automatically interpret graph edges as probabilistic implications.

Only verified native PLN implications may propagate truth values.

Host-side dependency tracking is permitted for scheduling and invalidation.

Clearly distinguish dependency scheduling from probabilistic inference.

---

# 10. Work Package C12-05 — Field Interaction Experiments

Construct controlled experiments involving simultaneous changes in multiple field families.

Required examples:

1. Opening a rook file.
2. Opening a bishop diagonal.
3. Moving a pinned defender.
4. Removing a blocker.
5. Capturing a defender.
6. Creating a discovered attack.
7. Removing a discovered attack.
8. Increasing mobility while exposing the king.
9. Promotion changing attack influence.
10. En passant opening a ray.

For each experiment, produce:

- Initial position.
- Candidate move.
- Relative observations.
- Before fields.
- After fields.
- Typed field differences.
- Native proof traces.
- Evidence provenance.
- Unknown relations.
- Reference evaluation.

Do not reduce field interactions to one handcoded strategic score.

---

# 11. Work Package C12-06 — Strategic Concept Representation

Develop a typed ontology for strategic concepts.

Initial concepts:

    Pin
    Fork
    DiscoveredAttack
    DiscoveredDefense
    OverloadedDefender
    TrappedPiece
    MultipleAttackers
    ThreatRemoval

For every concept, specify:

- Required relational roles.
- Necessary structural observations.
- Candidate probabilistic premises.
- Potential conclusions.
- Dependence assumptions.
- Native PLN capabilities required.
- Unsupported composition requirements.

Distinguish:

1. Structural candidate.
2. Learned conditional concept.
3. Native PLN-derived concept.
4. Unverified concept hypothesis.

Do not label a structural candidate as a complete learned concept.

---

# 12. Work Package C12-07 — Pin Experiments

Investigate pins using piece-relative relationships.

A pin candidate may involve:

- Sliding attacker.
- Intervening piece.
- Protected target.
- Relative alignment.
- Potential exposure after movement.

Distinguish:

- Absolute pins against the king.
- Relative pins against another valuable piece.
- Geometric alignment.
- Legal movement restriction.
- Probabilistic exposure evidence.

Do not hardcode a fixed board pattern.

Train on selected relative configurations.

Evaluate on unseen translations, reflections, piece identities, and ray lengths.

Require at least five inspectable pin-transfer examples.

Every result must disclose whether it was structurally observed or inferred through native PLN.

---

# 13. Work Package C12-08 — Fork Experiments

Investigate forks as multi-target influence relationships.

The system should represent:

    One attacker
         |
         +-- influence target A
         |
         +-- influence target B

The two influence relationships may be learned independently.

Investigate whether the existing native PLN rules can support a reusable fork conclusion.

Do not fabricate conjunction.

If a complete native proof is unavailable, preserve both independently supported influence relationships and classify the fork as a structural or partial concept candidate.

Test:

- Knight forks.
- Pawn forks.
- Queen forks.
- Rook forks.
- King forks where applicable.

Evaluate transfer across board locations.

Avoid hardcoded target-value scores.

---

# 14. Work Package C12-09 — Discovered Attack and Defense

Investigate relational chains where moving one piece changes another piece's influence.

Examples:

- Pawn moves and opens bishop diagonal.
- Knight moves and opens rook file.
- Capturing a blocker opens queen attack.
- Moving a defender reveals a protected piece.
- A move removes an existing defense.

Use before/after field evidence.

Distinguish:

- Structural ray opening.
- Learned attack relation.
- Learned defense relation.
- Native PLN-derived consequence.
- Host-side field comparison.

Require evidence-backed explanations.

---

# 15. Work Package C12-10 — Overloaded Defenders

Investigate situations where one piece participates in multiple defensive relationships.

Represent:

- Defender.
- Protected target A.
- Protected target B.
- Candidate movement.
- Lost defense relationships.
- Potential exposure.

Do not assume that defending two pieces automatically makes a defender overloaded.

Overload requires additional contextual evidence about competing obligations and consequences.

Develop a conservative partial representation.

Report missing inference capabilities.

Avoid hardcoded material-value heuristics.

---

# 16. Work Package C12-11 — Trapped Pieces

Investigate probabilistic mobility restrictions.

A trapped-piece candidate may involve:

- Restricted geometric mobility.
- Occupancy constraints.
- Attack influence.
- King-exposure constraints.
- Limited supported escape relationships.

Distinguish:

- No geometric moves.
- No supported legal moves.
- Unknown legal moves.
- Strategically unfavorable moves.

Do not equate unknown mobility with zero mobility.

Do not claim a piece is strategically trapped solely because its legal-move count is low.

Produce controlled positive, negative, and uncertain examples.

---

# 17. Work Package C12-12 — Temporal Field Evolution

Extend field reasoning across actual move sequences.

For a sequence:

    S0 -> S1 -> S2 -> ... -> Sn

Track:

- Field creation.
- Field removal.
- Field persistence.
- Field strengthening.
- Field weakening.
- Changed evidence.
- Changed dependencies.

Preserve game-history provenance.

Distinguish changes in:

1. Observed relational state.
2. Learned conditional beliefs.
3. Native inference results.
4. Diagnostic field projections.

A change in field strength is not automatically evidence that a learned rule itself changed.

Implement deterministic replay.

Support partial histories.

---

# 18. Work Package C12-13 — Temporal Strategic Demonstrations

Construct at least ten multi-move demonstrations.

Include:

- Developing attack.
- Discovered attack preparation.
- Defender removal.
- Pin formation.
- Pin release.
- Fork creation.
- Fork escape.
- Mobility restriction.
- Promotion threat development.
- King-exposure change.

For every sequence, record:

- Initial position.
- Move history.
- Relative field states.
- Field changes after each move.
- Concept candidates.
- Native proof traces.
- Evidence lineage.
- Reference labels.

Do not claim that the system planned the sequence.

The system is observing and explaining temporal evolution, not choosing moves.

---

# 19. Work Package C12-14 — Independent Concept Learning

Create training and held-out datasets for strategic concept candidates.

Partition by structural family.

Prevent leakage through:

- Translations.
- Reflections.
- Piece-ID renaming.
- Repeated tactical motifs.
- Equivalent move sequences.

Train using native PLN revision where supported.

Evaluate:

- Concept recognition.
- Transfer accuracy.
- Abstention.
- False positives.
- False negatives.
- Evidence-removal sensitivity.
- Proof completeness.

Distinguish learning a conditional concept from discovering a new logical composition rule.

Do not claim native multi-premise reasoning when host-side grouping supplies the combined premise.

---

# 20. Work Package C12-15 — Counterfactual Concept Testing

Create controlled counterfactual pairs.

Examples:

- Pin with and without protected target.
- Fork with one versus two influenced targets.
- Discovered attack with and without blocker.
- Defender with one versus multiple obligations.
- Trapped piece with and without escape.
- Attack relation with and without obstruction.

Require the model to distinguish relevant changes.

Test invariance under irrelevant changes.

Each experiment must include:

- Source case.
- Counterfactual case.
- Changed relation.
- Native truth values.
- Proof differences.
- Evidence-removal controls.

Do not accept a concept learner that merely memorizes complete board configurations.

---

# 21. Work Package C12-16 — Interaction Propagation and Incremental Updates

Investigate incremental propagation of field changes.

When a piece moves:

1. Identify changed occupancy.
2. Identify affected relative rays.
3. Identify affected attack relationships.
4. Identify affected defense relationships.
5. Identify affected mobility relationships.
6. Identify affected king-exposure relationships.
7. Update dependent concept candidates.

Use dependency tracking to avoid recomputing unrelated fields.

Do not invent probabilistic propagation formulas.

Native PLN remains responsible for supported inference.

Verify exact equivalence between:

- Full recomputation.
- Incremental recomputation.

Compare proof identity, evidence lineage, and truth values.

---

# 22. Work Package C12-17 — Strategic Concept Inspector

Extend the Cycle 11 inspector.

Allow users to select:

- Board position.
- Piece.
- Candidate move.
- Field family.
- Strategic concept.
- Temporal step.

Display:

- Relative relational graph.
- Before/after fields.
- Concept candidates.
- Native truth values.
- Proof status.
- Evidence IDs.
- Rule IDs.
- Unknown relationships.
- Temporal evolution.

Use board overlays only as visual projections.

The underlying knowledge must remain piece-relative.

Preserve desktop and mobile compatibility.

Do not implement independent inference logic in the UI.

---

# 23. Work Package C12-18 — Evaluation and Benchmarks

Create separate evaluation metrics for:

- Legal-move inference.
- Field inference.
- Strategic concept recognition.
- Temporal field evolution.
- Incremental update correctness.

Report:

- Precision.
- Recall.
- F1.
- Abstention.
- False-positive rate.
- False-negative rate.
- Transfer accuracy.
- Proof completeness.
- Evidence-removal sensitivity.
- Runtime.
- Memory.
- Cache behavior.

Use evaluation-only reference chess engines and tactical annotations where appropriate.

Do not treat engine evaluations as native PLN conclusions.

Benchmark realistic multi-piece positions.

Preserve full proof provenance.

---

# 24. Work Package C12-19 — Regression and Acceptance Gates

Mandatory requirements:

1. Accepted legal-move results remain reproducible.
2. No new false-legal classifications on established acceptance cohorts.
3. No new false-illegal classifications on established acceptance cohorts.
4. No new self-check false positives.
5. All 287 negative evidence-removal controls pass.
6. Native proof and cache parity remain valid.
7. No production chess-oracle dependency.
8. No new native PLN inference operator.
9. No silent truth-value formula changes.
10. Historical evidence provenance remains intact.
11. Clean-checkout bootstrap succeeds.
12. Automated tests pass.
13. Existing APIs remain compatible or have documented migrations.
14. Strategic concept experiments do not change operational legal-move classifications.
15. Failed experiments are preserved and documented.

If the experimental legal improvement passes all acceptance gates, it may be promoted.

Strategic concept modules remain experimental throughout Cycle 12.

---

# 25. Work Package C12-20 — Consolidated Delivery

Produce:

    docs/cycle12/engineering-report.md
    docs/cycle12/package-matrix.md
    docs/cycle12/legal-promotion-review.md
    docs/cycle12/field-interaction-ontology.md
    docs/cycle12/dependency-graph.md
    docs/cycle12/field-interactions.md
    docs/cycle12/strategic-concepts.md
    docs/cycle12/pins.md
    docs/cycle12/forks.md
    docs/cycle12/discovered-attacks.md
    docs/cycle12/overloaded-defenders.md
    docs/cycle12/trapped-pieces.md
    docs/cycle12/temporal-evolution.md
    docs/cycle12/concept-learning.md
    docs/cycle12/counterfactuals.md
    docs/cycle12/performance.md
    docs/cycle12/reproduction.md

Required artifacts:

- Baseline manifests.
- Legal-move regression reports.
- Strategic concept datasets.
- Relative ontology manifests.
- Native proof traces.
- Temporal field sequences.
- Transfer-learning experiments.
- Counterfactual controls.
- Evidence-removal controls.
- Incremental-update benchmarks.
- Browser verification.
- Test logs.
- Reproduction receipts.
- Artifact hashes.

Provide a complete work-package status matrix.

Do not mark a research target complete without reproducible evidence.

---

# 26. Research Acceptance Targets

The following are research targets, not guarantees.

## Legal-Move Track

- Reproduce both recovered en-passant cases.
- Preserve all 76 independent legal holdouts.
- Preserve all 27 temporal evidence controls.
- Preserve all established legal-move regression gates.
- Promote the experimental improvement only if safe.

## Field Interaction Track

- At least ten multi-field interaction demonstrations.
- At least twenty transformation and locality controls.
- Exact full-versus-incremental field parity.
- Explicit evidence provenance for every supported influence.

## Strategic Concept Track

- Implement typed representations for all eight initial concepts.
- At least five transferable pin demonstrations.
- At least five transferable fork demonstrations.
- At least ten independent concept-learning holdouts.
- Explicit native proof status for every concept.
- No unsupported claims of complete multi-premise inference.

## Temporal Track

- At least ten multi-move field-evolution demonstrations.
- Deterministic temporal replay.
- Preserved event and evidence provenance.
- Explicit handling of missing historical information.

---

# 27. Native PLN Research Boundary

The current verified native PLN implementation supports selected operators including:

- Modus ponens.
- Revision.
- Negation.
- Deduction.
- Induction.
- Inheritance.
- Confidence-based evidence choice.

The project has not established a general native conjunction-introduction mechanism.

Do not disguise host-side construction of compound observations as native logical composition.

Where a concept requires several independently supported premises, distinguish:

1. Independently supported relations.
2. Host-assembled structural candidate.
3. Learned conditional concept.
4. Native PLN-derived conclusion.

If a complete native proof cannot be produced, preserve the partial representation.

Do not introduce an unapproved composition operator.

---

# 28. Cycle 13 Readiness Assessment

The final report must assess whether the system is ready for probabilistic strategic move comparison.

Consider:

- Field reliability.
- Strategic concept transfer.
- Temporal consistency.
- Proof completeness.
- Dependence semantics.
- Native PLN composition limitations.
- Computational cost.
- Availability of learning signals.

Do not implement strategic move selection during Cycle 12.

Recommend one of:

### Option A — Continue relational concept learning

If concepts remain insufficiently transferable.

### Option B — Introduce experimental strategic field comparison

If field dynamics and concept recognition are reliable enough.

### Option C — Revisit native PLN composition research

Only if new evidence materially changes the earlier no-go decision.

Provide an evidence-based recommendation.

---

# 29. Autonomous Execution Contract

Codex is authorized to:

- Inspect the repository.
- Make local source changes.
- Run native PLN experiments.
- Generate datasets.
- Train experimental models.
- Run tests and benchmarks.
- Produce reports and documentation.
- Create local commits.

Codex is not authorized to:

- Push to GitHub.
- Deploy external services.
- Modify upstream PLN repositories.
- Introduce new native PLN operators.
- Replace native PLN inference with custom probability calculations.
- Introduce deterministic production legality gates.
- Add conventional chess evaluation heuristics.
- Delete historical evidence.
- Weaken mandatory regression gates.
- Promote experimental strategic models into operational inference.

Complete all feasible packages in one consolidated execution.

Do not request approval after each milestone.

Make routine local implementation decisions independently.

Continue independent work when one experiment fails.

Stop only for essential blocking dependencies, external actions requiring authorization, or architectural decisions outside this brief.

---

# 30. Final Codex Report

The final response must include:

1. Starting commit.
2. Ending commit.
3. Working-tree status.
4. Commit list.
5. Work-package completion matrix.
6. Legal-move baseline comparisons.
7. En-passant promotion decision.
8. Field-interaction results.
9. Strategic concept results.
10. Transfer-learning results.
11. Counterfactual experiments.
12. Temporal evolution results.
13. Native PLN proof evidence.
14. Incremental-update parity.
15. Performance comparisons.
16. Regression test results.
17. Clean reproduction status.
18. Known limitations.
19. Cycle 13 readiness assessment.
20. Recommended next engineering priorities.

Distinguish:

- Verified native PLN derivations.
- Partial conditional inference.
- Host-side structural observations.
- Diagnostic field comparisons.
- Experimental concept hypotheses.
- Unsupported conclusions.

Do not claim strategic chess competence solely from concept recognition.

---

# 31. Final Objective

Cycle 12 must demonstrate that local probabilistic field relationships can support reusable higher-level strategic structures.

A pin should be represented through relative alignment, obstruction, and exposure.

A fork should be represented through multiple influence relationships.

A discovered attack should emerge from a change in obstruction and a newly supported attack relation.

An overloaded defender should be represented through competing defensive dependencies.

A trapped piece should be represented through constrained and uncertain mobility.

These concepts must remain transferable across board locations and piece configurations.

The system must preserve the distinction between structural observation, learned conditional knowledge, and genuine native PLN inference.

The long-term objective is not to memorize tactical patterns.

It is to construct a probabilistic relational intelligence in which strategic concepts arise from local interaction rules and can eventually support uncertainty-aware planning.

**Cycle 12 establishes the foundations of strategic understanding. Cycle 13 may begin investigating strategic decision-making only if the evidence supports that transition.**
