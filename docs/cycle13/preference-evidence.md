# Preference evidence contract

The registered contract is implemented in `src/pln_chess/cycle13/evidence.py` and the isolated offline learner in `training/cycle13_learning.py`. The starting baseline passed before fitting. Each study retains its complete `ledger.jsonl`, checkpoint and ordered native training trace under `artifacts/cycle13/learning/`.

Preference evidence is separate from the Boolean legal-move ledger. It records a supplied position, two candidate moves, independently inferred field records, their relative categorical descriptor, the external supervision source, a four-way label, source-game and dependence ancestry, temporal context, and field/concept/preference/native-runtime identities. Evidence and proof identifiers bind content; measured elapsed time cannot change a scientific observation's identity.

The labels are `A`, `B`, `no-demonstrated-preference`, and `unknown`. The third records that the registered comparison did not demonstrate a directional margin. It does not prove strategic equivalence. Unknown supervision remains in the append-only evidence but cannot update a direction as if it were negative evidence.

The ledger must validate the whole batch before writing, lock concurrent appends, flush durable records, reject conflicting reuse of an observation identity, and make repeated delivery idempotent. The original source observation remains inspectable even when it is not eligible for learning. Derived training receipts record why each dependent or ambiguous observation was excluded.

Learning groups evidence by a relative hypothesis and connected ancestry. One representative of a consistent component contributes to revision. Multiple records connected through a source game, original pair or transformation lineage cannot acquire extra confidence by being submitted again. Internally contradictory dependent observations are withheld. Opposing observations from independent components remain native revision inputs and are visible in the training proof.

The offline reference source is pinned Stockfish 18. Its two explicit candidate roots, node budgets, score perspective, PVs, score bounds, depths and source hashes are retained. The registered label policy is in [research-registration.md](research-registration.md). Scores serve supervision and evaluation only; the production descriptor and conditional model contain no centipawn utility. Offline label outputs have no status as native PLN conclusions.

Two- and three-ply evidence inherits its original game's ancestry. The continuation registration selects 36 training, 12 calibration and 12 test pairs in fixed hash order, requiring a supplied three-ply line for each candidate. It selects neither a favorable reference result nor a successful PLN prediction. Separate endpoint searches use the original actor's perspective and full supplied game history. Immediate and continued observations remain distinct contexts, while their shared ancestry remains connected.

The negative dependence control deliberately repeats deliveries of the same supervision through distinct observer identities. The ordinary learner must retain one effective contribution; the explicit no-dependence ablation may count them and disclose the resulting confidence inflation. Repeated deliveries do not enlarge the claimed independent dataset.

No ledger operation updates the accepted legal checkpoint. Experimental evidence cannot become an operational default, certify a move's legality, or imply unobserved continuations.
