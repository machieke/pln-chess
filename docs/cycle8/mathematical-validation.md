# Mathematical validation and explicit limitations

The [isolated reference laboratory](../../evaluation/cycle8_composition_lab.py) uses exact rational arithmetic. It is outside production inference and returns probability bounds with `native: false`. Its [results](../../artifacts/cycle8/composition/mathematical-validation.json) must be generated, not inferred from these arguments.

## Bounds, normalization and sharpness

Write `x=P(A and B)`, `a=P(A)`, `b=P(B)`. The four cell masses are

`p00=1-a-b+x`, `p01=b-x`, `p10=a-x`, `p11=x`.

They sum to one. Requiring each to be nonnegative gives `max(0,a+b-1)<=x<=min(a,b)`. Conversely every `x` in this interval constructs a valid table with the specified marginals; the bounds are sharp. For marginal intervals, minimize the lower endpoint using both lower marginals and maximize the upper endpoint using both upper marginals. The same construction attains the endpoints. Additional logical constraints may narrow them; ignoring such constraints remains conservative but loses precision.

The finite check constructs both extreme tables for 441 exact marginal pairs on a twentieths grid, verifies normalization and marginal recovery, and checks 225 pairs of intervals on a quarters grid. These checks catch implementation errors; the algebra above supplies the general two-event argument.

## Why products fail without assumptions

For `P(A)=P(B)=4/5`, admissible intersections range from `3/5` to `4/5`. Independence gives `16/25`, which is one possible answer, not a determined answer. If `A=B`, the answer is `4/5`; if `B=Not(A)` and both marginals are `1/2`, the intersection is zero, not `1/4`. Distinct acquisition files do not rule out either dependence structure.

Pairwise independence also does not imply mutual independence. Assign mass `1/4` to each of `000,011,101,110`: all marginals are `1/2`, all pairwise intersections `1/4`, yet `P(111)=0`. Assign instead mass `1/4` to `001,010,100,111`; the same marginals and pairwise intersections give `P(111)=1/4`. Multiplying three marginals produces `1/8`, which neither table attains. The laboratory verifies both exact tables.

## Consequents are not introduced by conjunction

Even if `P(J)=1/2` and a logical implication makes `P(C|J)=1`, `P(C)` can be anywhere in `[1/2,1]`: it depends on the complement of `J`. Reporting `P(C)=1/2` silently assumes `C` never occurs outside `J`. Without any relation between `J` and `C`, the conclusion is completely unconstrained. With both conditional constraints, the total-probability expression `qr+(1-q)t` is affine in each variable separately, so extrema over a rectangular domain occur at its corners. A more constrained joint model must be optimized as a whole; independently mixing incompatible extrema is forbidden.

## Unknown evidence and confidence

An unknown marginal has interval `[0,1]`. Combined with known `P(A)=4/5`, an unconstrained conjunction has `[0,4/5]`; absence of evidence does not justify a positive point estimate. An uncalibrated native STV cannot be converted to a sharp interval simply by retaining its strength. In the chess laboratory, original native premise TVs are retained, but the proposed conclusion remains unknown.

Confidence certificates quantify coverage of the input constraints, not the truth frequency of the conclusion. The union bound follows from `P(any certificate fails)<=sum P(certificate fails)`. It requires no independence, but each individual coverage claim must itself be justified. If the same certificate is used twice, the failure event is unchanged: it must be counted once. Unknown coverage remains unknown. The tested two-certificate example with alpha `1/20` and `1/10` yields at least `17/20` simultaneous coverage; duplicating the first alone leaves `19/20` unchanged.

Native `Truth_Revision(A,A)` can increase its native confidence when invoked without an overlap guard. The C8 native transcript records that behavior. This is a counterexample to treating native revision as automatically duplication-safe; it does not invalidate its arithmetic under its intended evidence assumptions. A credal adapter must preserve identity and cannot use that unguarded result as a new independent constraint.

## Contradiction, revision and ordering

The event `A and Not(A)` has probability zero. In contrast, assessments `P(A)>=4/5` and `P(A)<=1/5` describe an empty admissible set and must return an inconsistency status. They are not interchangeable with zero probability. Noisy positive/negative samples may be statistically compatible; resolving them requires an explicit estimator and sampling design, not arbitrary normalization of conflicting hard constraints.

Set union of immutable constraints and source IDs is commutative and idempotent. Feasibility and event projection therefore do not depend on input order. Logical conjunction is associative on one retained joint model. Replacing that model with an interval and then assuming independence at the next step can lose dependence or double-count an ancestor. Cache and revision must retain the original model/provenance, not rely on scalar associativity.

For compatible hard constraints, removing an essential constraint can only enlarge the feasible set, so its lower probability bound cannot increase and its upper bound cannot decrease. Duplicating a constraint has no effect. Adding compatible constraints can tighten bounds but cannot increase justified confidence by itself. Aggregating genuinely new observations may improve a future estimator's certificate; that is a different operation. The current native STV revision and proposed constraint intersection are intentionally not claimed to commute.

## Remaining proof obligations

The mathematics establishes sound bounds conditional on correctly specified scopes and constraints. It does not establish population transport, event independence, sampling independence, calibration of native STVs, acquisition honesty, or an implication from partial chess features to global legality. Universal king safety and legal historical play remain separate obligations. The laboratory is a reference calculation, not a validated new native operator, and finite chess successes cannot discharge these obligations.

A native implementation would need exact solver certificates or outward-rounded numerics, canonical formula identities, infeasibility witnesses, budget-safe exits, immutable-source validation, causal retraction, differential testing against the reference, and a separately reviewed statistical front end. No production integration or STV projection is proposed for immediate activation.
