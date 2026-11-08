# Promotion error forensics

All eight C7 mistakes occur in `c7-french-709071-ply-56`: `r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29`.

Each case was checked independently against its recorded native graph and original training ledger. The first incorrect step is the optional level-2 evidence selection: it removes destination occupancy before applying a learned local conditional. Native inference faithfully propagates the selected, inapplicable conditional. This is not evidence of a faulty native truth-value operator.

| Move | Reference | C7 learned | Frozen | Destination | First evidence mismatch |
|---|---|---|---|---|---|
| f7f8q | illegal | supported-legal | unknown | Opponent King | Forward-empty positive evidence applied to an occupied forward destination |
| f7f8r | illegal | supported-legal | unknown | Opponent King | Forward-empty positive evidence applied to an occupied forward destination |
| f7f8b | illegal | supported-legal | unknown | Opponent King | Forward-empty positive evidence applied to an occupied forward destination |
| f7f8n | illegal | supported-legal | unknown | Opponent King | Forward-empty positive evidence applied to an occupied forward destination |
| f7e8q | legal | supported-illegal | unknown | Opponent Knight | Diagonal-empty counterevidence applied to an opponent-occupied capture destination |
| f7e8r | legal | supported-illegal | unknown | Opponent Knight | Diagonal-empty counterevidence applied to an opponent-occupied capture destination |
| f7e8b | legal | supported-illegal | unknown | Opponent Knight | Diagonal-empty counterevidence applied to an opponent-occupied capture destination |
| f7e8n | legal | supported-illegal | unknown | Opponent Knight | Diagonal-empty counterevidence applied to an opponent-occupied capture destination |

The four promotion choices have separate hypothesis IDs and evidence. Choice identity was retained, so these are not queen/rook/bishop/knight substitutions. The forward cases reuse positive empty-destination evidence; the diagonal cases reuse negative empty-destination evidence. Those two directions require distinct counterexamples even though the same projection removes the distinction.

The position has no supplied history. Castling or en-passant provenance does not justify these decisions. The observed errors are not self-check errors. Destination piece identity and ownership must remain observable: in particular, the forward destination contains the opposing king. New training must distinguish local transition eligibility from post-move exposure instead of assigning every illegal label to movement.

The [case inventory](../../artifacts/cycle8/promotion-errors.json) contains each FEN, move, target, orientation, occupancy, history, raw TV, selected hypothesis, original/projected descriptors, source evidence, dependence groups, policy node and full native graph. The [compressed copy](../../artifacts/cycle8/proofs/promotion-errors.json.xz) is lossless. Proposed fixes are evaluated separately; this forensic finding alone does not establish safe generalization.
