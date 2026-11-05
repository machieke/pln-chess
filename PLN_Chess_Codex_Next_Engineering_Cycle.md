# PLN Chess — Consolidated Codex Engineering Brief, Cycle 2

**Repository:** https://github.com/machieke/pln-chess  
**Target:** existing default branch, preserve existing code and provenance  
**Assignment:** implement, test, benchmark, document, and commit the next research-engineering cycle in one autonomous pass  
**Date:** 2026-11-05  
**Priority:** generalizable piece-relative probabilistic rule learning, not chess playing strength

## 0. Executive mandate

Continue the existing `pln-chess` implementation. Do **not** rebuild the repository or replace native PLN with a bespoke probabilistic classifier, deterministic legality gate, Python chess-engine inference, neural network, or brute-force program synthesis. Deliver a functioning, reproducible Cycle 2 implementation that learns reusable relative movement constraints from evidence, exposes the actual native PLN proof paths, and demonstrates meaningful improvement on **independent, structurally held-out** chess positions.

Complete the work as one substantial engineering package. Do not stop after auditing, planning, implementing one rook case, or reporting that native conjunction is missing. Pursue verified native alternatives and implement the strongest defensible bounded solution available. If full compositional legality cannot be achieved with the pinned native operators, deliver measurable hierarchical relational generalization with explicit remaining gaps. Never represent host-side feature assembly as a PLN proof.

**Non-negotiable scientific distinction:** a movement relation learned at one location should transfer to a different location *and to novel irrelevant board context*, without needing an exact fingerprint match. Controlled translation of an identical full configuration is a necessary but insufficient demonstration.

## 1. Grounded starting point and baseline

Before modifying code, inspect the current HEAD and record its commit SHA, runtime locks, working tree, tests, artifacts, and relevant files. Do not assume these descriptions remain exact; confirm against source.

Existing architecture (as reviewed):

- Native `trueagi-io/PLN` at `4405956947c4b53c7ff01bd565aa3b114bc970a1`, executed through pinned PeTTa at `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`, with SWI-Prolog 10.0.1 and Python 3.12.12.
- `src/pln_chess/hypotheses/__init__.py` enumerates bounded geometrically plausible candidate offsets for six piece types, with special-move proposals.
- `src/pln_chess/observations/__init__.py` hashes a context containing movement pattern, path occupancy, destination, boundary and special-move metadata, and the complete list of post-move opponent-to-king frames.
- `src/pln_chess/learning/__init__.py` performs native revision over typed categorical hypotheses. Native induction is audited, but not integrated into learning.
- `src/pln_chess/inference/__init__.py` schedules native modus ponens, negation elimination, and confidence choice. It cannot claim compositional conjunction-based legality.
- Evidence ledger, checkpoints, proof inspector, CLI, reproducible fixtures, oracle isolation, ablations, and performance measurements already exist.

Reported baseline from `docs/final-report.md` (verify, reproduce, and distinguish reproduced from previously reported):

| Split | Precision | Recall | F1 | Exact legal move sets |
|---|---:|---:|---:|---:|
| Train | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Controlled transfer | 1.0000 | 0.9474 | 0.9730 | 0.0000 |
| Heldout transfer | n/a | 0.0000 | 0.0000 | 0.0000 |
| Validation | n/a | 0.0000 | 0.0000 | 0.0000 |
| Adversarial | 1.0000 | 0.2222 | 0.3636 | 0.4000 |

The previous benchmark recorded ~24 seconds for a 214-candidate full-position batch with ~12,051 native invocations; 61 tests passed. Treat all numbers as historical reported evidence until reproduced.

Create `artifacts/cycle2/baseline/` containing immutable snapshots of test results, dataset hashes, configuration, runtime versions, metrics, benchmark results, and original model/checkpoint references. Never silently overwrite Cycle 1 artifacts.

## 2. Invariants and forbidden shortcuts

