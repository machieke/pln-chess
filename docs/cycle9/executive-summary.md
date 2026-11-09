# Cycle 9 executive summary

The accepted **C8-promotion-relative checkpoint is retained**. Cycle 9 adds immutable-state/serialization optimizations, a larger independent evaluation, offline calibration, typed temporal provenance, and inspector/CLI exports. No new operational model, threshold, native operator or production oracle was introduced. Isolated dependence ablations retain their experimental checkpoints separately.

The final game test comprises **100 complete synthetic games and 500 sampled nonterminal positions**, separate from 20 development and 20 calibration games. Independent-game recall is **99.992%**, with **499/500 exact legal sets**. The 128-position adversarial cohort has **112/128 exact sets**. Error and in-board counts are in the [engineering report](engineering-report.md); these finite synthetic cohorts do not establish universal correctness.

The historical 214-candidate workload changed from **4.770 → 4.008 seconds cold** and **3.463 → 2.748 seconds warm**. Proof payloads match exactly. Timing tails remain weak estimates from seven repetitions per arm. [Measured benchmark evidence](../../artifacts/cycle9/performance/C9-optimized.json).

2 of 2 developmental castling abstentions resolve when supplied full game events are reused; missing events, removed rights and temporal-channel removal remove support. Raw native TVs and thresholds stay unchanged. Positive support remains partial conditional evidence. [Experiment](../../artifacts/cycle9/abstention/summary.json).

Calibration is fit only on separate games and is displayed as an empirical diagnostic. Native confidence is not a probability of correctness. [Calibration findings](calibration-report.md).

**Architecture recommendation:** retain existing operators in production. A separately authorized, bounded credal prototype is justified as research; production activation is **no-go** until statistical, conditional-learning, solver and provenance obligations are met. [Decision](architecture-decision.md).

365 tests passed; 26 original baseline and 26 optimized historical evaluations passed; 287/287 negative controls preserved; 90,511 new and 81,944 historical row proofs reconstructed; 252 serial benchmark samples passed full candidate/proof identity checks. Fresh bootstrap and desktop/mobile browser verification passed. The delivery contains local commits only; no push or external deployment is authorized by this brief. [Verification](../../artifacts/cycle9/verification.json), [browser evidence](../../artifacts/cycle9/ui-verification.json).
