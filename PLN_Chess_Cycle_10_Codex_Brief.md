# PLN Chess — Cycle 10 Engineering Implementation Brief

## Distribution-Robust Generalization, Temporal Evidence, Adversarial Completion, and Strategic Readiness

**Repository:** https://github.com/machieke/pln-chess  
**Starting commit:** `257473d2462c75f84d3975bb91d85a8c1cc269dd`  
**Accepted model:** `C8-promotion-relative`  
**Execution:** Consolidated autonomous engineering cycle  
**Delivery:** Implementation, datasets, experiments, proofs, benchmarks, documentation, and local commits  
**Authorization:** No GitHub push, no external deployment, no unapproved native PLN operators

---

# 1. Mission

Cycle 10 must determine whether the existing probabilistic chess-rule learner generalizes beyond the synthetic distributions used during Cycles 1–9.

The principal research question is:

> Can a probabilistic logic network, trained on piece-relative spatial relationships, reliably infer chess move legality across independently sourced games, unfamiliar structural combinations, incomplete historical evidence, and adversarial configurations without relying on absolute board coordinates or deterministic legality checks?

The system must retain its native PLN architecture.

This cycle must not become a conventional chess-engine implementation.

The work is divided into four coordinated research tracks:

### Track A — Independent generalization

Evaluate the accepted learner against genuinely independent chess positions and game histories.

### Track B — Temporal and adversarial reasoning

Improve historical evidence transport and resolve remaining adversarial and special-move abstentions.

### Track C — Probabilistic reliability and performance

Evaluate confidence calibration under distribution shift, optimize inference, and preserve proof integrity.

### Track D — Strategic readiness

Establish whether the learned relational representation can support future probabilistic potential fields, attack relationships, and strategic concepts.

Track D is architectural preparation only. Do not introduce a chess-playing evaluation function or strategic move-selection engine during Cycle 10.

---

# 2. Starting Baseline

Cycle 9 delivered the following reported results.

| Cohort | Recall | Exact legal-move sets |
|---|---:|---:|
| 100 synthetic games, 500 positions | 99.992% | 499/500 |
| Adversarial, 128 positions | 99.233% | 112/128 |
| Special moves, 80 positions | 99.254% | 71/80 |

Additional results:

- Zero observed false-legal classifications.
- Zero observed false-illegal classifications.
- Zero observed false-positive self-check classifications.
- 365 passing tests.
- 287 preserved negative evidence-removal controls.
- 48 evaluation shards.
- 252 benchmark samples.
- 12 browser verification checks.
- Exact native proof parity preserved.
- Accepted C8 model unchanged.

Full-position inference medians:

- Cold: 4.008 seconds.
- Warm: 2.748 seconds.

Held-out in-board calibrated Brier score:

- Before calibration: 0.005278.
- After calibration: 0.00000127.

These measurements must be reproduced and their provenance verified before new development.

Native positive composition remains unproven.

The Cycle 9 architectural decision was:

**No production implementation of a new PLN composition operator.**

This decision remains binding.

---

# 3. Architectural Invariants

The following constraints apply throughout Cycle 10.

1. All learned chess knowledge must remain piece-relative.
2. Learned movement rules must not depend on absolute board coordinates.
3. Board coordinates may be used for input, output, state reconstruction, and reference evaluation.
4. Native PLN must perform truth-value inference and revision.
5. Do not replace native PLN formulas with custom host-language probability calculations.
6. Do not introduce a deterministic legality gate into production inference.
7. Reference chess engines are permitted only for dataset preparation, evaluation, and testing.
8. Preserve operational, strict, and experimental inference modes.
9. Preserve evidence IDs, dependence groups, native rule IDs, and proof graphs.
10. Preserve the distinction between supported conclusions, contradictions, unknowns, and incomplete inference.
11. Do not present partial positive conditional evidence as a complete legality proof.
12. Do not interpret PLN confidence as an empirically calibrated probability without validation.
13. Do not enable new native PLN inference operators.
14. Preserve all previously accepted operational models and historical artifacts.
15. Never weaken acceptance criteria merely to improve recall.

