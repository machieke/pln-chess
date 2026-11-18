# Evidence correction and active views

The Cycle 19 journal is a host-managed dependency policy around immutable historical records. Its edges are environment → measurements → annotations → parameter generations → applications → cache entries. Shared publisher or source-game metadata alone never creates an invalidation edge. This policy does not extend native inference, weaken StampDisjoint, or implement native automatic belief propagation.

An event ID cannot be reused with a changed payload. Exact repeated delivery is idempotent. A new ID for an identical environmental payload is retained as a separate delivery record, but source-group deduplication prevents it from becoming another independent training observation. Conflicting active annotation lineage for one rule/source is rejected; correction requires supersession.

Supersession computes the explicit descendant closure, marks the affected current records stale, and blocks the current view while a private rebuild is pending. The old snapshot remains immutable and can be selected explicitly for historical replay. Stale fitting, environmental references, dependent annotations, and cache retrieval are rejected. A disconnected record sharing the same statistical ancestry remains unaffected. Unknown corrected occupancy remains unknown.

The transaction rebuilds measurements and actually refits the affected model using native revision. It requires replacements for affected active parameter arms before publication. Failed or interrupted rebuilding leaves current access blocked and never exposes an old/new mixture. A successful commit replaces the in-memory view atomically; immutable JSON generations are published using a complete fsynced temporary file and atomic hard-link creation. Existing generation destinations are rejected.

Generation identity binds admitted component records, payloads, evidence versions, assumptions, learner hash, frozen structures and runtime. Genuine source stamps remain attached to learned rules. Cache identity additionally binds the complete observed state/history, environmental version, model generation, query/roles, raw facts, rules, runtime lock, policy and budgets. Cache hits return the original proof, with zero new native calls. Timing those hits does not measure faster native reasoning.

The control suite covers all thirteen requested lifecycle cases. The occupied correction rebuilds the first A training source; the resulting native query changes to supported NoAttack. The unknown correction and obsolete attacker identity remain unknown. Two dependent application branches become stale, while the disconnected branch remains valid. Incremental descendant traversal is compared with a full graph scan; independent full measurement/refit reconstruction must produce exactly the same generation, active snapshot, and observable native proof hashes. Historical replay reruns native inference over the explicitly selected old snapshot.

Inspect `artifacts/cycle19/lifecycle/summary.json`, `incremental.json`, `full.json`, and the correction demonstrations. Bulk snapshots and complete revision receipts remain in the verified local evidence packs. The compact CLI reproduces actual measurement, fitting, stale rejection, correction, replay and reconstruction with two measured training games and one held-out episode.

## Measured refit outcomes

| Refit | Clear sources | Terminal sources | Native revisions | Clear strength / confidence | Terminal strength / confidence |
|---|---:|---:|---:|---|---|
| duplicate | 24 | 24 | 48 | 1 / 0.96 | 1 / 0.96 |
| reverse | 24 | 24 | 48 | 1 / 0.96 | 1 / 0.96 |
| remove-all-clear | 0 | 24 | 24 | 0.5 / 0 | 1 / 0.96 |
| leave-one | 23 | 24 | 47 | 1 / 0.9583333 | 1 / 0.96 |
| incremental-refit | 23 | 24 | 47 | 1 / 0.9583333 | 1 / 0.96 |
| full-refit | 23 | 24 | 47 | 1 / 0.9583333 | 1 / 0.96 |

On the registered first A root, Attack returned answer (1, 0.885285) before removal and answer (1, 0.883748) after removing its clearance training source and refitting. Superseding its first empty cell with a blocker instead returned contrary (1, 0.931095). The two corrected native requests took 5.377 total native wall seconds. Each model and replay ledger is linked by its content identity. [Refit parameters, revision counts and support](../../artifacts/cycle19/lifecycle/refit-audit.json)

The registered rebuild benchmark declares D-AB as the active model in its snapshot. Other experimental arms remain archived. The dependency walk found 649 records including the superseded environment, two measurements, two annotations, three generation records, 640 applications, and one cache entry. This count includes descendants that were already archived. The transaction refitted the affected current D-AB generation. While its transaction was pending, current reads were blocked for the view. After publication the disconnected branch was available with the same identity. The full-scan comparison starts from the same immutable snapshot, recomputes the closure using a separate traversal, and remeasures and refits its affected current dependency set. The benchmark covers this single active model and in-memory policy.
