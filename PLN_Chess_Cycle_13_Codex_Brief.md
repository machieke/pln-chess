# PLN Chess — Cycle 13 Engineering Implementation Brief

## Probabilistic Strategic Preference Learning, Relational Move Comparison, and Bounded Temporal Reasoning

**Repository:** https://github.com/machieke/pln-chess  
**Starting commit:** `b000898a0a1f46e556f161982f2c0e6d3944c322`  
**Accepted legal-move baseline:** Cycle 12 promoted en-passant checkpoint  
**Execution:** Consolidated autonomous engineering cycle  
**Delivery:** Source code, experiments, native PLN proofs, tests, benchmarks, reports, and local commits  
**Authorization:** No GitHub push, external deployment, upstream PLN modifications, or unapproved inference operators.

---

# 1. Mission

Cycle 13 must establish the first experimental strategic decision-making capability in PLN Chess.

The system currently supports:

- Piece-relative movement knowledge.
- Probabilistic legal-move inference.
- Native PLN revision and conditional inference.
- Attack, defense, mobility, and king-exposure fields.
- Before/after relational field comparisons.
- Incremental field updates.
- Strategic concept representations.
- Temporal field evolution.
- Evidence provenance and native proof inspection.

Cycle 13 must investigate whether these capabilities can support learned preferences between candidate moves.

The principal research question is:

> Can a probabilistic logic network learn transferable preferences between chess moves from their relative relational consequences, without relying on absolute board coordinates, conventional chess evaluation scores, or unrestricted search?

The objective is not to build a competitive chess engine.

The objective is to demonstrate evidence-based strategic choice.

---

# 2. Engineering Tracks

Cycle 13 consists of five coordinated tracks.

## Track A — Strategic Preference Learning

Learn probabilistic relationships between relational field changes and observed move preferences.

## Track B — Candidate Move Comparison

Compare candidate moves using native PLN beliefs while preserving uncertainty and proof provenance.

## Track C — Bounded Temporal Reasoning

Investigate two-ply and three-ply relational consequences without unrestricted chess-tree search.

## Track D — Strategic Concept Generalization

Resolve remaining fork abstentions and expand independent tactical transfer evaluation.

## Track E — Operational Preservation

Preserve the accepted legal-move learner, historical evidence, field models, and all regression guarantees.

Experimental strategic modules must remain isolated from operational legality inference.

---

# 3. Starting Baseline

Cycle 12 reported:

- 20/20 engineering packages delivered.
- 534 passing tests.
- 303 correct classified concept examples from 306.
- Three fork abstentions.
- No incorrect classified concept answers.
- 144/144 pin classifications.
- 21/24 fork classifications.
- 48/48 discovered-attack classifications.
- 48/48 discovered-defense classifications.
- 38 spatial transfer controls.
- 90 counterfactual transformations.
- Exact full/incremental field parity.
- 12 temporal sequences covering 50 supplied moves and 62 states.

The accepted legal model achieved:

| Cohort | Exact legal-move sets |
|---|---:|
| External FEN-only | 793/1,020 |
| External history-assisted | 1,020/1,020 |
| C9 adversarial | 112/128 |
| C9 special moves | 71/80 |
| C10 synthetic adversarial | 98/112 |

History-assisted external recall reached 100% on the evaluated cohort.

These are reported measurements, not universal correctness guarantees.

Codex must verify the baseline before development.

---

# 4. Architectural Invariants

The following constraints are mandatory.

1. All learned chess knowledge must remain piece-relative.
2. Absolute coordinates may be used for board I/O, state reconstruction, and visualization, but not as learned strategic rule constants.
3. Native PLN must perform probabilistic inference and truth-value revision.
4. Do not replace native PLN formulas with custom host-language probability calculations.
5. Do not introduce deterministic legality gates into production inference.
6. Reference chess engines may be used for training labels, evaluation, and testing only.
7. Preserve operational, strict, and experimental inference modes.
8. Preserve evidence IDs, dependence groups, rule IDs, native expressions, and proof graphs.
9. Distinguish raw PLN strength, PLN confidence, and empirically calibrated probabilities.
10. Preserve unknown and incomplete inference states.
11. Do not claim complete positive legality proofs where only partial conditional evidence exists.
12. Do not introduce new native PLN inference operators.
13. Do not activate the proposed multi-premise composition extension.
14. Do not implement conventional chess-engine evaluation functions, material scores, or piece-square tables.
15. Preserve all historical datasets, checkpoints, and proof artifacts.
16. Experimental strategic reasoning must not alter operational legality classifications.
17. Do not present host-computed strategic comparisons as native PLN proofs.
18. Every strategic preference must disclose its evidential and inferential basis.