The accepted C8 model must remain the operational default until a replacement passes all mandatory gates.

---

# 4. Work Package C10-01 — Baseline Reproduction and Provenance Lock

Verify the starting repository state.

Record:

- Git commit.
- Working-tree status.
- Runtime versions.
- Native PLN source hashes.
- Dataset hashes.
- Model hashes.
- Dependency versions.
- Evaluation configuration.
- Inference thresholds.
- Cache configuration.

Reproduce the Cycle 9 acceptance results.

Preserve all historical baselines.

Create:

`artifacts/cycle10/baseline/`

Deliver:

- Baseline manifest.
- Reproduction receipt.
- Model identity.
- Dataset identity.
- Native proof parity report.
- Dependency lock verification.

Do not overwrite earlier-cycle evidence.

---

# 5. Work Package C10-02 — External Chess Dataset Acquisition

Build an evaluation corpus from at least three independently sourced chess-game collections.

Possible sources include:

- Public tournament PGN archives.
- Openly licensed online chess-game datasets.
- Public chess-study or annotated-game collections.
- Historical master-game collections with suitable reuse permissions.

Before acquisition, verify:

- Source identity.
- License and permitted use.
- Download provenance.
- Data integrity.
- Game validity.
- Duplication.
- Source overlap.

Do not assume different websites provide independent underlying games.

Maintain source URLs, license information, content hashes, acquisition dates, and original game identifiers.

Prefer data sources that differ meaningfully in:

- Playing strength.
- Time controls.
- Historical period.
- Opening distribution.
- Tactical complexity.
- Endgame representation.

Do not require paid services or private credentials.

If network access is unavailable, implement the acquisition pipeline and use already available public fixtures, while explicitly reporting which external provenance targets could not be verified.

Do not mislabel generated positions as externally sourced.

Deliver:

`docs/cycle10/dataset-provenance.md`

and machine-readable source manifests.

---

# 6. Work Package C10-03 — Independent Position Corpus

Construct a reproducible evaluation corpus containing at least 1,000 diverse positions.

Prefer a larger corpus when computationally practical.

Include:

- Opening positions.
- Early middlegames.
- Complex middlegames.
- Tactical positions.
- Reduced-material endgames.
- Pawn endgames.
- Rook endgames.
- Minor-piece endgames.
- Promotion races.
- Positions with multiple attackers.
- Positions with pinned pieces.
- Positions with discovered attacks.
- Positions with restricted king mobility.
- Castling and en-passant opportunities.

Sample positions from complete games rather than independently synthesizing every FEN.

Preserve complete move histories where available.

Partition evaluation by source game and structural family.

Implement duplicate detection using:

- Exact FEN matching.
- Canonical position fingerprints.
- Relative structural descriptors.
- Symmetry-aware comparisons.
- Game provenance.

Prevent leakage from:

- Training data.
- Validation data.
- Previous evaluation cohorts.
- Translated copies.
- Reflected copies.
- Repeated game positions.

Distinguish strict independence from merely different random seeds.

Deliver dataset and overlap-audit manifests.

---

# 7. Work Package C10-04 — Out-of-Distribution Evaluation

Evaluate the frozen accepted model before training on any new external examples.

This is essential.

The first external evaluation must be a genuine zero-update generalization test.

Measure:

- Precision.
- Recall.
- F1.
- Exact legal-move-set accuracy.
- Abstention rate.
- False-legal count.
- False-illegal count.
- Self-check false-positive count.
- Incomplete inference count.
- Per-piece performance.
- Special-move performance.
- Runtime and memory.

Report complete candidate-set and in-board metrics separately.

Compare performance across source collections.

Evaluate whether model performance varies with:

- Game complexity.
- Material count.
- Game phase.
- Opening family.
- Tactical density.
- Number of legal moves.
- Number of attacking pieces.
- Historical evidence completeness.

Do not modify the frozen model during this baseline evaluation.

