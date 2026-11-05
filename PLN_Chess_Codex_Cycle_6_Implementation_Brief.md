# PLN Chess — Cycle 6 Consolidated Codex Engineering Brief

**Theme:** Operational recovery, verified native-PLN composition feasibility, and evidence-safe integration  
**Repository:** `https://github.com/machieke/pln-chess`  
**Starting commit (verify locally):** `6c7538cedeb52fa4a921e3549ac57022ff7874d8`  
**Previous stable behavioral baseline:** Cycle 4, commit `d5cfcb126acc9c3e5da669744d661e6895fb9303`  
**Delivery:** complete work in one consolidated run; commit locally; **do not push**, publish, deploy, or modify upstream repositories without explicit authorization.

## 1. Mission and non-negotiable constraints

The project aims to learn chess move permissibility using **piece-relative, locally transferable probabilistic relations** and **actual verified SingularityNET/OpenCog PLN inference**, rather than absolute board coordinates, brute-force rule discovery, a hidden deterministic chess engine, or a bespoke probabilistic calculus. The board is the environment; it is not the learned rule's absolute reference frame. Absolute coordinates may exist only at the FEN, UI, state-adapter, or oracle boundary.

Cycle 4 reported strong operational predictions, while Cycle 5 enforced strict positive proof composition and consequently abstained on **every legal move**. Cycle 5 also added 238 inspectable negative proofs. Recover a useful operational mode **without misrepresenting the strength of its proofs**. Investigate existing native PLN capabilities before considering any extension. **Do not add or activate a new conjunction rule** under this brief: the user originally required only rules already present in SingularityNET's PLN. An extension may be documented as a proposal, with isolated research notes, but must not be part of the default or accepted native-only result.

**Scientific honesty:** report truth-value strength and confidence separately. Neither is automatically a calibrated probability. Distinguish native derivations, supplied observation primitives, learned categorical conditionals, host-side structural processing, and oracle labels. Never claim that a host-assembled joint observation constitutes native PLN conjunction. Do not fabricate successful positive composition when the native runtime cannot derive it.

## 2. Starting-state audit and baseline lock (C6-01)

1. Inspect repository, branch, working tree, tags, commit ancestry, vendored PLN/PeTTa versions, current configuration, documentation, and artifacts. Verify the stated starting commit; if HEAD differs, document it and work from the actual checkout without discarding user changes.
2. Preserve immutable copies of the C4 and C5 models, configs, datasets, proof traces, reports, and manifests. Hash and version all baselines. Re-run their exact evaluations where dependencies permit. Do not substitute newer datasets or thresholds while claiming baseline parity.
3. Establish **frozen evaluation** for: C4 frozen holdout (40 positions, 2,635 candidates), adversarial (24, 1,208), older eight games, C4 twelve games, C5 validation, combination and structural holdouts, and C5 sixteen games. Record split membership, oracle legal counts, source hashes, model hashes, and dataset leakage/overlap audits.
4. Capture C5 failure mechanism at source level: find precisely which positive-proof acceptance condition causes 0% recall. Identify whether it is configuration, inference logic, proof-policy gate, or absent derivation. Provide call-graph and before/after example traces.
5. Create `artifacts/cycle6/baseline/` with machine-readable reports and a human-readable comparison.

## 3. Three explicit inference modes (C6-02)

Introduce or refine **independently selectable**, versioned modes:

- `operational`: C4-compatible learned positive predictions, with C5 verified negative counterevidence where safe. A positive prediction must be labeled **native-partial / evidence-supported**, never **composition-proven** merely because it has a native MP trace.
- `strict`: C5's strict proof policy; abstain if native positive derivation is unavailable. Maintain its negative proof capability and preserve current scientific semantics.
- `experimental`: isolated native-only composition candidates and ablations. Never auto-promote into operational.

Each output must include `classification` (`supported-legal`, `supported-illegal`, `unknown`, or `incomplete`), `mode`, raw STV, `proof_status` (e.g. `native-composed`, `native-conditional`, `native-negative-chain`, `insufficient-native-proof`), evidence IDs, dependence groups, matched native rule IDs, source of observation primitives, model/runtime versions, and any proof gaps. Do not encode a proof-quality distinction by silently changing the truth value. Make mode explicit in CLI, Python API, and inspector; maintain compatibility aliases where possible and test migrations. Default to `operational` **only after** the regression gates in section 12 pass; otherwise preserve the previous default and report the blocker.

## 4. Recover positive predictions without invented proofs (C6-03)

Restore the C4 learned local positive inference path as an **honestly labeled operational inference policy**, preserving its source model and semantics. Carefully integrate C5's additional negative proofs, distinguishing contradictory evidence from independent support. Do not simply choose whichever TV has higher confidence when evidence dependencies overlap. For every conflict, show both channels and the decision rationale. If native choice cannot handle the dependency structure defensibly, abstain and record the reason.

Compare at least four variants: C4 frozen; C5 strict; C4 operational plus C5 verified negatives; and operational without the new negatives. Re-run exactly matched datasets and thresholds. Attribute any changed classification to its specific inference/proof/evidence node. Ensure no candidate is supported-legal solely because the oracle says it is legal. Add a targeted suite for the 49 C2 false-legal cases and 238 additional C5 negative proofs. Prevent reintroduction of false-legal or false-illegal cases on the frozen evaluation suites.

