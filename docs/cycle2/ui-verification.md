# Cycle 2 inspector verification

[ProofShot report and video](../../proofshot-artifacts/2026-11-05_12-32-42_cycle-2-hierarchical-hypotheses-native-p/SUMMARY.md) record six screenshots and desktop/mobile interactions. Browser console and server error counts were both zero. Invalid FEN returned the expected handled HTTP 400 and cleared stale proof/hierarchy state.

Verified B0/B1/B2 comparison on the same move; reusable long-ray obstruction evidence; matched tiers and provenance; native versus host-derived descriptions; and pinned-rook abstention despite a positive raw local conditional TV. At a 390 × 844 viewport the document had no horizontal overflow and the board contained 64 cells. A direct inspector/API contract test checks identical candidate results.

The pin displayed **unknown**, with strength 0.926966 and confidence 0.856731 retained and an explicit exposure/conflict explanation. These numbers are conditional evidence, not a certified legal move. Full metadata is in [ui-verification.json](../../artifacts/cycle2/ui-verification.json).

The [final-checkpoint recording](../../proofshot-artifacts/2026-11-05_12-47-23_final-cycle-2-checkpoints-with-held-out/SUMMARY.md) repeats the comparison, unseen long-ray blocker and exposure-abstention checks after enforcing the training-distance mask. It adds three screenshots, again with zero console/server errors. The new long-ray blocker TV was strength 0.0032679738562090277 and confidence 0.8777616279069769; B0 remained unknown. Final model versions are recorded in the verification JSON.
