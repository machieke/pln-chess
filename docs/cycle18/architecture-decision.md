# Architecture decision: B + D

**B:** executable, source-bound joint semantics are specified for a small set of
explicit hypothetical models, while a native bridge has unresolved obligations.
**D:** the intended empirical reliability meaning and observation/noise population
are not identified by this selected all-positive corpus. Existing information
supports point calculations only after supplying restricted assumptions (the
condition described by A). Cycle 18 does not claim C: it is not ready to propose
a sound probability-and-confidence native replacement for authorization.

The decisive new evidence is that the two conditional labels copy one evaluation
result. A faithful event identity contract can preserve this immediately. A
faithful empirically calibrated stochastic model cannot be recovered merely by
renaming the labels as separate observations, interpreting native confidence as
a posterior or assigning a joint law from source overlap.

The following is a **proposed, inactive** `shared-parameter-bridge-v1` interface.
No endpoint, native operator, inference clause or migration is activated.

| Operation | Required input/output contract |
| --- | --- |
| RegisterObservation | Immutable event/version, source groups, parent events, typed measured variables, method and admission. Return existing identity for identical replay; reject collision or require explicit supersession. Predictions are inadmissible. |
| EstimateParameters | Exact active event/component set, schema IDs, declared prior and group likelihoods, conflict policy, resource limits. Return a versioned joint-generation handle with full table or conservative identified set, original evidence IDs and computational receipt. |
| ApplyKnowledge | Existing generation handle, entity bindings, context/state/history and current environment references. Return an application identity; never append observations or multiply training likelihoods. |
| DeclareDependence | Versioned event/parameter sharing, within-group joint model and across-group factorization constraints. Missing declarations yield identified bounds or unresolved status. |
| EvaluateQuery | Explicit event/conditional definition q and information set, joint handle and context. Return separately typed probability/bounds/status plus assumption provenance. No automatic native `stv` conversion. |
| ResolveConflict | Named noise likelihood or explicit inconsistency; supersession requires a new event/version and full rebuild. No hidden epsilon or arbitrary winner. |
| RecordProof | Exposed native selections/retained statements plus parameter/event/application references. Fired parents remain unobserved unless a separately authorized trace mechanism provides them. |
| EnforceLimits | At most two parameters, 25 states, 100 groups, 2,500 group likelihood evaluations/fit, 16,384-bit rationals, 1,000 applications. Exhaustion returns incomplete, not unsupported/negative. |

A future bridge would need a **joint-parameter object** or an explicitly
constrained factorization, with retained events or sufficient statistics justified
for that exact model. It would need interval-valued support when only a feasible
set is known. The evidence identity of a reusable schema, its parameter generation,
an external observation and an application must remain distinct. It would need
a versioned admissibility/propagation policy for shared generations and current
environmental evidence. Ignoring rule stamps would specify none of these.

The bounded proposed representation is a table of `(theta_clear, theta_attack,
probability)` entries plus schema/model/evidence identities, or a finite coupling
constraint object with extremal witnesses. It must remain distinct from native
strength/confidence. A native extension cannot collapse this object into a scalar
TV until confidence semantics and compositional laws are established. Retaining
only counts is insufficient when two annotations share an observation, different
joint likelihoods are possible, or source groups require different models.

| Obligation | Demonstrated here | Still open before a native bridge |
| --- | --- | --- |
| Probability interpretation | Complete finite likelihood/prior/query semantics under named hypotheses | Empirical interpretation and population sampling/noise validation |
| Confidence interpretation | Explicitly separate and unresolved | Mapping and composition law compatible with native calculus |
| Duplicate evidence | Immutable replay, component identity and exact recomputation | Migration of all existing checkpoint/evidence conventions |
| Shared parameter reuse | Same generation applied repeatedly without posterior updates | Native propagation across arbitrary derivation patterns |
| Shared observation update | Actual copied labels counted once under copy semantics | Richer multi-event/multi-source joint measurement models |
| Cycles and diamonds | Bounded application journal preserves identity; native controls unchanged | General inference termination, cyclic semantics and complete proof provenance |
| Conflict/noise | Exact inconsistent state and explicitly separate noisy controls | Measured domain noise model and migration/conflict policy |
| Unknown dependence | Sharp bounds for fixed posterior marginals; explicit unresolved result otherwise | Conditioning with an incompletely specified prior/likelihood |
| Backward compatibility | Unchanged source/checkpoint/native replay and complete preservation gate | Separately versioned new-policy replay and old-policy migration |
| Resource growth | Enforced finite state/group/arithmetic/application bounds | General graph complexity and any approximate inference guarantees |
| Approximation | No approximation inside supplied finite grids | Continuous approximation error; grid sensitivity is not a guarantee |

The next justified experiment is a small **measurement contract**: name one
specific imperfect pipeline variable (for example independently audited
representation/annotation error), define the antecedent-qualified sampling frame,
record an independent outcome once per episode, and distinguish copied labels
from genuinely separate readings. Preregister the observation/noise and selection
model, including negative/error outcomes if they genuinely occur. Do not generate
negative conditional outcomes from blocked antecedents. Test joint update and
reuse on a finite known-generative control before considering a native bridge.

Only after that meaning is settled should a separate authorization request name
the exact native change, versioned joint representation, unchanged Cycle 12
baseline, probability/confidence semantics, resource bounds, replay/migration
plan and regression counterexamples: actual eleven-stamp witness, reciprocal
disjoint/shared arms, one-source overlap, duplicate delivery, copied annotations,
shared environment, diamonds, cycles, conflicts and unknown dependence. No such
native change is implemented during this cycle.