1. **Native PLN truth-value calculations:** native verified upstream operators must perform inference and belief revision. Do not implement a parallel `strength/confidence` calculus in Python. Host-side deterministic bookkeeping is allowed for sensing, indexing, scheduling, provenance, structural state edits, and evaluation only.
2. **No oracle leakage:** `python-chess` or another chess referee may label training examples and score evaluation results only. Production inference must not call or import it, including indirectly through observation, feature construction, caching, or model loading.
3. **No hidden chess legality in sensors:** do not construct a feature named `legal`, `safe`, `unblocked`, `attacked`, etc. by running a deterministic chess-rule adjudicator and then feed it to PLN as if it were learned. Raw occupancy, relative geometry, temporal state and directly sensed relations are permitted. Clearly distinguish direct sensor primitives from derived predicates.
4. **No invented native capabilities:** verify exact rule signatures, domains, marginal requirements, truth-value behavior, and execution with runnable probes. Never assume nested implications are conjunction, or transplant an unverified formula from older PLN implementations.
5. **Relative invariance:** learned hypothesis keys must not include absolute square names, piece IDs, position IDs, FEN strings, dataset IDs, or irrelevant global board configuration. Boundary and history relations may appear only when causally relevant.
6. **Unknown stays unknown:** do not convert absence of evidence into negative evidence or a high-confidence safe/legal assertion. Preserve native TVs, confidence, provenance, truncation, and abstention.
7. **No fake metrics:** independent held-out splits must remain disjoint by motif family/game and transformation lineage. Report selective accuracy, abstention, candidate recall, exact-set accuracy, false legal moves, and latency, including regressions.
8. **No hard-coded chess-rule lookup table disguised as learning:** the bounded hypothesis grammar may encode plausible geometric relationships, but must not directly seed certain legal/illegal decisions. Explicitly document the inductive bias.
9. **Backward compatibility:** preserve Cycle 1 CLI/API/checkpoints when feasible; version any breaking model or proof schema and provide a migration or clear compatibility error.
10. **Reproducibility:** pin dependencies, deterministic seeds, artifact hashes, evidence provenance, and the exact native runtime. No paid services or unapproved external writes.

## 3. Architecture goal: hierarchical local relational knowledge

Replace the single monolithic categorical lookup as the primary generalization mechanism with a **hierarchy of independently reusable relative relations**, keeping exact-context lookup only as a low-priority optional specialization.

Suggested conceptual layers (adapt names to the codebase):

- **L0 — Direct observations:** mover type/owner, owner-relative displacement, direction family, distance, intermediate cell occupancy sequence, destination occupancy, edge proximity, en-passant/castling state observations, and post-move opponent/king relative frames. These are *sensor facts*, not chess legality claims.
- **L1 — Reusable local motifs:** same-ray step, ray occupancy segment, empty intermediate cell, first obstruction at relative step `k`, friendly/opponent destination, knight leap geometry, pawn-forward relation, pawn-diagonal relation, boundary encounter, and potential king exposure relation. Learn support for motifs from labeled evidence; do not adjudicate them deterministically in production.
- **L2 — Piece movement hypotheses:** piece-kind + relative motion family + selected contextual motifs, e.g. rook axial movement, bishop diagonal movement, knight jump, pawn forward/diagonal, king adjacency. Learn and revise these with native PLN.
- **L3 — Contextual constraints:** obstruction, own-piece destination, capture conditions, pawn starting-edge conditions, promotion, castling rights/transit, en passant temporal context, and exposure after structural successor.
- **L4 — Candidate legality:** infer from the strongest native-supported proof path, explicitly distinguish full composition from partial or contextual evidence. Preserve contradictory evidence and abstention.

The hierarchy is an **engineering target**, not permission to invent a new PLN connective. Every edge labeled as a PLN inference must have a verified native operator and an executable trace. Host-side construction of typed relational observations must be visibly tagged `sensor` or `host-derived`, not `native-derived`.

### 3.1 Locality and irrelevant-context invariance

Implement local context selection with explicit relevance boundaries. An unrelated piece far from a proposed rook move must not change the learned movement hypothesis merely because it changes the global `postmove_opponents` list. King-exposure evidence should be queried as a *separate* relation, with opponent-specific provenance, not serialized into every movement key.

Build focused descriptors for:

- mover relative displacement and piece class;
- path/ray relation and occupancy (including distance-dependent and distance-agnostic versions);
- destination relation;
- own-king exposure and opponent attack motifs;
- temporal/special-move state.

