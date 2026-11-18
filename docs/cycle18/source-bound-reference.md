# Source-bound exact finite results

The new calculation uses the actual mapped Cycle 17 evaluation events, selected
components and source memberships. Each result exposes all event/group IDs,
complete prior, joint observation tables, per-group likelihood factors,
normalizer, posterior, query and generation identity. It does not start from
native truth values. The [72-case summary](../../artifacts/cycle18/contract/reference_cases/summary.json)
links by directory key to exact result and bound files. The main examples are
[shared copy](../../artifacts/cycle18/contract/reference_cases/primary/S-AA/M-J-copy/result.json),
[shared factorized](../../artifacts/cycle18/contract/reference_cases/primary/S-AA/M-F/result.json)
and [disjoint copy](../../artifacts/cycle18/contract/reference_cases/primary/D-AB/M-J-copy/result.json).

The three families are M-F (explicit factorization), M-J (explicit joint
semantics) and M-B (partial identification). M-J has three registered hypotheses,
not three additional families. All fit calculations explicitly assume conditional
factorization between source games. Shared engines/openings/publisher leave that
assumption unverified even in native-disjoint arms.

For parameters a,b and a binary vector (Yc,Ya), the full observation table is
P11=t, P10=a-t, P01=b-t, P00=1-a-b+t. M-F sets t=ab, M-J-upper sets t=min(a,b),
and M-J-lower sets t=max(0,a+b-1). The latter two have the same conditional
Bernoulli marginals for every parameter state but different dependence. They
start with the same uniform product prior. This is equality of **conditional
observation marginals**, not a claim that their resulting parameter posteriors
have equal marginals. M-J-copy restricts support to a=b and sets t=a, assigning
zero probability to disagreeing aliases. Its uniform diagonal prior has the
same one-parameter prior marginals as the product prior, but a different joint law.

For a shared source vector, the likelihood is the appropriate single joint-table
entry. If an arm admits only one of its components, the likelihood is its marginal
Bernoulli probability. Selecting a label twice cannot add factors. Multiple
distinct measurements inside one game require another declared joint likelihood
and are rejected by this bounded implementation. The noisy-measurement control
is an explicitly separate finite example.

Primary support is {1/4,1/2,3/4}, giving at most nine joint states (three for the
copy restriction). Uniform priors are supplied design choices. The query is
E[a b] for two distinct future conditionally independent trials, as defined in
[parameter semantics](parameter-semantics.md).

| Arm | M-F | M-J-copy | M-J-upper | M-J-lower |
| --- | ---: | ---: | ---: | ---: |
| S-AA / S-BB | .5596341154 | .5601089465 | .5573170889 | .5624084919 |
| D-AB / D-BA | .5596341154 | .5624814376 | .5596341154 | .5596341154 |
| overlap-1 | .5596341154 | .5624721572 | .5596250530 | .5603570831 |
| overlap-6 | .5596341154 | .5622886919 | .5594458952 | .5619870041 |

The exact shared copy result is **2399677/4284304**. The factorized result is
**160503595641/286800949444**. The disjoint copy result is
**1270966468597/2259570509584**. Equal factorized answers across arms follow from
twelve selected positive components per parameter and the imposed product model.
The copy model instead sees 12, 24, 23 or 18 unique evaluations, respectively;
two aliases do not double the count. This is an evidence-contract consequence
under the supplied model, not evidence that the native disjoint policy estimates
these probabilities.

M-B fixes the posterior parameter marginals from each named fitted model and
allows all nonnegative couplings with those marginals. For the primary M-F
posterior, the sharp interval is
**[2397627/4284304, 2399677/4284304]**. The
[extremal witnesses](../../artifacts/cycle18/contract/reference_cases/primary/S-AA/M-F/bounds.json)
give complete feasible joint distributions attaining both ends. Quantile
alignment maximizes E[ab], while opposite ordering minimizes it: an uncrossing
mass transfer changes the objective by mass*(a2-a1)*(b2-b1), which is nonnegative.
The tests and acceptance gate verify row/column marginals, total mass and exact
objectives. This establishes sharpness for this finite marginal-coupling problem.

These bounds **do not** solve Bayesian conditioning with an unspecified prior
coupling or observation model. The range across M-F/M-J cases is a sensitivity
range over selected hypotheses, not a sharp identified set over every possible
model. Without supplied posterior marginals or a complete prior/likelihood, the
[actual empirical query](../../artifacts/cycle18/contract/reference_cases/not-identified.json)
returns `not_identified`, no point estimate and no invented interval.

The actual S-AA M-F and M-J-copy fits have exactly the same posterior parameter
marginals and event set, but different joint predictions. The
[source-bound comparison](../../artifacts/cycle18/marginal-comparison.json)
verifies their full marginal tables and shows that the copy law attains the
upper coupling endpoint. Equal marginals therefore still omit relevant joint
information in this actual-source example. The known copy operation is additional
information: M-F remains a counterfactual independent-measurement hypothesis,
not an equally faithful description of that operation.

Registered grid sensitivity is substantial:

| Support / shared S-AA | M-F | M-J-copy | M-J-upper | M-J-lower |
| --- | ---: | ---: | ---: | ---: |
| {1/4,3/4} | .562498589 | .562499059 | .562497648 | .562500000 |
| {1/4,1/2,3/4} | .559634115 | .560108947 | .557317089 | .562408492 |
| {1/10,3/10,1/2,7/10,9/10} | .792693948 | .794600085 | .779396804 | .799044571 |

All-positive observations concentrate near a supplied grid ceiling. The grid
omits theta=1, even though the selected deterministic labeling code produces
only positives here. The resulting subunit probabilities therefore cannot be
interpreted as measured failures. Exact rational arithmetic is exact for these
finite designs, not an exact continuous-parameter posterior or a validated
approximation. No model was chosen to reproduce native success or failure.

All 72 fits complete within the registered 25-state/2,500-likelihood-per-fit
limits. The exact laboratory, replay controls and deliberately incomplete
budget cases are separately counted in the resource receipt. None of these
numbers is serialized as a native `stv`, checkpoint or chess classification.
