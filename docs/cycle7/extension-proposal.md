# Capability boundary and proposed extension — not implemented

The pinned rule set eliminates supplied implications, revises evidence, and chooses among alternatives. Typed predicate inheritance is source-present, but both the exact typed transfer probe and its aligned-type control returned empty in the pinned runtime. The bounded laboratory tests whether these mechanisms supply a joint eligibility proposition from independently learned geometry and destination premises. Neither a supplied curried eligibility axiom nor a host-constructed joint sensor establishes that capability. The executable witnesses and source definitions are retained in `artifacts/cycle7/native/`.

The missing capability is **joint introduction with an explicit dependence model**, followed by a separately justified eligibility implication. Even an adequate joint introduction operator would not prove universal king safety, learn chess's rules automatically, or justify the implication from that joint proposition to global legality. Those are distinct obligations.

## Proposed types and semantics

This is a specification for discussion, not an enabled PLN rule or a request to import an experimental formula. Existing scalar STVs alone are insufficient to identify joint probability or dependence.

```text
EvidenceStamp := finite set of immutable evidence IDs and ancestor groups
Prop[X]      := typed proposition about the same candidate/environment X
Posterior[P] := probability measure over P's population frequency in [0,1]
Belief[P]    := (P, Posterior[P], EvidenceStamp, population, scope)
Dependency   := certified factorization assumptions OR supplied joint posterior

JointIntroduction:
  Belief[A(X)] × Belief[B(X)] × Dependency(A,B)
  -> Belief[And(A(X),B(X))] | InsufficientDependenceEvidence
```

For the independent case, require **both** conditional independence of the events within the named population and epistemic independence of their estimated frequencies. Disjoint evidence stamps alone prove neither. If frequency random variables are U and V, the output posterior is the pushforward of the joint posterior of (U,V) under `(u,v) -> u*v`. The independent posterior is the product measure only when explicitly justified. This defines the complete uncertainty distribution rather than inventing a scalar-confidence product. A dependent case requires an independently justified joint model, or returns insufficient evidence. Identical propositions use identity, not independence: `And(A,A)=A` with unchanged evidence and uncertainty.

For scalar inputs without an approved dependence model, only the Fréchet interval `[max(0,sA+sB-1), min(sA,sB)]` is justified for fixed marginal frequencies. Uncertain marginal distributions require propagation of those bounds over the joint posterior. These are mathematical constraints for a proposed richer truth domain, **not computed by production code**. STV confidence cannot be uniquely recovered from these inputs. An upstream extension must specify and validate a distribution-to-STV projection before compatibility with current acceptance thresholds can be claimed. Until then the output is typed as a distribution/bound, never `(stv s c)`, and the current classifier must return unknown for it.

The output evidence stamp is the set union of input stamps, with a derivation DAG containing both parents, the dependence certificate, population and scope. Shared ancestors prevent an independence certificate from being accepted by default. Any correlation model must be separately sourced and must account for those ancestors. Duplicating an input or reordering a stamp must not increase confidence.

## Required properties and counterexamples

| Property | Required check |
|---|---|
| Commutativity | Reorder A/B and obtain an equivalent posterior, canonical proposition and evidence set. |
| Idempotence | Duplicate A returns A, without increased evidence weight. |
| Bounds | Joint support never exceeds either marginal support; Fréchet bounds hold. |
| Missing evidence | Missing/zero-confidence premise cannot produce a supported new joint conclusion. |
| Certain inputs | Certain true A acts as an identity only with compatible population/scope; certain false A makes the conjunction false. |
| Uncertainty | A scalar confidence of one is not silently treated as infinite revision weight; native revision's undefined endpoint remains distinct. |
| Monotonicity | Under the certified independence model, increasing one fixed marginal strength increases joint strength. No monotonic-confidence claim under contradictory new evidence. |
| Correlation | Perfectly correlated `.8` events have joint `.8`, while independent `.8` events have joint `.64`; the marginals alone cannot choose between them. |
| Contradiction | Positive and negative evidence retain distinct sources; no hidden maximum-confidence choice removes a contradiction. |
| Context | Matching candidate, population, time and orientation are required. Mixing unrelated candidates cannot introduce a move-specific conjunction. |

Proposed native pseudocode (deliberately **non-executable**):

```text
JointIntroduction(Belief(A, qA, stampA, ctx), Belief(B, qB, stampB, ctx), certificate):
    require certificate validates event AND posterior dependence for ctx
    if A == B: return same belief with canonical union of identical lineage
    qAB := PushForward(certificate.joint(qA, qB), Product)
    return Belief(And(A,B), qAB, Union(stampA,stampB), ctx)

EligibleElimination(jointBelief, separatelySupportedEligibilityImplication):
    require approved native semantics for this truth domain and rule
    return native conditional consequence with both derivations retained
```

This is an **introduction rule**, not unary implication chaining. The second step is elimination. Conditionalizing marginal observations into an eligibility rule is a third capability; neither pseudocode step invents that rule from the desired answer.

Required tests include the held-out knight capture with independently learned A/B, individual premise deletion, reversed arguments, contradictory occupancy, shared evidence, adversarially forged ancestry, zero/one-confidence inputs, mismatched candidate contexts, and absent safety evidence. Rook/pawn composition proceeds only after the primary gate passes. No proposed result may be called a global legal-move theorem without the safety and temporal premises it requires.

## Risks, cost and migration

The main soundness risks are invented independence, forged provenance, a supplied target implication disguised as learning, unsound scalar compression, and absence-of-attack mistaken for safety. Validate types and lineage before inference; preserve raw distributions and assumptions in the proof. Resource limits must bound expression depth, stamp size and mixture expansion. An exact joint distribution may grow exponentially with premise count; a two-premise grid representation costs O(n*m), with any approximation error recorded. Canonical DAG storage reduces repeated serialization, not statistical dependence.

An upstream change would require a new runtime lock, operator signature audit, checkpoint/proof schema, replayed evidence, acceptance receipt, clean bootstrap and full frozen suites. Existing models remain available. No current cache key or STV classifier may interpret the new truth type implicitly.

| Alternative | Constraint compatibility | Estimated engineering effort after authorization |
|---|---|---|
| A. Current pinned PLN | Fully respects the existing native-only constraint; useful partial positives, conservative strict abstention. | 2–5 engineering days for another bounded data/diagnostic iteration; no promised composition breakthrough. |
| B. Upstream extension proposal | Preserves native execution as the destination, but changes the allowed pinned calculus only after separate approval and review. | 2–4 days to prepare/review an upstream issue and executable proposed tests; roughly 2–6 weeks for a prototype and revalidation, excluding upstream review. |
| C. Separately named experimental calculus | Requires relaxing the existing constraint; must never be presented as the current native PLN. | Roughly 1–3 weeks for an isolated prototype and soundness evaluation; production migration is additional. |

The smallest authorization is permission to submit the specification and tests for upstream discussion, without permission to merge a new rule or change production. This package does not submit anything externally and does not presume that authorization.
