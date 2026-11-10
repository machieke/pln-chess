# PLN Chess — Cycle 11 Engineering Implementation Brief

## Probabilistic Relational Potential Fields, Temporal Completion, and Local Interaction Dynamics

**Repository:** https://github.com/machieke/pln-chess  
**Starting commit:** `fe9e28edc03184fee02ec535399768fd9d5883fa`  
**Accepted operational baseline:** C8-promotion-relative, with Cycle 10 temporal-evidence transport  
**Execution:** Consolidated autonomous engineering cycle  
**Delivery:** Implementation, tests, experiments, native proofs, benchmarks, documentation, and local commits  
**Authorization:** No GitHub push, external deployment, upstream PLN modification, or unapproved inference operators.

---

# 1. Mission

Cycle 11 introduces the first experimental probabilistic relational potential-field system.

The long-term objective is to develop a chess intelligence that learns from local interactions and derives global behavior through probabilistic logic.

The architecture should be conceptually closer to smoothed particle hydrodynamics (SPH) than to a conventional chess evaluation engine.

In SPH, particles interact through local relative relationships. The resulting dynamics emerge from these interactions without requiring each particle to learn an absolute global coordinate system.

Apply the same principle to chess.

A chess piece should possess reusable relational knowledge concerning:

- Its own movement possibilities.
- Other pieces in its relative neighborhood.
- Directional influence.
- Attack relationships.
- Defense relationships.
- Mobility.
- Obstruction.
- King exposure.
- Changes in those relationships after movement.

The model must not learn that a particular square is inherently good or bad.

Instead, it should learn how relationships between pieces change when a piece moves.

The primary research objective is:

> Demonstrate that probabilistic local interaction rules can produce explainable, transferable spatial influence fields, and that changes in these fields can be inferred for candidate moves without relying on absolute-coordinate evaluation tables.

Cycle 11 must not attempt to create a competitive chess engine.

It must establish the representational and inference foundations for future strategic reasoning.

---

# 2. Two Independent Engineering Tracks

## Track A — Legal-Move Completion

Preserve and improve the existing legal-move learner.

Priorities:

1. Resolve the two outstanding en-passant cases.
2. Investigate remaining adversarial abstentions.
3. Improve historical evidence transport.
4. Preserve native PLN proof provenance.
5. Maintain operational classification accuracy.
6. Preserve all established regression guarantees.

## Track B — Probabilistic Potential Fields

Introduce an experimental relational field subsystem.

Initial fields:

1. Attack potential.
2. Defense potential.
3. Mobility potential.
4. King-exposure potential.

The subsystem must support:

- Field construction from relative relationships.
- Probabilistic evidence.
- Native PLN inference.
- Candidate successor-state reasoning.
- Before/after field comparison.
- Locality and transfer experiments.
- Evidence-backed explanations.

The two tracks must remain architecturally independent.

Failure of experimental potential-field research must not degrade legal-move inference.

---

# 3. Starting Baseline

Cycle 10 reported:

| Metric | Result |
|---|---:|
| External positions | 1,308 |
| External source games | 150 |
| Frozen external test positions | 1,020 |
| FEN-only recall | 99.2645% |
| History-assisted recall | 99.9939% |
| FEN-only exact move sets | 793/1,020 |
| History-assisted exact move sets | 1,018/1,020 |
| New adversarial exact sets | 98/112 |
| Outstanding en-passant cases | 2 |

Additional findings:

- No observed false-legal classifications on acceptance cohorts.
- No observed false-illegal classifications on acceptance cohorts.
- No observed false-positive self-check classifications.
- Historical evidence recovered 238 legal-move abstentions.
- Native positive composition remains incomplete.
- The production native-composition extension remains unauthorized.

These are reported results.

Codex must reproduce and verify their provenance before modifying the implementation.

---

# 4. Architectural Invariants

The following requirements are mandatory.

