# PLN Chess — Cycle 3 Consolidated Engineering Implementation Brief

**Target repository:** `machieke/pln-chess`  
**Expected starting commit:** `f80b27dc41e591c90ed7456f3730fb5c0ea5d28e`  
**Assignment:** Implement, validate, document, and locally commit the entire feasible Cycle 3 scope without routine intermediate handoffs.  
**Status of input evidence:** The Cycle 2 figures below were reported by Codex/user; independently reproduce them before treating them as verified. The target commit was reported as local and not pushed. Do not assume GitHub's default branch contains it.

## 0. Mission and non-negotiable scientific principle

Build a **piece-relative, locality-first, probabilistic chess-legality learner** that composes reusable PLN-derived beliefs into context-sensitive move assessments. Chessboard squares are **state input/output coordinates**, not constants in learned movement rules. The aim is to learn general local relationships transferable across translations, color orientation, unrelated-piece changes, distances, and unseen combinations of conditions. The eventual chess-playing system will depend on this learned legality substrate; **do not add strategic evaluation, minimax, MCTS, or an engine-based legality gate** in this cycle.

All probability-bearing chess conclusions must be produced through **verified native SingularityNET/OpenCog PLN rules** available in the pinned runtime, with provenance and actual truth values. Structural parsing, relative geometry sensing, candidate enumeration, scheduling, caching, and test-only oracle labeling may be implemented in the host language, but may not silently decide legality. Do not call an ad hoc weighted heuristic, Python Bayesian combination, confidence multiplication, Boolean conjunction, or chess-engine validation “PLN.” If the runtime cannot support a desired composition, provide a bounded, scientifically honest partial implementation and executable proof of the missing capability.

## 1. Baseline and previous-cycle evidence

Reported Cycle 2 local commit: `f80b27dc41e591c90ed7456f3730fb5c0ea5d28e`, parent baseline `64754bb`. Working tree was clean; no push occurred. Cycle 2 reportedly introduced versioned local hypotheses, separate exposure reasoning, 14 experimental native-induction hypotheses, proof-preserving caching, and inspector comparisons.

On **40 independent held-out positions, 2,635 candidates**, reported B1/B2 precision **97.25%**, recall **95.53%**, abstention **17.69%**, exact legal move sets **42.50%**. Frozen Cycle 1 recall **0%** and abstention **78.86%**. There are **23 false-positive self-check moves**, and adversarial precision is **89.39%**. Induction did not improve classification over B1. Three transfer motifs were reported: rook obstruction, bishop movement, queen movement. One rook transfer `c2e2` → unseen `a6e6` had TV `(0.003268, 0.877762)` without exact-context match. The optimized 214-candidate schedule reportedly improved from **20.58 s / 13,742 native calls** to **1.50 s / 158 calls** cold, **0.94 s** warm, preserving TV/proof/rule/evidence parity.

**Do not use these as unverified pass/fail baselines.** Capture their source artifact paths, dataset hashes, exact split IDs, hardware, runtime pins, configs, threshold choices, and reproducibility commands. If the target commit is unavailable locally, do not reconstruct it from a stale public branch; stop with an exact missing-commit diagnostic. If available, work from it.

## 2. Execution contract: minimize back-and-forth

1. Inspect repository source, commit, branch, tests, generated artifacts, docs, and existing engineering reports before modifying code. Record a baseline receipt.
2. Plan internally and implement the **entire feasible scope** in one integrated effort. Run independent tasks in parallel where safe; keep shared ontology/runtime changes coordinated.
3. Make ordinary technical choices autonomously. Do not stop after a feasibility audit or after completing one package. Continue other work if one research track is blocked.
4. Preserve existing public APIs, checkpoint compatibility or explicit migrations, evidence lineage, audit trails, and production/oracle separation.
5. No push, deployment, remote mutation, destructive history rewrite, external paid services, or unapproved credential use. Local commits are authorized. No need to ask approval for local code changes, tests, artifacts, or commits.
6. Never invent a supported PLN operator or silently substitute a custom truth formula. Pin and audit any proposed new upstream implementation separately; retain a reproducible default path on the existing pinned runtime.
7. Every claim of improved legality or transfer must be tied to held-out evaluation, with false-positive counts and abstention visible. Unknown/incomplete is a first-class outcome.
8. Commit all authored source/tests/docs/config changes locally in logically grouped commits if helpful, then provide the final HEAD, parent, clean/dirty state, commands, and artifact locations. Generated artifacts should follow existing repository conventions.
9. Escalate only if a critical dependency is unavailable, the starting commit cannot be located, or an action exceeds the stated authorization. Otherwise deliver a complete partial solution with documented blockers.

