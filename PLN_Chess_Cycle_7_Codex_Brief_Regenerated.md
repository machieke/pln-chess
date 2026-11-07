# PLN Chess — Cycle 7 Consolidated Codex Engineering Brief

**Theme:** PLN expressivity, positive-proof feasibility, and independent-game generalization  
**Repository:** `https://github.com/machieke/pln-chess`  
**Expected starting HEAD:** `ebe58a980d601ad8b8167a6533619c383109e08d`  
**Execution:** One autonomous engineering assignment; complete all feasible work without milestone-by-milestone handoffs.  
**Git policy:** Commit locally; **do not push**, publish, open PRs, or change external systems without explicit authorization.

## 1. Mission and non-negotiable principles

Cycle 6 restored useful operational predictions and retained 287 provenance-backed negative classifications, but **native positive composition remains unproved**. Cycle 7 must resolve the research question as far as the *existing pinned SingularityNET/TrueAGI PLN implementation* permits, then produce a precise, reviewable decision record. Do not run another open-ended survey of conjunction rules.

The core research question is:

> Can the existing, verified native PLN rules derive a supported positive move-legality proposition for a previously unseen configuration by combining **independently learned** movement geometry, destination eligibility, path clearance, and king safety, without a host-side Boolean legality gate or a preassembled joint observation masquerading as a proof?

Keep all three inference modes: **operational** (useful, explicitly partial positives), **strict** (only proven conclusions), and **experimental** (research-only). Operational must remain default. Never silently change what “supported,” “illegal,” “unknown,” or “native proof” means. A failure to establish positive composition is an acceptable *research finding*, not permission to regress the operational system.

Preserve the piece-relative/SPH-inspired model: rules refer to relative offsets, orientation, rays, intermediate occupancy, and local interactions; absolute board coordinates exist only at I/O and environmental boundary layers. Do not encode square-specific movement rules, use an external chess engine in production inference, or claim that high PLN confidence is a calibrated probability of legality.

## 2. Preflight and baseline lock (C7-01)

1. Inspect the actual repository and verify the HEAD, branch, working tree, pinned PLN/PeTTa commits, runtime lock, and current CI/test commands. If HEAD differs, record the difference and inspect it; do not reset or overwrite user changes.
2. Locate and read Cycle 6 reports, acceptance receipts, proof ledgers, and benchmark artifacts. Preserve their hashes and store a machine-readable baseline manifest under `artifacts/cycle7/`.
3. Reproduce the available Cycle 6 operational, strict, and experimental evaluations before modifying inference semantics. If system prerequisites are missing, record exact failures and continue with independent tasks.
4. Capture the 11 reported split summaries, including C6 new-game recall **96.799%**, new-game exact sets **12/32**, frozen recall **97.767%**, and all **287** evidence-removal controls. Treat these as **reported baselines until independently reproduced**.
5. Make regression comparisons on identical datasets, candidate sets, confidence thresholds, model hashes, and scoring definitions. Separate performance on legal candidates from easy negative/out-of-board candidates; count abstentions explicitly.

## 3. Bounded expressivity audit (C7-02)

Create a compact, executable operator inventory for the **pinned** native PLN version: modus ponens, deduction, induction, inheritance, negation, revision, confidence choice, any verified equivalence or conditional transformation, and their exact truth-value domains. Each claimed operator must have an actual native expression, raw output, source location, and executable test. Distinguish source-present from runtime-executable and production-integrated.

Investigate only a bounded shortlist of **plausible native encodings** for multi-premise reasoning, including nested implications, tuple/product propositions, conditional inheritance, chained unary consequences, and explicit rule antecedents. For each, identify whether the needed joint premise is (a) genuinely derived by PLN, (b) assumed as a primitive sensor proposition, or (c) assembled in host code. **Only (a) counts as native positive composition.** A host-generated tuple or joint feature may remain useful operationally but must not be relabeled a proof.

Do not import a formula from experimental PLN, introduce custom probabilistic AND, or reimplement native truth-value formulas in Python. Do not conflate `BestConfidenceCandidate` with conjunction or treat a sequence of unary implications as multi-premise introduction.

Set a strict experiment budget: at most **three carefully justified candidate encodings** after the inventory, each with a minimal runnable native witness and counterexample. Stop the search when the budget is exhausted and write a definitive feasibility report.

## 4. Positive-proof micro-laboratory (C7-03)

Implement a tiny standalone native-PLN test harness independent of chess's full candidate scheduler. It must define:

- Premise A: a learned relative movement pattern is supported.
- Premise B: a learned destination-occupancy relation is eligible.
- Optional premise C: no relevant obstruction is supported (or positive clearance evidence exists).
- Optional premise D: a supported non-exposure/safety condition.
- Conclusion: a novel positive eligibility proposition, with a complete native derivation if possible.

Train A and B from **disjoint examples and provenance groups**. Hold out every example containing the combined A+B configuration. Compare four conditions: A only, B only, A+B, and a negative/control premise. The positive conclusion must not arise from A alone or B alone if the proposed rule logically requires both. Verify the native truth values and dependency IDs and test premise deletion, reversal, contradictory evidence, and correlation duplication.

Use knight geometry + opponent destination occupancy as the primary witness (including the previously unresolved `f6h5`-type capture). Add rook obstruction and pawn capture only after the primary witness passes. Report separately whether any positive result relies on a host-built joint observation. Never declare success based solely on classification or matching the oracle.

**Research success gate:** at least one held-out combined configuration with a valid native proof that depends on both independently learned premises, and whose conclusion disappears or appropriately weakens when either premise is removed. If no candidate encoding satisfies this, record **native positive composition: not demonstrated** and proceed to the formal limitation report.

## 5. Formal capability boundary and extension proposal (C7-04)

If existing native rules cannot establish the witness, produce a precise specification of the missing operator or representation capability:

- Typed syntax, input propositions, output proposition, and truth-value semantics.
- Explicit independence/dependence assumptions, provenance propagation, and correlation handling.
- Required algebraic properties and counterexamples (e.g., monotonicity assumptions, commutativity where appropriate, no double counting, zero/one confidence edge cases).
- Whether a proposed rule is an introduction rule, elimination rule, or conditionalization mechanism.
- Minimal native MeTTa/PLN pseudocode and tests **as a proposal only**, not an active production operator.
- Security/soundness risks, uncertainty propagation, computational complexity, and migration implications.
- Comparison of (A) stay within current PLN, (B) request upstream PLN extension, and (C) introduce a separately named experimental calculus. State which option respects the original user constraint.

Do **not** implement or enable a new native PLN operator without user approval. Provide a clear decision gate with the smallest meaningful authorization request and the expected engineering effort for each alternative.

## 6. Operational generalization and abstention analysis (C7-05)

While the expressivity work proceeds, improve the existing operational model **without changing its proof claims**:

1. Partition unknowns by movement geometry, occupancy, obstruction, attack/exposure, history, unseen feature combination, confidence, and missing evidence.
2. Diagnose the 32-position C6 independent-game set and at least one new disjoint game-family split; audit leakage by position, game, structural family, and transformation lineage.
3. Develop bounded hierarchical backoff using existing relative predicates and native supported inference only. Keep coarse hypotheses from overriding strong local counterevidence; expose the selected level and lineage in every proof.
4. Add active-learning example selection as an **offline training/evaluation** facility, prioritizing uncertain and structurally novel cases. Oracle labels may be used in training/evaluation only.
5. Quantify learning curves by independent evidence budget and structural family, not merely by number of examples. Compare against a frozen C6 model and a no-new-learning control.
6. Keep false-legal, false-illegal, and self-check false-positive counts visible; never optimize exact-set accuracy by turning all predictions into abstentions.

**Research targets, not guarantees:** improve new-game exact sets beyond 12/32, preserve or improve 96.799% recall, and maintain zero observed false-legal/self-check predictions on the locked evaluation suites. If targets are missed, retain the superior model as default and explain why.

## 7. Temporal evidence and negative-proof preservation (C7-06)

Retain the Cycle 6 temporal trust modes. Test castling and en passant under (i) FEN-only metadata, (ii) validated supplied move history, and (iii) unknown/inconsistent history. Make explicit which statements are observed, assumed, or inferred. Do not convert FEN rights into a proof of the entire prior game. Preserve the complete 49+238 negative-proof regression suite and their evidence-removal controls. Check that new backoff or temporal evidence does not silently turn those supported negatives into legal predictions.

## 8. Inference performance and provenance (C7-07)

Profile the current optimized schedule and locate redundant grounding, duplicate proof nodes, and repeated native calls. Preserve exact native TV, rule ID, evidence ID, and proof-graph parity whenever claiming a cache-equivalent optimization. Report cold/warm times, native call counts, checkpoint size, memory, and proof graph size for a fixed 214-candidate fixture and larger independent-game positions. If an optimization changes proof identity, classify it as a semantic change and test it separately. Do not trade away correctness for speed without disclosure.

## 9. APIs, CLI, and inspector (C7-08)

