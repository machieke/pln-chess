# Codex Master Implementation Brief: Piece-Relative PLN Chess Learner (Expanded, Consolidated)

## Purpose
Build a first-stage chess learner that infers **allowed moves** using the actual native inference rules of SingularityNET/OpenCog Probabilistic Logic Networks (PLN). The learned model must be **relational and translation-invariant**, not tied to absolute board squares. Like local-neighborhood rules in smoothed particle hydrodynamics (SPH), the same rule should transfer to a different location when the relative relationships are preserved. This is a locality analogy, not a physical simulation.

## Non-negotiable architecture
- Absolute coordinates are allowed **only** for board input/output and evaluation. They must not occur as constants in learned movement rules or index learned rule weights.
- All movement and legality judgments must be PLN propositions with native truth values; **no deterministic legality or king-safety gate** in the inference path.
- Use only PLN inference operators verified in the pinned implementation. Do not invent conjunction, probability multiplication, negation, or revision formulas and label them PLN.
- Keep an external chess oracle exclusively in training/evaluation, never in production inference.
- Avoid brute-force program synthesis: seed a compact vocabulary of relative relational templates and learn their strengths/confidences from contrasting evidence.
- Preserve provenance and evidence dependence; repeated or symmetry-augmented evidence is not independent.

## Phase 0 — Verify actual PLN capabilities (mandatory gate)
1. Pin the target repository, branch, commit, interpreter, AtomSpace/MeTTa version, and PLN implementation.
2. Inspect source and runnable examples for: modus ponens, deduction, induction, inheritance, negation, multi-premise combination, and truth-value revision. **Do not assume any are implemented.**
3. Create `docs/pln-compatibility-matrix.md`: exact native symbol, signature, source path, truth-value behavior, smoke test, supported/unsupported.
4. Create executable smoke tests for every operator chosen. Check whether confidence represents evidential support rather than probability of truth; document native truth-value semantics.
5. If essential native operators are missing, stop and report the gap and viable reduced scope; never silently implement a new logical rule.

## Phase 1 — Relational ontology
Define atom types in the native representation (names below are conceptual, not claimed MeTTa syntax):

```
PieceType(P, Rook)
Owner(P, White)
SideToMove(S, White)
CandidateMove(S, P, M)
RelativeDisplacement(M, East, 2)
RelativeOffset(M, Forward, 1, Lateral, 1)
OrthogonalRay(M)
DiagonalRay(M)
IntermediateCellEmpty(S, M, Step)
DestinationEmpty(S, M)
DestinationFriendly(S, M)
DestinationOpponent(S, M)
DestinationExists(S, M)
RelativeStartingRank(S, P)
WouldExposeOwnKing(S, M)
MovementPatternSupported(S, M)
LegalMove(S, M)
```

Every proposition carries a native PLN truth value or points to an atom with one. Piece and position IDs are observation identifiers, not reusable rule constants. Pawn `Forward` is oriented to the owning player. Board boundaries are relational features, not absolute square rules.

The observation adapter may parse FEN, enumerate relative cells and candidate displacements, and emit uncertain observations. It **must not** call `legal_moves`, `is_check`, `is_attacked`, or any equivalent chess-oracle functionality for inference. If it directly senses a compound feature like `RayClear`, document that as a sensor with a calibrated truth value; preferably infer it from intermediate occupancy using verified native PLN operators.

## Phase 2 — Small hypothesis vocabulary
Seed low-confidence candidate hypotheses, not certain chess rules:

| Piece | Relative movement schema | Learned contextual dependencies |
|---|---|---|
| Rook | orthogonal ray, distance >= 1 | clear path, destination allegiance, king exposure |
| Bishop | diagonal ray, distance >= 1 | clear path, destination allegiance, king exposure |
| Queen | orthogonal or diagonal ray | clear path, destination allegiance, king exposure |
| Knight | signed offsets (1,2) and (2,1) | destination allegiance, king exposure; jumping |
| King | one-cell neighborhood | opponent attack, king exposure |
| Pawn | one step forward | destination empty, side orientation |
| Pawn | two steps forward from relative start | intermediate and destination empty |
| Pawn | one step forward-diagonal | opponent destination, capture |