---

# 5. Core Research Principle

Strategic preferences should be learned from relative relational consequences.

For example, consider two candidate moves:

Move A:

- Opens an attack relationship.
- Removes a defensive relationship.
- Creates potential king exposure.

Move B:

- Preserves defensive relationships.
- Changes mobility.
- Avoids creating a known exposure relationship.

The system should not automatically assign arbitrary numeric weights to these effects.

Instead, it should investigate whether observed outcomes support reusable conditional beliefs such as:

    RelativeFieldChangePattern
        -> PreferredMoveRelation

The pattern must not encode absolute board coordinates.

The preference must be supported by evidence.

A learned preference is not automatically a complete strategic proof.

---

# 6. Work Package C13-01 — Baseline Preservation

Verify the starting repository state.

Record:

- Git commit.
- Working-tree status.
- Native PLN version.
- PeTTa runtime version.
- Dependency hashes.
- Accepted legal checkpoint.
- Field model hashes.
- Strategic concept model hashes.
- Dataset hashes.
- Inference thresholds.

Reproduce Cycle 12 acceptance results.

Preserve historical artifacts.

Create:

    artifacts/cycle13/baseline/

Deliver:

- Baseline manifest.
- Reproduction receipt.
- Proof parity report.
- Model identity report.
- Dataset identity report.

Do not overwrite previous-cycle evidence.

---

# 7. Work Package C13-02 — Strategic Preference Ontology

Introduce a typed ontology for move preference.

Candidate concepts include:

    CandidateMove
    CandidateSuccessor
    RelativeFieldChange
    AttackChange
    DefenseChange
    MobilityChange
    ExposureChange
    StrategicConceptChange
    MovePreference
    PreferenceEvidence
    PreferenceUncertainty
    PreferenceComparison

Specify:

- Predicate signatures.
- Argument types.
- Relative spatial semantics.
- Temporal semantics.
- Evidence provenance.
- Truth-value semantics.
- Unknown-state behavior.

Distinguish:

1. Observed field changes.
2. Learned conditional preference.
3. Native PLN-derived preference.
4. Host-side comparison.
5. Unsupported preference.

Avoid opaque full-position identifiers as learned hypothesis keys.

Deliver:

    docs/cycle13/preference-ontology.md

---

# 8. Work Package C13-03 — Preference Evidence Model

Design an append-only evidence model for move preferences.

Each observation must record:

- Source position.
- Candidate moves.
- Relative field descriptors.
- Evidence source.
- Preference label.
- Dependence group.
- Game provenance.
- Temporal context.
- Model version.
- Native runtime version.

Support:

- Preferred A over B.
- Preferred B over A.
- No demonstrated preference.
- Unknown or insufficient evidence.

Do not force a binary preference when evidence does not justify one.

Distinguish preference evidence from legal-move evidence.

Do not contaminate the accepted legality checkpoint.

---

# 9. Work Package C13-04 — Preference Training Curriculum

Construct a reproducible preference-learning dataset.

Include at least 100 independent move pairs.

Prefer a larger corpus where practical.

Cover:

- Attack creation.
- Defense preservation.
- Defender removal.
- Mobility changes.
- King exposure.
- Pins.
- Forks.
- Discovered attacks.
- Promotion consequences.
- Tactical threat removal.
- Quiet positional moves.
- Ambiguous alternatives.

Use independent structural families.

Prevent leakage through:

- Board translations.
- Reflections.
- Repeated game positions.
- Equivalent tactical motifs.
- Duplicate move-pair labels.

Training labels may come from:

- Annotated games.
- Human preference judgments.
- Reference-engine comparisons.
- Observed continuation outcomes.

All labels must disclose their source.

Reference-engine evaluations are training or evaluation evidence, not native PLN conclusions.

Avoid silently converting centipawn scores into hardcoded strategic utility.

---

# 10. Work Package C13-05 — Native PLN Preference Learning

Use existing verified native PLN operators to learn conditional preference beliefs.

Investigate:

    RelativeFieldChangePattern
        -> Preference(A, B)

Use native revision for independent evidence.

Use native modus ponens for supported conditional inference.

Use native negation where appropriate.

Preserve evidence dependence.

Do not invent conjunction.

If multiple relational changes cannot be composed natively, distinguish:

- Independently supported changes.
- Host-assembled categorical descriptor.
- Learned conditional preference.
- Native inference result.

Report exactly what the PLN learned.

---

# 11. Work Package C13-06 — Pairwise Move Comparison

Implement an experimental pairwise comparison API.

Conceptual interface:

    compare_moves(position, move_a, move_b)

Return:

- Move A legality belief.
- Move B legality belief.
- Before/after fields.
- Relative field changes.
- Relevant strategic concepts.
- Preference belief.
- Raw PLN truth value.
- Evidence provenance.
- Proof status.
- Unknown relationships.

Do not force a winner.

Support:

- A preferred.
- B preferred.
- Indeterminate.
- Incomplete.

The comparison must not rely on conventional material evaluation.

Keep the API separate from operational legal-move inference.

---

# 12. Work Package C13-07 — Preference Symmetry and Consistency

Investigate consistency properties.

For a pair A and B:

- Preference(A, B) should be examined alongside Preference(B, A).
- Contradictory evidence must remain inspectable.
- Reversing pair order must not silently alter evidence semantics.
- Duplicate evidence must not increase confidence improperly.

Do not assume perfect transitivity.

A preference between A and B and another between B and C does not automatically establish A over C.

Any transitive inference must be justified through verified native PLN rules and explicit assumptions.

Create counterexamples for inconsistent preferences.

---

# 13. Work Package C13-08 — Transferable Preference Motifs

Train preferences on one structural configuration.

Evaluate them on unseen configurations sharing the same relative relational consequences.

Examples:

- Rook attack creation transferred across files.
- Bishop diagonal opening transferred across locations.
- Knight fork creation transferred across colors.
- Defensive preservation transferred across piece identities.
- King-exposure avoidance transferred across positions.

Require at least ten inspectable transfer demonstrations.

Each demonstration must include:

- Training evidence.
- Held-out configuration.
- Relative descriptors.
- Native inference expression.
- Raw truth value.
- Rule IDs.
- Evidence IDs.
- Proof graph.
- Reference preference label.

No exact-context memorization.

---

# 14. Work Package C13-09 — Fork Abstention Resolution

Investigate the three remaining Cycle 12 fork abstentions.

Determine whether they result from:

- Missing evidence.
- Overly specific abstractions.
- Multi-target composition limitations.
- Incorrect dependence grouping.
- Confidence selection.
- Incomplete relational observations.

Implement justified improvements.

Do not hardcode fork recognition.

Preserve all previously correct concept classifications.

Require independent counterfactual and transformation tests.

---

# 15. Work Package C13-10 — Strategic Concept Robustness

Expand tactical concept evaluation.

Include:

- Pins.
- Forks.
- Discovered attacks.
- Discovered defenses.
- Multiple attackers.
- Overloaded defenders.
- Trapped pieces.
- Threat removal.

Use independent external tactical positions where available.

Separate:

- Structural candidates.
- Learned conditional concepts.
- Native-derived conclusions.

Do not claim complete strategic understanding from partial concept classifications.

---

# 16. Work Package C13-11 — Two-Ply Relational Reasoning

Implement bounded two-ply consequence analysis.

Conceptually:

    S0
      |
      +-- Candidate move A
              |
              +-- Opponent response R
                      |
                      +-- Resulting relational field

The purpose is to inspect how an opponent response changes field relationships.

Do not implement unrestricted minimax or alpha-beta search.

Use a small bounded set of candidate responses.

Candidate selection must be explicit and reproducible.

Do not claim exhaustive opponent-response coverage unless all responses are evaluated.

Preserve uncertainty from the legal-move learner.

---

# 17. Work Package C13-12 — Three-Ply Relational Reasoning

Extend the experiment to three plies.

Conceptually:

    Our move
       |
       v
    Opponent response
       |
       v
    Our continuation
       |
       v
    Relational consequences

The objective is temporal explanation, not optimal move search.

Use bounded workloads.

Track:

- Attack creation.
- Attack removal.
- Defense changes.
- Mobility changes.
- King exposure.
- Concept persistence.
- Concept disappearance.

Do not reduce the sequence to a handcoded scalar score.

Preserve proof provenance at each state.

---

# 18. Work Package C13-13 — Temporal Preference Evidence

Investigate whether preference beliefs remain stable after opponent responses.

For example:

- A move appears favorable because it creates an attack.
- The opponent can immediately remove that attack.
- The preference should reflect the observed continuation evidence.

Distinguish:

1. Immediate field consequences.
2. Continuation-dependent consequences.
3. Learned preference evidence.
4. Unknown future responses.

Do not treat an unexamined response as impossible.

Do not assume that a locally favorable field change guarantees a favorable outcome.

---

# 19. Work Package C13-14 — Preference Evaluation

Evaluate pairwise preferences separately from legal-move accuracy.

Metrics:

- Pairwise accuracy.
- Precision.
- Recall.
- Abstention.
- Contradiction rate.
- Transfer accuracy.
- Calibration.
- Evidence-removal sensitivity.
- Proof completeness.

Report separately for:

- Training motifs.
- Held-out structural families.
- Independent games.
- Tactical positions.
- Quiet positional positions.
- Ambiguous move pairs.

Use bootstrap uncertainty intervals where appropriate.

Avoid treating correlated pairs from the same position as independent observations.

---

# 20. Work Package C13-15 — Preference Calibration

Evaluate raw PLN preference strength and confidence.

Do not interpret confidence directly as probability of strategic correctness.

Investigate:

- Reliability diagrams.
- Brier score.
- Expected calibration error.
- Selective risk.
- Coverage versus accuracy.
- Dependence on evidence volume.

Calibration remains diagnostic.

It must not silently replace native PLN inference.

Report distribution-shift behavior.

---

# 21. Work Package C13-16 — Preference Evidence Ablations

Run controlled ablations.

Examples:

- Attack changes only.
- Defense changes only.
- Mobility changes only.
- Exposure changes only.
- No strategic concept evidence.
- No temporal continuation.
- No dependence handling.
- Weaker relative abstraction.
- Full relational descriptor.

Determine which evidence families contribute to predictive performance.

Do not interpret correlated improvements as proof of causal importance without controls.

Preserve native proof traces.

---

# 22. Work Package C13-17 — Interactive Preference Inspector

Extend the existing inspector.

Allow users to:

1. Select a position.
2. Select two candidate moves.
3. Compare legality beliefs.
4. Compare field changes.
5. Inspect strategic concepts.
6. View preference truth values.
7. Inspect evidence provenance.
8. Explore bounded continuations.

Display:

- Preferred move, if supported.
- Indeterminate comparison.
- Native proof status.
- Raw strength.
- Raw confidence.
- Evidence IDs.
- Rule IDs.
- Temporal context.
- Unknown relationships.

Do not display a preference as certain merely because its strength is high.

Preserve desktop and mobile behavior.

---

# 23. Work Package C13-18 — Performance and Incremental Updates

Benchmark:

- Single preference comparison.
- Multiple candidate comparisons.
- Two-ply analysis.
- Three-ply analysis.
- Cold inference.
- Warm inference.
- Full field recomputation.
- Incremental field updates.

Report:

- Runtime.
- Native invocation counts.
- Grounded atoms.
- Cache hits.
- Peak memory.
- Proof size.
- Truncation rate.
- Timeout rate.

Preserve exact proof parity.

Do not reuse stale evidence after hypothetical moves.

---

# 24. Work Package C13-19 — Operational Regression Gates

Mandatory requirements:

1. Accepted legal-move results remain reproducible.
2. No new false-legal classifications on established acceptance cohorts.
3. No new false-illegal classifications.
4. No new self-check false positives.
5. All 287 negative evidence-removal controls pass.
6. Native proof and cache parity remain valid.
7. No production chess-oracle dependency.
8. No new native PLN operator.
9. No silent truth-value formula changes.
10. Historical evidence provenance remains intact.
11. Strategic concept baselines remain reproducible.
12. Clean-checkout bootstrap succeeds.
13. All automated tests pass.
14. Existing APIs remain compatible or have documented migrations.
15. Experimental preferences do not alter operational legality.

If preference learning fails, preserve the accepted operational system.

Do not promote strategic preferences into production decision-making during Cycle 13.

---

# 25. Work Package C13-20 — Consolidated Delivery

Produce:

    docs/cycle13/engineering-report.md
    docs/cycle13/package-matrix.md
    docs/cycle13/preference-ontology.md
    docs/cycle13/preference-evidence.md
    docs/cycle13/preference-learning.md
    docs/cycle13/pairwise-comparison.md
    docs/cycle13/preference-transfer.md
    docs/cycle13/fork-resolution.md
    docs/cycle13/concept-robustness.md
    docs/cycle13/two-ply.md
    docs/cycle13/three-ply.md
    docs/cycle13/temporal-preferences.md
    docs/cycle13/calibration.md
    docs/cycle13/ablations.md
    docs/cycle13/performance.md
    docs/cycle13/reproduction.md

