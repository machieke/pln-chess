# Defense potential

Geometric protection of an observed friendly occupied target. Recapture legality, pin constraints and global king safety remain separate.

On the registered mixed test panel, precision is 100.000%, recall 100.000%, and abstention 0.239%, across 8,354 relations. False supported positives: 0; false supported contradictions: 0. Native conditional proofs: 8,334; global composition proofs: 0. [field-evaluation/summary.json](../../artifacts/cycle11/field-evaluation/summary.json).

On the published-game subpanel alone, precision is 100.000%, recall 100.000%, and abstention 0.334%. The empty checkpoint abstains on 100.000% of the full panel. These are relation labels, not legal-move or strategic-success labels.



The source/target context is observed by the host. A relative learned conditional is revised through native `Truth_Revision`, then applied through native modus ponens, negation and evidence selection. Every supported result retains native expressions, returned truth values, rule IDs, evidence IDs, dependence groups and model/runtime identities. The observation is one supplied local-context premise; the graph does not claim a native conjunction proof over independently uncertain subpremises.

For the `pinned-defender` demonstration, the hypothetical after-state relation `f2 → e1` is `contradicted` under rule `c11field:5b4f1c19e36e477a05e9a350b06ec335`. Its complete trace identity is `8c869f6fc2f156f79a4022e20c0e43e8e08f7556f5f94234c1ba2dcc09da5b6c`. The first two nodes apply the positive and negative learned channels; negation reverses the negative conclusion, and evidence selection returns the chosen native result.

| Native operator | Returned truth value |
|---|---|
| `Truth_ModusPonens` | `{'confidence': 0.0028779069767441885, 'strength': 0.003267973856209153}` |
| `Truth_ModusPonens` | `{'confidence': 0.8777616279069769, 'strength': 0.996732026143791}` |
| `Truth_Negation` | `{'confidence': 0.8777616279069769, 'strength': 0.0032679738562090277}` |
| `BestConfidenceCandidate` | `{'confidence': 0.8777616279069769, 'strength': 0.0032679738562090277}` |

The exact expressions, premise values, source observation and evidence IDs are retained in [the proof index](../../artifacts/cycle11/fields/worked-proof-index.json). This example is selected for review and adds no statistical evidence.

Worked coverage includes: Defended pawns/minor pieces, rook batteries, pinned defenders, multiple defenders and discovered defense. Before/after values and native proofs are retained even when the proposed candidate is unknown or contradicted by the accepted legality learner. [fields/worked-examples.json.xz](../../artifacts/cycle11/fields/worked-examples.json.xz).

Group-bootstrap 95% intervals: `{"abstention_rate": [0.0008682709005209626, 0.004598405885959534], "precision": [1.0, 1.0], "recall": [1.0, 1.0]}`. Only two controlled test generator groups limit uncertainty resolution; source games can share further dependencies. Raw-strength Brier diagnostic: 0.000609; calibration-only fitted diagnostic on test: 0.000038. Raw PLN confidence is not an empirical probability. Neither calibration nor visualization changes the native result. [field-evaluation/calibration.json](../../artifacts/cycle11/field-evaluation/calibration.json).

Missing required occupancy or an unlearned conditional remains unknown; execution limits remain incomplete. Shape/occupancy pooling and symmetry are supplied ontology assumptions. Accurate conditional influence cannot establish strategic competence.
