# Fork transfer

7/8 preregistered transfer demonstrations change from unknown under the empty
concept checkpoint to supported under training and back to unknown when the relevant conditional evidence is removed.
All have unseen raw structural families; successful cases intentionally reuse supplied pooled relative keys.

| Held-out case | Empty | Learned | Strength | Confidence | Evidence removed | Succeeded |
|---|---|---|---|---|---|---|
| fork-N-(1, 2)-(-2, 1)/base | unknown | supported | 0.987179 | 0.657155 | unknown | True |
| fork-N-(1, 2)-(2, -1)/base | unknown | supported | 0.987179 | 0.657155 | unknown | True |
| fork-P-(-1, 1)-(1, 1)/base | unknown | unknown | 0.500000 | 0.000000 | unknown | False |
| fork-K-(-1, 0)-(1, 0)/base | unknown | supported | 0.975000 | 0.495000 | unknown | True |
| fork-R-(-3, 0)-(0, 3)/base | unknown | supported | 0.987179 | 0.657155 | unknown | True |
| fork-R-(-3, 0)-(0, 2)/base | unknown | supported | 0.987179 | 0.657155 | unknown | True |
| fork-Q-(-3, 0)-(0, 3)/base | unknown | supported | 0.987179 | 0.657155 | unknown | True |
| fork-Q-(-3, 0)-(0, 2)/base | unknown | supported | 0.987179 | 0.657155 | unknown | True |

The fork observer retains two target-specific influences from one attacker. Knight, pawn, king, rook and queen inputs are present without target-value scores. The entire pawn fork family was withheld from training and remains unknown: its empty/learned/removed conditional stays at (0.5, 0). Both component attack relations can have native support without creating a joint fork theorem. Seven successful demonstrations cover knight, king, rook and queen families; the pawn failure is retained without retuning.

Translations, reflections, color orientation, identity renaming and irrelevant-context changes belong to their original ancestry
family. They are invariance controls, not additional independent holdouts. The complete per-case records include FEN, roles,
relative observations, model/rule IDs, native expressions, proof DAGs, evidence groups and removal controls.

Every concept remains experimental. Native operators derive a limited conditional from an explicitly host-observed `ObservedStructuralRolePacket`. Component field proofs are separate; their uncertain truth values are not conjoined into that packet. Complete joint concept proofs, native temporal implications, strategic overload theorems and strategic trapping theorems all remain zero. No move score, search, ranking, material-value table or move selection is implemented.

Evidence: [concepts/transfers.json.xz](../../artifacts/cycle12/concepts/transfers.json.xz), [concepts/transformations.json.xz](../../artifacts/cycle12/concepts/transformations.json.xz),
[concepts/controls-summary.json](../../artifacts/cycle12/concepts/controls-summary.json).
