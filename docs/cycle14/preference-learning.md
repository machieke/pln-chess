# Native preference learning

Development selected **shared-relation-v1**, using correct-answer yield, answered accuracy and then the registered simpler descriptor as tie breakers. The selected immediate model is `immediate-shared-relation-v1` and the continuation model is `temporal-selected`. Selection used 80 development roots; the [selection receipt](../../artifacts/cycle14/development/selection.json) states that final predictions were not observed. Thresholds, checkpoint hashes and calibration mappings were then bound in the [evaluation freeze](../../artifacts/cycle14/evaluation-freeze.json).

| Panel | All | Directional references | Answered | Correct | Wrong | Answered accuracy | Directional coverage | Unknown reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Immediate / new final test | 200 | 145 | 42 | 24 | 18 | 57.1% | 29.0% | 52 |
| Two supplied plies / same 50 roots | 50 | 33 | 3 | 2 | 1 | 66.7% | 9.1% | 17 |
| Three supplied plies / same 50 roots | 50 | 28 | 7 | 4 | 3 | 57.1% | 25.0% | 22 |
| TCEC / TCEC-excluded preference fit | 60 | 25 | 4 | 2 | 2 | 50.0% | 16.0% | 34 |

The immediate answered-accuracy 95% source-group bootstrap interval is 42.9%–71.4% (1000/1000 defined replicates); directional coverage is 21.5%–36.3% (1000/1000 defined replicates). The source-held-out accuracy interval is 0.0%–100.0% (991/1000 defined replicates). Undefined or very sparse answered denominators do not establish reliable preference quality.

| Panel | Independent groups | Answered accuracy 95% interval | Directional coverage 95% interval |
| --- | --- | --- | --- |
| Immediate | 200 | 42.9%–71.4% (1000/1000 defined replicates) | 21.5%–36.3% (1000/1000 defined replicates) |
| Two supplied plies | 50 | 0.0%–100.0% (943/1000 defined replicates) | 0.0%–20.7% (1000/1000 defined replicates) |
| Three supplied plies | 50 | 16.7%–100.0% (999/1000 defined replicates) | 10.0%–41.7% (1000/1000 defined replicates) |
| TCEC family holdout | 60 | 0.0%–100.0% (991/1000 defined replicates) | 4.0%–30.8% (1000/1000 defined replicates) |

| Model | Training observations | Hypotheses | Abstraction | Concepts | Dependence handled | Version |
| --- | --- | --- | --- | --- | --- | --- |
| frozen-c13 | 222 | 44 | relational | False | True | 658db2b50b90fe26f4bb27396a88b0ceb662e13e948d4f9cda57b1f3c390e13c |
| historical-dependent-repeat | 444 | 61 | c13-relational | False | True | 200b1027f6387efd10ece1935641243de113d7cb10017eed5e07754f9cd1af8d |
| historical-unsafe-repeat | 444 | 61 | c13-relational | False | False | 347bf598b1a6294db94435c60b5004d740b9236942973756834976070c73f79f |
| immediate-c13-relational | 422 | 80 | c13-relational | False | True | c1606cf9c3a2e28601ff034775000530842c68d6a47f46ace523039cd1f58f98 |
| immediate-role-change-v1 | 422 | 163 | role-change-v1 | False | True | b4b269c1da0f9281b848c3c170cca4068a1128133ffb6ad92704de8ebc77a9ed |
| immediate-selected-concepts | 422 | 319 | shared-relation-v1 | True | True | ca92286410ee5cf9bd577d8a11d5db150dfef698b903e600195f9c5bf2dc480b |
| immediate-shared-relation-v1 | 422 | 243 | shared-relation-v1 | False | True | 115d224536c5418d4d05daef7c3c5c1a7ab1a796d0046a1a06237e981356ccc8 |
| old-labels-old-descriptor | 222 | 44 | c13-relational | False | True | ee09db1d7931a54b42cff2d3332be96fc5a6133c19cda27c511c12f0507ea6b6 |
| revised-labels-historical-only | 222 | 61 | c13-relational | False | True | 5eca29dd06b6b6f09ab280aafe545ae185fbb692fb4eac2d0937b329b9a48ffe |
| source-family-heldout | 385 | 234 | shared-relation-v1 | False | True | c4f9996c8c0e3895f3a43fc0396881f2c296d8266d2f038263393e6e41245a99 |
| temporal-old-descriptor | 654 | 175 | c13-relational | False | True | 94e6b415c6660f0928931204d0fe38fae7b09165b0f1c7a2f14fc53ece4da5be |
| temporal-old-labels | 294 | 80 | c13-relational | False | True | 83e1924f7eddf6ebf1651272631e442dd3160c42a7e83a05d7dc82596765f3db |
| temporal-omission-robust | 886 | 380 | shared-relation-v1 | False | True | 6470ec19aff7219a81aa76a3b9ac081092be7a059421f9a0df77ca18112fe0f5 |
| temporal-revised-historical | 294 | 114 | c13-relational | False | True | d65b2afcc8b1748e25f39bd02dd5bfe04963903ae0c7844e08fb5fbe7d153c7d |
| temporal-selected | 654 | 378 | shared-relation-v1 | False | True | 1d9d0646cbe4f352b1c98a7650ff8834a9c343ffadcab04420867a97990c7a03 |
| temporal-selected-concepts | 654 | 465 | shared-relation-v1 | True | True | 81429456ce6c56718c40af053b251652a52e2a0134f980427da67ed75c3ab92d |

All fitted models remain experimental. Native `Truth_Revision` updates three independent channels from registered, generation-bound evidence. Native `Truth_ModusPonens` applies a learned conditional to an explicitly supplied observation packet. Host code supplies bounded descriptors, ancestry grouping and observation trust; it does not calculate substitute truth-value formulas. A, B and nondirectional channels are not a normalized distribution. Unknown labels are excluded from directional updates. Incomplete observations and indistinguishable directional packets are explicitly excluded, with counts in each [learning receipt](../../artifacts/cycle14/learning/).

Frozen C13, old-label historical, revised-label historical, expanded-corpus, refined-descriptor, concept, source-family and temporal arms remain separate checkpoint identities. The matched studies distinguish their effects. New data and repeated old observations are separate arms; unsafe counting is never a default. The dedicated source-family preference fit excludes all TCEC preference-training records. It retains the common development-selected descriptor and frozen upstream field/concept checkpoints; this is not an end-to-end claim of no prior exposure to that family.

The accepted legal checkpoint remains `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`. No experimental preference checkpoint becomes a legal default, strategic utility or automatic selector. Every answer is a native conditional on host-assembled relative evidence; complete joint strategic proofs remain unavailable.
