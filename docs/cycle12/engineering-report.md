# Cycle 12 consolidated engineering report

Cycle 12 delivers all 20 engineering packages: typed concept conditionals, dependency graphs, exact incremental fields,
observed sequence replay, a proof inspector, full legal promotion review, clean reproduction and isolated benchmarks.
Promoted the unchanged Cycle 11 special-local legal checkpoint. Strategic models remain experimental and cannot become the operational legal default.

Starting commit: `f4a9fd5536d001fa8830773012dcd578443b0b61`. Validated production freeze: `ae7411b2bd697015e5d675043a7be6ded2ad9b43`.
Production hash: `76b645e833a27c711d1b6ee503ff7382cbffc44b431669c38dcabd7acd1dc359`. Later commits contain reports/artifacts/driver improvements without changing production source.
The final delivery commit is necessarily recorded by the repository's history and final response rather than self-embedded in this file.
All commits are local; no GitHub push, external deployment or upstream edit is performed.

```text
eaa847f Register Cycle 12 studies and fresh Cycle 11 baseline replay
23839bf Register Cycle 12 concept families, sequence references and full legal review
443eee9 Specify Cycle 12 proof, temporal and incremental regression contracts
9ae1c59 Implement typed concept packets, dependency graphs and supplied field evolution
e666ad9 Add complete Cycle 12 studies, promotion gates and browser verification drivers
9051c69 Bind delivery acceptance to executed evidence and expose graph edge provenance
9f999f4 Complete replay entry point and clarify control and measurement accounting
32a0f3b Measure legal inference separately in each realistic performance workload
f953eb7 Withhold edit-legality diagnostics on incomplete motif boards before fitting
e5f2ec0 Record complete fresh Cycle 11 baseline and locked Cycle 12 bootstrap
50c989c Validate Cycle 12 learned concepts, dependency parity and temporal studies
ae7411b Verify Cycle 12 inspector graph contrast and mobile interactions
cff2f29 Add consolidated delivery reporting and verify Cycle 12 CLI contracts
691cf60 Tighten default identity checks and document measured research limits
e0a0c57 Compare research semantics independently of measured process memory
f4e7f1a Reproduce Cycle 12 research and frozen en-passant recovery gates
c822858 Verify frozen candidate history and negative evidence controls
408b329 Report explicit error and abstention rates across Cycle 12 panels
a03124c Verify final package hashes and avoid mutating the reproduction manifest
c8281ae Preserve complete current-source legal regressions and exact native proof parity
18fd0d0 Verify frozen legal candidate across all 206 regression jobs
8cc8202 Promote verified en-passant checkpoint and validate the accepted default
8c442fb Clarify the scope of child-process memory measurements
98b54cf Record all 42 isolated Cycle 12 benchmark workers
f7e9612 Verify final inspector workflows and desktop and mobile layouts
57ddeed Verify benchmark completeness against an independent native temporal replay
```

