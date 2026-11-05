# PLN Chess — Cycle 4 Consolidated Codex Engineering Brief

**Theme:** Compositional generalization, proof completion, and principled abstention resolution  
**Repository:** `https://github.com/machieke/pln-chess`  
**Required starting HEAD:** `38cd26b97c3cf2ffe33eac526006c9820f8c3f82` (local, unpushed, as reported)  
**Execution mode:** One autonomous, consolidated engineering cycle. Implement, test, benchmark, document, and commit locally. **Do not push.**  
**Status of baseline figures:** User-supplied Codex Cycle 3 report; independently reproduce before treating as verified.

## 0. Mission and non-negotiable design principles

Build the next version of a chess movement learner that uses **verified native SingularityNET/OpenCog PLN operators**, with piece-relative, translation-invariant relational knowledge. The goal is not to encode a conventional chess engine inside a probabilistic wrapper. It is to infer legal and illegal moves from transferable evidence, explicitly exposing strength, confidence, inference rule, dependency, and uncertainty.

Prioritize **compositional reuse**: a movement pattern, occupancy obstruction, destination allegiance, and king-exposure constraint should be reusable across unrelated positions, ideally combined by verified native PLN inference rather than a precomputed full-context key. Treat geometric coordinates as a sensor/interface representation, not as constants in learned rules. An exact FEN, board-square name, piece instance ID, game ID, or absolute square may appear in input, provenance, or proof-instance bindings but **must not define the learned movement rule**.

Hard constraints:

1. Use only verified operators and truth-value semantics of the pinned native PLN implementation. Do not implement custom probabilistic truth calculus in Python/MeTTa and call it PLN. If a required operator is absent, record an executable negative capability probe and pursue a rigorously validated alternative or a scoped native upstream contribution; do not silently replace the rule.
2. No deterministic legality gate, oracle-derived attack veto, Python-chess call, or hidden exact-rule fallback in production inference. The reference chess engine is restricted to fixture generation, training labels, evaluation, and diagnostics; explicitly test this boundary.
3. Retain a three-way output: **supported legal**, **supported illegal**, **unknown/incomplete**. Do not turn unknown into illegal or legal. Strength and confidence are distinct; confidence is not automatically a calibrated probability.
4. Preserve evidence dependence, no double counting, proof provenance, model/runtime hashes, replay, and translation invariance. Contradictory evidence must not disappear through arbitrary confidence selection.
5. Do not trade false positives for artificially high precision through universal abstention. Measure both selective risk and coverage, and count abstentions against recall and exact move-set completeness.
6. No changes to public interfaces without compatibility adapters and tests. Keep existing Cycle 1–3 artifacts immutable; write Cycle 4 results under versioned paths.
7. No push, external deployment, account changes, or destructive repository operations. Local commits are authorized. No recurring approval checkpoints for routine engineering choices.

## 1. Baseline and acceptance methodology

At startup, verify git status, branch, HEAD, dependency lockfiles, native runtime availability, artifact hashes, and the ability to reproduce Cycle 3. If the expected commit is not present, locate the local history and report the discrepancy; **do not overwrite or reset user work**. Save a signed-off-by-hashes baseline manifest and exact invocation logs.

Reported Cycle 3 reference:

| Dataset | Precision | Recall | F1 | Abstention | Exact move sets | Self-check false positives |
|---|---:|---:|---:|---:|---:|---:|
| Frozen held-out: 40 positions / 2,635 candidates | 100% | 95.53% | 97.72% | 18.14% | 67.50% | 0 |
| Adversarial: 24 positions / 1,208 candidates | 100% | 97.36% | 98.66% | 28.23% | 75.00% | 0 |
| Eight new independent games | 100% | 88.64% | — | — | 0% | — |

Reported 214-candidate benchmark: reference 24.87 s / 17,318 calls; cold cached 1.98 s / 179 calls; warm 1.95 s / zero new calls; checkpoint 1.25 MB; peak whole-process RSS ~660 MiB; 141 passing tests. These are **not guaranteed measurements**; repeat them and flag discrepancies.

**Primary acceptance gates (must attempt; performance targets are research goals, not grounds to falsify or hide results):**

