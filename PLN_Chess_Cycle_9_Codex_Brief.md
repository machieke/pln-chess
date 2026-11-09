# PLN Chess — Cycle 9 Engineering Implementation Brief

## Operational Consolidation, Generalization, Calibration, and Native PLN Composition Decision

**Repository:** https://github.com/machieke/pln-chess  
**Starting commit:** `36b5ea10395c0f41de4c03824ba6f8ee1c5dbad1`  
**Accepted baseline:** `C8-promotion-relative`  
**Execution mode:** Consolidated autonomous engineering cycle  
**Delivery:** Local commits, reproducible artifacts, complete technical reports  
**Restrictions:** No GitHub push, no new production PLN operators, no external deployment.

---

# 1. Mission

Continue development of the existing probabilistic chess-rule learner.

Cycle 8 established strong operational results using transferable piece-relative knowledge and native PLN inference. Cycle 9 must consolidate these achievements, improve independent generalization, evaluate probabilistic reliability, optimize performance, and produce a formal architectural decision regarding native multi-premise PLN composition.

This is not a new chess engine implementation.

The system must remain a probabilistic logic network that learns reusable local relationships rather than memorizing absolute board positions.

The engineering cycle consists of two independent tracks.

### Track A — Operational consolidation

Improve the accepted learner through:

- Broader independent-game evaluation.
- Adversarial robustness.
- Abstention analysis.
- Confidence calibration.
- Performance optimization.
- Temporal evidence improvements.
- Reproducibility and provenance validation.

### Track B — Native PLN composition decision

Review the Cycle 8 mathematical proposal and determine whether a native PLN composition extension is technically justified.

Do not implement or activate an unapproved operator.

A negative research conclusion is acceptable if supported by precise mathematical and experimental evidence.

Both tracks must be completed independently.

---

# 2. Starting Baseline

Cycle 8 delivered:

| Evaluation cohort | Recall | Exact legal-move sets |
|---|---:|---:|
| Frozen transfer | 99.882% | 39/40 |
| C7 independent-game positions | 99.649% | 28/32 |
| C8 independent-game positions | 100% | 16/16 |
| C8 adversarial | 92.084% | 32/36 |

Additional recorded achievements:

- All eight original promotion errors resolved.
- Zero observed false-legal and false-illegal classifications across 16 acceptance suites.
- 52 generalization demonstrations across 26 source groups.
- 18 strict held-out source groups.
- 32 successful transformation checks.
- 347 passing tests.
- 287 preserved negative evidence-removal controls.
- 236,414 checked proof records.
- 240 benchmark samples with proof parity.
- Native positive composition remains unproven.
- Positive legality remains supported by partial conditional evidence.

Recorded full-position inference latency for 214 candidates:

| Mode | Cycle 7 | Cycle 8 |
|---|---:|---:|
| Cold median | 4.04 s | 4.67 s |
| Warm median | 2.78 s | 3.33 s |

These are historical reported measurements.

Codex must verify their provenance before using them as acceptance baselines.

---

# 3. Non-Negotiable Architectural Constraints

1. Preserve piece-relative spatial representation.
2. Do not encode absolute board coordinates into learned movement rules.
3. Absolute coordinates are permitted only for environment representation, board I/O, state reconstruction, and evaluation.
4. Use actual supported native PLN inference and revision operators.
5. Do not replace PLN truth-value calculations with custom Python probabilistic formulas.
6. Do not introduce a deterministic chess-legality gate into production inference.
7. Keep the chess reference oracle outside production inference.
8. Preserve operational, strict, and experimental inference modes.
9. Preserve explicit evidence provenance, dependence groups, rule IDs, and native proof traces.
10. Distinguish raw PLN truth values from empirically calibrated probabilities.
11. Preserve unknown and incomplete states where evidence is insufficient.
12. Do not represent partial conditional evidence as a complete proof of legality.
13. Do not silently modify the pinned native PLN calculus.
14. Do not promote an experimental model unless all mandatory acceptance gates pass.

The accepted Cycle 8 operational model must remain available throughout development.

---

# 4. Work Package C9-01 — Baseline Lock and Reproduction

Before changing the implementation:

- Verify starting HEAD.
- Verify working-tree state.
- Inspect Cycle 8 model and dataset manifests.
- Record native PLN and PeTTa runtime versions.
- Verify dependency hashes.
- Reproduce accepted operational evaluations.
- Reproduce strict and experimental comparisons.
- Preserve previous proof and benchmark artifacts.

Create:

`artifacts/cycle9/baseline/`

Required outputs:

- Baseline manifest.
- Model identity.
- Dataset identity.
- Runtime identity.
- Evaluation summaries.
- Proof hashes.
- Reproduction commands.
- Known limitations.

