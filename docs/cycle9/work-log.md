# Cycle 9 engineering log

Starting commit: `36b5ea10395c0f41de4c03824ba6f8ee1c5dbad1`. The supplied Cycle 9 brief was the sole untracked file at entry. Work is authorized for local commits only; the current brief prohibits pushing and external deployment.

The original implementation is locked in `/data/pln-chess-cycle9-baseline`. Its native runtime points to the audited existing runtime during the pre-edit replay. All historical Cycle 8 manifest entries were checked before evaluations started. Operational, strict and experimental replays compare classifications, raw TVs, rule/evidence identities, dependence groups and reconstructed native proof hashes.

The preregistered dataset generated 140 complete games, 700 sampled positions, 128 adversarial positions and 80 special-move positions. Development, calibration and final game evaluation use disjoint opening families and game provenance. Full-board translation/reflection/color equivalence is excluded against historical data and current samples. The final held-out test has not been used to change hypotheses or thresholds.

Developmental temporal evidence reuse resolved two castling abstentions at unchanged raw native TVs. Missing events, removed rights and suppressed temporal evidence remove positive support. Full-position proof IDs differ from selected-candidate proof IDs because schedule node ordinals differ; both original graphs are retained. Historical regression parity continues to compare identical invocation contexts exactly.

Two development failures are preserved under `artifacts/cycle9/development/`: an incorrectly specified double-check counterfactual was rejected by the dataset generator and corrected before the dataset was accepted; an overstrict cross-schedule proof-ID assertion was replaced with equal semantic outputs plus retention of both graphs. Neither failure changed native inference or relaxed a historical acceptance gate.

The initial research checks passed (11 tests). Temporal-category and evidence-dependence preflights passed. Duplicate and annotated correlated records preserve native belief values; removing all groups removes the hypothesis. Repeated raw training rows change the audit ledger identity even when dependence-aware beliefs stay equal; this distinction is recorded explicitly.

Profiling found repeated state identity, FEN generation, native-TV dictionary conversion and model serialization work. Optimizations are prepared but are gated behind completion of the pre-edit baseline replay. New source-bound acceptance will preserve the C8 checkpoint and require all historical gates, fresh bootstrap, proof parity and full tests before operational default approval.

The composition review and architectural decision are complete as research recommendations. Production extension is no-go; a bounded, isolated credal prototype is conditionally justified only under future explicit authorization. No new native operator is implemented.
