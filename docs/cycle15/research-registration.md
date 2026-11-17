# Cycle 15 research registration

Registered on 2026-11-17 at publication baseline
`d2f8b2c9fcb125266aa8b7b51dd97c5cd1dcf51d`, on the isolated local branch
`cycle15-native-consequences`. The user-supplied brief is retained unchanged.
This cycle permits local commits only. Historical source, runtime, checkpoints
and evidence are immutable. The existing conditional implementation remains the
operational reference. No autonomous move selection is implemented.

## Questions and separate outcomes

1. Can `PLN.Derive`/`PLN.Query` derive an absent conclusion with rule and premise
   interventions? Ground retrieval alone does not qualify.
2. Can native variables preserve shared roles across unfamiliar entities? Test
   direct relational atoms, the upstream Inheritance/Product encoding, and at
   most one uniform type-compatible grounding diagnostic if necessary.
3. Can native revision of a supplied rule template change held-out inference?
   Supplied structure is not discovered structure.
4. Can occupancy-constrained sliding influence be derived from raw observations?
   Imported-attack Stage A and raw-observation Stage B are scored separately.

## Observations and templates

Permitted inputs are typed piece identity/kind/owner, state/history identity,
original actor, relative offsets, structural ordered ray cells, occupancy,
explicit emptiness/unknown occupancy and a supplied structural transition.
No raw arm receives clearance, attack, exposure, legality or reference labels.
Every state-dependent atom includes its state. Entity identifiers are local;
rules contain variables rather than episode identifiers or absolute squares.
Neighborhood selection follows the whole structurally aligned ray, including
distant endpoints, independently of labels. Full-scope distractors are retained
as a comparison.

The bounded grammar has at most twelve supplied templates: slider-kind/shape
compatibility, fixed one-cell clearance, optionally list-based path composition,
occupancy obstruction, and role/owner-constrained exposure. Nested implications
are supplied curried domain knowledge, not a new conjunction calculus. Generic
PLN operators and the pinned interpreter remain untouched. Stop a failed
capability after three materially different representations; retain each raw
counterexample. Do not replace failed composition with host clearance.

## Truth values and evidence

Observed atomic facts use `(stv 1.0 0.99)`; supplied domain rules use
`(stv 1.0 0.95)`. These are disclosed modeling assumptions, not measured sensor
calibration. No implicit marginal `STV` declarations are added. Dedicated
marginal probes may declare `(stv 0.5 0.9)` as an explicit synthetic assumption.
Training begins at `(stv 0.5 0.0)` and admits finite `(stv label 0.5)` evidence
from each independent training ancestry group once per template, using native
revision. Unknown labels are recorded and do not update truth values.

Each observed atom has a stable occurrence stamp bound to its state and content;
its root ancestry is recorded separately. Different atomic observations within
one root are not claimed statistically independent. Reused rules retain their
same stamp; learned rules also carry admitted ancestry stamps. Never mint new
stamps per firing. Replay is idempotent. Native stamp disjointness and host
ancestry admission are audited separately, including chain and diamond cases.

## Corpus and evaluation

Generate at least 24 training, 12 development and 48 held-out structural root
families before fitting. Split by ray geometry and source ancestry, not by
before/after rows. A root owns its states and counterfactuals; renamings and
translations are dependent diagnostic variants. Hold out combinations of ray
length, direction, blocker index, identities and board locations. These are
controlled synthetic families, not independent natural games or a population
estimate of chess strength. Evaluation-only python-chess checks occupancy-
constrained influence; unknown occupancy remains unknown. Test references are
not visible to production or training. Do not retune on final outcomes.

Required cases: sole blocker leaves; blocker stays on ray; second blocker stays;
unknown cell; irrelevant move; removed attacker; removed/replaced target;
renaming/translation; actor's king; conflicting or stale observations.
Infer each endpoint separately. A host endpoint comparison is diagnostic only.

Compare A, the frozen field conditional; B, the same conditional through native
derivation; C, connected rules; D, learned rules and interventions, only on
matching attack targets. Report unsupported targets rather than score them as
false. Include rule/fact removal, truth-value change, shared-role swap, equal
counts/different connectivity, replay and leave-one-ancestry-out refitting.

Report supported positive/negative, unknown, conflict and incomplete outcomes;
classified correctness, positive recall including abstention, negative coverage,
schema transfer, errors, rule/premise intervention results and budget failures.
Use root-cluster bootstrap intervals (1,000 draws, seed 15) when defined.
Keep diagnostic variants separate from final test estimates.

## Budgets and stopping

Capability defaults: 24 selected tasks, queue bounds 64 tasks/128 beliefs,
10 seconds per invocation. Operational chess: 64 steps, 128/256 queues,
15 seconds. Generous diagnostics: 128 steps, 256/512 queues, 30 seconds.
Probe exact small boundaries including zero steps, queue sizes 1 and 2, tied
confidence and reversed inputs. Treat timeout/error as incomplete and an empty
bounded result as no support found, never logical falsity or saturation.

Research ceiling: 10,000 native processes, 8 CPU-hours, 2 GiB generated research
evidence; legal preservation separately allows four workers, 24 CPU-hours and
8 GiB output. Generated evidence goes to
`/home/purplezky/cycle15-evidence-20261117`, with hashes and local restoration
instructions. Git holds compact fixtures, summaries and representative proofs,
targeting less than 20 MiB of new data and no new blob above 5 MiB.
Stop budget overruns explicitly; do not weaken an acceptance criterion.

Use ten repetitions for small headline workloads: cold native inference on new
states, repeated inference with serialization caches, stored-answer retrieval,
and full proof reconstruction. Caches are host infrastructure. Capture exact
native programs, stdout/stderr, selected tasks, returned beliefs/stamps and
resource usage. No fired-rule tree is claimed unless observed. Post-hoc witnesses
must be labeled and cannot choose production answers.

Run a targeted starting smoke suite. Freeze implementation before the single
complete final source-bound legal preservation run; check all 287 negative,
27 history, two en-passant recovery and 76 legal holdout controls, the full legal
panel and historical field/concept behavior. Hash protected files at both ends.
Report unavailable checks as blocked rather than infer preservation from smoke.