1. All learned spatial relationships must remain piece-relative.
2. Learned knowledge must transfer across board translations where semantics are preserved.
3. Learned knowledge must not contain absolute-square constants.
4. Absolute board coordinates may be used for I/O, visualization, and environment state reconstruction.
5. Native PLN remains responsible for probabilistic inference and truth-value revision.
6. Do not implement substitute PLN truth-value formulas in Python.
7. Do not introduce deterministic chess-legality checks into production inference.
8. The reference chess oracle remains restricted to training, evaluation, and testing.
9. Preserve operational, strict, and experimental inference modes.
10. Preserve all native proof traces, evidence IDs, rule IDs, dependence groups, and model identities.
11. Distinguish PLN strength from confidence.
12. Do not present confidence as a calibrated probability without empirical validation.
13. Preserve unknown and incomplete inference states.
14. Do not introduce a new native PLN operator.
15. Do not activate the previously proposed composition extension.
16. Do not silently replace local probabilistic reasoning with conventional chess heuristics.
17. Preserve the accepted legal-move learner throughout Cycle 11.
18. Potential-field reasoning must be independently testable and removable.

---

# 5. Core Concept: Relational Potential Fields

A potential field is a representation of how an entity influences its environment.

For this project, a field must not be defined as a fixed numerical score attached to each absolute board square.

Instead, define it through relative relationships.

Conceptually:

    Piece P
       |
       +-- relative geometry
       |
       +-- local occupancy
       |
       +-- movement relationships
       |
       +-- attack relationships
       |
       +-- defense relationships
       |
       +-- king exposure
       |
       +-- probabilistic influence

The field associated with a piece may influence multiple relative locations and other pieces.

The influence depends on:

- Piece type.
- Relative direction.
- Relative distance.
- Intermediate occupancy.
- Destination occupancy.
- Piece allegiance.
- Learned movement relationships.
- Available evidence.
- Confidence in applicable relationships.

A field must remain interpretable.

Every supported influence must be traceable to its premises and native PLN derivations.

---

# 6. Mathematical and Epistemic Requirements

Do not assume that a potential field is automatically a scalar function.

Investigate at least three representations:

1. Relational graph of probabilistic influence.
2. Directional field over relative displacements.
3. Derived spatial projection for visualization.

The first two are candidate reasoning representations.

The third is a visualization or analysis view, not the primary knowledge representation.

For each representation, specify:

- Domain.
- Codomain.
- Truth-value semantics.
- Evidence semantics.
- Locality assumptions.
- Translation behavior.
- Symmetry behavior.
- Update behavior.
- Unknown-information handling.

Avoid arbitrary weighted sums.

For example, do not assume:

    strategic_score =
        3 * attack +
        2 * defense +
        1 * mobility

Such coefficients would introduce conventional handcoded evaluation heuristics.

If an experimental aggregate is needed, clearly label it as a diagnostic rather than a learned PLN conclusion.

Native PLN truth values must remain distinct from any visualization intensity or statistical summary.

Do not multiply or add strengths as if they were independent probabilities without a verified semantic justification.

---

# 7. Work Package C11-01 — Baseline Preservation

Verify the starting commit.

Record:

- Git state.
- Native PLN version.
- PeTTa runtime version.
- Dependency versions.
- Accepted model hash.
- Dataset hashes.
- Inference thresholds.
- Existing proof hashes.

Reproduce Cycle 10 acceptance results.

Preserve historical artifacts.

Create:

    artifacts/cycle11/baseline/

Include a machine-readable baseline manifest and reproduction receipt.

Do not overwrite previous-cycle reports.

---

# 8. Work Package C11-02 — En-Passant Completion

Investigate the two unresolved external en-passant cases.

For each case, reconstruct:

- Complete game history.
- Previous pawn movement.
- En-passant target.
- Relevant board state.
- Relative pawn relationships.
- Capture eligibility evidence.
- King-exposure evidence.
- Native PLN inference.
- Resulting abstention.

Determine whether the cause is:

- Missing historical evidence.
- Incorrect temporal transport.
- Missing local abstraction.
- Evidence dependence.
- Missing native inference.
- Incorrect observation completeness.

Implement justified corrections where feasible.

Do not add special-case FEN exceptions.

Require before/after native proof comparisons.

---

# 9. Work Package C11-03 — Adversarial Legality Completion

Reproduce the remaining adversarial and special-move abstentions.

Prioritize:

- Pins.
- Discovered attacks.
- Double checks.
- Check resolution.
- Multiple attackers.
- King exposure.
- Castling.
- En passant.
- Promotion interactions.

Create a complete unresolved-case inventory.

For each improvement:

- Preserve the original proof.
- Record the new proof.
- Identify changed evidence.
- Verify relative transfer.
- Run evidence-removal controls.
- Test independent structural variants.