## 3. Work packages

### C3-01 — Reproduce and freeze Cycle 2

- Verify HEAD/commit and clean state; capture runtime lock, PLN source hash, PeTTa/SWI-Prolog/Python versions, dataset identity and fixture manifests.
- Reproduce the Cycle 2 B1/B2 baseline and optimization parity on identical datasets and thresholds. Preserve a frozen baseline model and outputs; do not train on the held-out split.
- Produce a **per-candidate error ledger** with FEN, candidate move, piece, oracle label, predicted class, raw `(strength, confidence)`, matched hypotheses, proof IDs, evidence IDs, abstention reason, and split/family identifiers.
- Separate false positives into: self-check, illegal capture/occupancy, castling, en passant, promotion, boundary, history, and other; allow multiple tags but distinguish root causes.
- Create `docs/cycle3-baseline.md` and machine-readable `artifacts/cycle3/baseline.json` (or equivalent consistent repository locations).

**Exit:** Exact provenance and reproducible baseline; report any divergence before continuing, but do not automatically stop.

### C3-02 — Native PLN compositional capability investigation

- Audit the **actual** pinned PLN source, not assumed PLN capabilities. Inventory verified signatures, domains, truth formulas, stamp behavior, premise requirements, and inference results for modus ponens, deduction, induction, revision, negation, inheritance, and any available conjunction/equivalence/similarity mechanisms.
- Execute minimal MeTTa/PeTTa probes for: independent premises A and B; explicit `And(A,B)` observations; nested implications; variable binding and grounding; conditional chain composition; multiple counterevidence paths; contradiction and evidence overlap; low/high/zero confidence and degenerate values.
- Distinguish: (a) native verified compositional inference, (b) native verified inference from a **joint sensor observation**, (c) host-computed aggregation, and (d) unsupported. Do not conflate these.
- Explore upstream alternatives **only as separate opt-in experiments**. Require source pinning, license, runnable proof, TV behavior, and regression comparison before adoption. Do not transplant unverified conjunction formulas.
- Deliver a compatibility matrix and decision record: chosen inference route, semantic limitations, rejected alternatives, and exact runnable probes.

**Exit:** A documented, executable composition boundary that constrains all further claims.

### C3-03 — Decompose local conditions into stable relational predicates

Refactor overly specific context keys into a **versioned hierarchy of reusable local propositions**. Suggested families (adapt to existing ontology):

- `PieceMovementFamily(pieceType, movementClass)` and owner-relative `Offset/Direction/Distance`.
- `RayCellAt(relativeStep, occupancyClass)`, `RayInterveningOccupancy`, `FirstBlocker`, `DestinationRelation`.
- `CaptureRelation`, `FriendlyDestination`, `OpponentDestination`, `BoundaryRelation`.
- `PawnForward`, `PawnStartEdgeDistance`, `PawnPromotionEdge`, `EnPassantRelativeTarget`.
- `RelativeAttackGeometry`, `AttackRayObstruction`, `KingExposureAfterMove`, `KingEscape/CheckResolution`.
- `CastlingTransitRelation`, `CastlingRightObservation`, `CastlingRookRelation`.

