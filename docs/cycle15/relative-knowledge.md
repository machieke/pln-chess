# Connected relative knowledge

The experimental implementation is in [research/cycle15](../../research/cycle15/),
outside `src/`. The existing operational acceptance mechanism hashes every
Python file under `src/`; this placement preserves that exact accepted identity.
No existing public API or checkpoint is changed. Run the opt-in API or CLI from
the repository root; it is not added to the installed operational CLI.

[Observations](../../research/cycle15/observations.py) carry piece identity, kind,
owner, state, history, original actor, raw occupancy, explicit emptiness/unknowns,
relative offsets, ordered ray membership and a supplied candidate. Native cell
names are local structural identities. Coordinates occur only in environmental
state and scope diagnostics; they do not become rule constants. Structural
successors displace the supplied piece, preserve the original actor and mark
history as hypothetical. They do not adjudicate move legality.

The whole geometrically aligned attacker/target ray is included, including
distant cells. Scope selection does not inspect reference labels or determine
clearance. Occupied ray pieces, the endpoints and the supplied moved piece are
included. Full scope additionally retains unrelated pieces. Each fact keeps an
origin and ancestry record. Missing target/source identities remain explicit.

| Declaration | Category and meaning |
| --- | --- |
| `PieceKind`, `Owner`, `Occupies`, `Occupied`, `Empty`, `UnknownOccupancy` | Environmental observation |
| `State`, `History`, `OriginalActor`, `SuppliedCandidate` | Environmental context; supplied or hypothetical |
| `RelativeOffset`, `RayPath`, `RayMember`, `OrderedRayCell` | Structural geometry observation, without attack adjudication |
| Eleven `Rule` records | Supplied domain templates |
| Checkpoint strengths/confidences | Learned rule truth values for five templates |
| `PathEmpty`, `Clear`, `Attack`, `NoAttack`, `KingExposed` | Native results when derived; attack is also explicitly imported in Stage A only |
| Endpoint differences, scope census, confidence classifications | Host diagnostics, with no native change theorem |

The [domain file](../../knowledge/cycle15/domain_rules.metta) and
[schema inventory](../../knowledge/cycle15/schemas.json) are separate from
orchestration. The templates cover empty-tail initialization, path extension,
clearance, fixed one-cell clearance, rook/bishop/queen influence, obstruction,
and two actor-side exposure rules. Currying is supplied domain structure, not a
new conjunction calculus or discovered chess knowledge.

Facts use assumed `(stv 1.0 0.99)` and supplied templates `(stv 1.0 0.95)`.
No marginal probability is silently invented for chess deduction. The display
policy calls a channel supported at strength >=0.6 and confidence >=0.1; both
channels remain visible. These experimental display thresholds were fixed in
the implementation before final evaluation. Matched baseline B retains the
operational field thresholds, 0.8/0.2 strength and 0.25 confidence.

The public state schema rejects labels, scores, unknown fields, duplicated
identities, duplicate occupancy and conflicting known/unknown occupancy. Unknown
cells do not emit emptiness. Low-level audit injection of competing observations
is reported separately. State-specific atoms prevent stale before-state support
from silently becoming after-state support. Native processes are fresh for each
request. There is no persistent native knowledge base or cross-request evidence.

[Boundary and observation tests](../../tests/test_cycle15_observations.py) and
[consequence tests](../../tests/test_cycle15_consequences.py) verify role binding,
explicit state changes, source removal, rule removal and oracle-disabled execution.
The final admission guard also checks exact preregistered training records;
changing a test root's split string cannot turn it into training evidence.