Deliver:

`docs/cycle10/external-generalization.md`

---

# 8. Work Package C10-05 — Structural Failure Taxonomy

Analyze every position without an exact legal-move-set prediction.

Classify the failures into:

1. Movement geometry.
2. Ray obstruction.
3. Destination occupancy.
4. Friendly-piece interaction.
5. Capture eligibility.
6. King exposure.
7. Pins.
8. Discovered attacks.
9. Double check.
10. Check resolution.
11. Promotion.
12. Castling.
13. En passant.
14. Historical uncertainty.
15. Insufficient evidence.
16. Overly specific relational abstraction.
17. Native PLN inference limitation.
18. Candidate-generation limitation.
19. Timeout or inference-budget limitation.

For each category, report:

- Number of affected positions.
- Number of affected candidates.
- Error versus abstention breakdown.
- Representative proof traces.
- Relevant learned hypotheses.
- Supporting evidence.
- Root-cause assessment.

Distinguish missing knowledge from missing inference capability.

Do not automatically interpret an abstention as an error in the movement ontology.

---

# 9. Work Package C10-06 — Adversarial Abstention Resolution

Investigate the 16 non-exact adversarial positions reported in Cycle 9.

Reproduce each failure.

Determine the precise unresolved candidates.

For each candidate, inspect:

- Relative movement geometry.
- Occupancy relations.
- Obstruction evidence.
- King exposure.
- Historical context.
- Native inference chain.
- Truth values.
- Evidence provenance.
- Dependence groups.

Develop targeted relational improvements.

Avoid memorizing individual FENs.

Avoid broad threshold relaxation.

Every improvement must include:

- Before/after proof comparison.
- Evidence-removal control.
- Structural counterfactual.
- Independent held-out test.
- Regression analysis.

The goal is to resolve uncertainty using better relational knowledge, not to force classifications.

---

# 10. Work Package C10-07 — Special-Move Completion

Investigate the nine non-exact special-move positions from Cycle 9.

Cover:

- Kingside castling.
- Queenside castling.
- Castling through attacked squares.
- Castling while in check.
- Castling after king movement.
- Castling after rook movement.
- En-passant eligibility.
- En-passant king exposure.
- All four promotion choices.
- Capture promotions.
- Underpromotion.

Separate geometric movement from historical eligibility.

A structurally plausible castling move is not sufficient evidence that castling rights exist.

A FEN en-passant target must not automatically be represented as independently observed move history.

Preserve epistemic distinctions.

Produce dedicated native proof traces and counterfactual controls.

---

# 11. Work Package C10-08 — Temporal Evidence Transport

Implement a versioned mechanism for carrying historical evidence through actual move sequences.

The model must distinguish:

- Observed historical events.
- Trusted imported state metadata.
- Inferred historical relationships.
- Unknown history.

Introduce explicit temporal relations where supported by the existing architecture.

Examples of conceptual predicates:

- `ObservedMove`
- `PreviouslyMoved`
- `RetainedCastlingRight`
- `LastMoveDoublePawnAdvance`
- `HistoricalEvidenceSource`
- `HistoryConfidence`

These are ontology concepts, not authorization to introduce new PLN inference operators.

The implementation must preserve:

- Event sequence.
- Source identity.
- Evidence IDs.
- Dependence groups.
- Trust policy.
- Model version.
- State transition provenance.

Support replay from a complete PGN sequence.

Support partial histories.

Support imported FEN positions without complete history.

Do not fabricate missing events.

If historical information is unavailable, preserve uncertainty.

---

# 12. Work Package C10-09 — Temporal Counterfactuals

Construct paired experiments in which board geometry is identical but historical eligibility differs.

Examples:

- Same piece arrangement, different castling rights.
- Same pawn arrangement, different en-passant history.
- Same board state, complete versus incomplete history.
- Same apparent eligibility, conflicting historical evidence.

Verify that the model distinguishes these cases appropriately.

Do not encode historical conditions through absolute-coordinate memorization.

History should be attached to relational events and state transitions.