- No production oracle leakage; native operator verification and proof lineage pass.
- No regression in known Cycle 3 proof parity, transformation invariance, replay, and evidence-dependence tests.
- On frozen held-out and adversarial sets, maintain zero observed self-check false positives **if feasible without collapsing coverage**; any regression requires an explicit case-level explanation.
- Improve exact move-set accuracy and reduce abstention on **independent, unseen games**. Aspirational: ≥25% exact sets on a pre-registered independent-game test set and ≥90% recall while preserving ≥98% precision. Report the actual outcome even if these goals fail.
- Demonstrate at least **three independently trained premise families** contributing to an unseen conclusion, or state precisely why the native runtime cannot prove such composition and show the strongest supported alternative with counterexample tests.
- Demonstrate at least **five newly resolved abstentions** from distinct structural families with traceable native evidence, without using oracle information at inference. If this cannot be done honestly, record the failure and root cause.
- Preserve or improve throughput within a declared budget; aspirational ≤3 s cold for the existing 214-candidate benchmark, and no more than 2× Cycle 3 memory without justified gain.

## 2. C4-01 — Repository inventory and reproducible baseline

Audit the actual code, not only the reports: native bridge, inference scheduler, local hypotheses, evidence ledger, induction integration, safety/exposure rules, caches, tests, and CLI/inspector. Map every feature to source path, callable, upstream PLN operator, and supporting test. Reproduce Cycle 3 metrics and report hashes. Freeze train/validation/holdout/adversarial/game partitions; ensure no overlap by game, transformed motif, board symmetry, or source evidence lineage. Save `docs/cycle4/baseline.md`, `artifacts/cycle4/baseline.json`, and reproducibility logs. Do not tune against frozen test labels.

## 3. C4-02 — Error and abstention taxonomy

Enumerate every remaining unknown, false negative, false positive, and incomplete candidate from the frozen evaluation and independent games. Classify into mutually reviewable root causes: missing movement prior; insufficient evidence; geometry abstraction mismatch; blocker composition; friendly destination; attacked destination; pin/exposure; double check; castling history/transit; en passant discovered attack; promotion; board boundary; contradictory evidence; scheduler budget; other. Include candidate IDs, source/target relational descriptors, raw TVs, selected/losing proofs, dependence groups, and oracle comparison **evaluation-only**. Produce a machine-readable case ledger, ranked by error frequency and expected generality of fix. No cherry-picked examples.

## 4. C4-03 — Native multi-premise PLN feasibility laboratory

Inspect pinned PLN `lib_pln.metta`, upstream tests/examples, PeTTa execution semantics, and maintained upstream alternatives. Build executable probes for: conjunction introduction/elimination, deduction across implications, implication nesting, inheritance-based abstraction, inversion, similarity/equivalence where supported, negation, revision, confidence choice, and rule application with variable bindings. Test both strengths and confidence over boundary conditions, unknown premises, conflicting evidence, correlated evidence, and repeated premises.

For each candidate composition strategy, record: exact native symbol/signature, source hash, expression, input TVs, output TVs, operational semantics, whether it genuinely combines **independent** premises, evidence overlap behavior, and a negative control. A nested implication is **not** assumed to implement conjunction. A joint categorical sensor is **not** a proof of conjunction. If upstream native conjunction can be implemented safely, isolate it as an explicit optional, independently tested, documented contribution with source/license provenance; do not patch vendored PLN silently. If semantics remain unverified, do not ship it as production inference.

**Decision gate:** choose the strongest verified native strategy, with a proof of what it does and does not establish. Continue all other packages even if general conjunction remains blocked. Write `docs/cycle4/native-composition-feasibility.md` and executable probes.

## 5. C4-04 — Factored local relational ontology

Refactor sensory features into independently addressable, piece-relative propositions: piece class, relative displacement/direction, ray segment, occupancy and allegiance, destination relation, edge/start relation, temporal rights, candidate successor, opponent attack ray, king exposure, and move admissibility. Use bounded local scopes and canonical variable roles rather than full-board fingerprints. Keep absolute positions only as instance bindings. Support translation, color/forward orientation, and compatible reflections with explicit rejection where historical semantics change.

Introduce a versioned ontology, serialization and migration plan. Preserve existing joint categorical hypotheses as a baseline/fallback **only when explicitly labeled as non-compositional**. Do not embed a hidden Boolean `is_clear`, `is_attacked`, or `is_legal` sensor that already computes chess rules. Tests must demonstrate that unrelated remote pieces do not alter a local movement hypothesis key unless they create a causally relevant attack/exposure relation.

## 6. C4-05 — Reusable obstruction and destination reasoning

