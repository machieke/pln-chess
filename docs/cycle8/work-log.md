# Cycle 8 execution record

Starting commit: `c6ee658352395abe6e276cafdf1ddf59830a17a0`. The user-supplied Cycle 8 brief was the only untracked input at start. Local implementation and commits are authorized; pushing and enabling a new native operator are prohibited.

The initial replay uses `/data/pln-chess-cycle8-baseline-c6ee658`, cloned from the starting commit, and `/data/pln-chess-cycle8-work/baseline`. The clone imports its own pinned source through explicit `PYTHONPATH` and `PLN_CHESS_ROOT`. It reuses the existing verified runtime only for this preflight. A separate fresh bootstrap is required for final acceptance. Baseline replay covers 12 frozen operational suites, 12 learned-candidate suites, 12 strict suites and the two existing experimental-mode suites. Production source remains unchanged during this replay.

Forensics reads all eight recorded errors, their native graphs and training evidence. The mathematical reference and proposal are isolated under `evaluation/` and `docs/`; production does not import them. The next implementation stages are the relative transition ontology, family-disjoint curriculum, bounded learner and ablations, transfer/removal controls, full evaluation, performance, public interfaces, fresh reproduction and final local delivery.

`configs/cycle8.json` records the prospective candidate and acceptance policy before generating new holdouts. Existing C7 failed cases are diagnostic data, never new training examples. Structural families describe complete interaction configurations; shared local predicates are intended transfer units and must be quantified, not falsely claimed disjoint.

Before any C8 model training or evaluation, the selection registration also names the conservative exact-only, no-promotion-training candidate as an eligible fallback under identical full-suite gates. The initial generated dataset preceded this registration metadata addition; its board/game content is unchanged and will be regenerated with the final registration hash. No model outcomes were inspected to choose this eligibility order.

The first focused run passed 26 tests and exposed one existing C7 zero-budget
failure (`typed_premises` absent on a truncated candidate). Both C7 and C8 now
initialize the missing diagnostic list without changing a native expression or
completed proof. The targeted replay passed; the corrected focused suite passed
28 tests, including the new inspector contract. Original logs are retained.

Before full matrix execution, the trained candidate corrected all eight original
promotion errors with supported decisions. The transfer pilot found 52 successful
case demonstrations among 96 attempts; mirrored cases share source groups and
must not be described as 52 independent observations. Final reporting will count
source groups and prefer combination/adversarial representatives. This pilot did
not change model architecture, training, thresholds, registration or eligibility.
`configs/cycle8-replay.json` freezes dataset/model replay digests before the clean
study. Full matrix outcomes and acceptance are still pending at implementation
commit time.