## 5. Native PLN capability investigation (C6-04)

Inspect the **pinned, actually executable** SingularityNET/OpenCog PLN core and its current upstream history, if locally available. Enumerate relevant rules with exact source location, signatures, argument requirements, evidence assumptions, truth-value formulas, and runnable probes. Prioritize native modus ponens, deduction, induction, revision, negation, inversion, inheritance, implication, similarity/equivalence, abduction if present, and evidence choice. Differentiate verified runtime support from source-inspected or experimental symbols.

Design a minimal composition laboratory where A and B are learned from **disjoint training evidence**, and a novel conclusion C is required in a held-out case. Attempt only semantically valid native derivations. Probe chaining, inheritance-mediated generalization, conditional nesting, and supported multi-input rule forms; demonstrate whether each truly depends on **both** independent premises, rather than a preconstructed `A-and-B` sensor or an implication already containing C. Include missing-premise, swapped-premise, contradictory-premise, correlated-evidence, and renamed-symbol controls. Log the exact MeTTa expression, stdout, STVs, proof graph, versions, and failure modes.

**Critical rule:** a native `|-` expression is not sufficient proof of conjunction. A valid composition claim must have an independently checkable semantics and counterfactual dependence on both premises. If no existing operator suffices, publish a precise **native composition impossibility/limitation report for the audited rule set**, without claiming a universal theorem about all PLN implementations.

## 6. Independent-premise factorial transfer laboratory (C6-05)

Create controlled curricula with **disjoint provenance groups** and train/test splits that withhold entire combinations, not just translated coordinates. Cases should cover: knight geometry × opponent destination occupancy; bishop/rook ray geometry × obstruction at unseen distances; queen movement × capture; pawn forward/capture × destination type; king movement × learned attack exposure; castling rights × transit occupancy/attack; en-passant target × discovered exposure. For each, distinguish:

1. each primitive learned separately;
2. combination absent from training;
3. positive and negative contrast cases;
4. translated/reflected/owner-flipped variants where semantics are preserved;
5. a misleading unrelated piece introduced far from the move;
6. a missing/uncertain premise;
7. evidence dependence and contradiction controls.

Report success separately for **native composed**, **native conditional transfer**, and **host-assembled composite category**. A classifier that merely recognizes a joint fingerprint does not pass the native-composition experiment. Include the unresolved C5 knight capture `f6h5` as a mandatory traceable case.

## 7. Negative-proof preservation and conflict handling (C6-06)

Keep C5's verified obstruction, boundary, exposure, pin, and discovered-attack reasoning. Verify 49 prior false-legal cases and all 238 newly reported negative classifications against their original exact data, with counterfactual removal tests and provenance. Evaluate false-illegal risk under independent games and adversarial configurations. Distinguish a native negative proof from mere absence of a positive proof. Add explicit handling for contradictory positive/negative beliefs, overlapping evidence, missing observations, and low confidence. The default policy must not silently turn unknown into illegal.

## 8. Temporal evidence and special moves (C6-07)

Retain and test three provenance modes: trusted FEN metadata, externally supplied observed move history, and unknown/unverified history. Clearly distinguish state metadata from a native derivation of historical legality. Implement versioned event/evidence records and replay for castling-right changes, en-passant opportunities, pawn two-step history, promotions, and capture effects where feasible. Tests must include contradictory or incomplete histories and state edits that change rights. No deterministic chess-engine legality check in production. Reference engines remain confined to training/evaluation. Do not infer a complete historical theorem from FEN alone.

## 9. Induction and abstraction research (C6-08)

Revisit C2–C5 induction probes, including the C5 experimental output and its zero classification benefit. Audit marginal estimates, population assumptions, disjoint evidence, rule activation, and application to novel contexts. Run enabled/disabled/sham, marginal-perturbation, dependence-overlap, and unseen-combination ablations. Require actual classification changes backed by native proof traces before claiming predictive benefit. If no defensible improvement is found, leave induction disabled in operational mode and report why. Do not count redundant derivations of already-supplied abstractions as new discovery.

## 10. Locality, invariance, and anti-memorization (C6-09)

Inspect all learned hypothesis keys and their pre-hash descriptors for absolute square names, board-position identifiers, global opponent enumerations, and accidental full-board fingerprints. Maintain a clear division between local primitives, boundary-relative context, historical evidence, and globally relevant king-exposure reasoning. Test translations, file reflections, color/rank flips, and piece-ID renaming, excluding transformations that genuinely change castling/EP semantics. Verify that adding a distant unrelated piece does not invalidate a truly local learned movement rule. Produce counterexamples for any remaining nonlocal dependence.

## 11. Inference efficiency and proof-preserving caching (C6-10)

