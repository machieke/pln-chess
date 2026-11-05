# Temporal evidence modes

| Mode | Meaning | Confidence and limits |
|---|---|---|
| `fen-only` | Current rights/EP fields are unverified metadata | Temporal support starts unknown; FEN does not prove history |
| `trusted-metadata` | A named external source asserts current metadata | Caller-supplied finite reliability is preserved; it is not learned historical evidence |
| `event-backed` | Supplied initial state and ordered move events reproduce the current state | Structural consistency and event IDs are recorded; legal play is not certified |

Event identity hashes source, sequence and observed transition. Missing event fields fail explicitly; an empty sequence is truncated. Mismatched final state, changed rights or impossible structural transitions produce a conflicting receipt. Confidence must be finite and below one. Metadata source, reliability and receipt identity participate in cache scope and deterministic replay.

An observed immediately preceding double pawn edit can establish the EP predecessor observation. At reliability at least 0.99 it permits the existing structural EP observer to continue. It does not attest castling history. A separate `castling_history_attested` claim is required for the king/rook history scope; the claim remains external and does not prove legality of prior moves. A FEN right alone never becomes that attestation. Current transit/successor attack frames are independently observable from the board, but no complete native positive temporal/safety conjunction is available.

Trusted metadata exposes its raw temporal TV without silently upgrading it to a fully known event history. All three modes still obey the strict positive proof planner. Thus higher temporal confidence alone cannot manufacture supported legal. Promotion replacement and edge context remain structural/learned local inputs, not a complete theorem.

Temporal evidence is rejected for automatic spatial transforms. Supply an independently justified history for a transformed position. The layer is intentionally partial: no general native theorem of unmoved-piece history or historical legal play is claimed. [Mode, conflict and truncation receipts](../../artifacts/cycle5/temporal.json).
