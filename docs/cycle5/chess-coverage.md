# Chess coverage and proof examples

All rows use default C5 strict classification with the registered confidence floor 0.25, positive strength 0.8 and negative strength 0.2. Full model version: `f1893f11340954d8af675a1738d98cdcc01bf818294e0e8448b1f6a4ca5defb2`. Dataset semantic hash: `8568a37be74da40a2c05691299147b13ad064c239d915dceb9a4dbe5b49f91a0`.

| New independent games: piece | Candidates | Oracle legal | Supported legal | Supported illegal | Unknown |
|---|---:|---:|---:|---:|---:|
| Bishop | 1736 | 152 | 0 | 1578 | 158 |
| King | 320 | 85 | 0 | 231 | 89 |
| Knight | 464 | 163 | 0 | 296 | 168 |
| Pawn | 855 | 209 | 0 | 625 | 230 |
| Queen | 1232 | 153 | 0 | 1069 | 163 |
| Rook | 1820 | 135 | 0 | 1651 | 169 |

The 32 positions come from 16 new source games. Positive recall is 0%; positive precision is undefined. All observed false-legal, false-illegal and incomplete counts are zero. The one exact set is an empty terminal move set.

## New negative proof examples

Each example below was C4 unknown, is C5 supported-illegal, and becomes unknown when the ray premise family is removed. The retained artifact contains the exact FEN, all native steps, evidence IDs and before/after TVs. These five sampled game contexts span only rook and queen; the three-piece-family aspiration is not achieved.

| Fixture / game | Piece | Move | Native legal TV (strength, confidence) |
|---|---|---|---|
| c5-independent-games-517151-ply-28 / c5-independent-games-517151 | Queen | `f3f7` | (0.0295781249999999, 0.4007885869565219) |
| c5-independent-games-517152-ply-28 / c5-independent-games-517152 | Queen | `a4a7` | (0.0295781249999999, 0.4007885869565219) |
| c5-independent-games-517153-ply-28 / c5-independent-games-517153 | Queen | `a2a5` | (0.0295781249999999, 0.4007885869565219) |
| c5-independent-games-517155-ply-28 / c5-independent-games-517155 | Queen | `d2g5` | (0.0295781249999999, 0.4007885869565219) |
| c5-independent-games-517157-ply-56 / c5-independent-games-517157 | Rook | `h2h5` | (0.0295781249999999, 0.4007885869565219) |

[Full example index](../../artifacts/cycle5/proof-examples.json), [all 238 new negatives with removal proofs](../../artifacts/cycle5/proofs/new-negative-counterfactuals.json.xz). Counts across multiple declared splits are not asserted to be 238 independent source contexts.

The target knight capture `f6h5` at `2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1` remains unknown with TV `(0.5, 0.0)`. Geometry and destination beliefs do not establish their conjunction or king safety. Native induction activates 12 local predictions, but 7 would be false legal if promoted to global legality. It remains experimental and disabled.

All 49 historical self-check mistakes retain their C2 supported → C3 unknown → C4 supported-illegal → C5 supported-illegal transition. Castling and event-backed en-passant still lack a complete global positive proof. Neither an absent negative witness nor metadata consistency is treated as safety.