Keep a fine-grained descriptor for diagnostic specialization, but avoid requiring a full-context match for general support. Explicitly document when a context is necessarily nonlocal (e.g. sliding-piece attacks on the king).

### 3.2 Relative ray decomposition

Support learning reusable local ray rules without memorizing every entire ray occupancy string. Explore prefix/suffix decomposition and first-obstruction motifs using relative steps. The *observation* that a cell at relative step `k` is occupied may be exact; the *inference* that this blocks a rook/bishop/queen move must remain learned/probabilistic. Avoid looping over all legal moves as a hidden chess solver.

### 3.3 Generalization and specificity

Implement an explicit hypothesis lattice, such as:

`piece family` → `piece + movement family` → `piece + movement family + occupancy motif` → `piece + movement family + destination relation` → `piece + selected contextual constraints` → `exact contextual specialization`.

Support multiple applicable hypotheses for a candidate. Record which were matched, their support, dependence overlap, native operators, and why one result was chosen. Do not treat competing dependent hypotheses as independent evidence. Define and test a conservative conflict/selection policy using verified native capabilities. If no defensible combination exists, abstain rather than invent an aggregation formula.

## 4. Native PLN research and integration workstream

### 4.1 Capability audit extension

Extend `docs/pln-compatibility-matrix.md` with executable tests for the exact upstream revision in use:

- native induction on inheritance links with measured population marginals;
- deduction, inheritance, inversion, similarity, equivalence, abduction only where source and executable tests support them;
- evidence stamps, overlap checks, confidence choice, negation;
- candidate native patterns for multi-premise inference, conjunction introduction, conjunction elimination, conditionalization, and rule chaining;
- zero-confidence, confidence-one, contradictory, dependent, and incomplete-input cases.

For each candidate operator record signature, upstream source line/commit, expected premises, actual native expression, actual output TV, edge cases, and status (`verified-production`, `verified-experimental`, `unsupported`, `failed`). Avoid adding custom operators to the core just to claim compatibility.

### 4.2 Verified compositional alternatives

Investigate, in order:

1. Whether the pinned maintained PLN has an executable native way to express multiple independently evidenced premises without a synthetic conjunction.
2. Whether a *separately pinned* upstream-maintained PLN branch/release offers a verified conjunction rule with defensible truth-value semantics.
3. Whether native implication/inheritance chaining plus appropriately scoped relational atoms can support a useful restricted proof without claiming full AND semantics.
4. Whether a safe hierarchy of conditional hypotheses can provide measurable generalization while conjunction remains unavailable.

Do not change the pinned runtime casually. Any alternative runtime must be opt-in, reproducibly pinned, license-compatible, tested against Cycle 1 and Cycle 2, and accompanied by a semantic compatibility matrix. If no verified conjunction exists, **continue with the strongest native-partial design** and make the blocked claim explicit.

### 4.3 Native induction in the actual learner

Integrate at least one genuine native `Truth_Induction` / `|-` induction path into model training and inference where its premises and marginal estimates are well defined. Do not count a standalone smoke test as integration. Develop an auditable marginal-estimation procedure with denominators, sampling frame, confidence, and dependence groups. Ensure induction is not driven by hidden oracle labels at inference time.

Report separately:

- learned hypotheses obtained through native induction;
- hypotheses inherited from grammar or host-side generalization;
- revised hypotheses from direct observations;
- hypotheses that remain unknown.

If native induction cannot be used without unjustifiable marginals, implement a guarded opt-in experiment, explain the mathematical blockage, and do not fabricate probabilities. The default production path must remain sound.

## 5. Evidence, learning, and negative examples

### 5.1 Evidence model

Retain append-only provenance, idempotency, dependence groups, transformation lineage, replay, rollback, and checkpoint integrity. Extend records to identify **which local motif(s)** an observation can update and why. Distinguish direct legal labels, auxiliary attack labels, and derived/inferred hypotheses. Make sure one legal/illegal move label does not naively become independent evidence for every correlated motif.

### 5.2 Credit assignment

Design conservative credit assignment for labeled legal and illegal moves. A positive legal example can support its applicable geometric/contextual motifs, subject to dependence controls. A negative example must not indiscriminately discredit the movement family: it may be illegal because of obstruction, friendly destination, king exposure, rights/history, or a boundary. Use matched controlled contrasts, auxiliary supervised motif labels in **training only**, or abstention where attribution is ambiguous. Document exactly what supervision is supplied and what is inferred.

