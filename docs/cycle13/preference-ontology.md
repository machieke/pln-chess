# Experimental preference ontology

This specification separates five claims: observed relational changes, a learned conditional, a native conditional application, a host comparison, and unsupported strategic conclusions. A preference is not a proof of legal play, safe continuation, optimality, or competitive strength.

## Types and signatures

| Predicate | Argument types | Meaning and origin |
|---|---|---|
| `CandidateMove` | supplied state, entity, relative displacement, optional promotion kind | Host structural candidate; board coordinates are transport only. |
| `CandidateSuccessor` | supplied state, candidate, hypothetical state | Host application of a supplied edit; independent legal belief accompanies it. |
| `RelativeFieldChange` | field family, source role, endpoint role, before relation, after relation | Diagnostic comparison of separately inferred field records; no change truth value. |
| `AttackChange` | relation change, actor/opponent role | Change in a bounded attack-field domain. Empty destinations are not occupied attack targets. |
| `DefenseChange` | relation change, friendly ward role | Change in local defense potential, without proving a legal recapture. |
| `MobilityChange` | source role, ordinary-destination domain, relation change | Ordinary potential mobility; special-move history remains a separate legal question. |
| `ExposureChange` | attacker role, opposing king role, relation change | Local king-exposure potential; absence of one relation is not global safety. |
| `StrategicConceptChange` | concept family, explicit role binding, endpoint conditionals | Separate limited concept hypotheses; no complete pin, fork, overload or trapping theorem. |
| `ObservedRelativeComparisonPacket` | registered descriptor grammar, categorical relative changes, provenance | Host assembly of a bounded comparison. Its finite sensor trust is supplied, not calculated from component TVs. |
| `MovePreference` | comparison packet, canonical candidate role | Native application of a learned preference conditional. |
| `PreferenceEvidence` | source observation, label, dependence group, runtime/model identities | Append-only external supervision; separated from legal-move evidence. |
| `PreferenceUncertainty` | comparison, missing observations, incomplete work, conflicting support | Explicit gaps; unknown relationships never become false through omission. |
| `PreferenceComparison` | candidate A, candidate B, directional channels, no-demonstrated channel | Host presentation of independently computed native channels and a threshold-based state. |
| `SuppliedContinuation` | candidate, response, optional continuation, selection provenance | Bounded hypothetical branch; no exhaustive opponent coverage. |
| `ContinuationComparisonPacket` | initial packet, branch endpoints, depth, branch provenance | Host temporal descriptor with separate endpoint proofs; not a native temporal implication. |

Coordinates, full FENs, source/game IDs, pair IDs, proof IDs and evidence IDs belong to observation and provenance records. They are forbidden as learned descriptor constants. Relative actor/opponent roles and typed categorical changes may be learned. Partition ancestry hashes may be used only for evaluation grouping and dependence handling.

## Truth values and proof boundaries

Each channel retains raw PLN strength and confidence. Native `Truth_Revision` combines registered independent observations. Native `Truth_ModusPonens` applies an existing conditional to the explicitly supplied comparison packet. Where negation or evidence choice is used, the exact native expression and premises must be retained. No host arithmetic synthesizes a PLN truth value.

Categorical counts and differences are observations of separate result records. They have no inferred joint truth value. The supplied packet's observation confidence does not establish that every uncertain component is true. A complete native conditional application is therefore still a partial strategic argument. Complete strategic and joint uncertain-field proofs remain unsupported.

The preferred-A, preferred-B and no-demonstrated-preference channels are separate conditionals, not a normalized probability distribution. Confidence is an evidence parameter rather than a probability of strategic correctness. Empirical reliability, Brier score, ECE and coverage plots are separate evaluation artifacts and cannot replace inference.

## Order, dependence and state

Canonical ordering uses the relative descriptor, not absolute move notation or source position identity. Reversing the query swaps candidate roles without adding evidence or changing its meaning. A descriptor unable to distinguish the two candidates cannot support a directional answer. No transitive preference is implied.

Duplicate observations are idempotent. Connected ancestry groups contribute at most one consistent observation per conditional. Internally inconsistent dependent groups remain inspectable and are withheld. Opposing independent evidence remains in the native revision trace. Different supported directions remain a contradiction rather than an arbitrary winner.

`A-preferred` and `B-preferred` require an eligible native conditional and the registered display thresholds. `indeterminate` includes insufficient evidence, indistinguishable descriptors, no demonstrated preference and unresolved contradiction. `incomplete` includes exhausted budgets, missing required computation and native failure. Unsupported legal moves and incomplete legal beliefs are disclosed independently; preferences never change legal classifications.

## Temporal scope

Each hypothetical state carries its own occupancy observations, field proofs, concept candidates, legal belief, model/runtime identities and source lineage. A response changes the context, so stale evidence from the parent cannot stand in for the successor. Initial, two-ply and three-ply descriptors remain distinguishable. Unexamined opponent responses are explicitly unknown. No branch comparison supplies a scalar score, minimax value, transitive preference, complete temporal theorem or automatic move choice.

The implemented schemas and measured examples are linked from the final [package matrix](package-matrix.md).
