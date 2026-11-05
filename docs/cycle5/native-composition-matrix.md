# Native capability matrix

| Operation | Result in this pinned configuration | Production role |
|---|---|---|
| `Truth_ModusPonens` | Executed with supported, absent and low-confidence premises | Unary conditional propagation |
| `Truth_Revision` | Executed; repeated evidence raises confidence unless stamps/groups exclude it | Same conditional only |
| `Truth_Negation` | Executed; raw strength/confidence retained | Negative legality projection |
| `BestConfidenceCandidate` | Executed; does not establish independent-premise fusion | Same-proposition evidence choice |
| `Truth_Deduction` | Measured consistency probes execute; zero marginal confidence does not suppress the result | Experimental only |
| `Truth_Induction` | Explicit measured marginals execute | Experimental; disabled by default |
| Independent conjunction introduction/elimination | Empty derivation | Explicit proof gap |
| Supplied compound antecedent | MP executes | Host-supplied compound assumption, native-partial |
| Supplied curried conditional | Two MP steps execute | Supplied combined rule, native-partial |
| Curry/uncurry discovery | No demonstrated derivation | Unsupported |
| Inheritance-to-predicate wrapper | Empty in the inherited operational probe | Unsupported; source syntax alone is insufficient |
| Typed substitution | Matching scope succeeds, repeated-variable mismatch fails | Typed matching verified |
| Context/intensional alternatives | No demonstrated conjunction | Unsupported |
| `StampDisjoint` | Rejects shared ancestor, accepts disjoint stamps | Explicit lineage gate; TV functions do not enforce it automatically |

[Executable audit](../../artifacts/cycle5/native-probes/audit.metta), [raw machine-readable record](../../artifacts/cycle5/native-probes/audit.json), and [decision](composition-feasibility.md). These are configuration-scoped observations, not a universal impossibility theorem about PLN.
