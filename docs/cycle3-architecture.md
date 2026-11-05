# Cycle 3 architecture

Cycle 3 is a relative conditional learner with separate native exposure chains. It is not a complete chess legality prover. The pinned runtime cannot construct a conjunction from independent propositions; a positive local conditional therefore remains `native-partial` even when separate path and destination beliefs are available.

## State, ontology, and migration

`src/pln_chess/cycle3/descriptors.py` defines `relative-conditions-v3`. Readable descriptors precede their `c3:` hashes. Production antecedents contain piece type, owner-relative motion, occupancy classes, destination relations, boundary observations and special-move observations. Absolute coordinates, piece identifiers, position hashes and attacker identities occur only in input/output and trace metadata. The diagnostic exact-context-only ablation deliberately retains the previous full relative context to measure memorization.

Movement tiers 0–3 retain positive-only movement supervision. Tiers 4–5 learn local outcome conditionals; tier 5 adds distance and first occupancy, with tier 4 providing distance-independent backoff. Ordinary C3 models omit the exact-context fallback. Independent `GeometryObserved`, `PathUnoccupied`, `DestinationAvailable`, `BoundaryObserved` and `TemporalMoveObserved` beliefs expose which local conditions have evidence. These beliefs are never combined by a host AND or weighted formula. A shared path-content predicate supports cross-piece observation reuse; this does not establish cross-piece legality transfer or a newly induced chess law.

Schema 1 and 2 checkpoints retain their original loaders and inference paths. Schema 3 verifies grammar, runtime and integrity. Migration means replaying original labeled inputs into the new schema; changing a checkpoint's schema number is rejected. New model versions cover training summaries, hypothesis/evidence identities, induction and configuration. Full excluded-update lists are reconstructible from the sealed ledger; checkpoints retain their count, digest and the first 50 exclusions.

## Exposure and temporal observations

Every post-move opponent-to-own-king frame is sensed, including non-attacking geometries. Castling additionally senses the starting king square and transit square. A move's board edits include captured pieces, en passant removal, rook relocation and all four promotions. These are proposed state edits, never acceptance gates.

Learned Attack conditionals feed native modus ponens through learned Attack→Exposure→NotLegal implications. Separate contact-training groups supply attack evidence and each of the two bridge implications. The three pools are disjoint, and every bridge's evidence is propagated into downstream proof nodes. Confidence choice selects among alternative paths without revising their overlapping evidence. Decisive opposing native conditionals trigger an explicitly named display abstention; the actual native TV is retained. Weak attack beliefs do not automatically veto a candidate. Missing attack evidence does not prove safety.

FEN-only en passant assessments abstain because the previous double push has not been observed. `cycle3.history.observe_transition` accepts an explicit predecessor and move only if the structural successor exactly matches the supplied FEN; its receipt states that this is not validation of historical legality. Callers may supply a `Position` with established history. Contradictory history, unknown castling rights, unknown squares, uncertain ownership, conflicting occupancy, and missing successor kings remain unknown. Repetition and fifty-move adjudication remain outside scope.

## Execution and audit surfaces

Native scalar caches are bounded and scoped by the entire runtime manifest, grammar, checkpoint, evidence digest, variant, state identity and options. Within that scope the exact expression and prerequisite identities determine a reusable scalar result. Every logical proof node and evidence identity remains distinct. Evidence changes, rollback, state changes and variant changes invalidate the scope.

`Cycle3Options` sets wall-time, scheduled-node, estimated proof-byte and cache-entry limits. Exhaustion returns `incomplete`; completed earlier candidate proofs remain available when scheduling is exhausted. A native process failure cannot fabricate a completed conclusion. The proof-byte limit estimates serialized inputs rather than enforcing process RSS; measured RSS is reported separately.

The existing CLI/API dispatch by checkpoint schema. The inspector displays independent condition beliefs, attack phases, native proof nodes and baseline comparisons. Counterfactuals add/remove/move pieces, flip orientation, or remove a right and rerun native inference. Edited states are explicitly not asserted to be reachable games. See `src/pln_chess/cycle3/counterfactual.py` and the proof artifacts.
