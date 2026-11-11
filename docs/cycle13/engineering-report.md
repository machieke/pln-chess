# Cycle 13 consolidated engineering report

Cycle 13 delivers experimental relative move comparison, native preference revision/application, bounded two-/three-ply explanations, learned fork generalization and a desktop/mobile proof inspector. All twenty packages have executed evidence. The operational legal model is preserved and preferences are not promoted into move selection.

The starting commit is `b000898a0a1f46e556f161982f2c0e6d3944c322`. Frozen production commit: `3e5aae6b6e4989cc8f0a5ad4eafcbd7df352f9dc`. Report content commit: `200e22f4a4d15e60bad4d4e1832992d5489917c3`; the final packaging commit is recorded by repository HEAD and in the delivery message. Local commits only; no push or external deployment was performed. The [package matrix](package-matrix.md) lists all 20 packages and evidence.

The legal model remains `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`, with zero new false-legal, false-illegal or self-check false-positive classifications. Full ordered native proof parity covers 206 shards and 584,112 candidate rows, including strict and experimental panels. These are measured acceptance cohorts, not universal correctness guarantees.

| Cohort | Starting exact sets | Final exact sets |
| --- | --- | --- |
| External FEN-only | 793/1020 | 793/1020 |
| External supplied history | 1020/1020 | 1020/1020 |
| C9 adversarial | 112/128 | 112/128 |
| C9 special moves | 71/80 | 71/80 |
| C10 synthetic adversarial | 98/112 | 98/112 |


The curriculum contains 340 independent pairs/games with conservative ancestry partitions. The fixed test set has 56 pairs, 15 resolved directional labels, 6 answered directions and 5 correct directions: answered accuracy 0.833, coverage 0.400. Unknown labels and abstentions remain visible. The complete [learning report](preference-learning.md) includes every cohort, precision/recall references and cluster uncertainty. [Transfer](preference-transfer.md) preserves the initial ten illustrations, nine of which have unresolved reference labels. Ten additional correct-reference illustrations are explicitly selected after outcomes from five test and five calibration cases; they demonstrate inspectable applications and are not an unbiased success rate.

All three old fork abstentions are resolved and all prior correct answers preserved: 306/306 concept test cases and 64/64 calibration cases. The 96-game external concept panel gives 28 correct classified answers, 68 abstentions and no wrong classified answers, with 312/312 dependent controls. The broader concept families remain weak; see [fork resolution](fork-resolution.md) and [concept robustness](concept-robustness.md).

Sixty registered supplied-branch plans yield 120 endpoint comparisons and ten [two-ply](two-ply.md) plus ten [three-ply](three-ply.md) demonstrations. [Temporal results](temporal-preferences.md) compare immediate and continuation-conditioned beliefs against the same endpoint labels, including reversals and unknown responses. Production performs no response search.

The host assembles a categorical packet from independently inferred field and concept records. Native revision learns three separate conditional channels, and native modus ponens applies those channels to the supplied packet. This is a native conditional derivation, not a native conjunction of uncertain fields, a complete strategic theorem, a proof of legality or an optimal move claim. No scalar strategic utility or automatic move selection is implemented.

The native boundary audit reexecutes 2988 ordered training nodes and 40 distinct preference proofs. It checks relative rule constants, protects 11553 historical files, runs oracle-disabled comparisons and verifies the isolated legal import path. No new native operator, host probability formula or upstream change is introduced.

Test-set raw-strength Brier score is 0.204 and ECE is 0.158; these are diagnostics, not a calibrated production probability. [Calibration](calibration.md) includes reliability, confidence selection, evidence-volume and true source-holdout studies. [Ablations](ablations.md) compare eight descriptor arms plus continuation and dependence interventions. The reversal controls pass 340/340; all 56 conditional-removal controls abstain. Controlled cyclic preferences show that transitivity cannot be assumed.

[Performance](performance.md) reports all 80 measured cold/warm requests across four workloads and full/incremental arms, with exact proof parity, memory, invocation counts, proof size and failures. Complete-output cost limits interactive use. The [inspector evidence](../../artifacts/cycle13/ui/verification.json) includes recorded desktop/mobile behavior, trained and indeterminate results, bounded continuations and an actual byte-preserving JSON download.

The starting suite passes 534 tests, the fresh frozen-source suite passes 584, and the final post-acceptance suite passes 588. All 287 negative controls, 27 history controls, two recoveries and 76 holdouts pass. [Clean reproduction](reproduction.md) independently rebuilds the reference engine, labels, native features, models, proofs and studies; 527 artifacts agree under documented semantics. The final package contains source, ledgers, checkpoints, full proofs, plots, logs and hashes.