Learn and test local movement primitives for rook, bishop, queen, knight, king, and pawn; distinguish geometry support, intermediate obstruction, friendly destination, opponent capture, and boundary validity. Build minimal counterfactual pairs differing in exactly one causal relation; test distances and directions not present in training. For sliding pieces, ensure a blocker at any intermediate ray position can contribute a transferable negative conclusion without a memorized whole-ray pattern. Include capture versus quiet move distinctions and knight jumps over blockers. Require native proof traces and no exact-context match for claimed transfer.

## 7. C4-06 — King safety as evidence-producing reasoning

Make king exposure an explicit, separately learned proposition with supporting and contradicting evidence. Model relative opponent-to-king attacks after a hypothetical move; include pins, discovered rook/bishop/queen rays, knight and pawn attacks, adjacent kings, double check, blocking/capturing a checker, and en passant opening a ray. Investigate whether native negation, revision, deduction, or supported conditional chains can turn sufficiently strong attack evidence into **supported illegal** rather than merely unknown. Keep a transparent conflict policy that does not overrule high-confidence contradictory evidence by arbitrary ordering.

Create a dedicated regression for the **23 Cycle 2 self-check errors** and **26 adversarial errors**: for each, track C2→C3→C4 raw TVs, final class, proof, evidence IDs, and whether a C3 abstention becomes a correctly supported negative. Include no-attack evidence versus mere absence of observed attack evidence as separate cases. Never infer safety from failure to find a threat.

## 8. C4-07 — Temporal and special-move reasoning

Represent historical conditions as explicit, uncertain evidence rather than unverified assumptions: castling rights and path/transit, king/rook prior movement, en passant's immediately preceding double pawn advance, pawn initial double step, and promotion choice. A FEN flag is a declared observation, not a proof of full game history. Add structured temporal evidence and unknown-history abstention. Ensure successor-state modeling accounts for capture removal, en passant removal, rook relocation, promotion replacement, and all resulting opponent-to-king relations. Preserve reference legality only for evaluation.

## 9. C4-08 — Make native induction useful or falsify the hypothesis

Audit Cycle 2/3 induction examples, marginal estimation, support thresholds, hypothesis ranking, evidence overlap, and downstream rule activation. Run controlled experiments distinguishing: (a) induction produces no useful rule, (b) it produces a rule never matched, (c) it matches but confidence is too low, (d) competing evidence suppresses it, (e) its representation is redundant with existing hypotheses. Use native induction on well-defined populations with measured marginals and provenance; compare against revision-only, manually seeded abstraction, and no-induction baselines. Pre-register at least one generalization task where induction could change a held-out classification. Report changes to TV, coverage, accuracy, calibration, and proof provenance separately. If no benefit, retain it as experimental rather than inflating production claims.

## 10. C4-09 — Evidence dependence and probabilistic conflict semantics

Review evidence-stamp propagation through induction, revision, abstraction, proof caching, and competing attack/legality channels. Prevent a single labeled move from being counted repeatedly as independent support via multiple derived rules. Test repeated translations, same-game correlated observations, duplicated inputs, contradictory independent observations, source retraction/rollback, and alternative proofs sharing ancestors. Explicitly distinguish lack of evidence, evidence against, and conflicting evidence. Do not use a host-side rule that treats confidence as a simple probability or combines independent truth values with an invented formula.

## 11. C4-10 — Adaptive inference without hidden legality heuristics

Improve bounded grounding and proof search: index candidate premises by typed relation, cache native results by canonical rule/premise/evidence identity, reuse proof DAG nodes, avoid redundant whole-position opponent frames, and prioritize premises by transparent information gain or expected proof utility **without changing logical conclusions**. Cache invalidation must account for model version, evidence, runtime, ontology, and context. Keep deterministic replay and parity checks for all existing proofs. Expose work counters: candidate count, unique groundings, native calls, cache hits, time, RSS, truncation, and unexplored branches. When budget is exceeded, mark incomplete rather than guessing.

## 12. C4-11 — Independent generalization curriculum

Generate new position families and full games with locked seeds and an oracle confined to training/evaluation. Include random legal play, tactical exposure motifs, sparse-to-dense configurations, novel ray lengths, unfamiliar opponent arrangements, different piece counts, and unseen combinations of individually trained premises. Create at least three tiers: translation-only control; structural-combination holdout; independent-game holdout. Split by causal motif and provenance, not just by FEN. Record dataset manifests, hashes, sample counts, candidate coverage, class balance, and leakage audit. Maintain the original frozen 40-position and 24-position sets as regression tests; do not retrain on them.

