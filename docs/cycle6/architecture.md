# Cycle 6 architecture

C6 is a lossless schema-5 model wrapper. It retains the frozen C4 source model and C5 conditionals; it adds no chess rule, native operator, conjunction, host TV formula, or oracle dependency. Policy `evidence-channels-v6.1` separates evidence from acceptance.

`operational` accepts C4's learned local positive projection as **native-partial / evidence-supported**. Its proof status is `native-conditional`, never `native-composed`. C4 negatives and independent C5 negative chains remain `supported-illegal`. `strict` and `experimental` abstain on unsupported positives; experimental findings never promote themselves. An incomplete native run stays `incomplete`.

`raw_stv` and the compatibility field `legal_move_truth_value` expose the same selected diagnostic channel in every C6 mode. Both C4 and C5 raw channels remain in `evidence_channels`; an unknown strict result can have a high-strength local STV. This is an explicit change from C5's global UNKNOWN sentinel, preserved separately in `evidence_channels.C5.truth_value`. Strength and confidence are distinct, uncalibrated quantities. `legacy_classification` maps public labels to earlier metric vocabulary.

A supported C4 global projection opposed by a C5 negative chain abstains. Strong negative premises whose bridge is blocked by overlapping or conflicting evidence also abstain. Both channels, dependence groups, node IDs and host decision rationale remain inspectable. The policy never chooses the highest confidence across opposing scopes. Local partial support alone does not contradict an already-established C4 negative chain.

The source call graph is `api.explain_move → inference.infer_moves → cycle6.inference → cycle5.inference → cycle4.inference → NativeSession → Runtime.batch → pinned PeTTa/PLN`. In C5, the final acceptance branch in `cycle5/inference.py` preserves a negative witness and otherwise assigns unknown because `proof_plan.positive_proof_complete` is false. C6 retains that result and exposes C4's pre-gate projection; it does not pretend the absent conjunction was implemented.

The default is `operational`. A promotion receipt must pass every required check and match the model, runtime, policy, production-source hash and preregistration hash. Missing/stale/failed receipts default to strict. Explicit operational requests remain available for research.

Cache scopes include runtime manifest, model, mode, proof policy, observation/event versions, all budget/threshold/history settings, then position and evidence identities in the underlying source sessions. Changing mode clears both source caches. Ordered interned native nodes reconstruct full proofs losslessly; host acceptance nodes are separately labeled non-native.

Migration: `pln-chess migrate-model --checkpoint artifacts/cycle5/model/C5-full.json --output /tmp/c6.json`. Exported C6 models embed the complete source, validate schema and runtime, and preserve the C5 semantic model hash. Old schemas remain readable with their original behavior.

| Case | Move | Operational / strict / experimental | Operational decision |
|---|---|---|---|
| rook-obstruction | `c2h2` | supported-illegal / supported-illegal / supported-illegal | native-negative-chain |
| king-into-attack | `c2d3` | supported-illegal / supported-illegal / supported-illegal | native-negative-chain |
| unresolved-knight | `f6h5` | unknown / unknown / unknown | insufficient-evidence |
| unverified-castle | `e1g1` | unknown / unknown / unknown | insufficient-evidence |
| operational-positive | `c2e2` | supported-legal / unknown / unknown | C4-learned-conditional-projection |
| contradictory-evidence | `c2e2` | unknown / unknown / unknown | opposing-global-channels; no defensible native dependency-aware choice |

These executed examples retain exact FENs, raw STVs, evidence groups and complete traces in `artifacts/cycle6/proofs/examples.json.xz`. The rook and king cases use negative obstruction/exposure chains. The knight `f6h5` lacks the required positive combination; unverified castling metadata supplies no historical theorem. The contradiction case is an isolated synthetic model with separately learned opposing ray evidence, never the production checkpoint. Every mode's raw diagnostic channel is preserved; acceptance policy alone distinguishes operational positives from strict/experimental abstention. A separate zero-budget example stays incomplete in all three modes.
