# Promotion outcomes and causal transfer controls

| Model | Original cases | Errors remaining | Correct supported | Unknown | Incomplete |
|---|---|---|---|---|---|
| C8-frozen | 8 | 0 | 0 | 8 | 0 |
| C8-promotion-relative | 8 | 0 | 8 | 0 | 0 |
| C8-no-promotion-training | 8 | 0 | 0 | 8 | 0 |

Abstention removes a wrong decision but is not counted as a correct supported resolution. The original eight cases and their first faulty evidence selection are analyzed in [promotion-error-analysis.md](promotion-error-analysis.md). Every replay retains the actual native graph in `proofs/*-original-errors.json.xz`.

The transfer study attempted **96** complete focus moves. It found **52** successful case demonstrations from **26** source groups; **18** groups belong to combination/adversarial holdouts. Color mirrors are correlated controls, not additional independent acquisitions.

A counted success has the expected supported decision, uses a new promotion hypothesis, differs from every source evidence FEN and complete C4 context, comes from a distinct structural family, and loses the conclusion or raw support after removing that hypothesis. Shared relative local transition categories are intentional. Removal of a whole hypothesis tests that evidence family causally; separate training-replay tests retract source groups. No arbitrary-context or unseen-type safety claim follows.

| Fixture | Split | Tested move | Tested choice | Learned rule | Raw native STV |
|---|---|---|---|---|---|
| c8-combination-holdout-0168 | combination-holdout | c7c8q | q | c8:689cd42d1ba19003db3bc7ec | {'confidence': 0.7221553454421085, 'strength': 0.008532864515397254} |
| c8-combination-holdout-0170 | combination-holdout | g7g8b | b | c8:7ffcb699745366111cb3bed6 | {'confidence': 0.7221553454421085, 'strength': 0.008532864515397254} |
| c8-combination-holdout-0174 | combination-holdout | b7b8b | b | c8:96de9753d9b31c8da93c330f | {'confidence': 0.8061011260397823, 'strength': 0.005378885178525361} |
| c8-combination-holdout-0176 | combination-holdout | f7f8q | q | c8:708e631d02325e9d8396139e | {'confidence': 0.7221553454421085, 'strength': 0.008532864515397254} |
| c8-combination-holdout-0178 | combination-holdout | c7d8b | b | c8:92cc91c21959649bfbca8a8a | {'confidence': 0.8777616279069769, 'strength': 0.996732026143791} |
| c8-combination-holdout-0180 | combination-holdout | g7f8q | q | c8:4860b71020979ba7a4209fbb | {'confidence': 0.8777616279069769, 'strength': 0.996732026143791} |
| c8-combination-holdout-0182 | combination-holdout | g7f8b | b | c8:b35c24f91f2838001e416164 | {'confidence': 0.8777616279069769, 'strength': 0.996732026143791} |
| c8-combination-holdout-0184 | combination-holdout | c7d8q | q | c8:1595785dab7a4d187bc38809 | {'confidence': 0.7889062500000001, 'strength': 0.9935064935064936} |
| c8-combination-holdout-0190 | combination-holdout | d7c8b | b | c8:b35c24f91f2838001e416164 | {'confidence': 0.8777616279069769, 'strength': 0.996732026143791} |
| c8-adversarial-0200 | adversarial | b7b8q | q | c8:689cd42d1ba19003db3bc7ec | {'confidence': 0.7221553454421085, 'strength': 0.008532864515397254} |

The [representative archive](../../artifacts/cycle8/proofs/representative-transfers.json.xz) includes full training evidence, actual tested move, descriptor, native expressions, raw STV, matched rule, full proof and removal replay. It also retains the original fixture focus when its choice differs from the round-robin tested choice. [All attempts](../../artifacts/cycle8/proofs/transfer-attempts.json.xz) retain unknowns, incorrect decisions and excluded exact-context controls.

Metamorphic file translations, file reflections, color-relative transformations and all resulting choices are summarized in [transformations.json](../../artifacts/cycle8/transformations.json), with [complete proofs](../../artifacts/cycle8/proofs/transformations.json.xz) retained separately. They share ancestry and do not increase the independent holdout count. Vertical translation across the promotion boundary is not treated as a symmetry.

Each of C8-frozen, the promotion candidate and the exact-only fallback reexecutes all **287** historical negative/removal pairs and the **36** temporal cases, with four missing-history rejections. Raw archives preserve premise/rule/evidence IDs, groups, runtime/model versions, truth values, derivation order, status and budgets. The verifier reconstructs every evaluation proof digest and requires the frozen native traces to match the original baseline. Temporal replay establishes structural consistency of supplied events, not legal historical play.
