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

During final interface review, the new benchmark CLI branch was found to ignore
an explicit strict/experimental mode. It now forwards the mode and writes
mode-specific benchmark artifacts; a focused routing test passes. This change
is made while clean baseline workers are still importing the separate immutable
C7 checkout, before any clean C8 tests, training or evaluation begin. The clean
working checkout advances to the committed interface/report revision. Bootstrap
context retains its original HEAD and records this transition explicitly; native
pins and dependency files are unchanged. The C8 study subprocesses all start from
the updated clean source. No baseline rerun with changed C8 code is substituted.

The clean run reproduced all 38 original baseline evaluations exactly, then
completed 81 registered matrix evaluations. All 347 tests passed. Both registered
candidate models recorded zero false-legal, false-illegal, self-check false-legal
and incomplete results across their 16 suites. The promotion candidate supported
the correct decision in all eight original error cases; the frozen and exact-only
models abstained on those cases. Each of the three C8 control models preserved
all 287 negative/removal pairs with exact historical native trace parity, plus
the temporal controls.

The clean transfer run found 52 successful case demonstrations from 26 source
groups among 96 attempted focus moves. Eighteen groups were combination or
adversarial holdouts. Ten representative groups retain complete training evidence,
native expressions, proofs and removal results. All 32 metamorphic promotion
controls preserved their descriptors and correct supported decisions. These
counts do not make mirrored examples independent or establish unseen-atomic-type
generalization. Serial cache benchmarks and fail-closed acceptance follow these
controls; promotion is not inferred from the preliminary matrix alone.

The fresh reproduction completed successfully at implementation commit
`4453b46217319fdbf22ac1d344c20111758798af`. The verifier reconstructed all
236,414 evaluation row proofs, preserved all 1,366 protected historical files,
and established frozen native parity on all 16 suites. All 240 serial benchmark
samples passed full candidate/proof equality, with zero warm native invocations
and no truncation. Both registered candidates passed every behavioral gate with
zero lost prior supported decisions; the registered preference selected
`C8-promotion-relative` as the operational default. Its accepted model version is
`1217e17552ff611bebf0efc650245b05fb71c93a8175b579b025d6273d5d781d`.

The clean default API, CLI, batch-mode, inspector export and legacy C6/C7 smoke
checks passed. Production source remains byte-identical to the verified
implementation. Supplementary audits found no complete-board translation or
symmetry overlap across C8 partitions or with historical training positions.
Final browser evidence, reports and the artifact manifest are produced from the
delivery checkout; their helpers do not change production inference.

Final ProofShot verification passed with zero console and server errors. The real
form exercised the accepted default, all eight original promotion comparisons,
promotion evidence, strict abstention, zero-budget incompleteness, invalid-input
clearing and a 390-pixel viewport. Desktop, promotion-panel and mobile screenshots
were visually inspected. The actual browser export contains 3,848,153 bytes;
its browser-computed SHA-256 matches the preserved diagnostic JSON. Video, full
command receipts and server/browser logs are bundled with the clean evidence.

Two final-browser tooling failures are retained separately. The first functional
pass left ProofShot's detached HTTP server running; cleanup now verifies and
terminates the owned server group. The next pass detected a resize command that
had not changed the actual viewport; it failed the mobile assertion and still
closed the server. The final pass uses a fresh browser session, waits for the
measured viewport, and invalidates stale success receipts before running. Its
cleanup receipt confirms both ownership and a closed port. Exact earlier verifier
sources and failed-run evidence remain in the development directories.

After copying the clean output into `artifacts/cycle8`, a separate real CLI
default check passed without an external output override. Its full proof is in
`proofs/delivery-default.json.xz`, with `delivery-smoke.json` recording the command
and source/model binding. The original clean smoke artifacts are unchanged.
All fourteen packages are complete. The delivery commit contains the generated
reports, all evidence and the final manifest; no push or new native operator is
part of this cycle.
