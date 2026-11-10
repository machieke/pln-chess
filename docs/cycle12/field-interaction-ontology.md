# Field interaction ontology

The ontology names relationships between observations and conditional field
propositions. A typed graph edge does not introduce a native inference rule.
Every edge carries its origin, state bindings, source proposition identities,
evidence and dependence references, matched rules, model and runtime identities,
and proof references where a native result exists.

| Predicate | Arguments | Evidence and TV semantics |
|---|---|---|
| Influences | piece, target cell or entity, state | A native local attack conditional; strength and confidence belong to that conditional |
| Supports | piece, friendly entity, state | A native local defense conditional; legal recapture remains unproved |
| Obstructs | observed occupant, relative ray, state | Observed occupancy in a ray; the host edge has no inferred TV |
| Exposes | attacking piece, king, state | A native local king-exposure conditional; absence is not universal safety |
| RestrictsMobility | mobility proposition, destination, state | Native counterevidence for that ordinary local move; no claim that every exit is impossible |
| RemovesDefense | change, before defense, after defense or domain, states | Host comparison with both endpoint proofs; an absent entity is not a false proposition |
| OpensAttack | change, before attack, after attack, states | Host comparison of separately inferred relations; no native temporal implication |
| ChangesInfluence | change, before proposition, after proposition, states | Observed context or belief difference, with no combined TV |
| PersistsAcrossMove | before proposition, after proposition, supplied move | Host correspondence; repeated provenance is not new independent evidence |
| ContradictsInfluence | native negative evidence, proposition, state | Existing native conditional counterevidence, retaining its actual proof |

Relative observation descriptors contain piece types, owner-relative movement
geometry, destination allegiance, observed ray occupancy and required boundary
context. Graph instances may name board squares and piece identities because
they explain a concrete observation. Learned rule keys must not specialize to
those identifiers or to a complete FEN.

Unknown cells stay unknown. A missing required ray cell withholds the observed
context premise. Missing conditionals leave an absence prior. Runtime failure or
an exhausted proof budget produces an incomplete record. Neither absence nor
incompleteness creates a negative interaction.

Before/after labels are deliberately weaker than a causal theorem. The engine
can report that a supplied blocker removal coincides with a newly supported
attack, and retain the two native proofs. It cannot silently conclude a native
`OpensAttack` theorem or propagate a numeric truth value along that graph edge.
Strength changes, confidence changes, evidence changes and observation changes
are recorded separately.

The existing native operator boundary remains unchanged: revision for learned
evidence, unary modus ponens, negation and the existing candidate selector. No
conjunction introduction, independent-support aggregation, strategic evaluation
score or move-selection rule is authorized by this ontology.
<!-- cycle12-measured-evidence -->

## Executed ontology audit

The implementation exposes all eight typed concept families and ten interaction labels. Ontology labels do not add native operators.
The grammar is `relative-role-packets-v12` and has 61 learned relative packet descriptors.
The boundary audit reports no production reference-engine imports, no Cycle 12 host truth-value arithmetic and no new native operators.
Only Truth_Revision, Truth_ModusPonens, Truth_Negation and BestConfidenceCandidate are authorized here.

40 distinct field/concept proof traces and 326
logical training nodes were re-executed against the pinned native runtime with exact truth-value equality.
Absolute coordinates remain I/O/observation bindings; native rule descriptors are relative.

Evidence: [ontology/manifest.json](../../artifacts/cycle12/ontology/manifest.json), [architecture/boundary.json](../../artifacts/cycle12/architecture/boundary.json).
