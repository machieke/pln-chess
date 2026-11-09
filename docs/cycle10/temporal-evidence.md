# Historical evidence transport and counterfactuals

The versioned transport replayed **150 complete published game records** and produced **21 inspectable demonstrations**. The native counterfactual error list is `[]`. Historical legality remains explicitly unverified by production replay. [temporal/game-replay.json](../../artifacts/cycle10/temporal/game-replay.json); [temporal/summary.json](../../artifacts/cycle10/temporal/summary.json)

The `temporal-transport-v10` receipt separates supplied events, trusted imported metadata, inferred structural relationships and unknown history. It records ObservedMove, PreviouslyMoved, LastMoveDoublePawnAdvance, RetainedCastlingRight, HistoricalEvidenceSource and HistoryConfidence as provenance relations. Their transport truth-value field is null: this module introduces neither a host probability formula nor a new native theorem. Existing native temporal inference receives the established history contract. [Implementation](../../src/pln_chess/cycle10/temporal.py).

Event IDs bind source, sequence, predecessor, mover, before/after state and effects. They remain stable across model versions. The enclosing receipt binds model/runtime identity, initial trust and the complete supplied input; appending preserves prefix event IDs and records the parent receipt. A reported-state mismatch is a conflict, not a fabricated transition. Up to 4,096 events are retained; the legacy 512-event window explicitly reports omitted prefixes. [temporal/external-replay-examples.json.xz](../../artifacts/cycle10/temporal/external-replay-examples.json.xz)

A standard-start PGN import explicitly attests its initial metadata. A partial SetUp game or plain FEN retains unknown prior history. A FEN en-passant flag never becomes an observed double step. Structural replay can represent an illegal proposed sequence and does not certify legal play or repetition termination. The offline PGN preparation command may validate the source with the reference library, within the preparation boundary. [Tests](../../tests/test_cycle10_temporal.py); [offline importer](../../training/cycle10_import.py).

All 16 Cycle 9 adversarial and nine special-move abstentions were reproduced. Each involved castling or en-passant history, with original proof traces retained. Added attestations or reverse-constructed predecessors are labelled controlled interventions; no actual historical record was recovered for those synthetic fixtures. [temporal/historical-abstentions.json.xz](../../artifacts/cycle10/temporal/historical-abstentions.json.xz)

| Cohort / split | Investigated candidates | Resolved under supplied evidence | Exact full positions after intervention | Missing local hypothesis |
|---|---|---|---|---|
| cycle10/synthetic-adversarial | 14 | 7 | 7 | 7 |
| cycle9/adversarial | 16 | 8 | 8 | 8 |
| cycle9/special-moves | 9 | 5 | 5 | 4 |

Across those interventions, 20 complete position evaluations became exact; removing the temporal evidence channel caused 39 abstentions. Removing eligibility left 0 supported-legal candidates. These are measured controls, not assumptions of success. [temporal/summary.json](../../artifacts/cycle10/temporal/summary.json)

After supplying history, 19 investigated candidates still report a missing matching pooled local hypothesis. Recognized historical evidence and adequate learned local knowledge are separate requirements; no classification was forced to meet a resolution target. [temporal/root-cause-assessment.json](../../artifacts/cycle10/temporal/root-cause-assessment.json)

The demonstrations cover both castling sides, moved-and-returned kings and rooks, castling through attack and in check, fresh/stale/conflicting en-passant evidence, en-passant king exposure, and all four straight and capture promotion choices. Paired geometry is identical while evidence or eligibility differs. Each record includes the starting state, supplied events, final state, propositions, expected reference outcome, native result, lineage and relevant removal control. [temporal/counterfactuals.json.xz](../../artifacts/cycle10/temporal/counterfactuals.json.xz)

The original FEN-only Cycle 9 measurements remain 112/128 adversarial and 71/80 special exact sets. Conditional interventions do not retrospectively convert those original unknowns into known facts. Independent actual-history evidence is evaluated on all 1,020 final external positions. [baseline/cohort-metrics.json](../../artifacts/cycle10/baseline/cohort-metrics.json); [analysis/temporal-summary.json](../../artifacts/cycle10/analysis/temporal-summary.json)

The actual-history arm retains 2 unresolved legal or erroneous candidates. Every one has a supplied published prefix and a transport ID. A legacy label such as `en-passant-history` is a structural heuristic, not proof that events are missing. The separate residual assessment records each native LocalAdmissibility derivation and its conditional premises, so weak learned support remains distinguishable from unavailable history. [temporal/actual-history-residuals.json](../../artifacts/cycle10/temporal/actual-history-residuals.json); [analysis/temporal-failure-proofs.json.xz](../../artifacts/cycle10/analysis/temporal-failure-proofs.json.xz)

| Actual-history fixture | Move | Classification | Native local value | Legacy heuristic |
|---|---|---|---|---|
| c10-position-00861 | d5e6 | unknown | {'confidence': 0.024750000000000005, 'strength': 0.5} | en-passant-history |
| c10-position-01151 | d5c6 | unknown | {'confidence': 0.0, 'strength': 0.5} | en-passant-history |

Replay overhead and fresh-versus-reused native cache proof equality after source, confidence and event changes are measured separately. [performance/temporal.json](../../artifacts/cycle10/performance/temporal.json)
