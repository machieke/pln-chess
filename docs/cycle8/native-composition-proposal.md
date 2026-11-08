# Proposed native composition contract — not enabled

The missing capability is a typed introduction of a joint proposition with a defensible dependence model. A separate, evidenced relation from that joint proposition to the requested conclusion is still required. Neither capability follows from independently learned marginal conditionals. This proposal is independent of chess and does not register a MeTTa operator or change native production arithmetic.

## Semantic boundary

Five different operations must remain separate:

| Operation | Object being combined | Required information |
|---|---|---|
| Logical conjunction | Events/formulas | Shared variables and population; logical identity/contradiction |
| Probabilistic dependence | Joint event distribution | Joint observations, constraints or explicit factorization assumptions |
| Conditional implication | Relation of a joint event to another event | Conditional constraints or a logical axiom with its own provenance |
| Evidence aggregation | Observational records | Sampling units, overlaps, conflicts and revision policy |
| Confidence estimation | Reliability of assessments | A justified sampling/calibration contract, not just disjoint filenames |

Current `(stv s c)` values do not uniquely specify any of these joint distributions. Strength is not automatically a calibrated population frequency; native confidence is not automatically a coverage probability. No implicit conversion is permitted. The default lift from an uncalibrated STV is an uninformative probability constraint, with the original STV preserved as metadata. The operational classifier cannot consume the proposed type.

## Proposed types

```text
Atom := (predicate, typed variable bindings, environment scope)
Formula := Atom | Not(Formula) | And(finite set of Formula)
Scope := (population identifier, sampling unit, time/context, transport assumptions)
Constraint := (immutable ID, rational linear probability bounds, source IDs)
CoverageCertificate := (ID, alpha in [0,1] | unknown, sampling/calibration contract)
Evidence := (observation IDs, ancestor groups, source digests, acquisition order)
CredalBelief := (Formula, Scope, ConstraintSet, Evidence, Certificates, DerivationDAG)
CredalResult := (Formula, [lower,upper], validity_coverage | unknown,
                 retained ConstraintSet, Evidence, DerivationDAG, proof_status)
Failure := ScopeMismatch | InconsistentConstraints | MissingConditional |
           UnsupportedAssumption | IncompleteBudget
```

For a finite atom universe of size `n`, let `w` range over its `2^n` Boolean assignments. The admissible set `K` consists of distributions `p_w >= 0`, `sum p_w = 1`, satisfying the supplied constraints and logical identities. An event probability is the sum of masses of satisfying worlds. The output bounds are the infimum and supremum of this sum over `K`. An empty `K` is an explicit inconsistency; never normalize an inconsistent set or silently average it. A timeout returns incomplete, never a narrower interval.

An implementation must preserve the full constraint set or a sound equivalent factorization. An interval alone is insufficient to retain dependence for later deductions. Symbol identity is semantic: `And(A,A)` is `A`; `And(A,Not(A))` is false. Normalized conjunctions flatten and sort children and remove duplicate formulas. This normalization must not equate differently scoped observations.

## Introduction and elimination

```text
JointIntroduce(Belief(A,X), Belief(B,X), optional DependenceCertificate)
    -> Belief(And(A,B), X) | Failure

ConditionalProject(Belief(J,X), Conditional(C | J,X),
                   optional Conditional(C | Not(J),X))
    -> Belief(C,X) | Failure
```

`JointIntroduce` is an introduction rule. `ConditionalProject` propagates an independently justified conditional; it does not learn one from marginal facts. In a future native implementation, both return a new truth-value type, never an ordinary STV disguised by a new label.

For exact marginal probabilities `a,b` without dependence information, the sharp conjunction interval is

`[max(0,a+b-1), min(a,b)]`.

For marginal intervals `[aL,aU]`, `[bL,bU]`, it is

`[max(0,aL+bL-1), min(aU,bU)]`

when there are no additional logical or joint constraints. Identity and contradiction are resolved before this generic case. A joint constraint may tighten the result. A valid factorization certificate may restrict the joint to a product, but must explicitly establish event independence in the named population. Distinct evidence groups, independent parameter-estimation errors, and event independence are three different statements. A signed assumption records responsibility; it is not empirical proof.

If `q=P(J)`, `r=P(C|J)`, and `t=P(C|Not(J))`, then `P(C)=qr+(1-q)t`. With rectangular bounds and no further dependence constraints, minimize/maximize this multilinear expression over the eight corners. Without `t`, use `[0,1]`, not an invented default conditional. Without any relation to `C`, its bounds remain `[0,1]`. Conditional constraints are expressed as `rL P(J) <= P(C and J) <= rU P(J)`; if `P(J)=0`, they impose no restriction on the otherwise undefined conditional ratio. Reject requests to interpret such a ratio as an observed conditional frequency.

## Strength and confidence

The proposed strength is an interval over event probability. It is not a scalar confidence-weighted product. Conditional on a fixed nonempty `K`, the optimization bounds are deterministic mathematical consequences of its constraints.

