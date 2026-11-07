# Structural-family analysis supplement

[structural-metrics.json](../../artifacts/cycle7/structural-metrics.json) groups every completed C7 matrix, learning-curve, and ablation report by structural motif. Opening-family metrics (`sicilian`, `french`, and the earlier fixture families) remain separate in the original reports.

The overlapping motifs include boundary, empty/friendly/opponent destination, opponent-king destination, capture structure, clear/obstructed slider ray, promotion, self-check, and history-sensitive moves. Recorded evaluation tags supply promotion, self-check, and history categories. A small FEN occupancy reader supplies destination and ray categories. These categories describe the observed configuration; they are never a production legality gate or a new proof claim. No inference, training, or oracle query runs in this supplement.

Each group reports its legal-candidate denominator, precision, recall, F1, abstention, unknowns, incomplete results, false legal, false illegal, and self-check false legal counts. Groups overlap and must not be added together. Exact whole-position sets and paired game-cluster intervals remain in the original evaluation and paired reports, where their denominator is well-defined. Learning curves are available under the `C7-learned-0/2/4/8` result keys, preserving independent-game evidence budgets.

The aggregation checks its all-candidate metrics against every stored report before writing a passing receipt. It records each input archive's SHA-256 and its own script hash. This is a report-only supplement to the clean-reproduced implementation at `0eab14ca5dd6926549d9772dc73d9cfd668de526`; production source, models, data, thresholds, and native traces remain unchanged.

After the main reproduction, run this script from the **final delivery checkout**, pointing it at the generated output directory:

```bash
python3 scripts/cycle7_structural_metrics.py --out /data/pln-chess-cycle7-output
```

The script uses only Python's standard library. It can also be invoked by absolute path from a separate checkout of the verified implementation. `--arm C7-frozen` is a limited diagnostic; omit it to generate the complete supplement.

## Exact ablation scopes

| Recorded arm | Removed capability; retained evidence |
|---|---|
| `no-backoff` | Removes coarse levels 1 and 2. Newly learned exact conditionals remain available. |
| `no-attack-exposure` | Removes learned attack/exposure reasoning; local conditional predictions remain. |
| `no-temporal` | Supplies no history and uses FEN-only trust. This is a null control on game inputs that already lack history; the separate temporal suite supplies history interventions. |
| `no-dependence` | Disables per-group training deduplication and runtime overlap guards. True evidence and ancestor IDs remain visible. |
| `no-learned-negatives` | Removes learned negative constraint families and every illegality bridge, including `LocalFailure-to-NotLegal`. Marginal counterevidence in local conditionals remains. This ablates negative proof paths; it does not retrain all models from positive-only examples. |
| `no-new-training` | Uses zero new game groups while still pooling historical evidence into the registered relative levels. The separate frozen arm adds no pooled hypotheses. |
| Independent-premise removal | Runs in the isolated native laboratory, with both direct native expressions and native dependency-stamp queries. |

All ablations are diagnostic and are excluded from this cycle's preregistered default selection. The exact-only result motivates a future prospective test, not post-hoc promotion on the observed holdout.