No square-specific hypotheses. No unconstrained search over arbitrary symbolic expressions. The supplied geometry and template family are explicit inductive biases; report them honestly.

## Phase 3 — Native PLN inference pipeline
Use five conceptual layers:
1. **Observations:** piece identity, ownership, turn, relative geometry, occupancy, boundary.
2. **Movement hypotheses:** support for a piece moving by a relative displacement.
3. **Context:** blockers, friendly destination, capture conditions, pawn start conditions.
4. **King exposure:** inferred post-move attack relations, including rays opened by vacating a square. This can be long-range but remains relative and compositional.
5. **Legal-move belief:** integrate movement, context, and king safety using *verified* PLN operators.

Conceptual specification only (NOT executable native PLN syntax):

```
Rook(P) AND OrthogonalRay(M) AND ClearPath(M)
  IMPLIES MovementPatternSupported(M)
MovementPatternSupported(M) AND DestinationPermitted(M)
  AND KingSafeAfter(M) IMPLIES LegalMove(M)
```

**Important:** `AND` above is descriptive. Codex must map it to actual supported multi-premise PLN reasoning and verify truth-value semantics. Chaining nested implications does not automatically implement conjunction. If unsupported, implement a smaller demonstrable native-PLN inference model and explicitly report what remains blocked.

Use native strength/confidence formulas, not arbitrary score multiplication or deterministic thresholds masquerading as probabilities. Thresholds may be used to *display* likely/unlikely/unknown, but cannot replace inference. Confidence should reflect evidence support; strength and confidence must not be conflated.

## Phase 4 — Evidence and learning
Create records with `position_id`, `move_id`, relative feature fingerprint, observed legal/illegal label, source, dependence group, and native observation truth value. Training labels may come from a reference chess library, but the oracle is isolated in `training/` and `evaluation/`.

Use contrastive examples: clear vs blocked rook ray; friendly vs enemy destination; protected vs pinned piece; pawn straight vs diagonal; king safe vs attacked destination. Use native induction/generalization and revision **only if phase 0 verifies them**. Keep evidence provenance and prevent confidence inflation from duplicate, correlated, or translated copies. Negative labels should inform specific contextual hypotheses, not indiscriminately negate all rook movement.

## Phase 5 — Worked rook example
Position A: rook P proposes moving two steps east. The intermediate relative cell is empty; the destination is empty; post-move king safety has supporting evidence. PLN should infer a supported movement pattern and a legal-move belief, with an inspectable proof and truth values.

Position B: same relative displacement, but the intermediate cell is occupied. PLN blocking evidence should lower legality support without changing the general rook geometry hypothesis.

Position C: rook is pinned along a line shielding its king from an opposing sliding attacker. A sideways move matches rook geometry but creates inferred king exposure. PLN should support the exposure proposition and reduce legality belief, **without any external king-in-check gate**.

Position D: translate A to another valid part of the board, preserving relative relations and boundary context. The rule matched, inference path, and truth values should be identical up to renamed entity IDs. This is the central transfer-learning test.

## Phase 6 — Candidate generation and API
Generate bounded candidates from the relative hypothesis vocabulary, **including potentially illegal moves**. The adapter only enumerates; PLN decides. Output for each candidate:

```
{
  "move": "input/output notation only",
  "relative_pattern": {"direction":"E", "distance":2},
  "legal_move_truth_value": {"strength":"native", "confidence":"native"},
  "classification": "supported | contradicted | unknown",
  "proof_trace": ["native rule IDs and premise/conclusion atoms"],
  "evidence_ids": ["..."]
}
```

Define `infer_moves(position)`, `observe_training_example(position, move, label, provenance)`, `explain_move(position, move)`, and `export_rule_beliefs()`. Keep the inference API free of oracle dependencies. Display thresholds are configurable and should be calibrated on held-out positions; abstain when confidence is insufficient.

