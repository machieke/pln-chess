# Cycle 4 architecture and source inventory

Cycle 4 adds schema `factored-constraints-v4`. It learns local movement support and negative constraints as **different propositions**. Every probabilistic update and inference operation runs in the locked, unmodified PLN library through PeTTa. The production package never imports the reference chess engine.

The observation layer exposes typed facts for mover class, displacement, each ray cell, destination occupancy and kind, boundary, temporal observations, and the proposed structural successor. Absolute squares and piece IDs bind instances; they do not identify learned rules. `LocalAdmissibility` retains an explicitly non-compositional pooled observation. Capture victim identity and empty-ray distance are omitted from that projection; pawn double steps retain the start-edge relation and promotions retain the destination-edge relation. Castling retains its declared rights, rook and path observations. These projections are host-provided inductive bias.

The negative routes are native MP chains:

```
opponent frame -> Attack -> WouldExposeOwnKing -> Not LegalMove
ray-cell observation -> Obstruction -> Not LegalMove
destination observation -> DestinationConflict -> Not LegalMove
boundary observation -> BoundaryConflict -> Not LegalMove
local negative channel -> LocalFailure -> Not LegalMove
```

The first route uses three separately trained conditional families and disjoint source groups. It is a unary chain, **not** conjunction of independently established movement, obstruction and king safety. Positive results remain a conditional local projection. No failure to find an attack creates a `KingSafe` or `NoAttack` conclusion.

| Feature | Source and callable | Native operation | Verification |
|---|---|---|---|
| Runtime pin and bridge | `src/pln_chess/pln/runtime.py:Runtime.verify/execute/batch` | Exact upstream expressions | Existing native tests; `evaluation/cycle4_native.py:audit` |
| Typed observation ontology | `src/pln_chess/cycle4/ontology.py:descriptors/relation` | None; sensed/host-grounded | Key, translation, remote-piece and capture-kind tests |
| Candidate and successor bias | `hypotheses.candidates`, `domain.Position.successor` | None | Existing grammar and structural special-move tests |
| Evidence ingestion | `cycle4.model.observe_example` | None until replay | Label validation and oracle-boundary tests |
| Training and rollback | `cycle4.model.train` | `Truth_Revision` | Duplicate, same-game, transformed ancestor, rollback, retraction tests |
| Constraint scheduler | `cycle4.inference.infer_moves` | MP, negation, confidence choice | Pins, double check, transit, protected capture, any-cell blocker tests |
| Native laboratory | `evaluation.cycle4_native.audit` | Deduction, inheritance, inversion, induction, similarity, equivalence; negative AND probes | Executable `.metta` and JSON receipts |
| Induction activation | `evaluation.cycle4_induction.experiment` | `Truth_w2c`, `Truth_Induction`, MP | Fixed population and matched/unmatched controls; experimental only |
| Temporal evidence | `cycle4.history.HistoryEvidence.apply` | None; structural consistency | Predecessor, weak observation, contradictory history tests |
| Calculation cache | `cycle3.native.NativeSession` reused unchanged | Memoized exact native expressions | Full candidate/proof reference, cold and warm equality |
| API compatibility | `api.explain_move/train/analyze_batch`; model/inference dispatch | Same scheduler | Schemas 1–4, batch and inspector contracts |
| Evaluation | `evaluation.cycle4.evaluate` | Calls production inference; oracle outside it | Full bounded candidate sets, complete error ledger |
| Reproduction | `scripts/cycle4_reproduce.sh`, `cycle4_deliver.py` | Locked runtime | Clean checkout and fresh output receipts |

The cache scope includes the runtime manifest, ontology, full model/evidence hash, observed state, and options. Cache entries are pure calculations; logical proof occurrences and evidence ancestry remain distinct. The implementation does not merge repeated logical nodes into a single exported DAG. Native work is memoized, while host grounding and proof serialization still cost time and memory.

Migration is replay from the original labeled inputs into schema 4. Renaming a Cycle 3 checkpoint header is rejected. Schemas 1–3 continue to load and dispatch to their original implementations; their artifacts remain immutable.
