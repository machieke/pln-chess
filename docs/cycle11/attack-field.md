# Attack potential

Geometric influence under observed occupancy. Friendly occupied endpoints and pinned attackers are included. It does not imply a legal capture.

On the registered mixed test panel, precision is 100.000%, recall 100.000%, and abstention 0.553%, across 15,557 relations. False supported positives: 0; false supported contradictions: 0. Native conditional proofs: 15,471; global composition proofs: 0. [field-evaluation/summary.json](../../artifacts/cycle11/field-evaluation/summary.json).

On the published-game subpanel alone, precision is 100.000%, recall 100.000%, and abstention 0.873%. The empty checkpoint abstains on 100.000% of the full panel. These are relation labels, not legal-move or strategic-success labels.



The source/target context is observed by the host. A relative learned conditional is revised through native `Truth_Revision`, then applied through native modus ponens, negation and evidence selection. Every supported result retains native expressions, returned truth values, rule IDs, evidence IDs, dependence groups and model/runtime identities. The observation is one supplied local-context premise; the graph does not claim a native conjunction proof over independently uncertain subpremises.

For the `rook-obstruction` demonstration, the hypothetical after-state relation `a4 → e4` is `supported` under rule `c11field:5a43cdad06e3b62378c3fff98666ea3c`. Its complete trace identity is `a0485f1333f22ed837c883fe8932e8878a030e2a794ea0283c4a6475f9895eff`. The first two nodes apply the positive and negative learned channels; negation reverses the negative conclusion, and evidence selection returns the chosen native result.

| Native operator | Returned truth value |
|---|---|
| `Truth_ModusPonens` | `{'confidence': 0.9267049180327871, 'strength': 0.9982517482517483}` |
| `Truth_ModusPonens` | `{'confidence': 0.0016229508196721342, 'strength': 0.0017482517482517513}` |
| `Truth_Negation` | `{'confidence': 0.0016229508196721342, 'strength': 0.9982517482517482}` |
| `BestConfidenceCandidate` | `{'confidence': 0.9267049180327871, 'strength': 0.9982517482517483}` |

The exact expressions, premise values, source observation and evidence IDs are retained in [the proof index](../../artifacts/cycle11/fields/worked-proof-index.json). This example is selected for review and adds no statistical evidence.

Worked coverage includes: Rook obstruction, bishop opening, discovered attack and knight relocation. Before/after values and native proofs are retained even when the proposed candidate is unknown or contradicted by the accepted legality learner. [fields/worked-examples.json.xz](../../artifacts/cycle11/fields/worked-examples.json.xz).

Group-bootstrap 95% intervals: `{"abstention_rate": [0.0024936482544462217, 0.009903765299448752], "precision": [1.0, 1.0], "recall": [1.0, 1.0]}`. Only two controlled test generator groups limit uncertainty resolution; source games can share further dependencies. Raw-strength Brier diagnostic: 0.001398; calibration-only fitted diagnostic on test: 0.000007. Raw PLN confidence is not an empirical probability. Neither calibration nor visualization changes the native result. [field-evaluation/calibration.json](../../artifacts/cycle11/field-evaluation/calibration.json).

Missing required occupancy or an unlearned conditional remains unknown; execution limits remain incomplete. Shape/occupancy pooling and symmetry are supplied ontology assumptions. Accurate conditional influence cannot establish strategic competence.
