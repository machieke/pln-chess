# Decisive episodes

Each episode links to the measurements and native inputs, including the selected and retained statements. The full environmental payload and the measured components are keyed by their IDs in the [lineage index](../../artifacts/cycle19/measurement/lineage-index.json). The model identity links to the actual admitted component records in [the learned generations](../../artifacts/cycle19/learning/models.json).

| Case | Game root | Arm | Audited Clear / Attack | Native Clear | Native Attack |
|---|---|---|---|---|---|
| [blocked](../../artifacts/cycle19/demonstrations/blocked.json) | c19root_1f5e7b556be3f84ec954 | F | False / False | unknown · no returned TV | supported-negative · contrary (1, 0.931095) |
| [environment-correction](../../artifacts/cycle19/demonstrations/environment-correction.json) | c19root_ad3338bf67bceedc086f | D-AB | False / False | unknown · no returned TV | supported-negative · contrary (1, 0.931095) |
| [heldout-direction](../../artifacts/cycle19/demonstrations/heldout-direction.json) | c19root_c5a139782c4f455d787f | D-AB | True / True | supported-positive · answer (1, 0.931487) | supported-positive · answer (1, 0.885285) |
| [missing](../../artifacts/cycle19/demonstrations/missing.json) | c19root_c5a139782c4f455d787f | D-AB | True / True | unknown · no returned TV | unknown · no returned TV |
| [new-endpoint](../../artifacts/cycle19/demonstrations/new-endpoint.json) | c19root_c5a139782c4f455d787f | D-AB | True / True | supported-positive · answer (1, 0.931487) | supported-positive · answer (1, 0.885285) |
| [positive](../../artifacts/cycle19/demonstrations/positive.json) | c19root_ad3338bf67bceedc086f | D-AB | True / True | supported-positive · answer (1, 0.931487) | supported-positive · answer (1, 0.885285) |
| [shared-limitation](../../artifacts/cycle19/demonstrations/shared-limitation.json) | c19root_ad3338bf67bceedc086f | S-AA | True / True | supported-positive · answer (1, 0.931487) | unknown · no returned TV |
| [source-removal](../../artifacts/cycle19/demonstrations/source-removal.json) | c19root_ad3338bf67bceedc086f | leave-one | True / True | supported-positive · answer (1, 0.92987) | supported-positive · answer (1, 0.883748) |
| [first-new-endpoint](../../artifacts/cycle19/demonstrations/first-new-endpoint.json) | c19root_d16e5489798ae737900b | D-AB | False / False | unknown · no returned TV | supported-negative · contrary (1, 0.931095) |

The new-endpoint entries cover the first qualifying development and final-test cases. The downward-ray example uses a direction absent from training. Renaming and board transformations remain dependent on their parent games. The shared-arm case uses the same environmental inputs as its disjoint counterpart. Source removal changes the admitted clearance evidence and requires a real refit. Environmental supersession invalidates both target measurements and downstream uses.
