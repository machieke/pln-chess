# Cycle 9 composition review

**Production extension: no-go. A separately authorized, isolated research prototype is technically justified, but neither a production operator nor an STV adapter is ready.** The accepted operational learner should continue with the pinned operators.

The reviewed specification is the [complete Cycle 8 proposal](../cycle8/native-composition-proposal.md), including its [mathematical argument](../cycle8/mathematical-validation.md). The [review receipt](../../artifacts/cycle9/composition/review.json) binds their hashes to the unchanged native library and adds three exact counterexamples. It does not rerun exhausted nested-implication experiments or implement an operator. Previous native behavior remains inspectable in the [C7 inventory](../../artifacts/cycle7/native/inventory.json) and [C8 laboratory](../../artifacts/cycle8/composition/laboratory.json).

| Review question | Finding |
|---|---|
| Logical syntax | Typed formulas, shared variable scope, canonical conjunction and explicit failure types are sufficient for a small formal core. Grounding/unification and quantification beyond a finite named population still need a contract. |
| Strength semantics | A finite probability constraint set defines sound lower/upper bounds, conditional on valid inputs. It cannot infer joint probabilities from marginal STVs. |
| Confidence semantics | Certificate coverage is distinct from native STV confidence and outcome frequency. No justified mapping from existing native confidence to an error budget exists. |
| Independence | Distinct records, independent acquisition, and independent events are different properties. The proposal correctly requires a scoped assumption/certificate; validating it remains unresolved. |
| Dependence and overlap | Retain all original constraints, source identities and ancestry. Intervals alone lose dependence needed by subsequent steps. |
| Contradiction | An empty feasible set is an inconsistency, not a zero-probability event. Contradictory noisy observations need an explicit estimator before they become constraints. |
| Revision | Native `Truth_Revision` combines scalar STVs. Constraint intersection, observation aggregation and source replacement are different operations and cannot share an unqualified name. |
| Deduction and modus ponens | Existing elimination rules require supplied links. They do not learn the missing conditional from a conjunction to legality. |
| Induction | Existing native guards and marginal assumptions do not establish sampling coverage or a joint-event relation. The proposed type must reject implicit STV coercion. |
| Negation | Credal complement reverses interval endpoints while retaining the full constraint model; native strength complementation alone cannot retain that model. |
| Runtime integration | A finite three-atom, rational constraint system is computationally implementable in principle. A tested solver, outward rounding or exact certificates, resource limits, and typed dispatch are still absent. No measured runtime-performance claim is made. |
| Isolation | Separate namespace/type, no production imports, no default model path, and no STV conversion can isolate a prototype. It must have its own acceptance process. |
| Upstream discussion | Suitable as a design question with explicit unresolved obligations. It is not ready as a claim of compatibility or a merge-ready operator. No upstream message was sent. |

The pinned source contains a consistency helper named `Consistency_ImplicationImplicantConjunction`; its name must not be confused with a proven general conjunction-introduction operator. Its actual signatures and the previously executed native probes govern capability claims. The library hash is checked against the runtime lock in the review receipt.

The new exact checks make three obligations concrete. First, two distributions can have identical `P(A and B)=1/2` and `P(C)=1/2` but triple intersections of zero and one half. Caching only the intermediate interval loses necessary information. Second, replacing a premise differs from intersecting it: with `P(C|A)=1/5` and `P(C|not A)=9/10`, replacing `P(A)=1` with zero changes the projected result from `1/5` to `9/10`; retaining both premises makes the constraints inconsistent. Third, twenty disjoint certificate-failure events of probability `1/20` each leave zero simultaneous coverage, despite every premise individually having 95% coverage. These are mathematical counterexamples, not chess benchmark measurements.

The finite formal semantics are sufficiently specified for review. The statistical front end, conditional learning, transport between populations, source-integrity/retraction protocol, and native proof-certificate implementation are not sufficiently specified for activation. Empirical calibration of the operational classifier cannot discharge those obligations: it estimates cohort frequencies and does not certify all premises of a future composition proof.