| Package | Work | Engineering status | Measured scope / limitation | Evidence |
|---|---|---|---|---|
| C12-01 | Baseline preservation | Delivered | Fresh f4 baseline; 463 tests; 26/48/132 native groups; protected prior evidence | [receipt](../../artifacts/cycle12/baseline/reproduction-receipt.json) |
| C12-02 | En-passant promotion review | Delivered | Promoted the unchanged Cycle 11 special-local legal checkpoint. | [receipt](../../artifacts/cycle12/legal/promotion-decision.json) |
| C12-03 | Interaction ontology | Delivered | Typed relations, explicit provenance and unsupported semantics | [receipt](../../artifacts/cycle12/ontology/manifest.json) |
| C12-04 | Dependency graph | Delivered | Native proof index; host edges carry no TVs | [receipt](../../artifacts/cycle12/architecture/boundary.json) |
| C12-05 | Field interactions | Delivered | 17 demonstrations and 38 transformation/locality controls | [receipt](../../artifacts/cycle12/interactions/summary.json) |
| C12-06 | Strategic representation | Delivered | Eight typed limited targets; no joint theorem | [receipt](../../artifacts/cycle12/concepts/summary.json) |
| C12-07 | Pins | Delivered | 8/8 inspectable transfers; legal restriction unproved | [receipt](../../artifacts/cycle12/concepts/transfers.json.xz) |
| C12-08 | Forks | Delivered | 7/8 transfers; held-out pawn abstains | [receipt](../../artifacts/cycle12/concepts/transfers.json.xz) |
| C12-09 | Discoveries | Delivered | Attack/defense endpoint evidence and controlled edits | [receipt](../../artifacts/cycle12/interactions/summary.json) |
| C12-10 | Overloaded defenders | Delivered | Partial obligations and two response branches; overload unproved | [receipt](../../artifacts/cycle12/concepts/overload-consequences.json.xz) |
| C12-11 | Trapped pieces | Delivered | Positive, escape-open and unknown diagnostics; strategic trapping unproved | [receipt](../../artifacts/cycle12/concepts/trapping-diagnostics.json.xz) |
| C12-12 | Temporal fields | Delivered | Deterministic state/field replay and four gap controls | [receipt](../../artifacts/cycle12/temporal/summary.json) |
| C12-13 | Temporal demonstrations | Delivered | 12 sequences, 50 supplied moves, 62 states | [receipt](../../artifacts/cycle12/temporal/summary.json) |
| C12-14 | Independent learning | Delivered | 125 held-out raw families from one controlled source | [receipt](../../artifacts/cycle12/datasets/audit.json) |
| C12-15 | Counterfactual testing | Delivered | 20/20 distinguished/retracted; 90/90 concept controls | [receipt](../../artifacts/cycle12/concepts/controls-summary.json) |
| C12-16 | Incremental updates | Delivered | 17 successors + 62 sequence states: exact full parity | [receipt](../../artifacts/cycle12/incremental/parity.json) |
| C12-17 | Inspector | Delivered | Eight concepts, graphs, sequence/gap/proof/export and mobile checks | [receipt](../../artifacts/cycle12/ui/verification.json) |
| C12-18 | Benchmarks | Delivered | Separate legal/field/concept/temporal metrics; 42 isolated workers | [receipt](../../artifacts/cycle12/performance/summary.json) |
| C12-19 | Acceptance gates | Delivered | 534 tests, full native cohorts and source-bound legal acceptance | [receipt](../../artifacts/cycle12/acceptance.json) |
| C12-20 | Consolidated delivery | Delivered | 17 requested reports, artifacts, hashes and local commits; no push | [receipt](../../artifacts/cycle12/delivery.json) |

| Cohort | Old exact sets | Candidate exact sets | Old recall | Candidate recall | False legal | False illegal | Self-check FP |
|---|---|---|---|---|---|---|---|
| External FEN-only | 793/1020 | 793/1020 | 99.2645% | 99.2645% | 0 | 0 | 0 |
| External history-assisted | 1018/1020 | 1020/1020 | 99.9939% | 100.0000% | 0 | 0 | 0 |
| C9 adversarial | 112/128 | 112/128 | 99.2333% | 99.2333% | 0 | 0 | 0 |
| C9 special moves | 71/80 | 71/80 | 99.2537% | 99.2537% | 0 | 0 | 0 |
| C10 synthetic adversarial | 98/112 | 98/112 | 99.2227% | 99.2227% | 0 | 0 | 0 |