Expose an explicit `proof_status` or equivalent field distinguishing `native-compositional`, `native-unary/partial`, `learned-conditional`, `negative-supported`, `unknown`, and `incomplete`. Ensure these labels reflect real derivations, not inferred from prediction strength alone. Add a side-by-side Cycle 6/Cycle 7 comparison view with raw TVs, inferred category, supporting/contradicting premises, evidence groups, and reason for abstention. Keep operational default behavior stable. Update CLI examples and machine-readable exports; maintain backward-compatible contracts or supply versioned migrations.

## 10. Evaluation matrix and ablations (C7-09)

At minimum evaluate:

- Frozen C6 operational and strict baselines.
- C7 operational with no new training.
- C7 operational with any new hierarchical/backoff or curriculum improvements.
- C7 strict unchanged.
- C7 experimental composition candidate(s), explicitly separate from production.
- Ablations: no backoff; no attack/exposure; no temporal evidence; no dependence handling; no learned negatives; no new training; independent-premise removal.

Report precision, recall, F1, abstention, exact legal-move sets, false legal, false illegal, false-positive self-check, terminal empty-set effects, in-board-only results, per-piece and per-structural-family metrics, and proof coverage. Include paired per-position deltas and bootstrap confidence intervals where sample size supports them. No evaluation on training-derived held-out transformations should be presented as independent game generalization.

## 11. Verification and reproducibility (C7-10)

Extend tests to cover native operator signatures, provenance dependence, false-positive controls, zero-confidence/unknown behavior, transform invariance, history trust, cache parity, API migration, and all three modes. Require a clean-copy bootstrap with pinned dependencies, deterministic dataset manifests, recorded commands, hashes, raw native transcripts, and an honest report of environment-specific failures. Never fabricate test or benchmark outcomes.

Produce `docs/cycle7/` reports and `artifacts/cycle7/` machine-readable evidence. Maintain a manifest that identifies which outputs are committed and which are generated. Preserve existing baseline artifacts and do not overwrite prior-cycle evidence.

## 12. Acceptance gates and failure handling (C7-11)

**Mandatory engineering gates:**

1. Operational remains default; frozen C6 predictions and proof labels are reproducible or any intentional deviation is documented and approved by tests.
2. Strict and experimental modes do not silently acquire unsupported positive proofs.
3. All 287 negative-proof removal controls remain valid, unless a specific justified change is separately documented.
4. No new production oracle dependency, absolute-square learning rule, host-side Boolean legality gate, or custom probabilistic formula masquerading as PLN.
5. Bounded native expressivity research finishes with either a reproducible positive witness or a falsifiable limitation report plus an extension decision proposal.
6. The independent-game benchmark and ablations execute with actual recorded results, even if the metrics do not improve.
7. Tests and clean reproduction pass, or exact environmental blockers are recorded without falsely claiming success.
8. A final local commit is produced with a clean working tree; **no push**.

**Non-mandatory research outcomes:** native positive composition, new-game exact-set improvement, native induction benefit, and performance improvement. Report negative findings as findings, not as completed breakthroughs.

If a branch of work is blocked by a native capability, stop that branch after the bounded experiment budget and continue all independent work. Ask the user only for authorization to change the PLN calculus, modify external resources, or resolve a genuinely unworkable prerequisite. Do not repeatedly stop for normal implementation decisions.

## 13. Required final delivery (C7-12)

Return a compact executive summary plus:

1. Starting HEAD, final HEAD, commit list, clean-tree status, and explicit push status.
2. A package matrix marking **complete**, **partial**, **blocked**, or **negative research finding** with evidence links.
3. Native composition verdict: exact tested expressions, raw outputs, independent-premise controls, and whether the proof meets the strict definition.
4. Frozen and new-game side-by-side metric tables, including per-position changes and zero-error claims with sample sizes.
5. Evidence lineage and proof references for at least five representative successes, five unresolved abstentions, and every regression.
6. Runtime performance comparisons and cache parity results.
7. Reproduction commands, test counts, dependency versions, artifact hashes, and known limitations.
8. A **one-page user decision memo**: continue current native PLN, authorize an upstream PLN extension proposal, or accept permanent partial positive proofs. Do not presume approval.

## 14. Suggested implementation sequence

Run baseline lock and expressivity audit first; then the isolated proof laboratory. In parallel, work on independent-game abstentions, temporal controls, and performance. After the native composition decision, integrate only verified capabilities, complete ablations, regenerate reports, run clean reproduction, and commit locally. Prioritize the research decision and reproducibility over peripheral UI polish.

**Final reminder:** The purpose is not to make a conventional chess engine. It is to learn transferable chess constraints through relative, locally grounded probabilistic reasoning, while maintaining strict epistemic honesty about what native PLN has actually proved.