## Phase 7 — Test strategy
- **Operator smoke tests:** every invoked PLN rule really executes in the pinned runtime.
- **Unit tests:** direction, distance, player-relative forward, occupancy, boundaries, candidate enumeration.
- **Metamorphic tests:** translation of an unchanged relational configuration leaves learned-rule lookup and inference invariant; valid reflections/rotations only when side/orientation semantics are transformed correctly.
- **Contrast tests:** rook clear/blocked, capture/friendly destination, knight jumping, pawn orientation, pinned piece, king exposure.
- **Evidence tests:** duplicated or correlated examples do not improperly raise confidence; conflicting observations revise according to native semantics.
- **Held-out evaluation:** compare complete move predictions with reference labels, tracking precision, recall, calibration, abstention rate, false positives on king-exposure cases, and inference latency.
- **Leakage tests:** prohibit reference-oracle imports or calls from production inference modules; inspect for absolute-square keys in learned rule storage.

Full parity with standard chess is **not** the first acceptance criterion. Castling, en passant, promotion, and checkmate/stalemate require separate state/history modeling. Mark unsupported cases explicitly, never silently claim correctness.

## Implementation sequence and checkpoints

1. **Audit deliverable:** runtime lock, compatibility matrix, native operator tests, list of blockers.
2. **Ontology deliverable:** typed relational atom constructors and observation adapter with tests.
3. **Rook MVP:** candidate rays, occupancy evidence, native PLN inference and proof traces; clear/blocked transfer test.
4. **King-safety MVP:** relative attack and exposure evidence; pinned-rook counterexample without external veto.
5. **Learning MVP:** contrastive labeled evidence, native revision/generalization, dependence handling, confidence evolution.
6. **Other pieces:** bishop, queen, knight, king, pawn; orientation and boundary tests.
7. **Evaluation:** held-out transfer split, calibrated uncertainty, report of failures and unsupported rules.

For each checkpoint, Codex must report exact source files changed, test commands/results, native PLN rules used, sample atom/truth-value traces, and remaining gaps. Do not claim completion when a required rule is absent or a demonstration depends on hidden deterministic chess logic.

## Definition of done for initial model
A user can submit a chess position and inspect PLN truth values and proof traces for candidate moves. The same piece-relative evidence generalizes across board locations without per-square relearning. At least the rook clear/blocked and pinned cases are demonstrated with actual native PLN operators; contradictory and dependent evidence behave as documented. Any unsupported chess features and runtime PLN gaps are explicitly listed.

## Codex kickoff instruction
**Execute all phases in one sustained run, starting with Phase 0.** Inspect the selected repository/runtime, produce the compatibility matrix, and demonstrate the minimum native PLN operator chain. Do not write a custom inference engine, hardcode move legality, or proceed to the full model until the available PLN rule set is verified. If no repository/runtime is specified, inspect the working checkout and installed dependencies, select the best verifiable native PLN implementation, pin it, document the decision, and continue. Ask only if no compatible runtime can be identified and no independent work remains.

---

# Expanded autonomous delivery package

## Phase 8 — Autonomous execution protocol and deliverables

**Do not stop after the compatibility audit or after the rook MVP.** Complete all independent work in one sustained engineering run. Do not request approval for routine local coding, tests, dependency installation, fixture generation, or documentation. Ask before pushing to remotes, external deployment, paid services, or changes to unrelated repositories. If an essential native PLN rule is absent, seek an equivalent composition of *verified* native rules, document the gap, and continue with unaffected components. Never replace native inference with an unannounced hand-written probability formula.

If the target repository is unspecified, inspect the existing checkout and installed dependencies; choose and pin the strongest verifiable SingularityNET/OpenCog PLN implementation. Document exact repository, commit, interpreter, truth-value type, and native operators. If network/dependencies are unavailable, finish independent modules and mark native integration **blocked**, not passed.

Deliver in one run: reproducible build, source code, runtime audit, ontology, hypothesis grammar, all six pieces, king exposure, special-move modeling, evidence ledger, learning pipeline, inference API, CLI, proof inspector, datasets, tests, benchmarks, documentation, and final coverage report. Use small internal checkpoints but avoid interim handoffs.

## Phase 9 — Architecture and code organization

Preserve logical separation even when adapting to an existing repository:

```text
src/domain/          chess state identity and external notation
src/spatial/         local frames, relative offsets, rays and transforms
src/observations/    board-to-atom sensing (never legality decisions)
src/hypotheses/     bounded typed movement hypothesis templates
src/pln/            native runtime bridge and truth-value serialization
src/inference/      grounding, native rule scheduling and proof traces
src/evidence/       source IDs, dependence groups and revision ledger
src/learning/       native PLN learning/revision orchestration
src/api/            infer/explain/observe/train/export/import
src/cli/            inspection, training and benchmarking commands
training/           reference-oracle labeling, isolated from inference
evaluation/         reference-oracle scoring, isolated from inference
fixtures/           contrastive, symmetry and edge-case positions
configs/            pinned runtime and reproducible experiment settings
tests/              unit/native/integration/metamorphic/leakage/e2e
docs/               architecture, decisions, semantics and reports
artifacts/          checkpoints, native traces, metrics and model cards
```

Add dependency-graph checks preventing production inference from importing the reference chess oracle. Ban production calls equivalent to `legal_moves`, `is_check`, `is_attacked`, and piece-specific legality gates. A host-language *structural* successor-state transformation is permissible, but a chess legality conclusion is not.

Provide stable typed contracts:

```text
infer_moves(position, checkpoint, options) -> InferenceResult
explain_move(position, move, options) -> NativeProofAndEvidence
observe_example(position, move, label, source, dependence_group) -> Receipt
train(dataset, checkpoint, options) -> TrainingReport
export_model(path) / import_model(path) -> ModelManifest
inspect_hypothesis(id) -> BeliefAndProvenance
compare_transforms(position, transform) -> InvarianceReport
```

All outputs must preserve raw native truth values, matched rule IDs, evidence lineage, runtime version, model version, inference budget and truncation status. Distinguish supported, contradicted, unknown and incomplete. Do not treat lack of evidence as a negative conclusion.

## Phase 10 — Complete piece coverage and stateful chess features

Implement the core pieces in this sequence, without waiting for user feedback between them:

1. Rook and bishop: relative cardinal/diagonal ray composition, clear/blocked paths, friendly/enemy destination.
2. Queen: reuse the two ray families rather than duplicate per-square rules.
3. Knight: relative `(1,2)` and `(2,1)` leaps, sign variants, and obstruction counterexamples.
4. King: one-cell relative moves, opponent attack relations, adjacent kings, and self-check exposure.
5. Pawn: color-oriented forward, diagonal captures, first-move two-step, intermediate occupancy, promotion choices.
6. State/history: castling rights, attacked transit cells, en-passant target, en-passant capture removal, and promotion successor states.
7. Combined legality: pins, discovered attacks, double check, capture of checking piece, blocking a check, king-exposure after a proposed move.

Treat every chess-specific condition as a **probabilistic hypothesis/inference target**, not a Boolean veto. Native PLN support determines which can be completed. For each feature produce a minimal positive example, contrastive negative, proof trace, and status: `native-end-to-end`, `native-partial`, `blocked-by-native-rule`, or `not-implemented`. FEN alone does not preserve complete historical evidence; unknown history must remain unknown.

## Phase 11 — Evidence, learning and provenance

Implement an append-only, replayable ledger containing: `evidence_id`, `position_id`, `candidate_id`, relative-feature fingerprint, legal/illegal observation, source, native observation TV, dependence group, transformation lineage, timestamp/sequence, and model/runtime version. Use idempotency keys; re-ingestion of identical evidence must not inflate confidence.

Build contrastive training pairs: clear versus blocked rook ray; friendly versus enemy destination; pinned versus unpinned; king entering attacked versus safe cell; knight leap with and without intermediate occupants; white/black pawn orientation; pawn double-step with changed history; castling rights present/absent; en-passant target present/absent. Ensure illegal labels update the *relevant context* rather than globally discrediting a geometry rule.

Native induction and revision must be verified in the runtime. If unavailable, report that learning capability as blocked and demonstrate supported native evidence operations only. Record actual before/after truth values from execution, never invented numerical examples. Group correlated examples (translations, augmentations, repeated observations, shared game history) so independence assumptions are respected. Export/import model checkpoints and support deterministic replay, versioning and rollback.

## Phase 12 — Dataset and experiment factory