Deliver at least ten inspectable temporal counterfactual demonstrations.

Each must contain:

- Initial state.
- Event history.
- Resulting state.
- Relevant temporal propositions.
- Native truth values.
- Evidence lineage.
- Expected reference outcome.
- Actual model outcome.

---

# 13. Work Package C10-10 — Calibration Under Distribution Shift

Evaluate the Cycle 9 diagnostic calibration model on external data.

Do not refit calibration before the initial frozen evaluation.

Measure:

- Brier score.
- Expected calibration error.
- Log loss where applicable.
- Reliability by strength bin.
- Reliability by confidence bin.
- Selective risk.
- Coverage versus accuracy.
- Distribution-specific calibration drift.

Evaluate separately for:

- Original synthetic positions.
- External game collections.
- Adversarial positions.
- Special moves.
- Positions with incomplete history.

Estimate uncertainty through bootstrap or other appropriate methods that respect game-level dependence.

Do not treat candidate moves from the same position as independent samples.

Compare:

1. Frozen Cycle 9 calibration.
2. Recalibration on a separate external validation subset.
3. Evaluation on untouched external test data.

Calibration must remain diagnostic.

It must not silently change native PLN inference or legality classification.

---

# 14. Work Package C10-11 — Evidence Dependence and Domain Shift

Investigate whether the existing evidence-dependence model generalizes across external collections.

Questions to answer:

- Do multiple positions from the same game count as independent evidence?
- Do structurally equivalent positions from different games provide independent support?
- How should repeated openings be grouped?
- Does translating a position create new evidence?
- How should contradictory observations from different collections be handled?
- Can correlated evidence inflate PLN confidence?

Run controlled dependence-policy ablations.

Preserve native revision semantics.

Do not double-count transformed copies.

Report the effects on:

- Truth values.
- Confidence.
- Prediction coverage.
- Error rates.
- Model size.
- Evidence lineage.

---

# 15. Work Package C10-12 — Controlled Adaptation Experiment

After completing frozen external evaluation, investigate whether the learner can adapt to unfamiliar structural families.

Use three distinct models:

1. Frozen accepted baseline.
2. Experimental model trained on a small external adaptation subset.
3. Experimental model trained on a larger adaptation subset.

Keep the final external test set untouched.

Measure sample efficiency.

Determine whether newly learned knowledge transfers beyond the exact training contexts.

Require:

- Native revision.
- Explicit evidence provenance.
- Dependence-aware learning.
- No absolute-coordinate hypotheses.
- No production oracle dependency.
- Independent structural holdouts.

Report performance as a function of additional evidence.

Do not promote an adapted model solely because it improves on the adaptation data.

---

# 16. Work Package C10-13 — Inference Performance and Memory

Preserve or improve Cycle 9 inference performance.

Investigate:

- Candidate generation.
- Observation construction.
- Relative relation indexing.
- Native PLN scheduling.
- Repeated proof construction.
- Cache key generation.
- Cache invalidation.
- Evidence lookup.
- Model checkpoint loading.
- Temporal replay overhead.

Benchmark realistic external positions with varying material and complexity.

Report:

- p50/p95/p99 latency.
- Cold latency.
- Warm latency.
- Native invocation count.
- Grounded atom count.
- Peak RSS.
- Checkpoint size.
- Cache hit rate.
- Proof equivalence.
- Timeout rate.
- Truncation rate.

Use enough repetitions to distinguish meaningful performance changes from noise.

Compare against Cycle 9.

No optimization may change truth values, evidence IDs, classifications, or proof semantics.

---

# 17. Work Package C10-14 — Strategic Readiness and Potential-Field Architecture

Prepare the architecture for future probabilistic chess strategy.

Do not implement strategic move selection yet.

Investigate whether existing relative propositions can support reusable concepts such as:

- Attack relationships.
- Defense relationships.
- Piece mobility.
- Local control.
- Obstruction.
- Pins.
- Discovered attacks.
- Relative influence.
- Threat exposure.
- Candidate successor states.