Retain C3/C4 optimized native scheduling and C5 cache parity. Profile duplicated proofs, candidate grounding, repeated opponent-frame evaluation, interpreter startup, and memory. Cache keys must include runtime, model, mode, proof policy, observation and evidence versions, and inference budget where relevant. Compare cold/warm timings and call counts on the original 214-candidate benchmark plus dense midgame positions. Require complete STV, classification, proof-node, evidence-ID, and matched-rule parity between cached and uncached paths. Optimization may not silently truncate proofs or reclassify incomplete results as unknown.

## 12. Evaluation and acceptance gates (C6-11)

**Mandatory correctness gates:**

- Operational mode restores **nonzero supported-legal recall** and retains C4-level utility; target at least C4's 97.77% frozen recall and 95.37% C4-new-game recall, or document any small justified regression with per-candidate evidence and do not silently change default.
- Preserve **zero observed false-legal, false-illegal, and false-positive self-check classifications** on the exact frozen baseline splits; also test new adversarial cases. This is an empirical requirement, not a universal guarantee.
- Preserve all 49 historical false-legal resolutions and C5's 238 additional negative proofs or explicitly document each excluded/changed case.
- Strict mode continues to abstain where positive native proof is absent; no fabricated proof-complete positives.
- All native composition claims pass the independent-premise counterfactual suite. If none passes, report **not achieved**, not a partial success disguised as proof.
- No production oracle imports, deterministic king-safety veto, host-side TV formula substitution, or undisclosed custom conjunction.
- Baseline reproduction, clean bootstrap, native operator probes, complete proof provenance, and cache parity all pass.

**Research targets (not acceptance blockers):** recover ≥75% frozen exact move sets, ≥40% independent-new-game exact sets, preserve ≥99% observed operational precision, improve abstention without introducing false positives, and keep 214-candidate cold inference within 2× the C4 benchmark unless an explicit justified proof-cost tradeoff is shown. Report both in-board and all-candidate metrics, precision/recall/F1, exact sets, abstention, confusion matrices, error families, confidence/strength distributions, calibration diagnostics, and 95% uncertainty intervals where meaningful. Empty-terminal exact matches must be reported separately.

**Scientific result acceptance:** an honest negative finding about native composition is acceptable if operational recovery, rigorous probes, reproducibility, and truthful mode separation succeed.

## 13. API, CLI, inspector, and developer experience (C6-12)

Expose `--mode operational|strict|experimental` consistently on `infer`, `inspect`, `evaluate`, `benchmark`, and API entry points. Show side-by-side per-move mode comparisons and trace why a classification changed across C4/C5/C6. Surface raw STVs, provenance, dependencies, missing premises, native operators, host observations, history trust mode, and proof completeness. Preserve export/import compatibility or supply a tested migration. Provide concise examples for a rook obstruction, king entering attack, knight capture `f6h5`, castling with unverified rights, and a contradictory-evidence case.

## 14. Test suite and independent verification (C6-13)

Add unit, integration, native operator, replay, provenance, transform, negative-proof, mode-isolation, cache-parity, and factorial-combination tests. Include property-based/metamorphic tests where feasible. Verify that changing one premise affects the relevant proof and that withholding a required premise prevents an unjustified composed conclusion. Run clean-copy bootstrap from pinned dependencies and preserve logs. Avoid rewriting old expected results to match regressions; add versioned fixtures instead. Clearly distinguish source inspection, recorded results, and tests actually executed in this run.

## 15. Delivery package and autonomous execution (C6-14)

Produce:

- `docs/cycle6/architecture.md` — operational/strict/experimental semantics and proof contracts;
- `docs/cycle6/native-capability-audit.md` — operator inventory and executable composition probes;
- `docs/cycle6/composition-lab.md` — independent-premise factorial results and failure analysis;
- `docs/cycle6/temporal-evidence.md` — history trust modes and special-move limits;
- `docs/cycle6/learning-and-induction.md` — evidence assumptions and induction ablations;
- `docs/cycle6/benchmark-and-evaluation.md` — matched baselines, metrics, latency, memory;
- `docs/cycle6/final-report.md` — work-package matrix, source changes, measured achievements, remaining limitations, next priorities;
- `artifacts/cycle6/` — machine-readable proofs, comparisons, tests, hashes, logs, benchmark traces, and reproducibility manifest;
- a clear README section explaining how to run and interpret all three modes.

Codex should proceed through **all 14 work packages** without pausing for routine decisions. Work around isolated research failures and complete independent packages. Stop only for a genuinely blocking dependency, an irreversible/external action requiring authorization, or a fundamental conflict with the native-only constraint. Make multiple logical local commits, preserve a clean working tree, and report commit hashes. **Do not push**; this overrides any previous cycle's contradictory delivery instructions.

## 16. Final response contract for Codex

Return: starting/final HEAD; whether anything was pushed (expected **no**); full package status matrix; exact model/runtime/dataset hashes; frozen and new-game C4/C5/C6 comparison tables; count and trace of supported legal/illegal/unknown/incomplete moves; evidence for all 49 and 238 negative cases; positive-composition verdict with exact native expressions and counterfactuals; temporal/induction findings; cache parity; benchmark metrics; test totals; clean-build result; outstanding scientific limitations; and links to local reports. **Do not claim full chess legality or native conjunction unless independently verified.**
