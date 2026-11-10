# Registered implementation contracts

These contracts accompany the executable regression tests prepared before new
production implementation. Numerical outcomes remain pending until execution.

## Observation and conditional inference

`observe_concept(case)` accepts a typed concept, FEN, named role squares, an
optional supplied structural move, unknown cells, source and optional explicit
piece identities. Reference labels are rejected. Local role occupancy and
component field observations determine a reusable descriptor. Absolute squares,
piece IDs, source identity, FEN and snapshot identity remain observation
provenance; they never become learned conditional keys.

Pin packets may include an explicitly hypothetical removal of the intervening
piece. This is a structural counterfactual, not a legally executable move or a
positive exposure theorem. Trapping packets observe the ordinary movement fan
from the existing candidate grammar; unique local observation profiles may be
pooled without counting them as independent evidence. The supplied pooling must
be named in the grammar and audited against raw held-out motifs.

`ConceptModel` validates its grammar, runtime, relative descriptors, evidence
partitions and checkpoint digest. Every mutation changes model identity.
`infer_concepts` returns native conditional records plus independent component
field proofs. The packet premise is named `ObservedStructuralRolePacket`.
`joint_proof_complete` remains false. Native failure, absence of learning,
missing observations, zero sensor confidence and exhausted budgets have
different explicit statuses. A warm cache cannot bypass a logical proof budget.

The relation cache excludes caller identity and full-state bindings from reusable
local proofs. Each response attaches current snapshot bindings and component
field records to a fresh copy. Changing model, runtime, options or provenance
invalidates the appropriate scope. Removing independent field learning need
not retract the separate packet conditional, and this limitation is tested.

## Dependencies and exact incremental fields

`IncrementalFieldSession.build` preserves the Cycle 11 field record contract.
Changed occupancy includes entity identity, kind, owner, relocation, capture,
promotion and unknown-observation status. En-passant metadata also invalidates
ordinary mobility applicability even without an occupancy change. Castling and
en passant include every structurally affected cell.

The scheduler regenerates affected relative observations and native queries;
unaffected local records are copied with current query and snapshot bindings.
New or removed field-domain members are handled explicitly. If a budget cannot
cover the full logical query population, the existing full planner remains the
reference path. Exact parity includes every relation field, native proof node,
evidence identifier, dependence group, directional index and board projection.

`build_graph` stores observation, field, concept and native proof identities.
Host dependency and comparison edges have no truth value. Native edges refer to
an executed conditional proof and its actual native TV. Shared parents are
retained; graph topology never creates independent evidence or automatic TV
propagation. Graph validation rejects invented truth values on scheduling edges.

`compare_fields` distinguishes observed occupancy changes, changes in model
belief, native results and display projections. Creation/removal of a relation's
domain is distinct from positive/negative field evidence. Unknown or absent
records cannot silently become false. All before/after change labels, including
opening, removal, persistence and strengthening, are host comparisons with
separate endpoint proofs and no native change TV.

## Supplied temporal evolution

`replay_fields` consumes an initial state and bounded, ordered supplied events.
It returns every state, structural transition, field, graph, concept candidate,
change and source lineage. It never chooses a move. Repeated execution must match
under `semantic_replay`, excluding timing and cache counters.

A missing move with an independently supplied snapshot creates an observed
state after a history gap, without an inferred transition. A gap with no snapshot
leaves the state unknown. A conflicting supplied successor is retained as a
conflict and cannot silently replace the structural prediction. No field delta
is asserted across such a gap. Piece identity continuity across an independently
reobserved snapshot is not invented. Unknown relocated pieces remain unknown,
and zero-confidence events cannot acquire certain fields.

## Integration and promotion

The inspector projects server-returned records and supports position, piece,
candidate move, field family, concept and temporal step selection. It performs no
inference or TV fusion in JavaScript. It exposes native strength and confidence,
proofs, relative rules, source lineage and missing premises, with desktop and
mobile proof capture.

The legal promotion review evaluates the exact frozen Cycle 11 candidate over
26 historical suites, 48 Cycle 9 shards and all 132 Cycle 10 shards. It compares
every candidate classification and preserves every native proof. Any loss of an
established supported classification, new error or incomplete evaluation blocks
promotion. Separate controls reproduce the two recoveries, 76 holdouts, all 27
temporal conditions and 287 negative/evidence-removal cases. Default selection is
source-bound and may only authorize the registered legal checkpoint. Field and
concept model identities cannot enter the legal default allowlist.