The eventual system should support probabilistic potential fields.

These fields must be based on local relational interactions rather than absolute board-coordinate evaluation tables.

Conceptually, a piece should influence nearby and reachable relationships through learned probabilistic rules.

A future move would alter those relationships, allowing the network to compare potential fields before and after the move.

The initial design should distinguish:

1. Spatial interaction fields.
2. Attack and defense fields.
3. Mobility fields.
4. King-exposure fields.
5. Strategic influence fields.
6. Successor-state changes.

Do not introduce handcoded piece-square tables or conventional chess-engine evaluation scores.

Deliver:

`docs/cycle10/strategic-readiness.md`

Include:

- Proposed ontology.
- Reusable relative relations.
- Required native PLN capabilities.
- Missing inference capabilities.
- Evidence requirements.
- Computational implications.
- Candidate future experiments.

This work must not interfere with the legal-move learner.

---

# 18. Work Package C10-15 — Native PLN Research Boundary

Preserve the Cycle 9 no-go decision on production native composition extensions.

Do not repeat previously exhausted conjunction experiments.

Review whether new external evidence or temporal modeling reveals any genuinely new requirement for the proposed extension.

If no new information exists, retain the previous architectural decision.

An isolated research prototype may be proposed but must not be enabled without explicit authorization.

Continue distinguishing:

- Existing verified native PLN inference.
- Partial conditional inference.
- Proposed probabilistic composition.
- Unsupported conclusions.

Do not misrepresent mathematical reference calculations as native PLN proofs.

---

# 19. Work Package C10-16 — API, CLI, and Inspector

Extend the existing interfaces to support:

- External dataset evaluation.
- Source provenance inspection.
- Historical event replay.
- Temporal evidence display.
- Model comparisons.
- Distribution-shift diagnostics.
- Calibration comparisons.
- Failure-family inspection.
- Evidence-removal controls.
- Performance profiling.

The inspector must display:

- Raw PLN strength.
- Raw PLN confidence.
- Classification.
- Proof status.
- Evidence lineage.
- Historical evidence status.
- Model identity.
- Runtime identity.

Keep calibration diagnostics separate from native truth values.

Preserve existing APIs wherever possible.

Verify desktop and mobile behavior.

---

# 20. Work Package C10-17 — Acceptance and Regression Gates

All previous accepted regression suites must remain available.

Mandatory requirements:

1. Accepted Cycle 8 operational behavior remains reproducible.
2. Cycle 9 frozen comparisons remain reproducible.
3. Zero new false-legal classifications on established acceptance cohorts.
4. Zero new false-illegal classifications on established acceptance cohorts.
5. Zero new self-check false positives on established acceptance cohorts.
6. All 287 negative evidence-removal controls pass.
7. Native proof and cache parity remain valid.
8. No production chess-oracle dependency.
9. No unapproved PLN inference operator.
10. No silent truth-value formula changes.
11. Historical evidence provenance is preserved.
12. Clean-checkout bootstrap succeeds.
13. Automated tests pass.
14. Dataset leakage checks pass.
15. Failed experiments remain documented.
16. Historical artifacts remain accessible.

New external-cohort errors must be reported explicitly. Do not hide them through abstention or dataset filtering.

A replacement operational model may be promoted only after passing all established regression gates and demonstrating a defensible improvement on independent evaluation.

---

# 21. Research Targets

These are research objectives, not guarantees.

| Area | Target |
|---|---|
| Independent external collections | At least 3 |
| External evaluation positions | At least 1,000 |
| Independent source games | At least 100 |
| Additional adversarial positions | At least 100 |
| Adversarial exact move sets | At least 95% |
| Special-move exact sets | At least 95% |
| False-legal classifications | Zero observed on acceptance cohorts |
| False-illegal classifications | Zero observed on acceptance cohorts |
| Self-check false positives | Zero observed on acceptance cohorts |
| Negative evidence controls | 287/287 |
| Full-position cold latency | No significant regression from Cycle 9 |
| Full-position warm latency | No significant regression from Cycle 9 |

