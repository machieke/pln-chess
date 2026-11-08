# Schema 8 interfaces and evidence contracts

`infer_moves`, `explain_move`, `analyze_batch`, model loading, the CLI and inspector
accept schema 8. Existing schemas remain loadable. `Cycle8Options` extends the
existing budgets and modes with an explicit promotion-training switch. Cache
sessions separate immutable source inference from bounded promotion projections;
retraction or model changes invalidate native scope keys.

A candidate carries the relative promotion transition, typed observation IDs,
selected promotion rule and grounded rule IDs, evidence IDs, dependence groups,
raw native STV, complete ordered native graph, host decision node, runtime/model
versions and budget. `evidence_state` distinguishes supported, contradicted,
unknown and incomplete. Classification and proof completeness are separate:
a positive learned conditional is useful operational evidence, not a complete
positive legality proof. A negative native chain can be complete for its stated
constraint. Unsupported joint composition is never labeled native-compositional.

`pln_chess.cycle8.api.compare_generations` is the single comparison contract used
by the CLI and browser. It executes C7-frozen, C7-learned-8, C8-promotion-relative,
and the accepted C8 checkpoint when new learning is promoted. Research checkpoint
names and inference modes are distinct: `--mode strict` runs each requested model
in strict mode. Comparison exports include full results, shared promotion
observations, raw-TV/classification differences, added/removed native node hashes
and evidence IDs. The UI contains no inference implementation.

```bash
.venv/bin/python -m pln_chess inspect --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2 --format json
.venv/bin/python -m pln_chess compare-generations --fen 'r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29' --move f7e8n
.venv/bin/python -m pln_chess serve --port 8765
```

The latest default path is `artifacts/cycle8/model/C8-default.json`, or the same
relative path below `C8_OUT`. It uses operational mode only when the acceptance
receipt matches source, runtime, registrations, model version and every required
check. Missing or stale receipts fail closed to strict. The C8 receipt also
attests preserved C6/C7 default versions without editing their historical
receipts; explicit `C6_OUT`/`C7_OUT` overrides retain isolation. An experimental
checkpoint can be requested explicitly in operational mode without being
accepted as the default.

Machine-readable API/CLI/inspector smoke results are in
[`default-smoke.json`](../../artifacts/cycle8/default-smoke.json); full exported
proofs are in [`proofs/default-api-cli-inspector.json.xz`](../../artifacts/cycle8/proofs/default-api-cli-inspector.json.xz).
Browser verification additionally exercises the actual form, comparison table,
export button, incomplete results and mobile overflow. Its video, screenshots,
server log and error report are linked from the final engineering report.
