# King-exposure potential

Individual opposing-source influence toward an observed king. A contradicted relation does not prove absence of all attacks or universal safety.

On the registered mixed test panel, precision is 100.000%, recall 100.000%, and abstention 2.446%, across 1,431 relations. False supported positives: 0; false supported contradictions: 0. Native conditional proofs: 1,396; global composition proofs: 0. [field-evaluation/summary.json](../../artifacts/cycle11/field-evaluation/summary.json).

On the published-game subpanel alone, precision is 100.000%, recall 100.000%, and abstention 6.744%. The empty checkpoint abstains on 100.000% of the full panel. These are relation labels, not legal-move or strategic-success labels.

The published-game subpanel contains only one positive king-exposure relation. Its perfect positive recall therefore provides very little independent evidence of generalization.

The source/target context is observed by the host. A relative learned conditional is revised through native `Truth_Revision`, then applied through native modus ponens, negation and evidence selection. Every supported result retains native expressions, returned truth values, rule IDs, evidence IDs, dependence groups and model/runtime identities. The observation is one supplied local-context premise; the graph does not claim a native conjunction proof over independently uncertain subpremises.

For the `king-exposure` demonstration, the hypothetical after-state relation `e8 → e1` is `supported` under rule `c11field:3572612658116656761e1eb79fe48b0e`. Its complete trace identity is `fbcea145f044e9666bd87db5e8d8aebdaf3a1e724846a49acbce0999bc09f32d`. The first two nodes apply the positive and negative learned channels; negation reverses the negative conclusion, and evidence selection returns the chosen native result.

| Native operator | Returned truth value |
|---|---|
| `Truth_ModusPonens` | `{'confidence': 0.8459328358208955, 'strength': 0.9956521739130435}` |
| `Truth_ModusPonens` | `{'confidence': 0.0036940298507462718, 'strength': 0.004347826086956525}` |
| `Truth_Negation` | `{'confidence': 0.0036940298507462718, 'strength': 0.9956521739130435}` |
| `BestConfidenceCandidate` | `{'confidence': 0.8459328358208955, 'strength': 0.9956521739130435}` |

The exact expressions, premise values, source observation and evidence IDs are retained in [the proof index](../../artifacts/cycle11/fields/worked-proof-index.json). This example is selected for review and adds no statistical evidence.

Worked coverage includes: Opened king rays, pinned blockers, multiple simultaneous attackers and en-passant exposure. Before/after values and native proofs are retained even when the proposed candidate is unknown or contradicted by the accepted legality learner. [fields/worked-examples.json.xz](../../artifacts/cycle11/fields/worked-examples.json.xz).

Group-bootstrap 95% intervals: `{"abstention_rate": [0.007251153592617007, 0.09968354430379747], "precision": [1.0, 1.0], "recall": [1.0, 1.0]}`. Only two controlled test generator groups limit uncertainty resolution; source games can share further dependencies. Raw-strength Brier diagnostic: 0.006151; calibration-only fitted diagnostic on test: 0.000114. Raw PLN confidence is not an empirical probability. Neither calibration nor visualization changes the native result. [field-evaluation/calibration.json](../../artifacts/cycle11/field-evaluation/calibration.json).

Missing required occupancy or an unlearned conditional remains unknown; execution limits remain incomplete. Shape/occupancy pooling and symmetry are supplied ontology assumptions. Accurate conditional influence cannot establish strategic competence.
