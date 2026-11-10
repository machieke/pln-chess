# Mobility potential

Ordinary occupancy-constrained movement. Pawn end-rank queries use a queen-promotion witness in offline labels; castle and en-passant eligibility are outside this relation domain.

On the registered mixed test panel, precision is 100.000%, recall 98.580%, and abstention 0.608%, across 15,464 relations. False supported positives: 0; false supported contradictions: 9. Native conditional proofs: 15,370; global composition proofs: 0. [field-evaluation/summary.json](../../artifacts/cycle11/field-evaluation/summary.json).

On the published-game subpanel alone, precision is 100.000%, recall 95.631%, and abstention 0.885%. The empty checkpoint abstains on 100.000% of the full panel. These are relation labels, not legal-move or strategic-success labels.

The post-freeze audit identifies 9 king-to-rook castling aliases among the 9 primary false-negative rows. The offline reference accepts those aliases, while the ordinary-mobility adapter excluded only two-cell king castling moves. This is a label-domain mismatch. All original labels, errors and denominators remain in the primary results; no model, threshold or test selection was changed. [field-evaluation/post-freeze-false-negatives.json](../../artifacts/cycle11/field-evaluation/post-freeze-false-negatives.json)

The source/target context is observed by the host. A relative learned conditional is revised through native `Truth_Revision`, then applied through native modus ponens, negation and evidence selection. Every supported result retains native expressions, returned truth values, rule IDs, evidence IDs, dependence groups and model/runtime identities. The observation is one supplied local-context premise; the graph does not claim a native conjunction proof over independently uncertain subpremises.

For the `promotion` demonstration, the hypothetical after-state relation `b8 → a6` is `supported` under rule `c11field:42fb52fa0340e692eb8ae939fe1ee4af`. Its complete trace identity is `c3f422e7699e12b2a68fede215024fa34ace36e1d8592271cd02cb244126005f`. The first two nodes apply the positive and negative learned channels; negation reverses the negative conclusion, and evidence selection returns the chosen native result.

| Native operator | Returned truth value |
|---|---|
| `Truth_ModusPonens` | `{'confidence': 0.9267049180327871, 'strength': 0.9982517482517483}` |
| `Truth_ModusPonens` | `{'confidence': 0.0016229508196721342, 'strength': 0.0017482517482517513}` |
| `Truth_Negation` | `{'confidence': 0.0016229508196721342, 'strength': 0.9982517482517482}` |
| `BestConfidenceCandidate` | `{'confidence': 0.9267049180327871, 'strength': 0.9982517482517483}` |

The exact expressions, premise values, source observation and evidence IDs are retained in [the proof index](../../artifacts/cycle11/fields/worked-proof-index.json). This example is selected for review and adds no statistical evidence.

Worked coverage includes: Blocker removal, knight relocation and promotion to a new piece kind. Before/after values and native proofs are retained even when the proposed candidate is unknown or contradicted by the accepted legality learner. [fields/worked-examples.json.xz](../../artifacts/cycle11/fields/worked-examples.json.xz).

Group-bootstrap 95% intervals: `{"abstention_rate": [0.0032444124008651765, 0.011451019725844199], "precision": [1.0, 1.0], "recall": [0.9444444444444444, 0.99706457925636]}`. Only two controlled test generator groups limit uncertainty resolution; source games can share further dependencies. Raw-strength Brier diagnostic: 0.002110; calibration-only fitted diagnostic on test: 0.000586. Raw PLN confidence is not an empirical probability. Neither calibration nor visualization changes the native result. [field-evaluation/calibration.json](../../artifacts/cycle11/field-evaluation/calibration.json).

Missing required occupancy or an unlearned conditional remains unknown; execution limits remain incomplete. Shape/occupancy pooling and symmetry are supplied ontology assumptions. Accurate conditional influence cannot establish strategic competence.