| Family | Limited target | N | TP | TN | FP | FN | Abstain | Precision | Recall incl. abstention | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| DiscoveredAttack | NewAttackAfterSuppliedEdit | 48 | 24 | 24 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| DiscoveredDefense | NewDefenseAfterSuppliedEdit | 48 | 24 | 24 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| Fork | PotentialMultipleTargetAttack | 24 | 7 | 14 | 0 | 0 | 3 | 100.0000% | 87.5000% | 93.3333% |
| MultipleAttackers | MultipleLocalAttackSources | 12 | 6 | 6 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| OverloadedDefender | CompetingDefenseObligations | 12 | 6 | 6 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| Pin | PotentialPinAlignment | 144 | 48 | 96 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| ThreatRemoval | ThreatAbsentAfterSuppliedEdit | 12 | 6 | 6 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |
| TrappedPiece | NoOrdinaryGeometricExit | 6 | 3 | 3 | 0 | 0 | 0 | 100.0000% | 100.0000% | 100.0000% |

All 17 interaction demonstrations, 38 field controls, 90 concept transformations, 20 counterfactual pairs,
20 actual conditional-evidence retractions, 8 pin transfers and 7 of 8 fork transfers pass their registered limited tests.
The held-out pawn fork abstains. All 12 supplied sequences (50 moves, 62 states) replay exactly;
all interaction successors and sequence fields match full native proof/evidence/graph recomputation.

The native boundary audit re-executes 40 distinct inference traces and
326 logical training nodes. There are no new native operators, host truth-value formulas,
production chess-oracle imports or modified upstream files. The current and accepted-default suites each pass
534 tests. All 287 negative controls, the complete historical and external legal populations and
all 7959 protected prior files pass their recorded checks.

| Workload | Full successor median s | Dependency successor median s | Full / incremental |
|---|---|---|---|
| en-passant | 3.753 | 3.434 | 1.093× |
| en-passant-exposure | 3.758 | 3.838 | 0.979× |
| promotion | 2.816 | 2.687 | 1.048× |
| published-midgame | 19.690 | 15.159 | 1.299× |
| rook-obstruction | 4.572 | 4.261 | 1.073× |
| standard-opening | 31.582 | 26.788 | 1.179× |

Performance uses 42 isolated fresh workers, including opening and middlegame positions, with parity before comparison.
See [performance.md](performance.md) for all conditions, native calls, memory and measurement limits.
Fresh data generation, training and research replay pass 55 comparisons; the two concept models are byte-identical.
The fresh baseline and full current-source legal gates are separately executed, not inferred from the research replay.
Final browser proof covers all eight concepts, all field families, graph/proof inspection, sequence steps, missing histories,
empty/unknown/budget states, actual proof export and desktop/mobile layouts, with zero captured errors.

Every concept remains experimental. Native operators derive a limited conditional from an explicitly host-observed `ObservedStructuralRolePacket`. Component field proofs are separate; their uncertain truth values are not conjoined into that packet. Complete joint concept proofs, native temporal implications, strategic overload theorems and strategic trapping theorems all remain zero. No move score, search, ranking, material-value table or move selection is implemented.

The scientific limitation is substantial: one controlled source, supplied structural roles and pooling, mostly shared conditional
keys, no arbitrary native conjunction, and no proof of safe strategic choice. Overload has two local consequence branches without
universal response exclusion. Trapping distinguishes unknown exits without evaluating desirability. FEN-only legal history remains
incomplete. Operational en-passant exposure-removal behavior remains unchanged. Candidate enumeration is bounded; full proof exports
can be large. Native call reductions need not dominate graph construction and serialization costs.

Cycle 13 recommendation: **Option A — continue relational concept learning**. Collect independent externally sourced role/field
annotations with explicit ancestry, test unseen conditional families including pawn forks, and quantify uncertainty and conflicting
observations. Expand overload response and safe-escape evidence while preserving abstention and proof boundaries. Measure and reduce
proof/graph transport cost without changing inference semantics. Reconsider experimental strategic comparison only after those
transfer and reliability gates improve. These results do not materially change the earlier no-go boundary on new native composition;
Option C is not supported by new operator evidence, and strategic move selection is deferred.

All required reports are linked in [package-matrix.md](package-matrix.md). The machine-readable
[delivery receipt](../../artifacts/cycle12/delivery.json) and [artifact manifest](../../artifacts/cycle12/manifest.json) bind final checks and files.
