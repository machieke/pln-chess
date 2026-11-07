# Temporal trust and negative-proof preservation

C7-frozen: 287/287 negatives preserved, 287/287 removals unknown, 287/287 exact C6 native traces.
C7-learned-8: 287/287 negatives preserved, 287/287 removals unknown, 287/287 exact C6 native traces.

The 49 historical and 238 later cases retain complete before/after traces and their removed evidence families in `proofs/*-negative-controls.json.xz`. No oracle is consulted during those inference calls.

The temporal matrix covers castling and en passant in all three inference modes, with FEN-only metadata, trusted metadata, structurally validated supplied events, missing history, inconsistent history and truncated history. Inputs and raw receipts distinguish observed board/event strings, assumed source confidence/initial rights, and inferred structural consistency. Replay does not prove a legally played prior game. `temporal.json.xz` contains all 36 actual candidate/receipt pairs.
