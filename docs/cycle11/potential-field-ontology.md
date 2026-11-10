# Relative potential-field ontology

This document specifies the Cycle 11 representation before its implementation and evaluation. Final measured capabilities and gaps are recorded in the field reports and package matrix. The field subsystem is experimental and independent of the accepted legality learner.

## Domains and representations

Let a supplied environment snapshot contain typed piece entities, their owners, observed occupied/empty cells and explicitly unknown cells. Coordinates identify observations and render the environment. They are not learned hypothesis arguments. For a source piece and a distinct target cell, the observer constructs an owner-relative displacement, geometric direction/family, distance, intermediate-cell observations, destination allegiance/kind and any relevant owner-relative boundary distance.

| View | Domain | Codomain | Role |
|---|---|---|---|
| Relational graph | Source entity, target entity or cell, relation family, relevant observed dependencies | A typed relation record with native `(strength, confidence)`, classification, premise/evidence/rule IDs and proof status, or explicit unknown/incomplete | Primary reasoning representation |
| Directional field | Source entity and signed owner-relative displacement | The same typed relation records, indexed by displacement; multiple relation families remain distinct | Alternate reasoning/indexing representation; no extra probabilistic calculation |
| Spatial projection | A supplied snapshot and graph/directional records | Board cells with labels and optional display intensity | Visualization/analysis only; no learned absolute-square scores |

The graph and directional view are isomorphic indexes of the same ground beliefs, rather than two independently combined sources of evidence. A projection cannot become a new training observation merely by being rendered. A difference in display intensity is not a native truth value for an `InfluenceChange` proposition.

## Typed relations

| Concept | Type and intended meaning |
|---|---|
| `Piece` | Entity with kind and owner; stable identity is preserved through structural movement and promotion |
| `RelativeDisplacement` | Signed file displacement and owner-oriented rank displacement |
| `RelativeDirection`, `RelativeDistance` | Structural geometry observations, with no embedded attack or legality verdict |
| `RelativeRay`, `IntermediateOccupancy` | Every intermediate cell on an aligned source-target path; each observation can be unknown |
| `DestinationOccupancy` | Empty, friendly, opposing or unknown endpoint, with kind when observed |
| `GeometricReachability` | Learned empty-board attack geometry; a separate auxiliary relation, not occupancy-aware influence or legal movement |
| `AttackPotential` | Learned geometric influence under observed occupancy; pinned attackers and friendly occupied endpoints remain representable |
| `DefensePotential` | Learned geometric protection of a friendly occupied endpoint; legal recapture requires separate evidence |
| `MobilityPotential` | Learned ordinary occupancy-constrained transition, with promotion witness semantics disclosed; historical special transitions remain separate |
| `KingExposurePotential` | Learned influence of one opposing source toward a king; a per-source negative does not establish universal safety |
| `CandidateSuccessor` | A proposed structural environment edit and its separately obtained legal classification |
| `InfluenceRelation` | A ground typed relation, observation fingerprint, model identity and native conditional derivation |
| `InfluenceChange` | A typed before/after comparison; host diagnostic unless an existing native rule actually derives the change proposition |
| `SupportingEvidence` | Immutable observation IDs, labels, sources, dependence groups and transformation ancestry |
| `FieldUncertainty` | Missing observation, unlearned conditional, weak/conflicting evidence, composition gap or incomplete execution |

No concept name defines a new PLN inference operator. The existing native revision, modus ponens, negation and evidence-selection rules are the only enabled operators.

## Truth values and evidence

The observer supplies a single local-context proposition, for example a rook, an orthogonal relative direction, a particular destination allegiance and the observed classes of intermediate contents. A learned conditional maps that context to a typed influence proposition. Native `Truth_Revision` learns positive and negative channels from the labeled evidence. Native `Truth_ModusPonens` applies the context observation to the learned conditional; native negation and evidence selection preserve the existing two-channel convention.

