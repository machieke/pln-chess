# Source-bound evidence contract

The actual preparation code generates one `reference(state, attacker, target)`
completion result per occupancy, then copies its label into both conditional
rows. Consequently, 48 admitted rule annotations represent **24 underlying
evaluation results**, with two deterministic annotation aliases apiece. There
is no separately measured clearance outcome. This is the main new source finding.

The [complete mapping audit](../../artifacts/cycle18/contract/mappings/audit.json),
[event registry](../../artifacts/cycle18/contract/mappings/events.json) and
[small decisive example](../../artifacts/cycle18/contract/mappings/decisive-example.json)
bind original artifact paths, hashes and JSON locators. The mapper verifies
original observation/state identities, complete row populations, checkpoint
content identities, ledger hashes, admissions, revision chains and raw revision
receipt hashes. It never reruns an evaluator to manufacture missing measurements.

| Original population | Count | Contract treatment |
| --- | ---: | --- |
| Natural training roots/games | 24 | PGN-derived environmental records |
| Natural EE evaluation results | 24 | Admitted vector events, one per root |
| Admitted conditional annotations | 48 | Two aliases per evaluation |
| Synthetic occupancy variants | 192 | Eight dependent interventions per root |
| Excluded conditional annotations | 384 | Blocked/unknown antecedents; no negative training labels |
| Total preparation records | 432 | Exactly one mapped annotation per row |
| Total registry records | 864 | 216 environments, 216 evaluations, 432 annotations |
| Verified original revision receipts | 144 | 24 updates in each of six experimental arms |

The 144 arm-specific updates are **not** 144 independent experiences. Their
union contains only the original 48 admitted annotations/24 vector events.

| Arm | Selected annotation components | Unique vector events/games | Two-component shared vectors |
| --- | ---: | ---: | ---: |
| S-AA | 24 | 12 | 12 |
| S-BB | 24 | 12 | 12 |
| D-AB | 24 | 24 | 0 |
| D-BA | 24 | 24 | 0 |
| overlap-1 | 24 | 23 | 1 |
| overlap-6 | 24 | 18 | 6 |

`Observation` is an immutable typed record in
[contracts.py](../../research/cycle18/contracts.py). Its event ID uses the
versioned original root/occupancy/role locator, independently of payload hash.
The canonical payload is held as immutable JSON; callers receive copies.
It includes artifact path/hash/locator, episode, ancestry groups, observation
kind, method, parents, admission/exclusion, generation/supersession identity and
an explicitly null historical measurement timestamp. A hash binds integrity,
not event identity. Different genuine events can carry identical payloads.

The registry accepts repeat delivery only when the entire event is identical.
Changed payload or provenance under the same ID is rejected. Supersession adds
a new event referencing the old version, keeps the old record, changes the active
view and rejects competing successors. Parents must already exist, preventing
event ancestry cycles. Superseded evidence cannot update the active reference
generation. Synthetic correction tests are quarantined; no historical row has
been corrected or relabeled.

Historical environmental records are typed as direct environmental observations
of the recorded state, with the method explicitly saying **PGN-derived**, not
sensor measurement. Synthetic environments retain the natural environment as
parent. Evaluation vectors retain their environment as parent. Both conditional
annotations retain the same vector parent. Unknown/missing annotation values
are explicit nulls. The superseded kind is exercised only in synthetic controls;
the historical mapping invents no supersession. An excluded row can retain a
reference-engine negative or unresolved completion result while its conditional
training label remains null. These are different fields.

`ParameterGeneration` distinguishes `native-original` from `reference-only`.
Every original rule generation records schema, exact admitted and excluded
annotation IDs, source groups, original learner identity, assumptions, native
truth-value representation and checkpoint reference. Reference generations
instead store an exact joint posterior and a model-assumptions identity. They
also bind the admitted component mask and payload hash of every selected vector;
equal posteriors do not erase different component-admission histories. They
cannot carry a native checkpoint destination. A generation's content identity
includes its evidence set and assumptions; another computation of the same active
set yields the same scientific identity. A new external event changes that set.
An explicit generation lineage records revisions without declaring old events new.

The application schema records generation references, entity bindings, current
environment events, state/history identity, query and native execution reference.
The [native/reference correspondence](../../artifacts/cycle18/correspondence.json)
maps the actual replayed Clear/Attack queries and facts. Current minimal fixtures
are explicitly synthetic contextual environments, never training admissions.
Their `c18-native-input` IDs locate application-local input occurrences, not new
independent measurements. Original fact stamps and ancestry remain in each
payload, exposing reuse of the same fixture across stages and arms.
Native selections and retained statements are observable; fired-rule parent
identities are not. Those parent fields remain null. Reference journal links
are declared host application links, never alleged native firing traces.

Unavailable historical information includes measurement time, a separate
clearance measurement, sensor/noise calibration and sampling probabilities.
Publisher, engines and openings can induce dependence across distinct games.
Neither new IDs nor source-disjoint native stamps establish independence.