Generate reproducible fixtures with fixed seeds, exact oracle version, dataset hashes and manifests. Use the reference engine **only in training/evaluation** to label candidate moves and score predicted move sets. Produce both synthetic controlled contrasts and varied multi-piece positions. Split by structural position family and board region, not randomly by individual moves, to avoid leakage.

Include: board edges, capture versus friendly destination, all ray lengths, pins in several orientations, discovered attacks, double check, king adjacency, promotion, castling through attack, en-passant opening a ray, positions with no legal moves, and incomplete-observation cases. Maintain separate training, validation, held-out transfer, and adversarial test sets.

## Phase 13 — Transfer-learning experiments and ablations

For any valid translation `T` preserving relative observations and contextual rights, verify:

```text
matched_rules(T(S),T(M)) == matched_rules(S,M)
proof_graph(T(S),T(M)) ≅ renamed(proof_graph(S,M))
native_TV(T(S),T(M)) ≈ native_TV(S,M)
```

Exclude transformations crossing board boundaries. For rotations/reflections, transform color, orientation, castling/en-passant semantics where applicable; do not assume arbitrary rotations are legal symmetries of chess state.

Compare the relative learner against: (a) an **evaluation-only** absolute-square-keyed baseline, (b) geometry-only priors, (c) a weaker-prior hypothesis grammar, (d) model without king-exposure inference, (e) model without dependence-aware revision, and (f) model without contextual occupancy hypotheses. Report accuracy and sample efficiency, not merely successful demonstrations.

## Phase 14 — Metrics, calibration and runtime budgets

Measure move precision/recall/F1, exact legal-move-set accuracy, false-legal rate (especially self-check), per-piece performance, unknown/abstention coverage, transfer gap, evidence-to-competence sample efficiency, latency p50/p95/p99, native rule invocations, grounded atom count, peak memory and checkpoint size.

Native PLN **confidence is not automatically a calibrated probability of legality**. If reporting Brier score, log loss, or calibration error, first define and validate a mapping from native strength (and optionally confidence) to predicted probability on held-out validation data. Report raw native TVs alongside calibrated outputs. Never modify inference with a hidden deterministic legality threshold; a configurable presentation threshold may classify supported/contradicted/unknown without changing beliefs.

Define inference budgets and return `incomplete` on exhaustion. Compare single-candidate and full-position inference costs, and report scaling with pieces, candidate count, ray length, and native grounding depth.

## Phase 15 — User-facing inference inspector

Implement a CLI first; add a lightweight local web inspector if dependencies permit. It should accept FEN, show the board and candidate moves, and let a developer select a move to inspect its piece-relative features, matched hypotheses, raw PLN TVs, proof graph, evidence IDs, counterevidence, runtime operator names, and whether inference was truncated. Add a before/after comparison for learning updates and a translated-position comparison. The interface is a visualization of actual native inference, never a second chess engine.

Suggested CLI commands (adapt syntax to repository conventions):

```bash
pln-chess runtime-audit
pln-chess inspect --fen '<FEN>' --move e2e4
pln-chess infer --fen '<FEN>' --format json
pln-chess train --config configs/training.yaml
pln-chess evaluate --split heldout-transfer
pln-chess invariance --fixture rook-clear --transform translate
pln-chess benchmark --config configs/benchmark.yaml
pln-chess report --output artifacts/final-report.md
```

Provide actual working examples in the README, not hypothetical commands unless clearly labeled.

## Phase 16 — Required native proof demonstrations

Ship machine-generated traces for at least ten scenarios: (1) rook clear ray, (2) blocked ray, (3) enemy versus friendly destination, (4) pinned rook exposing its king, (5) knight jumping, (6) pawn orientation transfer, (7) king stepping into attack, (8) castling rights and attacked transit square, (9) en passant removing a different square's pawn and potentially exposing a ray, and (10) evidence revision with repeated/correlated samples.

For each trace record input state, relative observation atoms, matched hypothesis IDs, native rule names and invocations, premise/conclusion TVs, provenance, final legal/illegal beliefs, and comparison to reference oracle **outside** the inference path. If a native rule is missing, preserve the fixture and mark the trace `blocked`, never fabricate its values.

