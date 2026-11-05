# Local inspector verification

The inspector was exercised using the installed ProofShot skill and a real headless Chromium browser on 2026-11-05. The final recording and nine screenshots are in [the ProofShot report](../proofshot-artifacts/2026-11-05_10-38-37_verified-final-board-layout-clear-blocke/SUMMARY.md); [the interactive recording viewer](../proofshot-artifacts/2026-11-05_10-38-37_verified-final-board-layout-clear-blocke/viewer.html) keeps the evidence together.

Verified interactions:

- Clear rook: supported, native strength `0.975`, confidence `0.495`.
- Blocked and pinned rook: contradicted, strength `0.025`, confidence `0.495`.
- Empty move field: all 38 bounded candidates displayed, 464 native invocations, no truncation.
- Recorded learning comparison: initial prior, first evidence, idempotent replay, excluded correlated contradiction, independent contradiction; native values displayed from generated artifacts.
- Translation comparison: identical native TVs/rules and isomorphic proof graphs for c3e3 → d3f3 in the controlled translated fixture.
- Invalid FEN: actionable validation message and cleared stale proof/board. The HTTP 400 is the expected validation response.
- Mobile viewport 390 × 844: 64 equal board cells, no horizontal overflow; proof/details remain accessible.

Visual inspection found and fixed unequal implicit grid rows before the final recording. The final ProofShot bundle reports zero console errors and zero server errors. An initial shared browser session timed out; a separate named browser session completed verification. The local server and browser were stopped after capture.

Browser checks are manual agent-driven verification, separate from the automated Python suite. Bootstrap rebuilds the model and test artifacts; it does not claim to rerun this browser recording.