Do not relax thresholds merely to eliminate abstentions.

---

# 10. Work Package C11-04 — Historical Evidence Robustness

Extend temporal evidence transport to handle:

- Missing historical events.
- Contradictory event claims.
- Duplicate events.
- Out-of-order event delivery.
- Partial PGN histories.
- Imported FEN metadata.
- Replayed complete histories.
- Conflicting provenance.

Distinguish:

1. Direct observations.
2. Trusted metadata.
3. Inferred history.
4. Unknown history.

Preserve event ordering and dependence groups.

A later contradictory event must not silently erase earlier evidence.

Implement deterministic replay and explicit conflict reporting.

---

# 11. Work Package C11-05 — Potential-Field Ontology

Design the initial relational ontology.

Candidate concepts include:

    Piece
    RelativeDirection
    RelativeDistance
    RelativeDisplacement
    RelativeRay
    IntermediateOccupancy
    DestinationOccupancy
    AttackPotential
    DefensePotential
    MobilityPotential
    KingExposurePotential
    CandidateSuccessor
    InfluenceRelation
    InfluenceChange
    SupportingEvidence
    FieldUncertainty

These are conceptual predicate names, not authorization to introduce new PLN inference operators.

Map the concepts to the existing MeTTa/PLN representation.

Preserve typed relations.

Avoid embedding complete board configurations into single opaque hypothesis keys.

Prefer reusable local propositions.

Document the ontology in:

    docs/cycle11/potential-field-ontology.md

---

# 12. Work Package C11-06 — Attack Potential

Implement the first experimental attack-potential field.

The objective is to represent probabilistic relationships such as:

    Piece P may attack relative target T
    under relational context C

The field must account for:

- Piece movement geometry.
- Direction.
- Distance.
- Obstruction.
- Destination occupancy.
- Piece allegiance.
- Learned attack evidence.

Separate:

- Geometric reachability.
- Attack potential.
- Legal capture eligibility.
- Actual legal move classification.

These are not equivalent.

For example, a pinned piece may geometrically attack a square while being unable to move there legally.

The attack field must not collapse these distinctions.

Use native PLN inference wherever supported.

If an inference requires unsupported conjunction, preserve partial evidence and report the missing composition.

---

# 13. Work Package C11-07 — Defense Potential

Implement a relational defense-potential field.

A piece may defend another piece or a relative location.

Distinguish:

- Geometric defense.
- Potential recapture.
- Legal defensive action.
- Defense constrained by king exposure.
- Defense obstructed by another piece.

Do not assume every geometrically defended piece can be recaptured legally.

Represent uncertainty explicitly.

Create controlled examples involving:

- Defended pawns.
- Defended minor pieces.
- Rook batteries.
- Pinned defenders.
- Multiple defenders.
- Discovered defenses.
- Defenders that cannot legally move.

Require native proof traces for supported conclusions.

---

# 14. Work Package C11-08 — Mobility Potential

Implement probabilistic mobility relationships.

Mobility should represent a piece's available or potentially available movement relationships.

Distinguish:

1. Geometric mobility.
2. Occupancy-constrained mobility.
3. Legal-move mobility.
4. Uncertain mobility.

Do not introduce a fixed strategic reward for mobility.

The initial objective is descriptive.

For example:

    A rook has several possible relative rays.
    Some are obstructed.
    Others are supported.
    Some remain unknown.

The field should express these relationships and their evidence.

A projected mobility count may be produced for diagnostics, but must distinguish supported, contradicted, and unknown candidate moves.

Do not convert unknown moves into zero mobility without disclosure.

---

# 15. Work Package C11-09 — King-Exposure Potential

Implement a relational field describing potential king exposure.

Include:

- Direct attack relationships.
- Open rays toward the king.
- Pinned defenders.
- Discovered attacks.
- Candidate moves that expose the king.
- Candidate moves that remove exposure.
- Multiple simultaneous attackers.

Reuse existing native negative-proof capabilities.

Do not invent a deterministic king-safety gate.

The field must preserve the distinction between:

- Evidence supporting exposure.
- Evidence contradicting exposure.
- Missing exposure evidence.

Absence of a known attack is not automatically proof of safety.

---

# 16. Work Package C11-10 — Locality and Spatial Transfer

Test whether potential-field knowledge transfers across board locations.

Required transformations:

- Translation.
- File reflection where valid.
- Color-relative orientation changes.
- Piece-ID renaming.
- Irrelevant distant-piece changes.

Test both invariance and sensitivity.

Expected invariance:

A local rook obstruction relationship should remain valid after a translation preserving the relevant context.

Expected sensitivity:

Adding an intervening blocker should change the relevant ray influence.

Expected locality:

Changing an unrelated distant piece should not alter an influence relation unless that piece participates in a relevant dependency.

Do not impose a fixed geometric neighborhood radius that incorrectly excludes long-range rook, bishop, or queen interactions.

Locality must be defined through relational dependencies, not merely Euclidean distance.

Deliver at least 20 controlled transformation experiments.

---

# 17. Work Package C11-11 — Candidate Successor-State Fields

Extend the experimental subsystem to construct relational fields for candidate successor states.

For a position S and candidate move M, produce:

    FieldBefore(S)

    FieldAfter(S, M)

These are conceptual interfaces.

The successor-state constructor may apply structural board transformations.

It must not independently determine legal move classification.

Reuse the operational legality learner for candidate classification.

The field subsystem should accept:

- Supported legal candidates.
- Unknown candidates.
- Contradicted candidates.

Mark their status explicitly.

Do not treat an unknown candidate as a verified legal move.

The field calculation must preserve the provenance of the candidate state.

---

# 18. Work Package C11-12 — Potential-Field Differences

Introduce a structured comparison between pre-move and post-move fields.

The principal output is:

    DeltaField(S, M)

The difference should identify relational changes such as:

- New attack relationship.
- Removed attack relationship.
- New defense relationship.
- Lost defense relationship.
- Increased mobility possibilities.
- Reduced mobility possibilities.
- Newly exposed king.
- Removed king exposure.
- Newly opened ray.
- Newly obstructed ray.

Do not initially reduce all changes to one scalar score.

Represent changes as a typed collection of probabilistic relational differences.

Each difference must include:

- Relation type.
- Before truth value.
- After truth value.
- Evidence provenance.
- Applicable native rules.
- Proof status.
- Confidence limitations.

A numeric difference between PLN strengths may be displayed as a descriptive diagnostic, but must not be interpreted automatically as a probabilistic truth value for the change proposition.

Where native PLN cannot derive a change proposition, label the comparison as a host-side diagnostic.

---

# 19. Work Package C11-13 — Worked Relational Examples

Create a reproducible library of examples.

At minimum include:

### Example A — Rook obstruction

A rook has an obstructed ray.

Moving the blocker changes the rook's attack and mobility relationships.

### Example B — Bishop diagonal

A bishop's diagonal influence changes after a pawn moves.

### Example C — Knight relocation

A knight changes the set of relative targets it influences.

### Example D — Pinned defender

A defender geometrically protects another piece but cannot legally move without exposing its king.

### Example E — Discovered attack

Moving one piece opens a sliding-piece attack relationship.

### Example F — King exposure

A candidate move creates a new attack relationship toward the moving side's king.

### Example G — Multiple defenders

Two pieces independently support a defended location.

Do not automatically aggregate their evidence as independent.

### Example H — Unknown observation

Incomplete occupancy information produces an uncertain field.

### Example I — Promotion

A pawn promotion changes piece identity and its subsequent potential field.

### Example J — En passant

An en-passant capture removes a pawn from a square other than the destination and changes relevant ray relationships.

Every example must contain:

- Initial FEN.
- Candidate move.
- Relative observations.
- Before field.
- After field.
- Field differences.
- Native truth values.
- Proof provenance.
- Reference evaluation where applicable.

---

# 20. Work Package C11-14 — Field Learning Experiments

Investigate whether the new field relationships can learn from evidence.

Do not merely construct deterministic geometric maps and label them probabilistic.

Use the existing native PLN learning and revision infrastructure.

Create independent training and holdout examples.

Evaluate:

- Attack relation learning.
- Defense relation learning.
- Mobility relation learning.
- Exposure relation learning.

Include positive and negative evidence.

Test transfer to unseen relative configurations.

Distinguish:

1. Seeded structural priors.
2. Learned conditional knowledge.
3. Native PLN derivations.
4. Host-computed observations.
5. Visualization-only projections.

The final report must state which field capabilities were learned and which were supplied by the ontology or candidate grammar.

---

# 21. Work Package C11-15 — Field Evaluation