## Phase 17 — Testing matrix and acceptance gates

### Native rule tests

Every invoked native PLN operator has an executable smoke test pinned to its source/version. Check variable grounding, negation semantics, conflicting evidence, dependence assumptions, and native revision behavior. Do not label a conceptual rule as tested.

### Spatial and metamorphic tests

Check all eight directions, pawn-relative forward for both sides, local offset sign conventions, ray step ordering, boundaries, identity renaming, translation invariance, valid reflections, and counterexamples where transformation changes castling/history semantics. Assert no square literals or position IDs appear in learned rule keys.

### Chess contrast tests

Test all piece families, own-piece capture prohibition, blockers, checks, pins, discovered attacks, promotion choices, en passant, castling, and incomplete history. Require a documented coverage status for every case; do not silently omit failing special moves.

### Learning and leakage tests

Verify replay idempotency, independent versus correlated evidence, model import/export consistency, no oracle imports or runtime calls from production inference, and no hidden deterministic `is_legal`/`is_check` implementation. Verify train/test separation by structural family and prevent symmetry augmentation leaking between splits.

### End-to-end tests

For a fresh checkout, one documented bootstrap command installs dependencies, runs native smoke tests, generates fixtures, trains a small model, infers a complete candidate set, prints a proof, and runs a held-out transfer evaluation. If a native runtime limitation blocks any part, the command exits with an explicit actionable diagnostic and the report identifies which parts ran.

## Phase 18 — Required reports and artifact formats

Produce:

- `docs/pln-compatibility-matrix.md`: verified operator symbols, source paths, semantics, tests and unsupported capabilities.
- `docs/architecture.md`: module boundaries and data flow; exact boundary between observed facts and learned chess rules.
- `docs/spatial-semantics.md`: coordinate frames, equivariance assumptions and exceptions.
- `docs/learning-semantics.md`: priors, evidence assignment, native revision and dependence policy.
- `docs/chess-coverage.md`: feature-by-feature status and minimal repro.
- `docs/decisions.md`: decisions made without handoff, alternatives and rationale.
- `docs/experiments.md`: datasets, seeds, metrics, ablations and transfer tests.
- `docs/model-card.md`: what was seeded versus learned, supported use cases, limitations and calibration caveats.
- `docs/final-report.md`: commits/files, commands/results, actual numeric TV traces, metrics, failures, next steps.
- `artifacts/`: pinned runtime manifest, dataset manifests, checkpoints, JSON proof traces, benchmark tables, and generated reports.

A passing test suite alone is not enough. The final report must explicitly distinguish **native PLN inference**, **host-language structural processing**, **reference-oracle labeling**, and **features blocked by missing native operators**.

## Phase 19 — Final definition of done

The full assignment is complete when a developer can build the project, train or replay evidence, submit a position, inspect candidate legal-move beliefs and native proof traces, and evaluate the learned model on unseen board locations without any square-specific rule relearning. All six piece types have tested relational hypotheses; king safety and special moves have either working native proofs or documented blockers with reproducible fixtures. Native truth values and evidence provenance survive serialization. A transfer benchmark and an ablation against an absolute baseline demonstrate the effect of the representation. Tests enforce absence of a deterministic legality gate in production.

**Do not assert full chess correctness unless the held-out evaluation actually supports it.** A complete engineering delivery may legitimately report unsupported native PLN operations, incomplete chess coverage, or weak learning performance. Evidence-backed limitations are preferable to a falsely complete system.

## Final instruction to Codex — execute, don't hand off

> Treat this document as one consolidated authorization for local engineering work. Start by auditing the available native SingularityNET/OpenCog PLN runtime, then implement the architecture, spatial ontology, inference and learning pipeline, all piece families, stateful features, evaluation infrastructure, test suite, inspector, and final report. Do not stop after the audit or any intermediate milestone. Make reasonable local choices and record them. Do not invent PLN inference rules or insert a conventional chess legality engine into production. If a native capability is missing, implement the largest truthful subset and continue independent work. Finish with exact commands, verified results, traces, coverage, blockers, and a prioritized next-step list. Request user input only for a genuinely blocking decision or an external action requiring authorization.
