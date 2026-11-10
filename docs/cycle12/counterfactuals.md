# Counterfactuals, invariance and evidence removal

All 20/20 counterfactual pairs distinguish their registered
local change, and all 20 previously classified conditionals retract to unknown after their learned
evidence is removed. Already-unknown queries are not counted as successful retractions (0).
All 90/90 concept transformation controls pass, separately from the 38 field controls.

| Pair | Changed relation | Before | After | Proof changed | Conditional removal |
|---|---|---|---|---|---|
| DiscoveredAttack-R-(1, 0)-1-3/remaining-obstruction | remaining-obstruction | supported | contradicted | True | unknown |
| DiscoveredAttack-R-(1, 0)-3-1/remaining-obstruction | remaining-obstruction | supported | contradicted | True | unknown |
| DiscoveredDefense-R-(1, 0)-1-3/remaining-obstruction | remaining-obstruction | supported | contradicted | True | unknown |
| DiscoveredDefense-R-(1, 0)-3-1/remaining-obstruction | remaining-obstruction | supported | contradicted | True | unknown |
| fork-N-(1, 2)-(-2, 1)/one-target | one-target | supported | contradicted | True | unknown |
| fork-N-(1, 2)-(-2, 1)/friendly-second-target | friendly-second-target | supported | contradicted | True | unknown |
| fork-N-(1, 2)-(2, -1)/one-target | one-target | supported | contradicted | True | unknown |
| fork-N-(1, 2)-(2, -1)/friendly-second-target | friendly-second-target | supported | contradicted | True | unknown |
| multiple-1-3/one-source | one-source | supported | contradicted | True | unknown |
| multiple-3-1/one-source | one-source | supported | contradicted | True | unknown |
| obligations-1-3/one-obligation | one-obligation | supported | contradicted | True | unknown |
| obligations-3-1/one-obligation | one-obligation | supported | contradicted | True | unknown |
| pin-R-(1, 0)-1-3-k/target-absent | target-absent | supported | contradicted | True | unknown |
| pin-R-(1, 0)-1-3-k/intervening-other-allegiance | intervening-other-allegiance | supported | contradicted | True | unknown |
| pin-R-(1, 0)-1-3-q/target-absent | target-absent | supported | contradicted | True | unknown |
| pin-R-(1, 0)-1-3-q/intervening-other-allegiance | intervening-other-allegiance | supported | contradicted | True | unknown |
| threat-removal-1-3/irrelevant-edit | irrelevant-edit | supported | contradicted | True | unknown |
| threat-removal-3-1/irrelevant-edit | irrelevant-edit | supported | contradicted | True | unknown |
| trapped-N-d4/escape-cell | escape-cell | supported | contradicted | True | unknown |
| trapped-B-d4/escape-cell | escape-cell | supported | contradicted | True | unknown |

Every pair retains source and edited input, changed relation, limited offline labels, before/after native TVs and proof traces,
conditional-rule identity, dependence group and both removal arms. Irrelevant translation, reflection, ID and context changes
are not counted as independent training evidence. Unknown required cells are a distinct abstention control.

Removing the separate field checkpoint may remove component proofs without retracting a packet conditional learned directly
from structural observations. This observed separation is intentional and disclosed: a packet conditional is not a theorem caused
by conjoining uncertain field evidence. The experiment establishes dependence on its learned conditional evidence and observed
local packet, not arbitrary causal reasoning about chess strategy.

Evidence: [concepts/counterfactuals.json.xz](../../artifacts/cycle12/concepts/counterfactuals.json.xz), [concepts/transformations.json.xz](../../artifacts/cycle12/concepts/transformations.json.xz),
[concepts/controls-summary.json](../../artifacts/cycle12/concepts/controls-summary.json), [learning/dependence.json](../../artifacts/cycle12/learning/dependence.json).