The names are **ontology proposals, not new PLN inference operators**. Grounding them as sensor facts must not hard-code chess legality. Ensure context identities do not contain absolute file/rank, piece IDs, move IDs, unrelated opponent lists, or position hashes. Keep absolute identifiers in trace metadata only. Design several levels of abstraction with explicit backoff/selection, but avoid unjustified probabilistic blending across levels.

**Exit:** Stable versioned schema, migration strategy, readable pre-hash descriptors, invariance tests, and no loss of proof provenance.

### C3-04 — Compositional movement and obstruction knowledge

- Learn and apply generalized rook/bishop/queen ray motifs across **unseen distances, blocker locations, destination occupants, and unrelated pieces**. Demonstrate that learning a blocker at one ray step can inform other ray lengths without memorizing a full occupancy vector.
- Learn knight jumps and king adjacency using piece-relative displacement; show unrelated occupancy changes do not alter the relevant learned hypothesis.
- Distinguish *movement geometry* from *path obstruction*, *destination occupancy*, and *king safety*. Never punish a general movement pattern solely because a specific instance is illegal for a contextual reason.
- Use verified PLN operations for inferential steps; if composition is not available, evaluate separately learned conditional layers and label final output as partial rather than pretending to prove their conjunction.
- Add proof examples where one training motif transfers to at least **three independent configurations** (different distance, location, opponent constellation), with no exact-context fallback.

**Exit:** Native traces show which reusable hypotheses caused the prediction and whether their combination was truly native.

### C3-05 — King safety and exposure reasoning (highest priority)

- Analyze all **23 reported false-positive self-check moves** individually and classify underlying failure modes. Include a fixture for each distinct mechanism.
- Model attack relationships from the **post-move** position without using a chess engine in production: sliding rays, knight leaps, pawn orientation, king adjacency, discovered attacks, pins, removal of blockers, captures of checking pieces, interposition, king escapes, and double check.
- Treat attack evidence, exposure, and negative-legality as separate PLN propositions with transparent confidence propagation and dependence stamps.
- Audit the current evidence-choice policy. A high-confidence context-positive prediction must not automatically erase strong contradictory king-exposure evidence; conversely, weak attack suspicion must not become a hard-coded veto. Compare native-supported arbitration variants, with tests for contradiction and shared evidence.
- Never infer “king safe” merely from absence of known attack evidence. Unknown attacks must remain unknown unless a verified closed-world assumption is explicitly represented and justified.
- For every false-positive self-check, record whether it is resolved, becomes abstention, or remains a false positive; avoid trading errors for blanket abstention without reporting coverage.
- Add focused tests for pinned rook/bishop/queen/knight/pawn, diagonal and orthogonal discovered attacks, double check, checking-piece capture, legal check block, king captures, castling transit attacks, and en passant opening a king attack ray.

**Exit:** Material reduction in false-positive self-checks on a frozen adversarial set, with no silent deterministic king-safety gate and no misleading proof claims.

### C3-06 — Special moves and temporal context

- Preserve and extend castling rights, rook/king move history where known, rook presence, transit exposure, and queen-side path details.
- Preserve en passant’s previous-double-push dependency and post-capture removal effects; distinguish known, unknown, and contradictory history.
- Represent all four promotions as candidate state transitions, without treating a promotion option as automatically legal.
- If FEN is insufficient to prove a historical claim, abstain or require explicit additional evidence. Do not invent game history.
- Keep repetition/fifty-move adjudication outside *move-legality learning* unless implemented as a clearly separate optional module.

**Exit:** Independent tests for valid, invalid, and history-unknown cases, with evidence-backed outcomes.

### C3-07 — Make native induction consequential, or diagnose why it is not

