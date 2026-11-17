# Cycle 16 study registration

Registered before new native experiments. Starting commit:
`e349c9c8c7c6506a367c28623e30373c59ffc59e`. This document is immutable after
registration; deviations receive separate dated addenda and retain failed runs.

The primary target is occupancy-constrained sliding influence, including friendly
occupied destinations, not legal capture, move legality, or move choice. Test
`Clear`, then `Attack`, then correctly bound original-actor king exposure. Four
claims stay separate: native applicability (A), supplied finite composition (B),
native parameter learning (C), and generic recursive reuse (D).

Arms: R uses all eleven unchanged Cycle 15 declarations; F adds exactly one
`clear-two` declaration with the proposed nested implication; F-minus removes
only that declaration; L learns only its truth value. Additional learning arms
are an untrained clear-two prior and a full chain learning clear-two and terminal
attack rules from the same episodes. No existing checkpoint is relabeled. All
arms load their entire knowledge file, independent of observed path length.

Facts have assumed STV (1,.99); supplied rules (1,.95); untrained parameters
(.5,0); admitted training samples (label,.5). Native revision alone updates TVs.
Display thresholds remain strength >= .6 and confidence >= .1, independently
for positive and contrary channels. Raw TVs are always retained. Unknown,
below-threshold, conflict, invalid domain and incomplete execution are distinct.
Currying is supplied structure, with no assertion of conjunction semantics.

Stable rule identities, occurrence identities and real training episode ancestry
survive every application. No stamp removal, per-firing identities, cloned
recursive rules, native operator change or host clearance facts are permitted.
Separate synthetic audits test shared rule, environmental and training stamps,
diamond joins, replay, cycles, and explicitly disjoint support. Direct `|-` and
`StampDisjoint` calls are diagnostics, never answers to the main query.

Budgets: small 24 steps/64 tasks/128 beliefs; primary medium 64/128/256;
generous diagnostic 128/256/512; timeout 15 seconds (30 generous). Effective
retained queue capacity is checked against the pinned implementation. Fixed
input ordering follows observation construction, then the knowledge file. Reverse
ordering and premise confidence .5/.99 swaps are diagnostics, not tuning.

Early gate: execute the minimal symbolic recursion and matched raw two-cell R/F
cases before expanding the corpus. Retain failures and continue independent work.

Corpus: use the existing TCEC Season 26 Division P PGN, with no downloads.
Select at most one root from each source game: scan plies from 12 and choose the
first geometrically compatible slider/occupied-target pair with exactly two
intervening cells, using sorted square order, without attack labels or clearance
tests. Deterministic source order assigns 12 train, 6 development and 24 test
episodes. Record source hash, game identity, ply, full observed state, source
ancestry and geometry before fitting. Retain the original episode and dependent
E/E and O/E counterfactuals. Training additionally retains all nine E/O/U variants
and admits only the exact all-empty conditional. Unknown and blocked antecedents
are excluded, not negative samples. Every transformation remains in its source
ancestry group. Duplicate source delivery is rejected per template.

Coarse geometry ignores piece kind, absolute location and reflection: exactly
two cells on an orthogonal or diagonal ray. These two geometry strata are too
narrow for meaningful independent geometry generalization. Partition by source
episode, audit both strata across partitions, report overlap explicitly, and do
not call unseen episodes/bindings unseen geometry. Repeated openings and engines
also limit independence; no population accuracy confidence interval is claimed.

Metrics: per arm and stage raw support, classified correctness, false positives,
unknowns, conflicts, incomplete runs, positive recall including abstention;
report root and dependent endpoint counts separately. Test labels are excluded
from all training. Predictions precede evaluation-only reference calls. Partial
states use all relevant completions to establish ambiguity, not one hidden board.

Pre-registered controls: nine occupancy combinations for rook, bishop and queen;
each emptiness premise/rule removal, state and role mismatch; supplied movement,
remaining blocker, unrelated movement, removed/replaced entities, owners/kinds,
renaming, reflection, owner swap, translation, stale-state facts, zero/one/three
cell paths; low-level conflicting occupancy separately. Replay and leave-one-
source native refit check learned provenance. Shared learned chain is primary;
synthetic disjoint-support controls make only their disclosed assumption. No
post-hoc selection of disjoint training episodes to rescue the learned chain.

Optional work registered now: direct operator witnesses for returned premises,
query API compatibility, exact stored-proof round trips and fresh source replay.
No three-cell template or preference study is included.

Resource ceilings: research <=10,000 native processes, 8 measured CPU-hours and
2 GiB retained research payload; full preservation <=24 CPU-hours and 8 GiB.
Source/manifests/compact examples <=20 MiB added to Git, every new blob <5 MiB.
Bulk records and local verified packs remain outside Git. Benchmark ten repeats
per small workload after preservation stops; stored lookup and full reconstruction
are separate from native inference. Retain process, memory, task and proof sizes.

Freeze experimental source before the full established 206-shard legal suite,
controls and full tests. Verify historical files, runtime pins, source identity
and accepted checkpoint bytes. Local commits only; no remote write is authorized.
