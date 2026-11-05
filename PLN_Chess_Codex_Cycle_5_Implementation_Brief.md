# PLN Chess — Cycle 5 Consolidated Codex Engineering Brief

**Project:** `machieke/pln-chess`  
**Starting reference:** `d5cfcb126acc9c3e5da669744d661e6895fb9303` (Cycle 4)  
**Theme:** Systematic relational composition, temporal evidence, and independent generalization  
**Execution mode:** One consolidated autonomous engineering cycle  
**Status:** Implementation instructions, not a claim of completed work

## 0. Mission and non-negotiable principles

Extend the *existing* PLN Chess research package. Do not rebuild it or replace its native inference with a conventional chess engine, a deterministic legal-move gate, an ad hoc Bayesian formula, a neural classifier, or an unverified PLN operator. The objective is to learn and apply **piece-relative, reusable probabilistic relations** that generalize across translations, reflections, different pieces, ray lengths, unrelated opponent arrangements, and unseen games. Absolute coordinates belong only in board I/O, reference evaluation, and structural bookkeeping, not in learned rule identities.

The core Cycle 5 question is:

> Given separate training evidence for a movement geometry relation and a destination-occupancy relation, can native PLN derive a defensible legality belief for a **new conjunction of those facts** that never appeared as a training context?

Distinguish three outcomes rigorously: (a) genuine native multi-premise derivation, (b) a verified unary-chain or explicitly supplied compound-premise workaround, and (c) host-side feature composition. Never label (b) or (c) as a native conjunction proof. If the audited upstream runtime cannot perform (a), preserve the limitation, implement the strongest verifiable partial alternative, and complete all other packages.

**Do not request approval at intermediate milestones.** Inspect the repository, run existing checks, implement feasible packages, execute experiments, fix regressions, and commit locally. Do not push, publish, deploy, modify external systems, or change upstream repositories. Report blockers and failed experiments explicitly. Preserve the current working tree and do not overwrite unrelated changes. If the working tree is dirty, inspect and preserve it before editing.

## 1. Baseline and provenance lock (C5-01)

1. Confirm repository, branch, HEAD, working-tree state, dependency lock, native PLN source SHA, PeTTa SHA, interpreter versions, model/dataset hashes, and the exact C4 evidence artifacts. If HEAD differs from the supplied reference, identify why and use the actual repository state as the authoritative source; never reset or discard work blindly.
2. Locate the Cycle 4 architecture, inference scheduler, factored observation schema, learning/revision, exposure chains, temporal evidence, evaluation harness, UI, native audit, and benchmark scripts. Produce `docs/cycle5/baseline.md` with links to actual source paths and versioned artifacts.
3. Reproduce C4 on the frozen 40-position / 2,635-candidate holdout, 24-position adversarial split, older eight-game split, and new 12-game / 24-position split. If any dataset is unavailable, record the exact missing dependency and proceed with available independent tests.
4. Save immutable C4 result snapshots under a versioned `artifacts/cycle5/baseline/` directory. Record precision, recall, F1, supported-illegal and supported-legal counts, unknown/abstention, false-legal, false-illegal, incomplete, exact move sets, in-board-only metrics, confidence calibration, and per-family breakdowns.
5. Keep the 49 originally false-legal cases as explicit regression fixtures, including C2 supported → C3 unknown → C4 supported-illegal provenance.

**Baseline claims to verify, not assume:** frozen recall 97.77%, F1 98.87%, exact sets 75%; adversarial recall 99.12%, exact sets 91.67%; new-game recall 95.37%, exact sets 41.67%; zero observed false-legal and false-illegal in the reported default runs. Preserve evidence if actual reruns differ.

## 2. Native PLN composition feasibility (C5-02)

Audit the **actual pinned native PLN library** and execution backend, not remembered documentation. Build runnable minimal operator probes for:

- modus ponens, deduction, inheritance, induction, revision, negation, and evidence choice;
- multi-premise conjunction introduction, conjunction elimination, implication currying/uncurrying, implication over compound antecedents, and any supported intensional or contextual variants;
- variable binding and scope, rule substitution, conditional independence requirements, and evidence stamp propagation;
- whether multiple independent premises can produce a new conclusion **without** the host precomputing the joint truth of their conjunction;
- what happens for absent, contradictory, low-confidence, or correlated evidence.

For every probe record the literal MeTTa expression, native output, source file and line reference, input/output truth values, and whether it is executable under the pinned runtime. If considering upstream additions, implement them only in a separately labeled experimental adapter after verifying compatibility and mathematical semantics; do **not** silently edit the vendored PLN core or claim upstream support. Prefer no new operator over an invented one. Produce `docs/cycle5/native-composition-matrix.md` and machine-readable probe artifacts.

**Hard acceptance:** A purported multi-premise proof must expose the independently sourced premises, actual native inference steps, their dependence identities, and a reproducible native result. Otherwise classify it `native-partial`.

## 3. Compositional representation and abstraction hierarchy (C5-03)

Create a versioned representation separating **sensor facts**, **local relational abstractions**, **learned conditional beliefs**, and **move-specific conclusions**. At minimum represent:

- piece-relative signed displacement, owner-forward orientation, alignment family, and ray distance;
- source/destination occupancy as empty/friendly/opponent/unknown, with piece kind only when required;
- per-cell ray occupancy and the relation *some intermediate cell is occupied* without encoding a particular square or a whole-board fingerprint;
- jump-versus-ray geometry; pawn single/double advance and diagonal contact; edge/start/promotion context;
- pre-move and post-move relative king exposure, attackers, intervening defenders, and response to check;
- temporal predicates for castling rights and en-passant eligibility with explicit provenance.

Design a typed hierarchy, e.g. `RelativeGeometry`, `DestinationRelation`, `RayOccupancyRelation`, `ExposureRelation`, `TemporalEligibility`, `CandidateLegality`, with stable versioned hypothesis IDs. Prefer rule identities invariant under board translation, piece-ID renaming, and permissible symmetries. Avoid incorporating all opponent frames or unrelated pieces into a primary rule key. Keep detailed contexts as **optional refinements** only when coarse hypotheses cannot explain contradictory evidence. Track every refinement and why it was introduced.

Do not accidentally smuggle the chess rules into sensors: a sensor may report relative alignment and raw occupancy, but must not report `legal_rook_move`, `king_safe`, or an oracle-derived attack verdict as a production fact. Document the boundary between structural edits and learned semantic conclusions.

## 4. Independent-premise transfer laboratory (C5-04)

Build a controlled factorial experiment suite with **training/test disjointness by relational combination**, not merely FEN or square. Construct independent training partitions for:

1. knight geometry vs opponent occupancy → previously unseen knight capture;
2. rook/bishop/queen alignment vs intermediate blocker position and allegiance → new ray lengths and blocker distances;
3. pawn diagonal geometry vs opponent occupancy → unseen capture, and pawn forward geometry vs empty destination → advance;
4. geometric movement vs exposure relation → unseen pinned move, discovered attack, and check resolution;
5. king unit movement vs attacked destination → unseen unsafe destination;
6. special-move structural eligibility vs independently supplied temporal evidence.

For each experiment, enforce that **no training record contains the exact test combination**, including translated copies, source games, shared structural-family IDs, and derivative evidence. Provide a leakage auditor that hashes both fine and abstract descriptors, detects common ancestry, and emits an explicit leakage report. Include positive, negative, unknown, contradictory, and out-of-board controls. Use an external chess oracle **only** in training fixture generation and evaluation, never in production inference.

For every held-out case compare: C4 exact-context baseline; C5 abstract-only; C5 factored composition; C5 with/without native induction; and a deliberately absolute-coordinate baseline. Record sample efficiency and the number of *distinct* training contexts required for the first correct unseen prediction.

## 5. Positive legality proof completion (C5-05)

Target the documented C4 unresolved knight capture `f6h5` first. Trace why movement and destination relations cannot currently support a positive conclusion. Implement a proof planner that attempts only **verified native** operations and records what cannot be derived. If native multi-premise composition is unavailable, evaluate these separately labeled approaches:

- independently learned conditional rules over minimal **typed local composite observations**;
- soundly grounded context propositions whose construction and provenance are disclosed as host-side sensing rather than native AND;
- reusable unary implication chains that transfer without exact whole-context matches;
- hierarchical backoff from specific learned rules to general local motifs, with conservative abstention on unresolved conflict.

Do not combine truth values using an unverified `min`, product, noisy-AND, custom Bayesian formula, or confidence multiplication. Do not treat high geometry confidence alone as evidence of legality. Require separate evidence for destination allegiance, obstruction, king safety, and temporal eligibility where applicable. If no supported native inference establishes a positive conclusion, return `unknown` with a proof-gap explanation.

Demonstrate at least one successful *previously unseen* positive composition or provide a negative feasibility report showing precisely why none is defensible in the selected native runtime.

## 6. Negative reasoning and safety completeness (C5-06)

Preserve the C4 policy that prevented false-legal self-check moves. Expand reusable negative evidence for: off-board destinations, friendly destination, blocked sliding rays, king moving into attack, pinned piece exposing its king, en-passant opening a ray, castling through check, and unresolved check. Keep all 49 regression cases.

Distinguish **supported-illegal** from `unknown`; never relabel an abstention as illegal merely because a move was absent from the learned positive set. Introduce explicit conflict diagnostics when positive and negative channels have overlapping or independent evidence. Audit evidence choice for shared provenance and ensure evidence is not counted twice through both exposure and context channels. Test adversarial confidence thresholds, correlated evidence, and deliberately contradictory labels.

A threshold-only fix is insufficient. Each newly resolved case must show a new or strengthened reusable native proof, with supporting evidence IDs and a counterfactual test where the decisive local relation is removed.

## 7. Temporal and historical evidence (C5-07)

Implement an explicit **temporal evidence layer**, not a hidden deterministic chess-rule checker. Represent move-event provenance, previous state observations, trusted-but-unverified metadata, inferred temporal conditions, and unknown history separately. Model castling eligibility (king/rook movement history, current rights claims, transit observations), en-passant eligibility (immediately preceding two-square pawn advance and target relation), and promotion context. Preserve the existing FEN-only API, but make its history assumptions explicit.

Define at least three inference modes:

- `fen-only`: only currently supplied position metadata, with unverified history appropriately marked;
- `trusted-metadata`: supplied rights/EP treated as stated external evidence with declared reliability, not a learned proof of history;
- `event-backed`: event sequence or independently attested history supplies provenance and permits higher-confidence temporal conclusions.

Test conflicting FEN rights versus event history, missing history, truncated event sequences, translated/reflected positions where history cannot safely transform, and temporal evidence replay. Preserve the C4 conservative castle abstention as a regression in `fen-only` unless new valid evidence justifies a different conclusion. No assumption that FEN alone proves the full history of the game.

## 8. Native induction: causal contribution study (C5-08)

The prior cycles executed `Truth_Induction` but reported no net classification benefit. Do not treat successful operator invocation as successful learning. Audit population marginals, sample frames, hypothesis scope, evidence dependence, priors, and rule activation. Compare induced rules against already supplied abstractions to identify redundant derivations. Build a **counterfactual induction benchmark** where the candidate abstraction is not supplied in advance, then ask whether native induction discovers a useful relation and improves held-out prediction.

Run induction-enabled, induction-disabled, and sham/redundant-induction controls with matched data and budgets. Require native input/output traces, rule IDs, evidence provenance, changes in classifications, held-out generalization, and false-positive impact. Keep induction experimental and disabled by default unless it produces independent measurable benefit without breaking safety. If it fails, explain the exact failure mode and provide a narrowly scoped future research path rather than forcing it into production.

## 9. Evidence semantics and provenance (C5-09)