Create a dedicated evaluation framework.

Do not evaluate potential fields solely through legal-move accuracy.

Measure:

- Relational prediction precision.
- Relational prediction recall.
- Abstention rate.
- Transfer accuracy.
- Evidence-removal sensitivity.
- Transformation invariance.
- Counterfactual sensitivity.
- Proof completeness.
- Calibration diagnostics.
- Runtime cost.

Use an evaluation-only reference engine to label relevant attack and defense relations where appropriate.

Do not use reference labels during production field inference.

Avoid conflating attack maps with legal move sets.

Report each field family separately.

Do not claim strategic competence from accurate attack-field prediction.

---

# 22. Work Package C11-16 — Interactive Field Inspector

Extend the existing inspector with an experimental potential-field view.

The interface should allow:

1. Selecting a board position.
2. Selecting a piece.
3. Selecting a field type.
4. Inspecting relative influence.
5. Selecting a candidate move.
6. Viewing the successor state.
7. Comparing before and after fields.
8. Inspecting native proof traces.

Suggested field views:

- Attack.
- Defense.
- Mobility.
- King exposure.
- Field differences.

A board overlay may use absolute coordinates for visualization.

However, the underlying learned representation must remain relative.

Display:

- Strength.
- Confidence.
- Classification.
- Evidence IDs.
- Rule IDs.
- Proof status.
- Unknown relations.

Do not present visualization intensity as calibrated probability unless justified.

Preserve desktop and mobile compatibility.

---

# 23. Work Package C11-17 — Performance and Incremental Updates

Potential-field inference may be computationally expensive.

Investigate incremental updates based on changed relational dependencies.

For a candidate move, identify:

- Moved piece.
- Origin square.
- Destination square.
- Captured piece, if any.
- Changed occupancy.
- Affected rays.
- Affected attack relations.
- Affected defense relations.
- Affected king-exposure relations.

Avoid recomputing unrelated field relationships where exact dependency tracking makes reuse safe.

Preserve proof identity.

Benchmark:

- Full field construction.
- Incremental field update.
- Single candidate.
- Multiple candidates.
- Cold execution.
- Warm execution.
- Cache effectiveness.

Report:

- Native invocation counts.
- Grounded atoms.
- Runtime.
- Peak memory.
- Proof size.
- Cache hits.
- Cache invalidations.

Do not use unsafe caching that reuses stale evidence after a move.

---

# 24. Work Package C11-18 — Operational Regression Gates

The legal-move learner must remain stable.

Mandatory gates:

1. Cycle 10 accepted operational results remain reproducible.
2. No new false-legal classifications on established acceptance cohorts.
3. No new false-illegal classifications on established acceptance cohorts.
4. No new self-check false positives.
5. All 287 established negative evidence-removal controls pass.
6. Native proof and cache parity remain valid.
7. No production chess-oracle dependency.
8. No new PLN inference operator.
9. No silent truth-value formula changes.
10. Historical evidence provenance remains intact.
11. Clean-checkout bootstrap succeeds.
12. All automated tests pass.
13. Existing APIs remain compatible or have documented migrations.
14. Potential-field experiments do not alter operational classifications.

If an experimental field model fails, preserve it as an isolated research artifact.

Do not replace the accepted legal-move learner.

---

# 25. Work Package C11-19 — Research Acceptance Criteria

The following are proposed research targets.

## Track A

- Resolve both outstanding en-passant cases where evidence permits.
- Improve adversarial exact-set accuracy.
- Preserve zero observed false-legal and false-illegal classifications on acceptance cohorts.
- Demonstrate robust temporal replay under missing and contradictory evidence.

## Track B

- Implement all four initial field families.
- Demonstrate at least ten complete before/after field comparisons.
- Demonstrate at least twenty spatial transformation controls.
- Demonstrate at least five field-learning transfers to unseen configurations.
- Provide native proof traces for supported relational conclusions.
- Preserve unknown classifications when evidence is insufficient.
- Demonstrate at least one exact incremental-update optimization.
- Provide an interactive inspector.

These are research targets, not permission to fabricate inference results.

If native PLN limitations prevent a field from being fully inferred, deliver the strongest defensible partial representation and document the gap.

---

# 26. Work Package C11-20 — Consolidated Delivery