Required artifacts:

- Baseline manifests.
- Preference datasets.
- Relative descriptor manifests.
- Native proof traces.
- Evidence ledgers.
- Model checkpoints.
- Transfer experiments.
- Counterfactual controls.
- Two-ply and three-ply examples.
- Calibration reports.
- Ablation results.
- Benchmarks.
- Browser verification.
- Test logs.
- Reproduction receipts.
- Artifact hashes.

Provide a complete work-package status matrix.

---

# 26. Research Acceptance Targets

These are research objectives, not guarantees.

## Preference Learning

- At least 100 independent move pairs.
- At least ten transferable preference demonstrations.
- Native PLN revision and inference.
- Explicit evidence provenance.
- No hardcoded strategic evaluation scores.

## Strategic Concepts

- Investigate all three fork abstentions.
- Preserve previous correct concept classifications.
- Expand independent tactical evaluation.

## Temporal Reasoning

- At least ten two-ply demonstrations.
- At least ten three-ply demonstrations.
- Explainable relational consequences.
- Preserved uncertainty and provenance.

## Operational Preservation

- All established legal-move regression gates pass.
- No new false-legal or false-illegal classifications.
- No unapproved native PLN operators.
- No conventional chess-engine evaluation function.

---

# 27. Native PLN Research Boundary

The existing verified native PLN implementation supports selected inference operators including:

- Modus ponens.
- Revision.
- Negation.
- Deduction.
- Induction.
- Inheritance.
- Evidence choice.

General native conjunction introduction remains unsupported in the audited runtime.

Do not fabricate multi-premise proofs.

Where a preference depends on multiple relational changes, distinguish:

1. Independently supported field changes.
2. Host-assembled relative descriptor.
3. Learned conditional preference.
4. Native PLN-derived conclusion.
5. Unsupported strategic conclusion.

A learned preference over a supplied composite descriptor is not equivalent to independently deriving that descriptor through native PLN.

Preserve this distinction in all reports.

---

# 28. Cycle 14 Readiness Assessment

The final report must determine whether the system is ready for experimental move selection.

Evaluate:

- Preference transfer.
- Pairwise consistency.
- Calibration.
- Temporal stability.
- Strategic concept robustness.
- Evidence dependence.
- Native proof completeness.
- Computational cost.
- Operational safety.

Recommend one of:

### Option A — Continue preference learning

If generalization remains insufficient.

### Option B — Introduce bounded experimental move selection

If learned preferences are reliable enough.

### Option C — Revisit native PLN composition research

Only if new evidence materially changes the existing no-go decision.

Do not implement full move selection during Cycle 13.

---

# 29. Autonomous Execution Contract

Codex is authorized to:

- Inspect the repository.
- Make local source changes.
- Run native PLN experiments.
- Generate datasets.
- Train experimental preference models.
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
- Promote experimental preference models into operational inference.

Complete all feasible packages in one consolidated execution.

Do not request approval after each milestone.

Make routine implementation decisions independently.

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
7. Preference-learning results.
8. Pairwise comparison results.
9. Transfer-learning results.
10. Fork-abstention outcomes.
11. Strategic concept evaluation.
12. Two-ply and three-ply demonstrations.
13. Temporal preference results.
14. Native PLN proof evidence.
15. Calibration findings.
16. Ablation results.
17. Performance comparisons.
18. Regression test results.
19. Clean reproduction status.
20. Known limitations.
21. Cycle 14 readiness assessment.
22. Recommended next engineering priorities.

Distinguish:

- Verified native PLN derivations.
- Partial conditional inference.
- Host-side structural observations.
- Diagnostic field comparisons.
- Experimental preference hypotheses.
- Unsupported conclusions.

Do not claim competitive chess strength based solely on pairwise preference accuracy.

---

# 31. Final Objective

Cycle 13 must demonstrate that transferable local probabilistic relationships can support evidence-based preferences between chess moves.

The system should learn that certain relational consequences are associated with preferable outcomes without relying on absolute-square memorization or conventional handcoded evaluation scores.

A move that creates an attack may be preferable in one context but unfavorable in another because it exposes the king or abandons a defender.

The learner must represent these distinctions through evidence.

The objective is not to hardcode strategic priorities.

It is to learn how local relational changes relate to observed outcomes.

**Cycle 13 establishes probabilistic strategic preference learning. Cycle 14 may investigate bounded move selection only if the evidence supports that transition.**