Preserve append-only evidence, replay, idempotency, dependence groups, model versioning, rollback, and source lineage. Extend provenance to factored premises and temporal events. Define explicit rules for when two observations share a source or transform lineage and must not be revised as independent evidence. Audit derived-premise re-use so an observation used to learn a local motif is not silently counted again when that motif participates in a legality chain.

Provide counterfactual proof inspection: for a chosen conclusion, remove one premise family at a time, recompute native results, and report the classification delta. Distinguish an absent premise, a negative premise, and an uncertain premise. Persist all before/after native TVs. Add corrupted-checkpoint, conflicting-idempotency, missing-event, and cross-version import tests.

## 10. Generalization and evaluation protocol (C5-10)

Keep the frozen C4 splits immutable. Add **new independent games and new combinatorial holdouts**, with dataset seeds, hashes, grouping policy, and overlap audits. Evaluate whole legal-move sets, not only cherry-picked examples. Report precision, recall, F1, false-legal, false-illegal, unknown, incomplete, exact sets, calibration, per-piece, per-special-move, and in-board-only metrics. Include selective-risk curves as the confidence threshold changes; do not hide coverage loss behind high precision.

Distinguish: seen-context accuracy; same-motif translation; unseen combination of known premises; unseen structural family; unseen game; and adversarial safety. Keep out-of-board negatives separately so they do not inflate perceived chess competence. Include a matched-budget comparison against C4 and at least two ablations of the new representation. All headline metrics must identify denominator, split, candidate count, model version, and confidence policy.

**Aspirational research targets, not acceptance gates:** new-game recall ≥97%, precision ≥99%, exact move sets ≥60%; frozen exact sets ≥85%; adversarial exact sets ≥95%; at least five newly resolved *independent* compositional cases across three piece families; zero observed false-legal self-checks in the default model. Report actual outcomes even if targets are missed. Do not tune thresholds on held-out test sets.

## 11. Performance and native scheduling (C5-11)

Preserve proof parity and benchmark the Cycle 4 reference: 214 candidates, reported 2.135 s cold / 1.275 s warm, 259 cold native calls, checkpoint 760,719 bytes, and 213 MiB inference peak RSS. Verify these rather than assuming the exact numbers reproduce on a different machine. Factor shared local premises and cache native intermediate proofs only when model/runtime version, truth values, evidence lineage, and dependencies match. Do not reuse a cached conclusion across different provenance or temporal states.

Measure p50/p95 latency, native invocations, grounded atoms, peak memory, checkpoint size, cache hit rate, proof sizes, and cold/warm behavior on sparse and full positions. Maintain a reference uncached execution path and test TV/classification/proof/rule-ID/evidence equality. Favor correctness over speed; document any intentional proof canonicalization differences. Avoid unbounded enumeration or brute-force rule synthesis.

## 12. API, CLI, and inspector (C5-12)

Extend existing interfaces compatibly where feasible. Expose:

- `infer`/`explain` with per-premise TVs, provenance, classification, native/host composition label, and explicit proof gaps;
- `compare-models` for C4 vs C5 on the same position;
- `counterfactual` to suppress one evidence family and recompute a conclusion;
- `temporal-inspect` for `fen-only`, `trusted-metadata`, and `event-backed` modes;
- `composition-audit` for executable native probes and unsupported operators;
- `evaluate` with split and representation variants, including unseen-premise-combination controls.

Enhance the local inspector to show the relative spatial neighborhood, rule hierarchy, positive/negative proof branches, temporal evidence, C4/C5 differences, and why a move is unknown. Make unsupported native conjunction visible rather than silently collapsing it into a generic error. No oracle-derived labels in production UI inference. Verify desktop and mobile usability, malformed inputs, unknown history, runtime errors, and proof-budget exhaustion.

## 13. Tests, reproducibility, and integration (C5-13)

Run the existing full test suite and add unit, integration, native-runtime, property-based, and metamorphic tests for all new components. Invariants include: translation and permissible symmetry; piece-ID renaming; unrelated-piece perturbation; evidence replay; provenance isolation; native proof identity under caching; history truncation; no oracle imports in production; and unchanged safety regression fixtures. Include negative tests that intentionally tempt the system to infer from missing evidence.

