# Chess coverage

`native-end-to-end` means a compositional native proof of the feature, not merely a correct trained label. No full chess feature is assigned that status in this delivery. `native-partial` means native conditional inference and/or a structural state feature is implemented with a reproducible demonstration. Numerical proof values come from the generated artifacts, never hand-written substitutes.

| Feature | Repro fixtures | Status | Remaining gap |
|---|---|---|---|
| Rook clear/blocked, allegiance | rook-clear, rook-blocked, rook-enemy, rook-friendly | native-partial | Joint categorical sensor; no native AND over occupancy |
| Bishop rays | bishop-clear, bishop-blocked, bishop-capture | native-partial | General compositional blocker rule |
| Queen shared ray families | queen-clear | native-partial | Generalization beyond learned relative cases |
| Knight jumping | knight-jump, knight-empty, edge-knight | native-partial | Jump geometry seeded; no discovery of offsets |
| King movement and adjacent kings | king-safe, king-attacked, king-adjacent | native-partial | Universal safe-square aggregation |
| Pawn orientation, two-step, captures | pawn-white, pawn-black, pawn-blocked, pawn-capture, pawn-empty-diagonal | native-partial | Compositional constraints and complete history |
| Promotion choices | promotion, promotion-friendly | native-partial | Four structural replacement states; only observed cases receive strong beliefs |
| Pins and discovered rays | rook-pinned, diagonal-pin, discovered-check | native-partial | Native attack/exposure chain exists; joint safety integration blocked |
| Double check, blocking/capturing checker | double-check, check-block, check-capture | native-partial | Held-out combinations may abstain |
| Castling rights and attacked transit | castle-clear, castle-no-right, castle-through-attack, castle-occupied, castle-queenside, castle-queenside-outer-blocked | native-partial | Transit sensory frames exist; no compositional transit safety theorem; full historical proof remains incomplete |
| En passant capture removal and opened ray | en-passant, en-passant-no-target, en-passant-opens-ray | native-partial | Structural removal and learned relative exposure; no general history theorem |
| Missing observations | incomplete-observation JSON proof | native-partial | Remains unknown; no imputation |
| Checkmate/stalemate | mate, stalemate | not-implemented | Fixtures evaluated as move sets; no terminal-state proposition |
| Repetition/fifty-move/draw history | FEN counters retained | not-implemented | Full temporal evidence unavailable |
| General conjunction of legality constraints | audit MISSING-AND probe | blocked-by-native-rule | Requires verified upstream rule/composition |

Inspect any focus fixture through `pln-chess inspect`; the fixture manifest records its FEN and focus move. All demonstration traces include an oracle comparison produced outside inference. The dataset contains strict held-out cases so correct training demonstrations cannot be confused with chess correctness. Candidate recall is separately assessed against complete oracle move sets.


## Cycle 5 scope

The earlier-cycle description above is preserved. See the [Cycle 5 update](cycle5/generalization-results.md) for strict positive proof gaps, typed native negative chains, temporal trust modes and measured coverage loss. No universal correctness or completed positive conjunction is claimed.
