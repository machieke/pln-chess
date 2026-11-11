# Cycle 13 implementation and replay contract

This is the integration contract for the gated study drivers. Production implementation starts only after the complete starting-baseline receipt passes. No measurements in this document are research outcomes.

## Production interfaces

- `cycle13.ontology.project(packet, abstraction)` returns `id`, `descriptor`, `rule_id`, `canonical_order`, `distinguishable`, and `complete`. Its key validates categorical relative features and excludes coordinates and provenance identifiers. `reverse_packet(packet)` swaps display roles without altering their observations or learned evidence.
- `cycle13.model.PreferenceModel(runtime_version, abstraction='relational', variant=...)` stores three independent `first`, `second`, and `no-demonstrated-preference` native channels, evidence IDs, connected dependence groups, a ledger digest and training report. It validates its grammar, runtime binding, relative descriptors and serialized content identity. It is never a legal checkpoint.
- `cycle13.evidence.PreferenceLedger(path).append_many(payloads)` returns one stable evidence record per submitted payload, preserving input order even for idempotent deliveries. It validates the complete batch before appending and rejects conflicting reuse of an observation identity. Record timestamps do not enter scientific evidence identities.
- `cycle13.inference.infer_preferences(packets, model, runtime=..., options=..., session=...)` returns `comparisons` plus `execution`. `PreferenceNativeSession` scopes native reuse by model, options and runtime. A comparison includes display channels `A`, `B`, and no-demonstrated preference; raw TVs, status, rule/evidence/dependence IDs, native trace and proof identity, conditional/joint completeness, contradiction and gaps.
- `cycle13.api.compare_moves(position, move_a, move_b, ...)` accepts explicit legal, field, concept, fork and preference models, a `PreferenceSession`, `PreferenceOptions`, optional supplied `history`, and an observation `source`. Its output includes `packet`, `preference`, `states` with separately inspectable field/concept graphs, legality beliefs, relative changes and `execution`. The extraction driver supplies an empty preference model.
- `cycle13.temporal.analyze_continuations(position, branches, ..., horizons=(2,3), selection_provenance=...)` accepts at most two explicit branches per candidate, each at most three plies. Branches have the form `{'A': [[candidate, reply, continuation]], 'B': [[candidate, reply, continuation]]}`. It returns separately proven states and a `comparisons` list containing `horizon`, `packet`, and `preference`. Missing or unequal-depth branches retain explicit uncertainty. `unexamined_responses` must never imply exhaustive coverage.

The registered abstractions are `relational`, `attack-only`, `defense-only`, `mobility-only`, `exposure-only`, `without-concepts`, `weaker-relative`, and `full`. Main and without-concepts use the four field families; full adds limited concept consequences. Weaker relative pooling may retain relative move geometry and mover kind. Horizon is part of a temporal conditional's context. No abstraction contains a weighted score.

## Fork interfaces

`cycle13.concepts.ForkModel` is a separate runtime-bound binary conditional checkpoint. `fork_packet(result)` observes the target occupancy/allegiance and the separately inferred component attack states of a supplied Cycle 12 fork candidate. It omits attacker kind and movement geometry. Unknown observation or component state prevents a complete packet; it never becomes a negative target.

`cycle13.concepts.infer_concepts(cases, starting_model, field_model, fork_model=..., ...)` returns a complete preserved `starting_conditional` and an independent `fork_role_conditional` for each fork, with an effective result. A classified starting answer remains unchanged. The new learned conditional can resolve a starting abstention. Its observation, rule, native trace, model identity and host packet must be exposed explicitly, not attached to the original packet as though it were the same proof. `ForkSession` retains distinct field and native scopes.

The concept evaluator compares all starting native TVs, traces, rule IDs, evidence IDs and classifications with the fresh baseline before checking preservation. It also evaluates the new generic fork conditional without fallback, so preserving old answers cannot conceal errors in the new abstraction.

## Observations and budgets

The shared sparse field domain covers actor attacks on occupied opponent targets, actor defenses of occupied friendly wards, opponent influence on the actor's king, and ordinary mobility of the supplied candidate mover identities. Changed occupancy reconstructs that domain. Captured entities and missing enumeration are domain changes, not newly inferred negative relations. Unknown and incomplete records remain distinct from supported and contradicted records.

Profiles may count separately supported records and compare those counts categorically. They must separately retain unknown/incomplete counts and the declared observation scope. No numeric weighting or TV aggregation is allowed. An indistinguishable primary descriptor cannot support a directional answer.

Cache keys bind actual dependencies, all relevant model/runtime identities and options. Full recomputation and incremental reuse produce the same semantic results and complete proofs. A returned object cannot mutate cached evidence. A logical proof-node budget still applies on a cache hit. Budgets must say whether they apply to each stage or the whole request; global deadline exhaustion makes the result incomplete.

The controlled full/incremental comparison should keep pure native-math memoization the same in both arms, while full recomputation clears relation records before rebuilding a state and incremental inference retains dependency-bound records. If an additional arm disables every cache, label that intervention separately. Report that the sparse query domain and observations are reconstructed even when unchanged local proof records are reused; do not claim a new spatial query scheduler. Native operator evaluations and interpreter process launches are distinct counts.

Execution counters, elapsed time, cache information and memory measurements belong under explicit `execution` fields. The pre-existing trapped-piece diagnostic's process RSS value is moved into an execution subrecord in new wrappers. Native proofs, observation identities, source lineage, gaps, classification, unknown state and truncation consequences remain semantic. This allows exact replay without silently removing scientific claims.

## Source freeze and reproduction

Before primary feature extraction, complete the production interfaces and inspector, run targeted tests and freeze the production source. Extraction receipts bind the production code hash, runtime and all checkpoints. If an inference-affecting source change invalidates a generation, preserve it and create a new generation rather than silently reusing stale features.

The clean-checkout legal driver uses the byte-identical accepted Cycle 12 model and all 206 registered jobs. It compares complete native DAG contents and candidate provenance with the fresh starting replay. It also executes all 287 negative controls, 27 history controls, accepted recoveries and holdouts, and the automated suite. Historical artifacts remain immutable.

Fresh research replay must regenerate the source selections, semantic teacher labels, native field/concept packets, ledgers, revision checkpoints, inference proofs, controls and bounded temporal examples. Timing differences are retained in raw artifacts but excluded from scientific identity through named execution fields. Native traces and truth values are never exempted from parity.

Only after actual gate receipts pass may a new source-bound acceptance receipt recognize the unchanged legal checkpoint. The acceptance chain may import the Cycle 13 acceptance module, but must not import experimental preference, field or concept inference. Explicit earlier-cycle output overrides keep their existing semantics. Final default verification exercises the actual CLI without an explicit checkpoint.

Benchmarks run after other native workers finish. Five repetitions cover single and multiple comparisons, two/three plies, cold/warm and full/incremental paths. Exact semantic and proof equality precedes speed claims. Browser verification uses the actual desktop/mobile inspector, evidence/proof export and bounded continuations, with retained ProofShot artifacts.
