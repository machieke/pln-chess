# Pin transfer

8/8 preregistered transfer demonstrations change from unknown under the empty
concept checkpoint to supported under training and back to unknown when the relevant conditional evidence is removed.
All have unseen raw structural families; successful cases intentionally reuse supplied pooled relative keys.

| Held-out case | Empty | Learned | Strength | Confidence | Evidence removed | Succeeded |
|---|---|---|---|---|---|---|
| pin-R-(1, 0)-1-3-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-R-(1, 0)-3-2-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-B-(1, 1)-1-3-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-B-(1, 1)-3-2-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-Q-(1, 0)-1-3-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-Q-(1, 0)-3-2-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-Q-(1, 1)-1-3-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |
| pin-Q-(1, 1)-3-2-k/base | unknown | supported | 0.991379 | 0.739286 | unknown | True |

The pin observer binds a slider, an intervening piece and a protected target along a relative ray. It distinguishes king and nonking targets and retains the hypothetical removal/exposure observation. Rook, bishop and queen rays transfer to unseen raw lengths; coordinate transformations and piece-ID changes are independently controlled. A relative pin against a nonking target assigns no material value. The intervening piece is not declared legally immobile. Every example retains the native packet proof and separate attack/exposure components.

Translations, reflections, color orientation, identity renaming and irrelevant-context changes belong to their original ancestry
family. They are invariance controls, not additional independent holdouts. The complete per-case records include FEN, roles,
relative observations, model/rule IDs, native expressions, proof DAGs, evidence groups and removal controls.

Every concept remains experimental. Native operators derive a limited conditional from an explicitly host-observed `ObservedStructuralRolePacket`. Component field proofs are separate; their uncertain truth values are not conjoined into that packet. Complete joint concept proofs, native temporal implications, strategic overload theorems and strategic trapping theorems all remain zero. No move score, search, ranking, material-value table or move selection is implemented.

Evidence: [concepts/transfers.json.xz](../../artifacts/cycle12/concepts/transfers.json.xz), [concepts/transformations.json.xz](../../artifacts/cycle12/concepts/transformations.json.xz),
[concepts/controls-summary.json](../../artifacts/cycle12/concepts/controls-summary.json).