### 5.3 Contrastive curriculum

Generate controlled paired examples differing in one causally relevant local relation, plus counterexamples that vary only irrelevant global context:

- rook/bishop/queen clear ray vs blocker at different distances;
- same blocker geometry moved to different ranks/files;
- friendly vs opponent destination;
- knight leap with unrelated intervening occupancy;
- pawn forward vs diagonal capture, one-step/two-step, owner orientation, starting edge;
- king adjacency, pinned piece, discovered check, double check;
- castling rights, transit attacks, occupied transit cells;
- en passant availability, expiry, capture-removal exposure;
- promotion choice and destination occupancy;
- irrelevant far-away piece added/removed;
- local pattern preserved while other opponent-to-king frames change.

Use reproducible seeds and explicit provenance. Train/test splits must be disjoint by motif family and source game, not just FEN string.

## 6. Successor-state and attack/exposure reasoning

Retain structural successor edits without introducing legality adjudication. Separate attack *observations* from attack *beliefs* and attack *inferences*. Implement reusable relative attacker-to-king hypotheses for pawn, knight, king, sliding pieces, and obstruction. Test that removing an irrelevant opponent does not invalidate an unrelated movement belief. Preserve unknown/incomplete board observations.

Explicitly inspect whether the existing weak `Attack → WouldExposeOwnKing → Not(LegalMove)` implication chain can swamp or be swamped by contextual evidence. Record raw TVs and dependence. Avoid interpreting `BestConfidenceCandidate` as probabilistic conjunction or as a logically valid universal king-safety test. If a candidate's final legality is supported only by a learned context category, mark its proof status accordingly.

## 7. Dataset design and evaluation protocol

Implement `cycle2` datasets without modifying Cycle 1 originals. Produce train, validation, independent heldout-transfer, adversarial, controlled-translation, and **irrelevant-context perturbation** splits. Include held-out ray lengths, blocker locations, opponent configurations, and special-move variants. Explicitly track overlap by hypothesis descriptor, motif family, game, and transformation lineage.

Run all evaluation variants on identical splits:

- **B0:** frozen Cycle 1 model and representation;
- **B1:** hierarchical descriptors without native induction;
- **B2:** hierarchical descriptors with verified native induction (if feasible);
- **B3:** ablation without obstruction motifs;
- **B4:** ablation without attack/exposure motifs;
- **B5:** ablation without dependence handling (diagnostic only);
- **B6:** geometry-only and absolute-coordinate baselines (evaluation only);
- **B7:** exact-context specialization disabled.

Report: precision, recall, F1, exact move sets, in-board metrics, false-legal rate, false-legal self-check rate, abstention, incomplete, per-piece breakdown, calibration (strength vs empirical outcome, separate from PLN confidence), support by rule tier, coverage by unseen motif, proof depth, native calls, runtime, memory, and checkpoint size. Report confidence intervals or uncertainty where sample size permits. Distinguish training, controlled-transfer, and independent held-out results prominently.

### 7.1 Primary acceptance targets

Targets below are **goals, not permission to manufacture results**:

- Independent heldout-transfer recall **strictly greater than Cycle 1's reported 0%** on a sufficiently large, genuinely independent split; aim for ≥ 50% recall while maintaining precision ≥ 90%, but report an honest shortfall if native semantics or sample coverage prevent it.
- Demonstrate at least **three independently learned, reusable relative motifs** that transfer to previously unseen board contexts without exact full-context fingerprint matches; at least one should involve an occupancy or obstruction condition, not only geometric displacement.
- Irrelevant-context perturbations preserve the applicable movement-level hypothesis IDs and TVs, even if separate king-safety evidence legitimately changes.
- No production oracle leakage; all raw reported TVs trace to verified native PLN calls.
- Existing Cycle 1 tests continue passing or receive justified, versioned updates; add substantive Cycle 2 tests.
- For the benchmark position with ~214 candidates, reduce native invocation count and latency by a measured amount, preferably ≥ 2×, **without altering the semantic result solely to improve speed**. Report cold and warm performance separately.

