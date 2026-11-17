# What the two parameters mean

The primary reference interpretation is the propensity of each recorded label
channel to output a positive label in a hypothetical repeated population of
antecedent-qualified, rook/two-intervening-cell pipeline episodes. The labels
are the actual recorded `clear-two` and `rook-attack` training annotations.
They are not independent measurements of two chess mechanisms.

For a declared context C (this representation, two-cell orthogonal geometry,
rook kind, natural EE qualification and the same selection/annotation pipeline),
theta_clear means P(Y_clear=1 | C, parameters), and theta_attack analogously.
The historical code copies the same evaluation result into both channels.
The identity-respecting primary hypothesis therefore imposes
Y_clear=Y_attack within an episode and theta_clear=theta_attack. A vector of
two positive aliases contributes one Bernoulli likelihood, theta, rather than
theta squared. The supplied stochastic hypothesis concerns future pipeline
outputs; the existing deterministic code does not establish such a noise process.

For the 24 registered natural EE states, the deterministic computation already
returns true and the observed fraction of positive admitted annotations is
48/48. Under a completely specified, correct occupancy/influence implementation,
the corresponding relation is deterministic. The finite reference posterior is
therefore not an estimate that chess rules randomly fail. Its uncertainty is
supplied as a hypothetical model of a less-than-perfect label pipeline. No
independent measurement of correctness, representation error or pipeline failure
exists in these observations. Empirical reliability remains unidentified.

| Candidate interpretation | Status |
| --- | --- |
| Recorded positive-output propensity in the declared qualified pipeline | Precise hypothetical reference target; identity restriction known, stochastic population unverified |
| Correctness against independently measured ground truth | Unidentified: no independent ground truth or noise calibration |
| Frequency that a chess rule changes | Inapplicable to this deterministic relation |
| Probability an already observed cell is empty | Different variable; not estimated by these conditional labels |
| Probability an arbitrary board is correctly classified | Unsupported transfer from the selected conditional population |
| Native confidence or a Beta posterior | No established interpretation or conversion |

Selection scans the existing TCEC season 26 division P games in source order,
excludes the registered Cycle 16 games, and uses phase/direction preferences
with fallback. The selector checks rook kind, two-cell geometry, existing target
and **natural emptiness of both intermediate cells** for training. It does not
inspect a conclusion label. Availability of suitable roots, ordering and the
antecedent nevertheless select a population where the supplied deterministic
influence target is positive. Evidence preparation then runs the evaluation
oracle, copying that result to both rules; the terminal antecedent uses an
evaluation-verified clear path. The selection/admission story is not outcome-
independent random sampling merely because the selector never calls an attack
oracle. Phase/direction balancing does not correct this selection.

The eight other E/O/U occupancy conditions are dependent transformations and
exclude the all-empty conditional. Blocked paths are not failures of a
conditional whose premise requires two empty cells. Unknown observations never
become negatives. The 96 held-out endpoints from 24 roots remain Cycle 17
evaluation context; Cycle 18 does not use them for posterior fitting or claim a
new accuracy result.

The registered query asks for success on **two distinct future trials**: one
clear-label trial and one attack-label trial, on independently generated future
episodes conditional on the same uncertain parameter pair and declared context.
That generative assumption gives q(a,b)=a*b. It is unrelated to the number of
rules in a native proof. For the copy model, it becomes E[theta²]. Repeating the
same event instead gives E[theta]; redrawing the parameter would give another
quantity. A single future joint vector could instead use min(a,b), a*b or
max(0,a+b-1) under its declared observation model; that is not the registered
two-distinct-trial query. This distinction prevents quietly changing the query
when changing training dependence assumptions.

No natively derived Clear or Attack is an observed training event. The model
consumes only the mapped external evaluation vector components. Groupwise
likelihood multiplication assumes conditional independence between games.
Within a group, the complete two-channel joint table determines the likelihood.
M-F and unequal-channel M-J sensitivity cases deliberately relax the known copy
identity; they investigate alternative measurement hypotheses, not a discovered
generative explanation of the historical code.

Outputs retain separate fields for native strength/confidence (null in the
reference schema), reference predictive probability, full parameter posterior,
posterior mean/variance, dependence bounds and empirical uncertainty (unavailable).
The native checkpoint still records strength 1/confidence .923076923076923 for
each targeted rule. Nothing maps posterior variance, a sample count or a bound
width into that confidence. **Confidence mapping remains unresolved.**
