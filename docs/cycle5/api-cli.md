# API and CLI reference

Existing schema 1–4 APIs and checkpoint imports remain compatible. Schema 5 uses `PremiseModel`, `Cycle5Options` and a two-stage `Session`; the public `infer_moves` and `explain_move` functions dispatch by checkpoint schema. Pass temporal mode/evidence in `Cycle5Options`, or supply `temporal_evidence` to `explain_move`. Batch requests may specify `temporal_mode` and `temporal_evidence` per request; the existing 64-request bound remains.

```bash
.venv/bin/pln-chess inspect --checkpoint artifacts/cycle5/model/C5-full.json --fen '2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1' --move f6h5
.venv/bin/pln-chess compare-models --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/pln-chess counterfactual --checkpoint artifacts/cycle5/model/C5-full.json --fen 'k3r3/8/8/8/8/4R3/8/4K3 w - - 0 1' --move e3f3 --family exposure
.venv/bin/pln-chess temporal-inspect --fen '7k/8/8/1pP5/8/8/8/2K5 w - b6 0 1' --mode trusted-metadata --history metadata.json
.venv/bin/pln-chess composition-audit
.venv/bin/pln-chess evaluate --checkpoint artifacts/cycle5/model/C5-full.json --split combination-holdout --variant C5-abstract-only
.venv/bin/pln-chess serve --checkpoint artifacts/cycle5/model/C5-full.json
```

`metadata.json` is caller-supplied, for example `{"source":"external-observer","confidence":0.8}`. Event-backed input additionally includes `initial_fen`, an ordered `moves` list and optional independently justified `castling_history_attested`. No history is inferred from missing fields. `--max-invocations 0` exercises the incomplete-budget contract.

Diagnostic candidates expose typed premise TVs, sources, dependence groups, rule hierarchy, pre/post relative frames, local legacy projection, positive proof plan, gaps, temporal receipt, negative witnesses and complete native traces. `proof_dag_refs` indexes the result-level DAG. Production API/UI inference does not import the reference engine; only explicitly selected training/evaluation/audit commands enter research modules.

The inspector provides C4/C5 comparison, history trust selection, JSON evidence, proof budgets, diagnostic export and mobile layout. Invalid inputs clear stale results and exports. Runtime errors fail explicitly; incomplete work has its own status.