## 13. C4-12 — Ablations, calibration, and error budgets

Compare at minimum: frozen C3; C4 factored observations without composition; C4 with verified native composition; C4 without exposure; C4 without induction; C4 without evidence-dependence handling; C4 with conservative versus coverage-oriented decision thresholds. Use identical data and candidate grammars wherever possible. Report precision, recall, F1, abstention, exact sets, false legal, false illegal, self-check false positives, per-piece/special-move metrics, confidence calibration, selective risk/coverage, proof depth, latency, native calls, and memory. Do not select thresholds on the final holdout. Publish confidence intervals or bootstrap variability when sample sizes permit; mark underpowered comparisons.

## 14. C4-13 — API, CLI, and inspector upgrades

Keep backward-compatible public APIs. Add commands or options to inspect a candidate's factored premises, abstraction path, native rule applications, evidence ancestry, conflict resolution, and why it abstained. Add C3-versus-C4 side-by-side comparison for the same FEN/move, including raw TVs and inference cost. Support batch analysis of unresolved abstentions and export machine-readable diagnostics. The UI must distinguish learned facts, sensed facts, host-grounded structural transformations, and native-derived conclusions. Do not describe a host-precomputed context as a native PLN proof.

## 15. C4-14 — Tests, reproduction, and local delivery

Expand native operator tests, ontology invariance tests, causal counterfactual tests, adversarial king-safety tests, history/special-move tests, dependence/replay tests, cache/proof parity tests, and independent-game evaluations. Run a clean-copy bootstrap from locked dependencies and a fresh generated artifact directory; verify reproducibility hashes, dataset isolation, and no oracle imports in production. Produce the final work-package matrix with **complete / partial / blocked** statuses and links to source/tests/artifacts. Include a clear statement of what is genuinely native-compositional, what is native-partial, and what is merely a host-provided inductive bias.

## 16. Suggested implementation sequence (no intermediate handoffs)

1. Inventory, baseline, leakage audit, and error taxonomy.
2. Native composition feasibility and choice of verified semantics.
3. Versioned factored ontology and migration with baseline parity.
4. Movement/obstruction/destination abstractions and king-safety proof completion.
5. Temporal/special-move reasoning and induction diagnostics.
6. Evidence lineage, conflict policy, inference optimization.
7. Independent curricula, ablations, calibration, inspector, and performance.
8. Clean reproduction, documentation, final report, and local commits.

Work on independent packages in parallel when safe. If an experiment fails, retain negative results, continue other work, and provide the strongest honest outcome. Do not stop merely because native conjunction is absent. Do not expand into move selection, strategic potential fields, evaluation, or gameplay until movement legality and uncertainty have been adequately characterized.

## 17. Required repository outputs

Use names appropriate to existing conventions, but include equivalents of:

- `docs/cycle4/architecture.md`, `native-composition-feasibility.md`, `learning-semantics.md`, `coverage.md`, `experiments.md`, `limitations.md`, `final-report.md`.
- `artifacts/cycle4/baseline.json`, `error-taxonomy.json`, `native-probes/`, `proofs/`, `datasets/`, `model/`, `evaluation/`, `ablations/`, `benchmarks/`, `verification.json`.
- Versioned source, migrations, native probes, fixtures, tests, CLI and inspector changes.
- A table mapping **every acceptance criterion** to its actual measured outcome and evidence path.
- A concise `NEXT_CYCLE.md` prioritizing unresolved architectural problems, not just feature additions.

## 18. Final Codex response format

At the end, provide:

1. Starting HEAD, final local commit SHA(s), clean/dirty status, and explicit confirmation **nothing was pushed**.
2. A compact executive summary stating which genuinely new generalization capabilities were demonstrated.
3. Frozen C3→C4 and independent-game metrics, including all abstentions and errors.
4. At least five case-level before/after proof examples, including one unsuccessful case.
5. Native composition and induction findings with exact operator evidence.
6. Inference parity/performance results and resource costs.
7. Package status matrix, all blockers, artifact locations, and reproduction commands.
8. Clear, falsifiable next steps without overstating chess competence.

**Definition of done:** A reproducible, source-grounded Cycle 4 research delivery, committed locally, with honest evidence of compositional transfer (or a precise demonstrated native limitation), measurable progress on independent-game coverage, and no hidden deterministic chess legality implementation.