A failure to hit aspirational numerical targets must not be concealed. If scientific constraints block them, produce the strongest honest implementation plus an actionable blocker analysis.

## 8. Inference scheduling and performance

Profile native invocations by stage: context, geometry, attack, exposure, choice, induction, and duplicate subexpressions. Implement semantic-preserving improvements:

- cache/reuse identical grounded native subproofs across candidates where evidence and contexts are identical;
- deduplicate opponent-to-king relative frames and shared observations;
- batch native calls without losing node/provenance identity;
- avoid serializing irrelevant global context into every candidate;
- use lazy scheduling and explicit budgets, with `incomplete` on truncation;
- investigate warm PeTTa process reuse as an optional, safely isolated mode;
- record cold-start vs steady-state time and proof counts.

Do not collapse independent evidence groups into a single count or change the truth-value calculation in the host to gain speed. Add parity tests proving optimized and reference schedules return identical native TVs/proof-relevant semantics for representative cases.

## 9. Public APIs, inspector, and usability

Preserve `infer_moves`, `explain_move`, `observe_example`, `train`, `compare_transforms`, checkpoint import/export, and CLI operations where feasible. Add opt-in `model_version`/`representation` selectors and a clear schema migration strategy. The inspector should show:

- board/candidate and original relative sensory facts;
- matched hierarchical hypotheses from general to specific;
- native vs host-derived provenance of each inference node;
- strength and confidence separately;
- evidence IDs and dependence exclusions;
- induction premises and population marginals where used;
- competing positive/negative hypotheses and selection rationale;
- why an unseen case generalizes or abstains;
- comparisons between B0/B1/B2 on the same candidate;
- explicit `native-compositional`, `native-partial`, or `unknown` proof classification.

Do not render a green `legal` state for an unknown or merely geometrically plausible move. Inspector labels must not imply certainty unsupported by native proof.

## 10. Work packages and dependencies

Execute the following as one coordinated run. Parallelize independent packages when safe; do not stop for milestone-by-milestone user review.

| Package | Work | Mandatory evidence |
|---|---|---|
| C2-01 | Baseline snapshot, source audit, pinned runtime verification | baseline manifest, tests, hashes |
| C2-02 | Native PLN rule/marginal/conjunction feasibility experiments | executable probe corpus, capability matrix |
| C2-03 | Versioned hierarchical relational ontology and descriptors | schemas, invariant tests |
| C2-04 | Locality and irrelevant-context independence | perturbation tests, descriptor comparisons |
| C2-05 | Ray/obstruction/destination motif abstractions | motif fixtures and learned beliefs |
| C2-06 | Hypothesis lattice, specificity and conflict policy | selection tests and proof traces |
| C2-07 | Native induction integration or rigorously blocked experiment | actual induction proofs or blocker report |
| C2-08 | Evidence attribution, correlation, replay, migration | ledger/checkpoint tests |
| C2-09 | Contrastive curriculum and independent splits | dataset generator, hashes, overlap audit |
| C2-10 | Attack/exposure and special-move relational integration | adversarial proof fixtures |
| C2-11 | Native scheduler optimization and parity | invocation profiles, parity tests |
| C2-12 | API/CLI/inspector enhancements | contract tests, inspector screenshots if possible |
| C2-13 | Baselines, ablations, calibration, evaluation | JSON metrics and reproducible commands |
| C2-14 | End-to-end clean bootstrap and final engineering report | clean-copy logs, tests, final manifest |

Do not declare completion merely because files exist. Each package must have runnable verification and meaningful recorded results. Mark `complete`, `partial`, or `blocked`, with exact evidence.

## 11. Testing requirements

Add unit, integration, native-runtime, metamorphic, adversarial, regression, and clean-bootstrap tests. Include at minimum:

1. Absolute coordinate translation and color-flip invariance where state semantics permit.
2. Irrelevant far-away piece insertion/removal with unchanged movement-level belief.
3. Different ray lengths and blocker positions reusing a generalized obstruction hypothesis.
4. Friendly/opponent destination contrasts.
5. Pinned piece and en passant discovered-ray counterexamples.
6. Unknown occupancy and unknown history producing abstention, not false certainty.
7. Repeated evidence idempotency and dependence-group exclusion.
8. Independent contradictory evidence updating through native revision.
9. Native induction proof with documented marginal provenance (if integrated).
10. Runtime mismatch, corrupted checkpoint, missing native dependency, timeout and budget exhaustion.
11. No production import or invocation of the reference oracle.
12. Optimized vs unoptimized schedule parity for TVs, lineage and rule identities.
13. Proof inspector consistency with inference API.
14. Disjoint independent held-out families and zero accidental leakage.
15. Reproducible clean checkout/bootstrap without preexisting generated artifacts.

Prefer tests that fail against the current Cycle 1 design and pass for meaningful Cycle 2 improvements. Do not relax existing tests to manufacture progress.

## 12. Documentation and artifact contract

Create or update:

- `docs/cycle2/architecture.md` — ontology, hierarchy, provenance, locality, and sensor/native boundary;
- `docs/cycle2/native-pln-feasibility.md` — exact operator probes, conjunction status, induction marginals;
- `docs/cycle2/learning-and-credit-assignment.md` — evidence semantics and dependence;
- `docs/cycle2/transfer-protocol.md` — split construction, overlap audit, invariance/perturbation tests;
- `docs/cycle2/experiments.md` — B0–B7, ablations, calibration and uncertainty;
- `docs/cycle2/performance.md` — call profiles, caching, cold/warm benchmarks;
- `docs/cycle2/limitations.md` — every remaining non-compositional or host-derived step;
- `docs/cycle2/final-report.md` — claims linked to tests, source and generated artifacts;
- `artifacts/cycle2/` — machine-readable baseline, fixtures, proof traces, checkpoint hashes, evaluation, benchmark, and test outputs;
- root README — short Cycle 2 reproduction path and honest coverage statement.

Provide `scripts/cycle2_reproduce.sh` (or equivalent) that verifies dependencies, regenerates datasets, trains, evaluates, benchmarks, runs tests and produces the report. Make it idempotent, non-destructive to Cycle 1, and fail loudly on unsupported runtime versions. Record exact commands, versions, seed, machine/runtime assumptions, and output hashes.

## 13. Decision rules and autonomy

You are authorized to make ordinary local design choices, add tests, refactor modules, install pinned local dependencies as needed, run benchmarks, and make local commits. Do not ask the user for approval between packages. Do not push, create remote PRs, deploy, or perform other external mutations without explicit authorization. Do not silently upgrade native PLN/PeTTa; if evaluating an alternative, isolate it behind a pinned opt-in configuration.

When a native feature is missing, follow this decision ladder:

1. Confirm with source inspection **and executable probe**.
2. Search within supported native rule combinations for a semantically valid solution.
3. Test an upstream-maintained alternative in isolation if available and justified.
4. Implement the strongest native-partial hierarchical design with explicit provenance and unknown outcomes.
5. Record the exact limitation, its effect on experiments, and the minimal upstream change needed.
6. Continue all other independent work.

Do not stop the whole project for a missing conjunction rule. Do not use a fabricated conjunction, host-side truth-value fusion, or deterministic legality filter to make the metric look better.

## 14. Final response contract for Codex

At the end of the engineering run, report:

1. HEAD and final local commit SHA(s), working tree status, and concise architecture changes.
2. A package-by-package C2-01…C2-14 status table with evidence paths.
3. Exact native PLN operators used in production, with source and executable proofs.
4. The strongest *new* generalization demonstration: training example, unseen test case, matched reusable rule, TV, evidence, and explanation of why the context was genuinely new.
5. Baseline-vs-Cycle-2 metrics on identical independent splits, including abstention and regressions.
6. Benchmark before/after, native invocation counts, and parity results.
7. Test counts and clean-bootstrap result; distinguish executed from unexecuted checks.
8. Remaining blockers and prioritized next work, especially whether compositional legality remains unsupported.
9. Exact reproduction commands.

**Definition of success:** a reproducible, auditable native-PLN research system that can transfer learned relative chess constraints across *unseen relational contexts*, with clear proof provenance and honest unknowns. Merely improving training accuracy, matching translated full-context fingerprints, or adding more pre-coded chess conditions does not satisfy the research objective.