Produce:

    docs/cycle11/engineering-report.md
    docs/cycle11/package-matrix.md
    docs/cycle11/legal-completion.md
    docs/cycle11/temporal-robustness.md
    docs/cycle11/potential-field-ontology.md
    docs/cycle11/attack-field.md
    docs/cycle11/defense-field.md
    docs/cycle11/mobility-field.md
    docs/cycle11/king-exposure-field.md
    docs/cycle11/field-differences.md
    docs/cycle11/field-learning.md
    docs/cycle11/field-evaluation.md
    docs/cycle11/performance.md
    docs/cycle11/strategic-roadmap.md
    docs/cycle11/reproduction.md

Required artifacts:

- Baseline manifests.
- Legal-move regression reports.
- Temporal evidence tests.
- Potential-field model checkpoints.
- Relative ontology manifests.
- Native proof traces.
- Field-difference examples.
- Transfer experiments.
- Evidence-removal controls.
- Performance benchmarks.
- Browser verification.
- Test logs.
- Reproduction receipts.
- Artifact hashes.

Provide a complete work-package status matrix.

Do not claim a package complete without supporting evidence.

---

# 27. Strategic Architecture Roadmap

The final report must explain how the potential-field subsystem could support future chess intelligence.

A future architecture may consist of:

    Board observations
          |
          v
    Relative spatial ontology
          |
          v
    Learned PLN movement relations
          |
          +----------------------+
          |                      |
          v                      v
    Legal-move beliefs     Potential-field beliefs
          |                      |
          +----------+-----------+
                     |
                     v
             Candidate successor
                     |
                     v
             Field transformation
                     |
                     v
             Probabilistic consequences
                     |
                     v
             Future strategic reasoning

Do not implement the final strategic reasoning layer in Cycle 11.

The roadmap should identify the requirements for:

- Learned strategic concepts.
- Probabilistic field interactions.
- Field propagation.
- Temporal planning.
- Uncertainty-aware move comparison.
- Experience-based learning.
- Long-term strategic memory.
- Native PLN composition.

The roadmap must explicitly identify which requirements are already supported by verified native PLN rules and which remain research problems.

---

# 28. Autonomous Execution Contract

Codex is authorized to:

- Inspect the repository.
- Make local source changes.
- Implement experimental potential-field modules.
- Run native PLN inference experiments.
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
- Promote an experimental model without passing acceptance requirements.

Complete all feasible work packages in one consolidated run.

Do not request approval after each milestone.

Make routine implementation decisions independently.

Continue independent work when one research experiment fails.

Stop only for essential blocking dependencies, external actions requiring authorization, or architectural changes outside this brief.

---

# 29. Final Codex Report

The final response must include:

1. Starting commit.
2. Ending commit.
3. Working-tree status.
4. Commit list.
5. Work-package completion matrix.
6. Legal-move baseline comparisons.
7. En-passant outcomes.
8. Adversarial outcomes.
9. Temporal evidence results.
10. Potential-field ontology summary.
11. Attack-field results.
12. Defense-field results.
13. Mobility-field results.
14. King-exposure results.
15. Before/after field demonstrations.
16. Transfer-learning results.
17. Native PLN proof evidence.
18. Performance comparisons.
19. Regression test results.
20. Clean reproduction status.
21. Known limitations.
22. Strategic-readiness assessment.
23. Recommended Cycle 12 priorities.

Distinguish:

- Verified native PLN derivations.
- Partial conditional inference.
- Host-side structural observations.
- Diagnostic calculations.
- Experimental hypotheses.
- Unsupported conclusions.

Do not claim strategic chess competence based solely on field construction.

---

# 30. Final Objective

Cycle 11 must establish the first working experimental foundation for probabilistic relational potential fields.

The system should be able to explain how local relationships change when a chess piece moves.

A rook moving away from a file may remove one defensive relationship while opening another attack relationship.

A knight relocating may create new local threats while abandoning previous coverage.

A pawn moving may open a bishop diagonal.

A pinned piece may possess geometric influence without corresponding legal mobility.

These effects must be represented through reusable, relative, evidence-backed relationships.

The central principle remains:

**The chessboard is the environment, not the coordinate system of the intelligence.**

The desired intelligence should emerge from transferable local interaction rules, probabilistic evidence, and relational reasoning.

Cycle 11 is the transition from learning permitted movement to learning the probabilistic consequences of movement.

It is not yet the transition to selecting optimal moves.