- Reproduce the 14 Cycle 2 induction experiments. Audit actual marginals, truth-value domains, directionality, population definitions, independence assumptions, evidence overlap, and hypothesis promotion/selection.
- Build a finite **population of relative motif observations** with a documented sampling frame and estimates for native induction’s required marginals. No hidden labels or test-set leakage.
- Execute native induction on candidates that could generalize across piece family, ray distance, obstruction category, and color-relative orientation.
- Feed verified induced hypotheses into the same native inference scheduler through an explicitly controlled `induction-enabled` model variant. Keep the `induction-disabled` baseline identical otherwise.
- Require proof traces showing *which induced hypothesis actually changed a previously unknown/incorrect prediction*; distinguish inference novelty from duplicate or dominated hypotheses.
- Evaluate precision, recall, exact move sets, abstention, calibration, runtime, and negative transfer. If induction still has no benefit, provide a concrete failure analysis rather than force an improvement.

**Exit:** Integrated and measured native induction, or a rigorous evidence-backed account of its noncontribution.

### C3-08 — Evidence dependence, conflict, and uncertainty

- Retain append-only provenance, idempotency, checkpoint replay, and rollback. Check for duplicate evidence through transformations, shared positions, repeated game trajectories, and reused labels.
- Compare conservative one-per-group selection with **only native-supported** alternatives; do not create unsupported correlated-evidence truth formulas.
- Test positive and negative examples for the same abstract motif; prevent a single illegal contextual move from globally discrediting geometry.
- Track separate sensor reliability, rule TV, inferred conclusion TV, and post-hoc empirical calibration. Do not call PLN confidence a calibrated probability of correctness.
- Test missing squares, uncertain ownership, unknown history, incomplete successor state, contradictory observations, zero confidence, and low-confidence evidence.

**Exit:** Stable, inspectable uncertainty behavior and no double-counting in proofs.

### C3-09 — Harder transfer-learning curriculum

Construct **independent**, stratified datasets with no structural-family or game leakage. Keep frozen Cycle 2 splits for backward comparison and create a new Cycle 3 evaluation split. Include:

1. Translation, reflection, and owner-relative color flip, only when semantics are preserved.
2. Held-out ray lengths and blocker distances.
3. Unrelated-piece perturbations and opponent-set perturbations.
4. Held-out combinations of previously learned constraints (e.g., legal geometry + newly introduced king exposure).
5. Cross-piece ray-family transfer where justified (rook/bishop/queen) and explicit negative-transfer checks.
6. Adversarial pins, discovered attacks, double check, check evasions, castling, en passant, promotions.
7. Sparse training and learning-curve studies (1, 2, 4, 8, … independent evidence groups).
8. Full-position legal-move-set evaluation, not just focus moves.

Maintain oracle labels **only in training/evaluation**, never production inference. Include dataset hashes, generation seeds, overlap audit, fixture validity checks, and per-family support counts.

**Exit:** Reproducible datasets that test compositional generalization, not only translation of the same complete motif.

### C3-10 — Experiments, baselines, and ablations

Compare at minimum:

- `B0`: frozen Cycle 1 if reproducible.
- `B1/B2`: frozen Cycle 2 reference variants.
- `C3-local`: new hierarchical/local representation without induction.
- `C3-exposure`: C3-local plus revised exposure reasoning.
- `C3-induction`: C3-exposure plus integrated native induction.
- `C3-full`: all supported features.
- Ablations: no obstruction abstraction, no exposure reasoning, no induction, no confidence arbitration changes, no dependence tracking, and exact-context-only.

For each model report: legal precision/recall/F1; illegal-class false positives; exact legal move sets; abstention; per-piece and per-feature metrics; self-check false positives; adversarial precision; calibration/Brier/ECE where statistically meaningful; inference time, native call counts, grounded atoms, memory, checkpoint size, and evidence count. Report denominators and confidence intervals or uncertainty ranges when feasible. Do not hide failures behind aggregate accuracy or out-of-board negatives.

**Exit:** Machine-readable comparison tables and a concise interpretation of *what improved and why*.

### C3-11 — Preserve and extend proof-preserving optimization

