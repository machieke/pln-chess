# Cycle 18 engineering report

Cycle 18 connects the evidence semantics to the actual Cycle 17 experiment.
The key finding is that **both learned-rule labels copy the same evaluation
result**. The 48 admitted conditional annotations are 24 underlying evaluation
vectors, not 48 separately measured successes. The source-bound contract
preserves that distinction across all six native arms and separates training,
parameter generations and knowledge applications.

The architecture decision is **B + D**: the isolated finite reference semantics
are executable under explicit hypotheses, while the empirical reliability
meaning and native confidence bridge remain unresolved. No native policy,
calculus, accepted legal learner, operational default or inference source changed.
A reference probability never replaces native unknown. The
[architecture decision](architecture-decision.md) identifies the exact missing
obligations and next measurement study.

Starting commit is `24f30ce8d4e0631f8937404929485dfdc0032f93`; delivery branch is
`cycle18-shared-parameter-contract`. Registration was committed before new
reference execution. Executable source/tests/delivery gates are frozen at
`9dc9159de311a2b5304e4051eef2919e7994c19f`, bound by the
[source manifest](../../artifacts/cycle18/source-provenance.json). Later reports
and compact evidence do not alter those files. The
[eight-package matrix](package-matrix.md) separates delivery status from findings.

The mapper accounts for all **432** original preparation records: **48 admitted**
annotations and **384 excluded** blocked/unknown conditional records. It verifies
all 144 original revision receipts across S-AA, S-BB, D-AB, D-BA and overlap 1/6.
Reuse across arms does not add experience. There are 864 typed mapping records:
216 environmental/intervention records, 216 evaluation vectors and 432
conditional annotations. The [decisive source example](../../artifacts/cycle18/contract/mappings/decisive-example.json)
and [complete audit](../../artifacts/cycle18/contract/mappings/audit.json) preserve
original paths, hashes, locators, ancestry, admissions and missing fields.

The primary hypothetical parameters describe positive output from the two
antecedent-qualified label channels. The actual copy operation imposes equal
within-episode outputs; the primary M-J-copy hypothesis also ties their
parameters. The query is success on two distinct future episode/channel trials
sharing that uncertain parameter pair, conditionally independent given it.
This explicitly stated generative assumption gives E[theta_clear theta_attack].
It is not inferred from logical proof length. Actual selected deterministic
labels are all positive; there is no measured stochastic error process or
independent correctness label from which to calibrate that hypothetical model.

The three registered families are factorized M-F, explicit joint M-J and bounded
M-B. All 72 grid/arm/model fits use exact rational arithmetic. On the primary
three-point grid, S-AA's two-trial prediction is .5596341154 under M-F,
.5601089465 under M-J-copy, .5573170889 under M-J-upper and .5624084919 under
M-J-lower. D-AB gives .5624814376 under copy semantics because it selects 24
distinct evaluations, versus twelve for S-AA. Factorized predictions are the
same across all six arms under the imposed product assumptions.

For the fixed M-F posterior marginals, the sharp coupling interval is
[2397627/4284304, 2399677/4284304], with feasible attaining joint distributions.
This is a posterior-marginal coupling problem, not Bayesian conditioning with
an unspecified prior. Without supplied marginals/prior/likelihood, the actual
empirical reliability query returns **not identified**. Strong grid sensitivity
(shared copy approximately .5601 on the primary grid versus .7946 on the five-
point grid) exposes the supplied support ceiling. These are neither calibrated
chess probabilities nor native truth values. [Exact source-bound results](source-bound-reference.md)
provide the assumptions, fractions, bounds and scope.

Repeated delivery adds no observation. Repeated applications at 1, 10 and 100
uses leave the event set, generation, posterior and bounds unchanged. A genuinely
new quarantined event creates a new generation; source removal rebuilds from
the remaining events. Incremental ingestion matches full recomputation and
reversed order. Shared-ancestor diamonds and cyclic uses cannot increase evidence.
Changed payload under the same ID is rejected; explicit supersession retains
the old version. Copy-model contradictions return inconsistency. Declared common
noise, independent noise and noiseless copies produce different results.
Predictions and derived annotations cannot become unapproved training evidence.
The [control report](replay-and-conflict-controls.md) links every executed case.

The unchanged native replay retains exact input, answer and observable trace
parity. S-AA/S-BB and overlap 1/6 derive clearance but leave attack unknown.
D-AB/D-BA derive attack with confidence .8184960085207099. The original
eleven-stamp witness remains blocked, and recursive reuse still fails at the
repeated `rule_extend-empty` stamp. Duplicate, diamond, cycle and disjoint-input
controls retain their prior behavior. Full fired-rule parents remain unobserved.
The [correspondence](../../artifacts/cycle18/correspondence.json) relates actual
native applications to external events and reference assumptions without a
numerical accuracy competition.

All 26 targeted tests passed, including four unchanged Cycle 17 reference
regressions and 22 new Cycle 18 cases. Static imports, literal dynamic-import
targets, reference runtime process denial, output destinations, checkpoint
construction and native oracle denial are tested. The clean compact reproduction
passed at the frozen source with historical Cycle 14–16 artifact and PGN reads
denied; it reused verified dependencies. Full historical preservation is running;
its complete source-bound receipt is required before final acceptance.

The frozen reference command executes 72 registered fits and 37 control fits,
with **14,740** group-likelihood evaluations total, at most **25** states and
**155-bit** rational numerators/denominators. It uses zero native processes.
Its measured wall time is about 2.79 seconds, CPU 2.14 seconds and process peak
RSS 30,968 KiB on this shared host. These timings include mapping/report output
and are not a benchmark for general correlated inference. Separate native,
preservation, memory and retained-byte accounting will be finalized after the
full run, including the limits of sampled process observations.

Ordinary Git contains the decisive mappings, exact finite results, native replay
records and all reports. Full historical exports stay in local checksummed packs;
no bulk hosting or release is authorized. [Reproduction](reproduction.md) gives
four levels, from compact contract example to full preservation.
[Publication](publication.md) describes whole-range blob/secret/remote checks and
independent final SHA/retrieval verification. Final engineering acceptance and
verified branch publication remain delivery gates, not scientific conclusions.

The next useful experiment is an independently measured, explicitly sampled
pipeline-error/annotation variable with a registered noise model. It should
resolve the smallest missing empirical meaning before a separately authorized
native bridge. Generic recursion, calibrated accuracy, a confidence conversion
and a general correlated-inference system remain unestablished.