Reliability of the constraints is separate. A certificate may assert that a population constraint is valid with coverage at least `1-alpha`, under a stated sampling/calibration design. For unique certificates the conservative simultaneous guarantee is `max(0,1-sum alpha)`. This union bound requires no independence between certification failures. Reusing the same certificate adds no new error budget. Unknown or absent calibration yields **unknown coverage**, not zero-confidence probabilistic certainty. Logical axioms may carry zero error only within their explicit formal model; empirically estimated premises cannot claim this by convention.

This is not current native STV confidence. There is no approved projection to `(stv s c)`, and no inherited operational threshold. Estimating certificates from learned chess evidence remains an unresolved obligation. In particular, treating `c` as a frequentist confidence level, treating `1-c` as alpha, or counting repeated transforms as independent samples is prohibited.

## Provenance and revision

Every derivation retains premise IDs, constraint IDs, evidence IDs, ancestor groups, scope, native runtime hash, model/specification version, exact/rational values, derivation order, budget and result status. Derived conclusions cannot be resubmitted as independent observations. Duplicate IDs with different payload hashes are rejected. Removing a record requires reconstructing the constraint set from retained sources; it cannot merely subtract a scalar confidence.

Revision is a separate, explicit operation. Compatible hard constraints intersect; conflicting hard constraints yield `InconsistentConstraints`. Noisy observational disagreement is not itself a logical contradiction: positive and negative samples belong to a declared sampling model. An approved estimator may convert those samples into a new certified constraint. This proposal does not invent that estimator or reinterpret native `Truth_Revision` as constraint intersection. Combining a native STV and a credal result is a type error until a separately reviewed adapter exists.

The native confidence-selection operator selects alternatives. It cannot merge their evidence or establish joint dependence. Selecting the narrowest interval would likewise be unsound unless the selection policy accounts for validity and provenance; no such policy is enabled here.

## Existing native operators

The pinned PLN source remains `vendor/pln/lib_pln.metta`, commit `4405956947c4b53c7ff01bd565aa3b114bc970a1`. The [C7 inventory](../../artifacts/cycle7/native/inventory.json) records exact signatures and execution results; the [C8 laboratory](../../artifacts/cycle8/composition/laboratory.json) reexecutes selected controls.

| Existing mechanism | Relation to this proposal |
|---|---|
| Modus ponens | Eliminates a supplied conditional; does not introduce its joint antecedent or learn its relationship to the target. |
| Deduction | Combines supplied links under native guards; does not recover arbitrary joint dependence from marginals. |
| Induction | Uses supplied marginal/link values with native assumptions; not a certificate of the missing joint relation. |
| Revision | Combines STVs; native arithmetic alone does not detect duplicated evidence. |
| Negation | Complements the native strength; a credal complement would reverse endpoints while retaining constraints. |
| Inheritance | Typed/unary transfer is distinct from intersecting independent concepts. Some pinned predicate probes return empty. |
| Evidence selection | Chooses a candidate by confidence; neither conjunction nor evidence aggregation. |

## Native implementation sketch and budgets

This pseudocode is a review artifact, not loadable production MeTTa:

```text
proposed JointIntroduce(left, right, certificate, budget):
    require compatible scopes and immutable source payloads
    normalize formula And(left.formula, right.formula)
    union original constraints and deduplicate original evidence
    validate optional dependence certificate against scopes and ancestry
    solve feasibility of the retained probability constraints
    if infeasible: return InconsistentConstraints with conflicting IDs
    if budget exhausted: return IncompleteBudget with unexplored work
    solve lower and upper event-probability objectives
    attach solver certificate, union coverage bound, both parent DAGs
    return proposed truth type; never coerce to native STV
```

The first implementation should support at most three atoms, rational linear constraints, and no unconstrained graph-wide inference. General finite-world construction is exponential in `n`; linear programs are polynomial in their explicit size, not in the symbolic atom count. Factorization introduces additional requirements and can make constraints nonlinear. A product shortcut is safe only for a declared, validated scope; it cannot silently expand to three atoms from pairwise independence.

Cache keys must include canonical formulas, complete constraints, evidence/source versions, scope, dependence certificates, solver version and budget. Cache hits must reproduce proof certificates, not just endpoints. Retraction invalidates all dependent conclusions. Resource limits must cap atoms, constraints, rational bit length, solver steps, wall time and proof bytes. Malformed IDs, contradictory certificates and cyclic derived-evidence reuse are rejected before inference.

## Approval boundary and implementation checklist

No native extension is authorized by this document. A future authorization would permit an isolated implementation of the richer type and solver, upstream review, exact native witnesses, oracle-independent property tests, provenance attacks, cache/retraction tests and a versioned API migration. Production enablement would remain a separate decision after confidence calibration, conditional-learning and scope-transport obligations are satisfied. Existing schema-7/8 checkpoints and operational behavior must remain replayable.

The design uses standard finite probability constraints. Related primary research studies coherence and Fréchet bounds for compound conditionals, including counterexamples to naive conjunction assignments; its conditional-event formalism is not silently treated as identical to this proposal. See [Gilio and Sanfilippo, 2021](https://arxiv.org/abs/2010.14382). The derivations and finite tests below are our own specification checks, not a claim that this paper validates a PLN extension.