Do not overwrite historical artifacts.

---

# 5. Work Package C9-02 — Independent Evaluation Expansion

Expand evaluation substantially beyond the existing synthetic cohorts.

Generate reproducible positions from independent complete games.

Use multiple:

- Opening structures.
- Middlegame structures.
- Endgame structures.
- Material distributions.
- Pawn structures.
- Tactical configurations.
- Castling-right states.
- En-passant states.
- Promotion configurations.

Separate structural families and game provenance.

Training and held-out evaluation must not share equivalent translated or reflected examples.

Use multiple deterministic random seeds.

Create at least:

- 100 independent games.
- 500 sampled nonterminal positions.
- 100 additional adversarial positions.
- A dedicated special-move evaluation cohort.

These are minimum research dataset targets, subject to practical execution constraints.

If resource limits prevent completion, record the exact shortfall.

Report both complete candidate-set metrics and in-board candidate metrics.

Avoid allowing abundant easy off-board negatives to inflate precision.

---

# 6. Work Package C9-03 — Structural Generalization Analysis

Determine where the accepted learner generalizes and where it abstains.

Group failures by:

- Piece type.
- Movement geometry.
- Ray length.
- Intermediate occupancy.
- Destination occupancy.
- Capture type.
- King exposure.
- Pin configuration.
- Double check.
- Check resolution.
- Promotion.
- Castling.
- En passant.
- Missing historical evidence.
- Unknown sensory observations.

For every major failure family, identify whether the cause is:

1. Missing learned hypothesis.
2. Missing supporting evidence.
3. Overly specific abstraction.
4. Incorrect evidence dependence.
5. Native inference limitation.
6. Classification threshold.
7. Incomplete history.
8. Candidate-generation limitation.

Provide representative native proof traces.

Do not automatically solve abstentions by weakening thresholds.

Deliver:

`docs/cycle9/generalization-analysis.md`

---

# 7. Work Package C9-04 — Adversarial Robustness

Create adversarial examples that challenge local relational abstractions.

Include:

- Multiple blockers along one ray.
- Different blocker identities.
- Friendly versus opponent blockers.
- Pinned pieces.
- Discovered attacks.
- Double checks.
- Multiple simultaneous attackers.
- King moves into attacked squares.
- En-passant discovered checks.
- Castling through attacked squares.
- Underpromotion.
- Promotion captures.
- Promotions affecting king exposure.
- Board-boundary interactions.

Use controlled counterfactual pairs.

For example:

- Same relative movement, different blocker.
- Same destination, different occupant allegiance.
- Same geometry, different king exposure.
- Same promotion square, different promotion choice.

The system must demonstrate sensitivity to relevant differences and invariance to irrelevant differences.

Require evidence-removal controls for new learned motifs.

---

# 8. Work Package C9-05 — Abstention Resolution

Identify high-value unknown predictions.

Prioritize cases where:

- All relevant local relationships have been observed separately.
- The candidate differs from a supported example only in irrelevant context.
- A native negative proof is already available.
- A missing local abstraction could be learned without memorizing a complete position.

Investigate improved relational abstraction and evidence reuse.

Do not fabricate a positive conclusion where native PLN composition is unsupported.

Every resolved abstention must include:

- Original classification.
- Revised classification.
- Native truth values.
- Supporting evidence.
- Rule IDs.
- Proof graph.
- Counterfactual controls.
- Regression comparison.

A candidate that becomes incorrectly supported is a failed experiment.

---

# 9. Work Package C9-06 — PLN Strength and Confidence Calibration

Investigate the empirical meaning of PLN truth-value strength and confidence.

Do not treat PLN confidence as a calibrated probability of correctness.

Evaluate separately:

- Raw strength.
- Raw confidence.
- Combined diagnostic scores.
- Empirical outcome frequency.
- Selective accuracy.
- Abstention versus error tradeoffs.

Use independent calibration and evaluation cohorts.

Methods may include:

- Reliability diagrams.
- Expected calibration error.
- Brier score.
- Log loss where probabilities are defined.
- Confidence-stratified precision and recall.
- Selective risk-coverage curves.

Any empirical calibration mapping must remain outside native PLN inference.

Do not use a calibration model as a hidden deterministic legality gate.

Compare calibration across:

- Piece types.
- Special moves.
- Independent games.
- Adversarial positions.
- Different evidence volumes.

Report sample sizes and uncertainty intervals.

Deliver:

`docs/cycle9/calibration-report.md`

---

# 10. Work Package C9-07 — Evidence Dependence and Revision

Review how evidence contributes to learned beliefs.

Investigate:

- Duplicate observations.
- Correlated game positions.
- Translated examples.
- Reflected examples.
- Shared structural families.
- Independent counterexamples.
- Conflicting observations.
- Evidence provenance across model versions.

Preserve native revision semantics.

Test whether dependence-group policies are overly conservative or permit double counting.

Any changed policy must be evaluated through controlled ablations.

Required properties:

- Idempotent evidence ingestion.
- Deterministic replay.
- Stable checkpoint reconstruction.
- Explicit excluded evidence.
- Preserved negative controls.
- Reproducible counterfactual removal.

Do not silently combine dependent evidence as independent support.

---

# 11. Work Package C9-08 — Temporal and Historical Evidence

Improve representation of time-dependent chess conditions.

Focus on:

- Castling rights.
- Previous king movement.
- Previous rook movement.
- En-passant eligibility.
- Previous pawn double-step.
- Promotion history.
- Incomplete game history.

Distinguish three epistemic categories:

1. Directly observed historical events.
2. Trusted state metadata.
3. Inferred historical conditions.

FEN metadata may be treated as evidence with an explicit trust policy, but must not be misrepresented as independently reconstructed history.

Implement versioned temporal evidence where appropriate.

Evaluate missing-history cases separately.

Do not claim a complete historical-legality theorem without a native proof.

---

# 12. Work Package C9-09 — Inference Performance Optimization

Investigate the Cycle 8 latency regression.

Profile:

- Observation construction.
- Relative descriptor generation.
- Candidate enumeration.
- Native operator scheduling.
- Repeated grounding.
- Proof construction.
- Evidence lookup.
- Cache serialization.
- Checkpoint loading.
- Inspector overhead.

Prioritize eliminating redundant work.

Preserve exact proof semantics.

Benchmark:

- Single-candidate inference.
- Sparse positions.
- Full positions.
- Promotion-heavy positions.
- Adversarial positions.
- Independent-game positions.
- Cold execution.
- Warm execution.
- Reference uncached execution.

Report:

- p50/p95/p99 latency.
- Native calls.
- Grounded atoms.
- Cache hit rate.
- Memory use.
- Checkpoint size.
- Proof identity.
- Truncation rate.

Aim to recover Cycle 7-level latency or better.

Performance improvements are unacceptable if they change inference results or evidence provenance.

---

# 13. Work Package C9-10 — Native PLN Composition Proposal Review

Review the complete Cycle 8 composition specification.

Inspect:

- Proposed logical syntax.
- Truth-value semantics.
- Confidence semantics.
- Independence assumptions.
- Dependence handling.
- Evidence overlap.
- Contradictory evidence.
- Interaction with revision.
- Interaction with deduction.
- Interaction with induction.
- Interaction with negation.
- Mathematical counterexamples.
- Proposed runtime integration.

Compare the proposal against the pinned native PLN implementation.

Identify whether it is:

1. Mathematically sufficiently specified.
2. Compatible with existing truth-value conventions.
3. Implementable in the MeTTa/PeTTa runtime.
4. Testable independently of chess.
5. Safe to isolate from operational inference.
6. Suitable for upstream discussion.

Do not enable the proposed operator.

Do not repeat previously exhausted native composition experiments unless a materially new hypothesis or implementation is available.

Deliver:

`docs/cycle9/composition-review.md`

---

# 14. Work Package C9-11 — Formal Go/No-Go Decision

Produce an explicit architectural decision memo.

Evaluate three alternatives.

## Option A — Remain with existing PLN operators

Advantages:

- No new inference calculus.
- Stable operational behavior.
- Existing provenance and verification.

Limitations:

- Positive legality remains partial.
- General multi-premise composition remains unavailable.

## Option B — Develop an isolated native PLN extension

Advantages:

- Potential genuine compositional reasoning.
- Reusable capability beyond chess.

Risks:

- Mathematical assumptions.
- Evidence dependence.
- Runtime compatibility.
- Additional proof obligations.
- Potential divergence from upstream PLN.

## Option C — Change the logical representation

Investigate whether a different representation within existing verified native rules could support the required reasoning without introducing a new operator.

Do not simply repeat failed nested-implication experiments.

For each option, provide:

- Technical feasibility.
- Research uncertainty.
- Expected engineering effort.
- Mathematical risks.
- Compatibility implications.
- Required tests.
- Migration impact.
- Recommendation.

The memo must explicitly state whether a native extension is justified.

This is a recommendation, not authorization to implement it.

---

# 15. Work Package C9-12 — API, CLI, and Inspector

Preserve existing public interfaces.

Add or improve:

- Model comparisons.
- Per-piece metrics.
- Calibration exports.
- Failure-family inspection.
- Evidence provenance navigation.
- Runtime and model identity display.
- Performance diagnostics.
- Temporal evidence inspection.