This is a conditional derivation from a host-constructed local observation. It is not a native conjunction proof assembled from independently uncertain geometry, occupancy and historical premises. Each record must therefore retain the observation, its declared sensor confidence, learned conditional truth values and native expression/output. A supported local relation has a native conditional proof; it does not have a complete global legal-move or king-safety proof.

PLN strength and confidence remain separate. The neutral prior `(0.5, 0.05)` supplies neither positive nor negative influence. Training observations use finite confidence and reference labels only in the offline boundary. Unknown required occupancy is not replaced with empty space. A missing conditional returns unknown; a runtime or resource limit returns incomplete. Calibration, if measured, is a separate empirical analysis of relation labels and never changes a native truth value or classification.

Evidence independence is a sampling assumption. A repeated record, color reflection, translated descendant or common source-game/opening ancestor cannot create independent revision weight for the same conditional. Contradictory observations within a dependence component are withheld with their identities retained; independent conflicting components revise the native channels. Multiple defenders are represented as separate relations. Their strengths or confidences are never added or multiplied to manufacture a combined defense belief.

## Locality, symmetry and abstraction

Locality is defined by dependency, not by a fixed geometric radius. A rook or bishop relation can depend on every cell of a long ray across the board. The relevant footprint includes source identity/kind/owner, target occupancy and identity, all ray cells used by that relation and any required boundary or transition observation. An unrelated distant piece is outside that footprint. The full environment snapshot still binds the relation through an explicit observation certificate.

Learned keys exclude absolute squares, entity IDs, FENs and complete board layouts. Sliding-piece shape pooling deliberately omits ray length while retaining observed obstruction classes. Pawn direction remains owner-relative. File reflection can canonicalize the sign of file displacement where the relation semantics permit it. King and knight displacement categories retain the relative magnitudes needed to distinguish their geometries. These are supplied representational assumptions, tested on unseen configurations; they are not claimed as abstractions discovered autonomously by PLN.

Translation invariance applies only when the relevant semantics are preserved: a translation cannot erase an observed blocker, move a target off-board or silently change a pawn's required boundary relationship. Standard castling is not assumed to be translation-invariant. Color orientation changes map the owner-relative forward axis. Entity renaming preserves conditional selection and native values while changing ground provenance identities. A blocker edit must affect the appropriate relation; a distant edit must not affect it unless that piece is in its dependency footprint.

## Successors, differences and reuse

The structural successor applies a candidate edit without deciding legality, including capture, promotion, castling rook motion and en-passant removal away from the destination. The accepted learner supplies the candidate's operational/strict/experimental classification separately. Supported, contradicted and unknown candidates can all be inspected, with their status attached to the successor. A hypothetical successor is never presented as an observed or verified legal continuation.

Unknown source observations propagate to the destination of a hypothetically moved entity, including an uncertain castling rook. Structural editing cannot manufacture a newly observed piece from an unknown source cell. Required unknown source, target and intermediate facts withhold the native context premise. The enclosing state and candidate certificate binds each reused local conditional to its supplied or hypothetical environment.

Before/after comparison retains the typed relation identity, both truth values, both native proofs, evidence/rule IDs, observation dependencies and uncertainty limitations. It identifies additions, removals and changed support, including opening/closing rays, without reducing the collection to a strategic score. A numeric strength difference, if displayed, is explicitly descriptive and is not submitted to PLN as the truth value of a change proposition.

Incremental reuse is exact only when the relevant dependency fingerprint, model, runtime and options match. Unchanged local proofs may retain their identity while the enclosing snapshot binding changes. Changes to a mover, capture victim, promotion kind, unknown cell or participating ray invalidate the corresponding records. Full recomputation is the reference for cache parity. The field cache does not alter the legality learner's caches or classifications.

## Explicit boundaries

Geometric defense is not legal recapture. Empty attack evidence is not a safety theorem. Occupancy mobility is not the set of legal moves. Native conditional proof completeness is not global positive composition. Board projections and strength deltas are diagnostics. No material weights, piece-square tables, move ranking, search, scalar strategic value or new native operator are introduced by this ontology.
