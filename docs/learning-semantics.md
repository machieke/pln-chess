# Evidence and learning semantics

Training begins with a finite piece-relative geometry grammar and a prior `(stv .5 .05)` for each conditional case. There are no seeded certain chess legality rules. A positive label may reinforce a geometry hypothesis. An illegal label updates its contextual case and never globally discredits the piece's geometry.

Every ledger record contains source, dependence group, transformation lineage, position/candidate IDs, relative descriptor fingerprint, legal label, native observation TV, target hypotheses, model/runtime versions, sequence and timestamp. Auxiliary attack labels must be supplied explicitly by a caller; the production API never obtains them from a chess engine. The dataset factory uses reference attack information only after structural state editing, in `training/`.

Two channels receive separate observations: the conditional legal proposition and the conditional negative-legal proposition. Their evidence IDs are identical, so inference selects between them rather than revising them as independent support. Native `Truth_Revision` executes via upstream `|-` for each channel. No formula is reimplemented in Python. Native confidence reflects the upstream evidential convention; a high confidence is not automatically a calibrated probability.

Idempotency compares payload hashes and explicit keys. Reusing a key for different evidence is an error. The first contribution from a dependence group to a hypothesis is accepted; later correlated contributions, even conflicts, are retained but excluded. This deliberately conservative policy can lose information. It avoids claiming a native correlated-evidence revision operator that does not exist. Contrasting synthetic positions share a structural-family group, translated probes share their source group, and positions from one game share game provenance.

Independent conflicting observations do revise natively. `artifacts/proofs/evidence-revision.json` contains actual before/after states for first observation, identical replay, correlated contradiction, and independent contradiction. `artifacts/training-report.json` includes per-update TVs and excluded evidence. Deterministic replay ignores wall-clock timestamps when hashing model content. Checkpoint import validates content, grammar and runtime. Rollback uses `pln-chess replay --through N` into a new path.

Relative abstraction is host-language grouping by typed sensory descriptors. Native induction is tested separately, including its need for population marginals; no automated chess predicate induction or arbitrary program synthesis is claimed. The lack of native conjunction blocks a general compositional movement/context/safety rule. A categorical observation is not presented as a logical conjunction proof.

Sensor observations of a complete FEN use `(1,.99)` as a declared reliability assumption. An explicitly unknown cell makes the joint case observation confidence zero and inference abstains. Unknown rights prevent a castling-case inference. FEN does not prove complete game history; repetition, fifty-move adjudication and terminal game reasoning are outside the current model.

Display thresholds are configurable: default confidence ≥ .25, strength ≥ .8 for supported, strength ≤ .2 for contradicted. These select labels only. Actual raw TVs and proof nodes are untouched. Evaluation fits an empirical validation-only probability mapping and reports it separately; that mapping never enters inference.


## Cycle 5 scope

The earlier-cycle description above is preserved. See the [Cycle 5 update](cycle5/learning-semantics.md) for strict positive proof gaps, typed native negative chains, temporal trust modes and measured coverage loss. No universal correctness or completed positive conjunction is claimed.