- Preserve Cycle 2’s batched/cached native schedule and prove equivalence on a broad fixture corpus before/after changes: raw TVs, classification, matched rule IDs, evidence IDs, native expressions, and proof DAG topology (modulo stable renaming).
- Cache only semantically valid immutable computations, with keys including runtime, grammar, checkpoint, evidence, relevant local observations, and model variant. Test cache invalidation after new evidence, rollback, runtime change, and variant switch.
- Deduplicate shared local propositions and opponent attack frames; batch native calls where supported. Do not merge distinct evidence streams or hide inference steps.
- Benchmark cold and warm paths separately; compare same model/same hardware/same candidates, including 214-candidate regression scenario and harder positions.
- Set configurable time/native-call/memory budgets. On exhaustion, return explicit `incomplete` with partial proofs, not a false legality conclusion.

**Exit:** Correctness parity and no uncontrolled performance regression; any slower compositional mode must be separately measured and explained.

### C3-12 — API, CLI, inspector, and human auditability

Extend existing surfaces rather than replace them. Support:

- Move explanation with independent geometry, obstruction, destination, attack, exposure, history, and final-legality beliefs; each carries raw TV and provenance.
- Hierarchical rule lookup and explanation of why a general rule transferred to an unseen instance.
- A clear distinction among `native-compositional`, `native-conditional`, `native-partial`, `unknown`, and `incomplete` where justified by executed evidence.
- Counterfactual local perturbations: add/remove a blocker, move an unrelated opponent, flip orientation, remove a castling right, and compare proof changes.
- Baseline-vs-Cycle-3 side-by-side prediction/proof comparison.
- Inference-budget and cache diagnostics; model/runtime/evidence version display.

Add documented CLI commands, example JSON, and UI smoke tests. The inspector must display the model’s actual conclusions, not compute legal moves independently.

**Exit:** Reproducible, inspectable explanations for both successes and errors.

### C3-13 — Testing, robustness, and reproducibility

- Maintain existing test suite and add unit, property-based/metamorphic, integration, native-runtime, proof-parity, checkpoint migration, and adversarial tests.
- Verify source/oracle isolation by disabling chess-oracle imports during production inference.
- Run from a clean checkout using pinned dependencies and documented prerequisites. Preserve hash verification and fail explicitly when native runtime unavailable; never substitute Python PLN.
- Include a clean-copy bootstrap test and evidence receipts. If a platform-specific native prerequisite cannot be provisioned, identify it precisely and still run independent static/unit checks.
- Test rollback, replay, corrupted evidence, conflicting idempotency keys, unknown inputs, timeout handling, invalid FEN, and candidate-boundary cases.

**Exit:** Reproducible suite, clean-install receipt, documented unresolved environmental failures.

### C3-14 — Documentation, final report, and local delivery

Produce/update:

- `docs/cycle3-architecture.md`: ontology, inference paths, and composition boundary.
- `docs/cycle3-native-pln-audit.md`: actual operators, probes, and limitations.
- `docs/cycle3-learning-semantics.md`: induction, marginals, dependence, conflict, calibration.
- `docs/cycle3-experiments.md`: split design, leakage audit, metrics, ablations.
- `docs/cycle3-error-analysis.md`: every self-check false positive and remaining failure classes.
- `docs/cycle3-final-report.md`: results, regressions, unresolved research questions, exact commands and artifact links.
- Machine-readable manifest with commits, runtime pins, dataset/model hashes, commands, tests, proof samples, benchmark results, and all known exceptions.

Locally commit authored changes. Do **not push**. Summarize HEAD, parent, clean tree, scope completed/partial/blocked, measurements, and the most important next research questions.

## 4. Mandatory acceptance gates versus stretch goals

### Mandatory gates (engineering integrity)

- All prior tests pass or documented regressions have justified fixes; new native probes and transfer tests execute.
- No chess oracle or deterministic legality veto in production inference.
- All claims of PLN inference correspond to audited, executed native operators and inspectable proof nodes.
- No absolute square constants in learned rule antecedents; coordinates permitted only in state I/O and observation metadata.
- Evidence replay/checkpoint/version integrity preserved, with migration where necessary.
- Frozen baseline and Cycle 3 evaluation reproducible, no held-out leakage.
- Full metrics include abstention, self-check false positives, and exact legal-move-set accuracy.
- Proof-preserving optimization validated; incomplete inference is explicit.
- Final documentation and local commit completed, without push.

