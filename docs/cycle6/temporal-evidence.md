# Temporal evidence

`unknown`, `trusted-fen`, and `observed-events` are aliases for C5's `fen-only`, `trusted-metadata`, and `event-backed`. Unknown history supplies no historical proof. Trusted FEN is a sourced external claim with finite confidence. Observed events replay structural transitions and compare the exact final FEN; they do not certify legal play.

`history-v6.1` receipts contain `events-v6.1` records, stable event IDs, before/after state IDs, source, sequence, rights/EP changes and removed/added/changed occupants. Seven executed cases cover pawn double steps, rook and king rights changes, castling, promotion, rook capture affecting rights, and EP capture. Contradictory final state, empty/incomplete history and rights-changing edits are tested in every case. Exact records are in `artifacts/cycle6/temporal.json`.

An EP predecessor and an independent castling-history attestation have different scopes. Reliable external observations can make the relevant C4 sensor available; they never establish a complete historical theorem or current king safety. Spatial transforms do not automatically certify transformed histories. No production reference-engine legality check is added.