Report statistical uncertainty where appropriate.

Do not tune against the final external test set.

A missed research target is acceptable when accompanied by reproducible evidence and a clear explanation.

---

# 22. Work Package C10-18 — Consolidated Delivery

Produce a complete engineering package.

Required reports:

- `docs/cycle10/engineering-report.md`
- `docs/cycle10/package-matrix.md`
- `docs/cycle10/dataset-provenance.md`
- `docs/cycle10/external-generalization.md`
- `docs/cycle10/generalization-failures.md`
- `docs/cycle10/temporal-evidence.md`
- `docs/cycle10/calibration-shift.md`
- `docs/cycle10/performance.md`
- `docs/cycle10/strategic-readiness.md`
- `docs/cycle10/architecture-decision.md`
- `docs/cycle10/reproduction.md`

Required machine-readable artifacts:

- Baseline manifests.
- External source manifests.
- Dataset hashes.
- Duplicate and overlap audits.
- Evaluation outputs.
- Native proof traces.
- Evidence-removal controls.
- Temporal replay records.
- Adaptation experiments.
- Calibration experiments.
- Performance benchmarks.
- Test logs.
- Artifact hashes.
- Reproduction receipts.

Every claim must link to supporting evidence.

Provide a one-page executive summary.

---

# 23. Autonomous Execution Contract

Codex is authorized to:

- Inspect the repository.
- Make local source changes.
- Download and process openly available datasets where access and licenses permit.
- Run native PLN experiments.
- Generate evaluation datasets.
- Train experimental models.
- Execute tests and benchmarks.
- Create documentation.
- Create local commits.

Codex is not authorized to:

- Push to GitHub.
- Deploy external services.
- Modify upstream PLN repositories.
- Introduce or enable a new PLN operator.
- Replace native PLN inference with custom probability formulas.
- Introduce a production chess-oracle legality gate.
- Weaken mandatory acceptance requirements.
- Delete historical evidence.
- Misrepresent synthetic data as external data.
- Use inaccessible or unlicensed datasets without authorization.

Complete all feasible work packages in one consolidated execution.

Do not stop after every milestone.

Make routine local engineering decisions independently.

If one research experiment fails, continue all independent work.

Stop only for an essential blocking dependency, an external action requiring authorization, or an architectural decision outside the scope of this brief.

---

# 24. Final Codex Reporting Requirements

The final response must include:

1. Starting commit.
2. Ending commit.
3. Working-tree status.
4. Local commit list.
5. Work-package completion matrix.
6. Baseline reproduction status.
7. External dataset provenance.
8. External generalization metrics.
9. Adversarial results.
10. Special-move results.
11. Temporal reasoning results.
12. Calibration under distribution shift.
13. Evidence-dependence findings.
14. Controlled adaptation results.
15. Performance comparisons.
16. Native PLN compatibility status.
17. Strategic-readiness assessment.
18. Test results.
19. Clean reproduction status.
20. Known limitations.
21. Recommended Cycle 11 priorities.

Distinguish:

- Reproduced measurements.
- New measurements.
- Experimental findings.
- Mathematical assumptions.
- Unverified hypotheses.
- Engineering recommendations.

Do not claim universal chess correctness based on finite datasets.

---

# 25. Final Objective

Cycle 10 must establish whether the current probabilistic chess-rule learner is genuinely robust beyond its original synthetic training and evaluation distributions.

The system should demonstrate that learned local relationships transfer across unfamiliar games, structural configurations, and temporal conditions.

At the same time, it must preserve the native PLN inference architecture, evidence provenance, and conservative operational behavior established during earlier cycles.

The long-term research objective remains:

**A probabilistic chess intelligence that learns transferable local interaction rules, constructs probabilistic potential fields from those relationships, and eventually reasons about the consequences of moves without relying on absolute-coordinate memorization or conventional handcoded chess evaluation functions.**

Cycle 10 is the validation and architectural-readiness stage before that strategic development begins.