Cycle 14 recommendation: **Option A — continue preference learning**. The fixed coarse abstraction, many unknown reference labels, limited independent test support, absent empirical probability calibration, partial conditional proof boundary, limited concept coverage and costly endpoint inference do not justify automatic move selection. No new evidence changes the native composition no-go decision, so Option C is not warranted. Option B should remain a future separately authorized experiment.

Next priorities are to improve reference supervision without silently interpreting unresolved bounds as exact scores; preregister a larger independent source holdout with more quiet/ambiguous pairs; investigate relative descriptors that distinguish conflicting contexts; evaluate response coverage and uncertainty propagation; and reduce complete-proof cost while retaining exact dependency/provenance parity. New data and abstraction experiments require new partitions and evidence generations, not test-set tuning.

Local commits through this report's content snapshot:

```text
c17dad5 Register Cycle 13 preference studies and freeze external reference sources
bf2deab Register 340 independent move pairs and reproducible offline labeling protocol
de75d51 Specify preference proof boundaries and register independent concept controls
6e42d47 Define preference metrics with abstention and clustered uncertainty controls
7e1f5cb Audit independent source partitions and register bounded continuation supervision
4d53892 Register preference evidence, comparison, and temporal proof contracts
18c05fb Prepare gated native preference and fork studies with diagnostic figures
e7e1e1c Prepare independent concept evaluation and configurable baseline concurrency
3c47e7d Prepare label-independent native feature extraction with source-bound receipts
05915f5 Prepare fixed-cohort preference, transfer, and temporal evaluation drivers
9b85c41 Prepare complete clean-checkout legality and native-proof regression gate
ebfedc9 Document production interfaces and exact-replay integration contract
e13ac99 Register controlled dependence and true source-holdout studies
0a1e3fa Queue registered reference studies behind the complete baseline gate
eab41a6 Preserve terminal mate outcomes in offline continuation supervision
563b3a1 Exclude training and duplicate raw motifs from independent concept controls
50b495d Prepare source-holdout reliability figures alongside primary calibration
6a47e2d Audit bounded endpoint labels against full source history and actor perspective
5f58c1c Include endpoint supervision audit in the gated reference study runner
94ec522 Specify controlled cache comparisons without conflating native memoization
058b7ba Prevent silent replacement of prior experimental checkpoints
fc0ad59 Clarify execution metadata boundaries for exact scientific replay
ddcf090 Bind preference fits to their exact training subsets
b06be4b Prepare isolated preference benchmarks with complete proof parity
8590e9f Summarize executed legal cohorts with exact native proof bindings
ef9e80e Handle history-assisted exact-position counters in legal summaries
806ea7c Fix categorical contrast and uncertainty semantics before preference fitting
4ce90c2 Verify complete fresh Cycle 12 legal and research baseline for Cycle 13
3e5aae6 Implement isolated native preferences, learned fork roles, bounded branches and proof inspector
aba3985 Add frozen-source study orchestration and complete clean research reproduction gates
95acbc1 Preserve native consistency controls and verified browser export development evidence
4c8530b Add measured report generation and final research verification workflow
a2ce71f Test source-bound legal acceptance and add fresh post-acceptance verification
48b7bbe Add complete delivery inventory and clarify empirical transfer limits
ad01379 Audit observed curriculum coverage against independent native replay
0c712fb Document inference boundaries and distinguish conflicting evidence from contradictory predictions
bae892c Measure complete proof package sizes and clarify benchmark memory scope
eb09df4 Capture recorded browser proof identities and document training-evidence lookup
975cfe2 Retain transparent successful-transfer illustrations and strengthen browser provenance capture
7b4479f Deliver frozen preference studies, native feature evidence, CLI checks and calibration results
3745da4 Verify trained browser workflows and preserve exact native proof exports
6e8b90c Run the final complete test collection in isolated audited partitions
77e42e8 Report complete proof export sizes and shared-host benchmark scope
0c02726 Reproduce all 527 research artifacts and verify explicitly selected transfer illustrations
74ac5bd Verify observed relational curriculum coverage against fresh native replay
eb7f9ca Preserve full legal proof parity, isolated benchmarks and source-bound legal acceptance
ad8f465 Verify all 588 final tests and actual legal defaults after acceptance
3ccd96e Clarify cumulative child-memory measurements in benchmark interpretation
200e22f Keep reproduction commands from overwriting delivered evidence
```
