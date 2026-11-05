# Model card

This is a first-stage relational native-PLN research demonstrator, version 0.1.0. It is suitable for inspecting native truth values, relative observation transfer, evidence provenance and runtime gaps. It is not a chess engine, tournament player, or source of guaranteed legal moves.

Seeded biases: six piece families, signed movement-template families, owner-oriented pawn forward, structural special-move edits, typed relative sensory descriptors, low-confidence hypothesis priors and weak attack/exposure implications. Learned content: two-channel conditional case beliefs and individual opponent attack beliefs, updated through verified native revision. Generalization: exact reuse of relative categories across translated observations, plus native unary attack/exposure support. Arbitrary symbolic rules are not synthesized.

The audited native core lacks conjunction introduction. A category matching multiple observed fields is not a compositional PLN proof that every chess condition holds. Complete state/history semantics, terminal-state inference, automatic chess induction and broad structural generalization remain incomplete. The strict held-out metrics and abstention rates in `docs/final-report.md` are the practical limits of the shipped checkpoint.

The oracle labels data only in training/evaluation. Production inference uses native MeTTa rules and cannot import the oracle. The native strength is a belief component; confidence is evidential support under upstream heuristics. Neither is automatically a calibrated probability of legality. Raw TVs are always retained. The separate validation-bin calibration experiment is small and exploratory.

Reproducibility: pinned PLN/PeTTa commits and source hashes, exact interpreter lock, pinned Python dependencies, fixed dataset seed/hash, append-only evidence with dependence groups, hashed model manifests, deterministic replay, and machine-generated proofs. Limitations include categorical sparsity, lost observations, conservative exclusion of correlated conflicts, seeded geometry bias, no uncertainty propagation through individual missing-cell combinations, and a cold-subprocess runtime cost.
