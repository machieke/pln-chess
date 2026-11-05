# Cycle 3 error analysis

Every original held-out self-check false positive is listed below. The frozen missing-contact patterns were bishop diagonal (20 king moves) and pawn forward diagonal (3 king moves). Training additions are new isolated contact positions, not relabeled held-out positions.

| Fixture | Move | Outcome | Final native TV |
|---|---|---|---|
| heldout-transfer-ray-0 | g3f4 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-ray-1 | e3e2 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-1 | e3d3 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-5 | a8b7 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-ray-8 | d6c5 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-ray-8 | d6c7 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-ray-11 | h3h2 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-11 | h3g3 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-12 | c6c7 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-12 | c6b6 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-15 | f3f2 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-17 | b8b7 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-17 | b8a8 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-20 | f2e3 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-ray-24 | f6g5 | abstention | {'confidence': 0.7392857142857144, 'strength': 0.9913793103448276} |
| heldout-transfer-ray-25 | b5c5 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-25 | b5b4 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-31 | a3b3 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-31 | a3a2 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-ray-35 | h4g3 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-game-2 | e2f3 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |
| heldout-transfer-game-3 | d3d4 | abstention | {'confidence': 0.8191142684401449, 'strength': 0.8370030581039754} |
| heldout-transfer-game-3 | d3c4 | abstention | {'confidence': 0.8077418379685609, 'strength': 0.8253822629969418} |

Abstention retains the raw native conclusion; it does not silently convert the TV into an illegal label. Exact move-set evaluation only counts supported moves, so abstention on an illegal move can improve an exact set while still leaving its negative legality unresolved.

All remaining false positives and uncertainty classes for every ablation are available in the compressed per-candidate reports indexed by `artifacts/cycle3/comparison.json`. Check in-board, per-piece and per-family breakdowns as well as aggregates. New independent games are the strongest check against fixture-specific improvements.