The inspector must distinguish:

- Operational predictions.
- Strict proof results.
- Experimental results.
- Calibrated diagnostic estimates.

Do not display calibrated estimates as native PLN truth values.

Keep all inference logic in the backend.

Verify desktop and mobile behavior.

---

# 16. Work Package C9-13 — Verification and Regression Gates

Run all previous acceptance suites.

Mandatory requirements:

1. Accepted Cycle 8 behavior remains reproducible.
2. No new false-legal classifications on established regression datasets.
3. No new false-illegal classifications on established regression datasets.
4. No new false-positive self-check classifications.
5. All 287 negative evidence-removal controls remain valid.
6. Native proof provenance is preserved.
7. Reference and cached inference remain equivalent.
8. No production chess-oracle dependency.
9. No unapproved PLN operator.
10. No silent inference-calculus changes.
11. Clean-checkout bootstrap succeeds.
12. All automated tests pass.
13. Historical reports remain accessible.
14. Failed experiments are documented.

A new operational model must not be promoted if any mandatory gate fails.

The previous operational model must remain the default until acceptance is established.

---

# 17. Research Performance Targets

The following are aspirational research targets, not mandatory correctness guarantees.

| Metric | Target |
|---|---|
| Independent-game recall | At least 98% |
| Independent-game exact sets | At least 85% |
| Adversarial exact sets | At least 95% |
| Observed false-legal classifications | Zero |
| Observed false-illegal classifications | Zero |
| Observed self-check false positives | Zero |
| Full-position cold latency | At or below Cycle 7 baseline |
| Full-position warm latency | At or below Cycle 7 baseline |
| Negative evidence controls | 287/287 preserved |

Evaluate these targets on both historical and newly generated cohorts.

Do not tune repeatedly against the final held-out test set.

Report confidence intervals and sample sizes where applicable.

---

# 18. Work Package C9-14 — Consolidated Delivery

Produce a complete engineering package.

Required documents:

- `docs/cycle9/engineering-report.md`
- `docs/cycle9/package-matrix.md`
- `docs/cycle9/generalization-analysis.md`
- `docs/cycle9/calibration-report.md`
- `docs/cycle9/performance-report.md`
- `docs/cycle9/composition-review.md`
- `docs/cycle9/architecture-decision.md`
- `docs/cycle9/reproduction.md`

Required artifacts:

- Baseline manifests.
- Dataset manifests.
- Model checkpoints.
- Evaluation outputs.
- Proof traces.
- Evidence-removal controls.
- Ablation results.
- Calibration results.
- Performance benchmarks.
- Test logs.
- Reproduction receipts.
- Artifact hashes.

Include a concise one-page executive summary.

Every claimed result must be linked to reproducible evidence.

---

# 19. Autonomous Execution Contract

Codex is authorized to:

- Inspect the repository.
- Make local source changes.
- Run native PLN experiments.
- Generate datasets.
- Train and evaluate models.
- Run tests and benchmarks.
- Produce documentation.
- Create local commits.

Codex is not authorized to:

- Push to GitHub.
- Deploy external services.
- Modify upstream PLN repositories.
- Enable a new inference operator.
- Replace native PLN inference with custom probability calculations.
- Introduce a production chess-oracle legality gate.
- Weaken mandatory acceptance criteria.
- Delete historical evidence.

Complete all feasible work packages in one consolidated execution.

Do not request approval after each milestone.

If one experimental track fails, continue all independent engineering work.

Stop only for an essential blocking dependency, an external action requiring authorization, or an architectural decision that cannot safely be made within this brief.

---

# 20. Final Codex Report

The final response must include:

1. Starting commit and ending commit.
2. Working-tree status.
3. Local commit list.
4. Work-package completion matrix.
5. Baseline versus Cycle 9 metrics.
6. Independent-game results.
7. Adversarial results.
8. Calibration findings.
9. Performance comparisons.
10. Native PLN composition review.
11. Go/no-go recommendation.
12. Test results.
13. Reproduction status.
14. Known limitations.
15. Recommended Cycle 10 priorities.

Distinguish measured results from hypotheses and recommendations.

Do not claim universal chess correctness from finite test cohorts.

---

# Final Objective

Cycle 9 must deliver two independently valuable outcomes.

**Operational outcome:** A more robust, empirically evaluated, and efficient probabilistic chess-rule learner that preserves the successful Cycle 8 architecture.

**Research outcome:** A technically defensible architectural decision about extending native PLN to support genuine multi-premise probabilistic composition.

The project must continue toward transferable, local relational intelligence rather than absolute-coordinate memorization.

Operational reliability and mathematical integrity take precedence over optimistic performance claims.
