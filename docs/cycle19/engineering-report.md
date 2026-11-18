# Cycle 19 engineering report

On the 56 held-out TCEC games, the disjoint D-AB model supported Attack in 30 positions, supported NoAttack in 26, and returned unknown in 0. There were 0 explicit false positives and 0 explicit false negatives. The two independently implemented target checks agreed on all 272 registered episodes. Each measurement retains its shared source ancestry.

**Decision A + B + C + D.** Current-position clearance and rook influence are measurable. Native revision of two supplied rules supports bounded transfer with disjoint training sources. Shared source stamps block positive terminal composition, and repeated recursive rule stamps remain a limitation. The data identify no current-position probability model or native confidence conversion. [Architecture decision](architecture-decision.md)

The census examined all 224 games available within the 240-game ceiling. It excluded 96 historical game identities. The 128 roots comprise 48 training, 24 development and 56 final test games. This falls 16 short of the requested test target. The cohort includes 55 held-out directions and endpoint pairs relative to training. The independent upstream join found 29 games already used in the Cycle 10 legal work, including eight roots at the same game and ply. [Corpus and transfer](corpus-and-transfer.md)

Each of 272 episodes has two target measurements and two annotation records. The 128 natural episodes supply 256 measurements. Twelve test games additionally supplied 48 known occupancy interventions, 60 withholding cases, and 36 representation transformations. Each of the 48 training roots qualifies for both targets. The primary fits admitted 48 distinct Clear and 48 distinct Attack annotations across arms, with zero conditional exclusions among training roots. Each target in a fitted arm uses its assigned 24 games and excludes the other 24 by design. The other 224 episodes per target were outside training. [Target definitions and lineage](targets-and-measurements.md)

The seven arms on natural roots and registered subsets on dependent cases produced 2,512 queries. The complete status tables, denominators and uncertainty intervals cover each target, split and arm. The first qualifying cases link to exact inputs and observable proofs. [Native results](native-results.md) · [Decisive cases](demonstrations.md)

Correction reached both measured targets and their dependent applications. Current requests rejected stale generations and cache entries. Removing a source refitted the model from the remaining records. The occupied correction produced supported NoAttack. Incremental dependency traversal and the separate full scan rebuilt identical active views and observable proofs for the registered case. Explicit historical replay recovered the old result. These controls exercise a single-process host journal with a fail-closed pending view. [Evidence lifecycle](evidence-lifecycle.md)

All 799 tests passed, with zero failures, errors or skips. All 206 legal shards and 584,112 rows matched canonical native proofs with zero classification changes. Preservation passed 287 removal controls, 27 history controls, two recoveries and 76 holdouts. All 24,175 baseline files and the Cycle 14–18 manifests passed integrity verification. [Preservation receipt](../../artifacts/cycle19/preservation/cycle19-verification.json)

The sealed evidence contains 3,153 metered native calls, 0 incomplete native process receipts, and 0 incomplete final study queries. Native research CPU was 5,167.5 seconds. The 209 timed preservation commands used 44,533.2 CPU seconds. Sampled proof-comparison child CPU was at least 5,914.2 seconds. Peak sampled preservation process RSS reached 8,312,864 KiB. Two historical-verifier setup attempts failed before the successful original-evidence check. The output and command receipts preserve both attempts.

The 11,747 files in the bulk manifest total 1,990,123,164 bytes before packing. The local packs total 1,991,976,960 bytes and passed actual restore and SHA-256 verification. The external publication receipt supplies the final Git range inventory, canonical remote SHA and fresh published-checkout result. [Reproduction](reproduction.md) · [Publication](publication.md)

| Study phase | Wall seconds | Host CPU seconds | Child CPU seconds | Native process calls | Peak host / child KiB |
|---|---:|---:|---:|---:|---|
| corpus-preparation | 4.50 | 2.50 | 0.00 | 0 | 50236 / 41224 |
| measurement | 2.52 | 1.37 | 0.00 | 0 | 71140 / 41224 |
| training | 243.19 | 1.99 | 129.99 | 192 | 73680 / 71140 |
| inference | 3844.79 | 57.53 | 4702.78 | 2512 | 109004 / 73680 |
| lifecycle | 457.11 | 9.27 | 229.40 | 290 | 172176 / 172176 |

The legal shards recorded 1,611,614 batched native operator requests. Wall time for the full preservation driver was 163.6 minutes. Category-specific metered receipts provide the research process counts in this table. The phase-wide counter deltas in the raw timings also include concurrent reproduction activity. Host and child RSS are process high-water marks. The preservation observer reports sampled lower bounds.

| Registered first-root benchmark | Wall seconds |
|---|---:|
| cold query | 6.221509 |
| full reconstruction measure refit query | 66.017424 |
| incremental correction measure refit query | 71.785477 |
| leave one source actual refit | 71.862812 |
| warm cache lookup | 0.020966 |

The warm query returned the identical cached proof with zero native calls. Incremental and full reconstruction timings include measurement, native refit, and corrected native query. These single observations do not establish a speedup. [Exact timings and status](../../artifacts/cycle19/lifecycle/summary.json)