### Quantitative stretch goals (not reasons to falsify or abandon work)

- Reduce frozen 23 self-check false positives to **zero**, or report each remaining one and abstention tradeoffs.
- Raise exact held-out move-set accuracy from **42.5% toward ≥70%** on the identical 40-position frozen split.
- Maintain held-out legal precision **≥97%** and recall **≥95%**, while reducing abstention where possible; show Pareto tradeoffs if targets conflict.
- Raise adversarial precision from **89.39% toward ≥95%**.
- Demonstrate **at least five** independently transferable relational motifs, including at least one king-safety motif and one combined-constraint challenge.
- Show at least one **genuinely classification-changing** native induction example on held-out data, or produce a rigorous negative result.
- Preserve the optimized 214-candidate inference path within a defensible performance envelope; target **≤2× Cycle 2 cold runtime** for the same semantics, and report extra cost of new compositional modes separately.

Do not claim all stretch goals were met without executed evidence. Do not optimize by labeling everything unknown. If zero self-check false positives are obtained by abstaining, report that separately from correct negative classifications.

## 5. Architectural decision rules

1. **Relative before global:** Local predicates must remain reusable under valid board transforms. Board edge and special history are explicit relative/contextual observations, not ignored.
2. **Learned before hard-coded:** Candidate enumeration may seed geometric families, but must not determine legality. Disclose every seeded inductive bias.
3. **Native before approximate:** Use only audited PLN operators for probabilistic inference. Host-side filtering for compute budget must not change semantics without a disclosed approximation mode.
4. **Compositional if verified; partial if not:** A categorical joint observation is not proof of conjunction. Do not silently invent an AND rule.
5. **Evidence before confidence:** Report sources, dependence groups, native TVs, and conflict behavior. Confidence is not automatically calibrated correctness probability.
6. **Generalization before training fit:** Independent structural splits are the main scientific result; perfect training-set accuracy is not sufficient.
7. **King safety before strategy:** No strategic move selection, game-playing engine, or tactical scoring until the legality substrate is materially more reliable.

## 6. Suggested execution order (without stopping for approval)

- **Stage A:** C3-01/C3-02 baseline + native capability probes.
- **Stage B:** C3-03/C3-04 ontology and reusable local movement knowledge.
- **Stage C:** C3-05/C3-06 king exposure and temporal special-move semantics.
- **Stage D:** C3-07/C3-08 induction and evidence/conflict research.
- **Stage E:** C3-09/C3-10 frozen/new split experiments and ablations.
- **Stage F:** C3-11/C3-12 optimization and inspection.
- **Stage G:** C3-13/C3-14 clean reproduction, reports, local commits.

Stages may overlap when safe. Keep an internal task ledger and resolve ordinary implementation issues without requesting further instructions.

## 7. Final response contract for Codex

Return one concise but complete delivery report containing:

1. **Git status:** starting commit, final commit SHA, branch, clean/dirty status, confirmation of no push.
2. **Work-package matrix:** C3-01 through C3-14 as complete/partial/blocked with paths to evidence.
3. **Baseline-vs-Cycle-3 table:** exact split denominators, precision, recall, F1, abstention, exact move sets, adversarial precision, self-check false positives.
4. **Transfer evidence:** five representative unseen motifs with training/test provenance and native TVs.
5. **PLN semantics:** audited native operators used, whether conjunction/composition is genuinely supported, induction’s measured effect, and any remaining blocked semantics.
6. **Performance:** cold/warm latency, native calls, cache parity, proof identity, memory and model size.
7. **Validation:** test counts, clean bootstrap status, dataset/model/runtime hashes, unresolved errors.
8. **Next priorities:** no more than five, ordered by scientific importance.

**Success means a defensible improvement in reusable probabilistic relational reasoning, not merely a larger chess-rule lookup table.**
