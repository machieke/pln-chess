# Spatial and structural semantics

Absolute coordinates enter through FEN and candidate bindings. Learned keys use piece type, owner-oriented displacement class, effect, required edge context, occupancy class and royal contact. Signed offsets, alignment/distance, per-cell steps and raw opponent frames remain inspectable observations; they do not decide movement legality.

Translation and permissible color/reflection controls preserve typed identities. Piece-ID renaming and unrelated remote pieces cannot alter a local typed hypothesis; remote pieces may add causally relevant opponent frames. The original bounded candidate grammar is unchanged and is explicitly a supplied geometric inductive bias.

An occupied-cell witness can match the same learned conditional at another intermediate distance. There is no host `is_clear`, `is_attacked` or `is_legal` fact. Candidate successor edits can remove a capture, remove an en-passant adjacent cell, relocate a rook and replace a promoted piece even for an illegal candidate. Such structural edits are not legality checks.

Historical evidence is not silently translated or reflected. A transformed board requires independently supplied temporal evidence; [temporal semantics](temporal-semantics.md) describes this exclusion.
