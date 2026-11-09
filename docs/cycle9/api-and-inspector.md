# Cycle 9 interfaces

The accepted C8 checkpoint remains the default checkpoint. A matching Cycle 9 acceptance receipt authorizes its operational default under the optimized implementation. The receipt binds production source, runtime, registered configuration and model identity; missing or stale acceptance leaves the conservative strict default. Explicit operational, strict and experimental requests remain available.

```bash
.venv/bin/pln-chess research-report --section summary
.venv/bin/pln-chess research-report --section failures --output /tmp/c9-failures.json
.venv/bin/pln-chess calibration-export --output /tmp/c9-calibration.json
.venv/bin/pln-chess temporal-inspect-v9 --fen '6k1/8/8/8/8/8/8/4K2R w K - 0 1' --mode fen-only
.venv/bin/pln-chess serve --port 8765
```

Research sections are `summary`, `calibration`, `failures`, `performance`, `temporal` and `identity`. Their responses identify the recorded artifact and its SHA-256 hash. They describe the delivered study, rather than a newly executed evaluation. Set `C9_OUT` to inspect a separately reproduced output directory.

```python
from pln_chess.api import research_report, inspect_temporal_v9

study = research_report("summary")
history = inspect_temporal_v9(
    "6k1/8/8/8/8/8/8/4K2R w K - 0 1",
    mode="trusted-metadata",
    evidence={"source": "explicit-state-provider", "confidence": 0.8},
)
```

The temporal response retains the legacy receipt and adds `temporal-epistemics-v9` categories: supplied observed transitions, trusted metadata, inferred historical conditions, and unverified FEN metadata. A structurally consistent supplied transition does not certify that the historical move was legal. Event-backed input uses the existing `initial_fen`, `moves`, `source`, `confidence` and optional `castling_history_attested` fields; an attestation is a trusted claim, not an independently reconstructed event.

The inspector's research panel compares complete and in-board populations, opens representative failure traces with their rule and evidence IDs, loads recorded performance/runtime identity, and exports the displayed research JSON. “Inspect this position” loads the archived position and mode into the existing backend inference form. Native proof results and empirical diagnostics remain separately labeled.

The recorded trace is the exact evaluation evidence. Re-running one selected candidate can assign different native schedule-node ordinals from the original full-position request, so its graph hash need not match the archived full-position hash. Historical parity checks compare identical invocation contexts; they require exact hashes.

Live HTTP inspection adds `research_diagnostics` after backend inference. A calibrated estimate is available only for the matching model in operational mode, with an intact accepted calibration artifact and a non-incomplete inference. It reports its calibration-bin sample count, fitted cohort, dataset and model identity, `native: false`, and `changes_classification: false`. Zero-count bins are explicitly visible and do not establish empirical support. The underlying Python inference result and raw native TVs are unchanged by this presentation layer.

Local report endpoints are `GET /cycle9?section=summary` and `GET /cycle9-proof?index=0`; both select only fixed recorded paths or bounded archive indices. Desktop/mobile interactions, JSON export content hashes and server cleanup are recorded in the [browser verification receipt](../../artifacts/cycle9/ui-verification.json). Actual API and CLI output comparisons are in the [application smoke receipt](../../artifacts/cycle9/smoke/verified.json).