Provide a clean-copy reproduction script that installs pinned dependencies, checks native runtime hashes, reconstructs evidence/checkpoints, runs operator probes, generates datasets, trains, evaluates, benchmarks, tests, and produces a final report. A missing native dependency must cause an explicit diagnostic, **never** a Python inference fallback. Record exact commands, stdout/stderr, environment, runtime SHA, dataset SHA, model SHA, artifact manifest, and a final verification receipt.

## 14. Documentation and final delivery (C5-14)

Update the README, architecture, spatial semantics, learning semantics, native capability matrix, chess coverage matrix, model card, CLI/API reference, and experimental protocol. Produce:

- `docs/cycle5/engineering-report.md` — concise executive summary and complete package matrix;
- `docs/cycle5/composition-feasibility.md` — exact native successes and failures;
- `docs/cycle5/temporal-semantics.md` — evidence and history trust modes;
- `docs/cycle5/induction-results.md` — causal contribution and failed experiments;
- `docs/cycle5/generalization-results.md` — all splits, leakage audit, and ablations;
- `docs/cycle5/performance.md` — baseline/parity/caching measurements;
- `docs/cycle5/verification.md` — clean reproduction and test receipt;
- versioned machine-readable datasets, proof traces, model/checkpoint hashes, and experiment outputs.

The final user-facing Codex report must include: starting/final commit, working-tree status, push status, exact files changed, full package completion matrix (`complete`, `partial`, `blocked`, `not started`), all headline metrics with denominators, key successful and unsuccessful proofs, native PLN boundary, performance comparison, reproducibility command, and ranked remaining research questions. Do not imply that zero errors on tested splits proves universal correctness.

## 15. Execution sequence and autonomy

Execute in this order unless repository realities justify a documented change:

1. Inspect actual code and lock baseline; run existing tests.
2. Probe native composition capabilities; publish capability matrix internally.
3. Design versioned factored abstractions and premise provenance.
4. Implement independent-premise transfer fixtures and leakage audit **before** tuning the learner.
5. Implement positive and negative reasoning improvements, preserving C4 safety.
6. Implement temporal evidence modes and history-aware inference.
7. Run induction counterfactuals and retain only defensible improvements.
8. Optimize scheduling with reference-proof parity.
9. Extend APIs/inspector, run complete evaluations and ablations.
10. Perform clean reproduction, write reports, and commit locally.

Continue through independent packages even if native conjunction remains unsupported. Use focused commits if helpful, then provide one final consolidated delivery. Do not push. Do not make unsupported claims of complete compositional chess legality. The project's primary success criterion is **transfer of learned local knowledge to unseen combinations with native, inspectable probabilistic evidence**, not a larger set of hardcoded chess conditions.

## 16. Final acceptance checklist

- [ ] Baseline reproducible and versioned, with no silent regression.
- [ ] Native composition audit includes exact executable probes and honest capability labels.
- [ ] No absolute-square constants in learned rule identities.
- [ ] No production chess-oracle legality checks or unverified probability formulas.
- [ ] Independent-premise combination holdouts and leakage audit exist.
- [ ] Positive legality proof gaps are inspectable; unsupported conjunction is not claimed.
- [ ] All 49 safety regression cases retained, with no unjustified false-legal claims.
- [ ] Temporal trust modes distinguish FEN metadata from event-backed history.
- [ ] Induction benefit tested causally, not inferred from successful invocation.
- [ ] Evidence provenance, revision, replay, and counterfactuals verified.
- [ ] C4/C5 results and complete move-set metrics reported across independent splits.
- [ ] Reference/cache native proof parity checked.
- [ ] API, CLI, inspector, tests, and clean reproduction completed.
- [ ] Final documentation, artifact hashes, and local commit delivered; no push.

**Research boundary:** A scientifically honest `native-partial` system with improved transfer and explicit abstentions is preferable to a superficially complete chess engine that conceals deterministic rules or fabricates PLN composition.
