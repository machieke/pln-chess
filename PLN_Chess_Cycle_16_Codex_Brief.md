# PLN Chess — Cycle 16 Consolidated Engineering Brief

## Native Rule Reuse, Evidence Provenance, and Bounded Path Composition

**Repository:** https://github.com/machieke/pln-chess
**Starting commit:** `e349c9c8c7c6506a367c28623e30373c59ffc59e`
**Starting branch:** `cycle15-native-consequences`
**Suggested local branch:** `cycle16-native-path-composition`
**Operational baseline:** Unchanged accepted Cycle 12 legal checkpoint
**Execution:** One consolidated autonomous engineering assignment
**Delivery:** Implementation, native experiments, tests, evidence, reports, and local commits
**Authorization:** Local work only; no push, publication, deployment, upstream changes, or new native inference operators

---

## 1. Mission

Cycle 16 must investigate a specific limitation identified in Cycle 15:

> Repeated application of a reusable rule can introduce overlapping provenance into two premises, causing the existing native evidence guard to reject their combination.

The main research question is:

> Can native PLN derive occupancy-constrained attack support across two empty intervening cells while preserving rule selection, shared-role binding, and honest evidence provenance?

Compare:

1. The existing recursive path representation.
2. An explicit, supplied two-cell conditional representation.
3. The same finite representation with learned rule truth values.

Keep the native runtime unchanged.

A successful finite two-cell derivation would demonstrate bounded conditional composition. It would not establish general recursion, arbitrary conjunction, or discovery of chess-rule structure.

Do not return to broad preference learning during this cycle.

---

## 2. Starting Findings to Reproduce

Read the actual Cycle 15 implementation and reports before editing.

Reported findings include:

- Native derivation produces absent conclusions and multi-rule chains.
- Native variables bind unfamiliar entities and preserve shared roles.
- Python does not ground schemas or select the experimental chess conclusion.
- A one-intermediate-cell path can support native attack and exposure conclusions.
- Longer empty paths remain unsupported in the tested recursive encoding.
- Stable rule stamps can overlap with the provenance of an intermediate result.
- Larger budgets did not resolve the retained long-path counterexample.
- Supplied and learned connected-rule arms classified 52 of 96 final endpoints correctly and abstained on 44.
- Positive recall was 4/48, or 8.33%.
- On the strictly unseen coarse-geometry subset, all 41 positives remained unknown.
- All admitted conditional learning outcomes were positive in the designed corpus.

These are reported experimental results. Reproduce the relevant cases before treating them as confirmed baselines.

### Important scope

The experimental attack target is occupancy-constrained sliding influence.

It is not:

- Full legal capture eligibility.
- General move legality.
- Strategic desirability.
- Universal king safety.

A friendly occupied destination can still be within a sliding piece's influence under the chosen reference semantics.

Preserve that definition throughout the study.

---

## 3. Source of Truth

Inspect at least:

    docs/cycle15/engineering-report.md
    docs/cycle15/native-capabilities.md
    docs/cycle15/relative-knowledge.md
    docs/cycle15/blocker-consequences.md
    docs/cycle15/learning-and-transfer.md
    docs/cycle15/architecture-decision.md
    docs/cycle15/performance-and-proofs.md
    docs/cycle15/reproduction.md

    research/cycle15/native_reasoner.py
    research/cycle15/knowledge.py
    research/cycle15/observations.py
    knowledge/cycle15/domain_rules.metta
    knowledge/cycle15/schemas.json
    training/cycle15_consequences.py
    evaluation/cycle15_consequences.py

    vendor/pln/lib_pln.metta
    configs/runtime-lock.json

Discover additional paths from the checkout.

Preserve these runtime pins:

- PLN: `4405956947c4b53c7ff01bd565aa3b114bc970a1`
- PeTTa: `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`

The actual runtime lock and source hashes remain authoritative.

The accepted legal checkpoint's reported file SHA-256 is:

`5c655e99f45089b6049c4819f3db42bf09f38906984a057200ce04ef10e82de8`

Verify the actual checkpoint path and hash. Do not confuse the file hash with the model's semantic version identifier.

---

## 4. Architectural Boundaries

### Permitted

- Raw occupancy and explicit unknown observations.
- Relative geometry and ordered ray membership.
- Structural successor states.
- New, explicitly supplied finite domain implications.
- Existing native derivation, query, and revision.
- Evidence and stamp diagnostics.
- Host-side scheduling, serialization, indexing, storage, and evaluation.
- Evaluation-only reference chess queries.
- Isolated experimental checkpoints.
- Local commits.

### Prohibited

- Changing `StampDisjoint`.
- Altering `PLN.Derive`, native truth formulas, or inference clauses.
- Giving repeated applications fresh evidential identities.
- Removing rule or training stamps to force a derivation.
- Assigning empty stamps to bypass overlap checks.
- Cloning the recursive rule under different names to simulate independence.
- Replacing native clearance inference with Python or custom MeTTa adjudication.
- Selecting a rule in Python because its chess conclusion is already known.
- Loading reference labels into production observations.
- Absolute-square constants in learned domain rules.
- Operational legal-model changes.
- New strategic preferences, search, or move selection.
- Remote writes or publication.

A finite declarative domain rule is allowed.

A new inference calculus or evidence policy is not.

Moving a forbidden operation into MeTTa does not make it an authorized native PLN inference.

---

## 5. Distinguish the Four Claims

Every result must identify which claim it supports.

### Claim A — Native applicability

The native reasoner binds facts to a reusable rule and determines the applicable inference.

### Claim B — Finite path composition

The supplied two-cell encoding derives a consequence from two separate occupancy observations.

### Claim C — Learned support

Native revision changes rule truth values and affects held-out native results.

### Claim D — Generic reusable-rule reasoning

The same recursive rule can be applied repeatedly without invalid evidence treatment.

Passing A, B, or C does not automatically establish D.

Similarly, native execution of nested implications does not establish that their probabilistic semantics are equivalent to a general conjunction operator.

---

## 6. Execution Strategy

Complete eight work packages in one run.

Recommended order:

1. Preserve the baseline and register the study.
2. Isolate the repeated-stamp failure.
3. Implement the finite two-cell comparison.
4. Run the complete occupancy and counterfactual panel.
5. Investigate learned-rule support and shared ancestry.
6. Write the evidence-policy decision.
7. Measure budget behavior, proof integrity, and cost.
8. Complete preservation, reproduction, and delivery.

Use an early gate:

> Do not expand the corpus before the minimal recursive-versus-finite comparison has executed.

If the finite representation also fails, investigate the failure without quietly changing the evidence policy.

Continue independent engineering and reporting work when a research target fails.

---

# C16-01 — Baseline Preservation and Study Registration

## Objective

Establish a reproducible starting point without modifying Cycle 15 or the operational system.

## Tasks

Verify:

- Starting commit and branch ancestry.
- Working-tree status.
- Native runtime and source hashes.
- Operational source identity.
- Accepted legal checkpoint.
- Cycle 15 rule structures and learned checkpoint.
- Relevant representative transcripts.
- Existing publication and evidence manifests.

Do not destructively reset unrelated work.

Place new experimental code outside the operational `src/` tree unless the repository's accepted source-binding mechanism explicitly permits otherwise.

Prefer:

    research/cycle16/
    knowledge/cycle16/
    training/cycle16_*.py
    evaluation/cycle16_*.py
    tests/test_cycle16_*.py

Do not rewrite historical rule files or receipts.

### Reproduce the relevant baseline

Run:

- One-rule and two-rule native probes.
- Shared-role binding and swapped-role controls.
- Reused-recursive-rule failure.
- One-cell positive attack.
- One-cell exposure.
- Longer-path failure at the recorded generous budget.
- Representative obstruction and unknown-occupancy cases.

Start with targeted checks. Run the complete expensive preservation suite once the final experimental source is frozen.

### Register the study

Write:

    docs/cycle16/research-registration.md

Freeze:

- Primary query semantics.
- Experimental arms.
- Observation and rule policies.
- Stamp and ancestry handling.
- Truth-value assumptions.
- Budget ladder.
- Dataset grouping.
- Training/development/test partitions.
- Metrics.
- Optional experiments.
- Compute and storage ceilings.

**Deliverables:** Baseline receipt, study registration, immutable input manifests.

---

# C16-02 — Minimal Evidence-Reuse Failure

## Objective

Identify exactly what prevents the second recursive composition.

Use both a tiny symbolic example and the corresponding chess-path example.

## 2.1 Primary recursive template

Preserve the existing semantics:

    Empty(cell, state)
        ->
    PathEmpty(tail, state)
        ->
    PathEmpty(Cons(cell, tail), state)

The template retains one stable rule identity across all applications.

Do not solve this experiment by renaming the rule.

## 2.2 Inspect intermediate support

For a two-cell path, record:

- The initial empty-tail support.
- The first extension's returned statement.
- The first extension's native stamp set.
- The partially applied rule for the other cell.
- Its native stamp set.
- The overlap between the prospective inputs.
- Whether the desired second extension appears in returned beliefs.

Use actual native statements where observable.

Do not invent a fired-rule trace when the runtime exposes only selected tasks and returned beliefs.

## 2.3 Native admissibility diagnostics

In separate audit programs, test the relevant stamp pair with the existing native `StampDisjoint`.

Where useful, apply the existing statement-level inference operator to the same statements as a diagnostic.

These calls answer different questions:

- Would the statements structurally match?
- Does the evidence guard admit their combination?
- Did the full native derivation produce the conclusion?

A direct operator diagnostic that bypasses the derivation guard must never be presented as the experimental answer.

Distinguish a verified admissibility failure from an observed runtime event. Do not claim the reasoner attempted a particular pair unless the trace actually shows that.

## 2.4 Dependency cases

Construct a small registered diagnostic matrix:

| Case | Question |
|---|---|
| Shared rule identity only | Does rule reuse alone prevent composition? |
| Shared environmental evidence | Does the guard prevent combining descendants of one observation? |
| Shared training ancestry | Can different learned rules conflict because they share supporting examples? |
| Diamond derivation | Can two branches from a common premise rejoin? |
| Replayed input | Does duplicate delivery alter belief support? |
| Circular chain | Can a conclusion recycle itself as independent support? |
| Truly disjoint synthetic support | What happens under the explicitly constructed disjoint control? |

Synthetic stamp arrangements are diagnostic assumptions.

They must not replace the provenance of real chess observations or be chosen after the fact to make the main experiment succeed.

Use namespaced stamps to avoid the identifier collision found in Cycle 15.

**Deliverables:** Minimal programs, raw outputs, stamp-overlap table, and a localized failure explanation.

---

# C16-03 — Explicit Two-Cell Native Encoding

## Objective

Compare recursion with a finite supplied rule while leaving the native runtime unchanged.

## 3.1 Candidate domain rule

Test the following declarative structure:

```metta
(Rule clear-two (Implication (RayPath $a $t (Cons $c1 (Cons $c2 Nil)) $shape $s) (Implication (Empty $c1 $s) (Implication (Empty $c2 $s) (Clear $a $t $shape $s)))))
```

This is a proposed experiment, not a preverified result.

The existing Cycle 15 loader reads one `Rule` per physical line. Store the declaration accordingly, or implement a separately tested generic data reader in the new research module.

Do not alter the historical loader merely for formatting.

The current file has eleven rules and a twelve-template limit. One new primary rule fits that bound. Verify these facts in the checkout.

## 3.2 Why this is a distinct comparison

The recursive encoding needs repeated application of the extension schema.

The finite encoding states the complete two-cell dependency as one supplied implication chain.

It does not:

- Inspect a specific board position.
- Include absolute coordinates.
- Select the expected answer in Python.
- Duplicate recursive-rule evidence.
- Establish arbitrary-length reasoning.

It adds domain structure explicitly. Report that inductive bias.

## 3.3 Experimental arms

| Arm | Knowledge |
|---|---|
| R | Unchanged Cycle 15 recursive knowledge |
| F | Same knowledge plus the supplied `clear-two` template |
| F-minus | F with only `clear-two` removed |
| L | Same finite structure with registered native-learned parameters |

Keep raw observations and terminal attack rules matched wherever the comparison intends to isolate the path representation.

Load each arm's entire registered knowledge file.

Do not use Python logic such as “path length is two, therefore select `clear-two`.”

Native matching must determine whether the exact two-cell path structure applies.

## 3.4 Checkpoint integrity

Adding a template changes the rule-structure identity.

Do not modify an old checkpoint's structure hash to make it load.

Create a new versioned checkpoint.

Any inherited truth values must retain:

- The exact original declaration.
- Original rule identity.
- Supporting ancestry.
- Source checkpoint identity.

Do not copy another rule's learned support into `clear-two`.

## 3.5 Staged queries

First query:

    Clear(attacker, target, shape, state)

Then query:

    Attack(attacker, target, state)

Only after those succeed, query role-correct king exposure where applicable.

This distinguishes path-composition failure from downstream attack or ownership failure.

Preserve both direct outputs and the complete native knowledge inputs.

## 3.6 Rule interventions

Verify:

- Removing `clear-two` restores the recursive arm's behavior on the matched case.
- Removing either sole emptiness premise removes the finite derivation.
- Changing the state on one premise prevents inappropriate cross-state binding.
- Changing the shared attacker/target roles prevents an unrelated ray from satisfying the query.
- Changing the rule truth value affects native support, subject to documented alternate derivations.

If another valid derivation survives, report it rather than demanding an unjustified classification flip.

**Deliverables:** Separate knowledge manifests, arm definitions, exact native programs, and rule-intervention results.

---

# C16-04 — Two-Cell Occupancy and Counterfactual Panel

## Objective

Determine the actual supported scope of the finite representation.

Use geometrically compatible rook, bishop, and queen queries.

Keep geometric influence separate from legal capture and move legality.

## 4.1 Complete occupancy matrix

Let E mean explicitly empty, O mean explicitly occupied, and U mean unknown.

For two distinct intervening cells:

| Cell 1 | Cell 2 | Intended epistemic outcome |
|---|---|---|
| E | E | Positive influence may be supported if all other declared requirements are satisfied |
| E | O | A known obstruction supports negative influence |
| O | E | A known obstruction supports negative influence |
| O | O | Known obstruction remains; do not count correlated support as independent automatically |
| O | U | The known obstruction is sufficient for the negative obstruction target |
| U | O | The known obstruction is sufficient for the negative obstruction target |
| E | U | Unknown unless another independent justified conclusion exists |
| U | E | Unknown unless another independent justified conclusion exists |
| U | U | Unknown |

Do not assign unknown cells convenient hidden contents.

For partial-state cases, use evaluation-only completions to demonstrate ambiguity where necessary. Do not score one arbitrary completion as the uniquely correct answer.

## 4.2 Structural and role controls

Include:

- Sole blocker leaves the two-cell ray.
- Blocker moves from one intervening cell to the other.
- One blocker leaves while another remains.
- Unrelated piece moves.
- Attacker is removed.
- Target is removed or replaced.
- Friendly versus opposing target.
- Ordinary target versus original actor's king.
- Correct versus incorrect actor/owner binding.
- Before-state facts mixed with correctly indexed after-state facts.
- Entity renaming.
- Valid reflection and owner-relative transformations.
- Translation where boundaries and context are preserved.

Missing query entities are invalid or unsupported query domains, not automatically negative attack conclusions.

Exposure must require the correct target kind, ownership, attacker side, and state.

## 4.3 Input validation and conflicting evidence

The public observation API should reject malformed occupancy and duplicated structural cells.

Use a separate low-level audit for deliberately competing observations.

Report positive and contrary support separately.

Do not silently resolve contradictory input by insertion order or by deleting the inconvenient observation.

## 4.4 Order and uncertainty

Keep ray order deterministic.

Test input ordering and selected premise-confidence variations in a diagnostic arm.

Do not assume that curried truth-value propagation is commutative or numerically equivalent to conjunction.

A logical symmetry test and an exact truth-value equality test are different requirements.

Report order effects instead of choosing the order that gives the strongest answer.

## 4.5 Beyond two cells

Preserve zero-, one-, and longer-path cases as controls.

The primary new rule must not match a three-cell path.

A three-cell finite template is optional secondary work only after the two-cell comparison is complete and frozen. It requires a separate registered knowledge manifest and must be labeled another supplied finite encoding.

Do not automatically generate a different rule for every observed position.

**Deliverables:** Full occupancy panel, counterfactual controls, role tests, and scope limitations.

---

# C16-05 — Learning, Shared Ancestry, and Transfer

## Objective

Determine whether learned rule support can be used honestly in the finite encoding.

Do not conflate confidence accumulation with rule discovery.

## 5.1 Learning arms

Run:

1. Supplied finite rule with disclosed assumed truth value.
2. Finite rule initialized with the registered untrained prior.
3. Finite rule updated through native revision.
4. Learned finite rule combined with learned downstream rules, preserving any genuinely shared training ancestry.

The first three isolate support for the new rule.

The fourth tests whether the composition succeeds when provenance is carried through the fuller learned chain.

Do not select disjoint training sources retrospectively merely because shared sources block inference.

Any disjoint-source control must be registered as an explicit experimental assumption.

## 5.2 Conditional evidence admission

Train the declared conditional, not a vaguely related target.

A blocked path does not contradict a rule whose antecedent requires both cells to be empty.

Unknown occupancy does not count as a false antecedent or negative conclusion.

Record all exclusions and their reasons.

If all admitted outcomes are positive, report that fact. Do not claim negative-example learning or noisy-supervision robustness.

An intentionally false domain hypothesis may be used as a separate falsification control, but it must never enter the accepted experimental arm unnoticed.

## 5.3 Stable provenance

Preserve:

- Rule schema identity.
- Training episode ancestry.
- Observation identity.
- Label generation.
- State identity.
- Native revision expression.
- Checkpoint generation.

Repeated delivery must be idempotent.

Removing a training group must cause an actual native refit, not merely removal of a displayed evidence reference.

Lowered confidence need not cross a display threshold to be a valid learning effect.

## 5.4 Corpus design

Use a small focused corpus.

Prefer existing independently sourced game episodes for sampling raw two-cell situations, supplemented by controlled synthetic fixtures.

Aim for:

- At least 12 training source episodes.
- At least six development source episodes.
- At least 24 held-out source episodes.

Use at most one primary root per source game where available.

These are sampling goals, not permission to invent statistical independence.

Every root's occupancy variants, translations, counterfactuals, and before/after states remain in one ancestry group.

Do not start a large external acquisition project if the existing corpus is sufficient.

## 5.5 Correct the Cycle 15 transfer grouping

Partition before learning using both:

- Source/episode ancestry.
- Coarse relative geometry, ignoring attacker-kind substitutions that do not change that geometry.

Report overlapping and wholly unseen geometry separately.

Do not claim that all sparse two-cell configurations are distinct structural families merely because they have different coordinates or piece names.

Sharing the abstract relation being learned is expected. It is not automatically leakage. But transformed copies and common source episodes are dependent.

If the narrow two-cell design cannot support a meaningful unseen-geometry split, say so. Demonstrate unseen bindings or episodes without renaming that result “arbitrary geometry transfer.”

## 5.6 Evidence source versus inference support

Ground-truth attack labels belong only to training/evaluation.

Held-out inference receives raw observations and the frozen rule checkpoint.

No label, final reference verdict, or expected derivation may enter the inference facts.

**Deliverables:** Native learning traces, checkpoint lineage, group audit, transfer results, and ancestry-removal experiments.

---

# C16-06 — Evidence Semantics and Architecture Decision

## Objective

Explain what the experiments establish about reuse without changing the policy.

## 6.1 Distinguish provenance categories

Analyze separately:

| Category | Meaning |
|---|---|
| Rule schema identity | Which reusable domain statement is being used |
| Learned rule support | Evidence from which the rule's truth value was estimated |
| Environmental evidence | Observations about the current state |
| Proof application | An occurrence of applying knowledge |
| Derivation ancestry | Earlier support contributing to an intermediate statement |

A new proof application is not automatically a new independent observation.

Conversely, applying a reusable rule again is not necessarily the same operation as revising two estimates as independent evidence.

The current runtime may treat these overlaps conservatively. Do not assert that it is mathematically wrong without specifying the intended semantics.

## 6.2 Analyze the matched findings

Answer:

- Does the recursive encoding fail at the same overlap as Cycle 15?
- Does the finite encoding avoid that overlap through different supplied structure?
- Does it still fail when learned rules share training ancestry?
- Is an observed failure due to missing binding, unavailable statements, overlap, confidence attenuation, queue eviction, or timeout?
- Does finite encoding change the meaning or independence assumptions of the supplied conditional?
- Does success require genuinely new domain knowledge?

Do not attribute every failed query to stamps merely because one stamp counterexample exists.

## 6.3 Policy proposal only

If a generic change appears necessary, describe—not implement—candidate distinctions between:

- Rule reuse.
- Shared empirical evidence.
- Circular derivation.
- Revision of multiple estimates.
- Repeated application of uncertain parameters.

Specify required tests and mathematical obligations.

Include counterexamples showing why these shortcuts are unacceptable:

- Removing all rule stamps.
- Making stamps unique per firing.
- Treating training overlap as irrelevant.
- Revising the same observation repeatedly.
- Allowing proof cycles to increase confidence.
- Replacing all dependence with a Boolean “independent” flag.

No alternative guard, custom native operator, or production prototype is authorized.

## 6.4 Decision outcomes

Choose one:

### Outcome A — Finite composition works; generic reuse remains blocked

Retain the finite result as a bounded native capability.

Recommend whether a separately registered finite-path extension is worthwhile.

Do not call recursion solved.

### Outcome B — Finite composition also fails

Identify the smallest failing stage and produce a reproducible counterexample.

Do not disguise it with a host clearance fact.

### Outcome C — Existing supported representation resolves reuse

Document why it preserves real evidence and does not merely relabel overlap.

Test duplicate, diamond, cycle, and shared-training controls.

No runtime or evidence-policy modification may be hidden in this outcome.

### Outcome D — Syntax succeeds but confidence/dependence semantics remain inadequate

Preserve the execution result while withholding stronger probabilistic claims.

A higher raw score is not proof of sound evidence treatment.

**Deliverables:** Evidence-semantics report and explicit next-step decision.

---

# C16-07 — Budgets, Proof Integrity, and Performance

## Objective

Separate semantic limitations from bounded execution and keep the experiment inspectable.

## 7.1 Native execution

Use the existing adapter and pinned derivation APIs.

Preserve:

    PLN.Derive
    PLN.Query
    StampDisjoint
    Native statement-level inference
    Native truth-value functions

Do not replace native schema binding with host grounding.

Use diagnostic direct calls only in separately labeled audit programs.

## 7.2 Budget ladder

Register a small budget ladder within the adapter's supported bounds.

For example, investigate:

- Small: 24 steps, task capacity 64, belief capacity 128.
- Medium: 64 steps, task capacity 128, belief capacity 256.
- Generous: 128 steps, task capacity 256, belief capacity 512.

Verify actual effective capacities against the pinned implementation.

These are proposed resource configurations, not a completeness guarantee.

Use the generous tier for minimal failing cases, not indiscriminately for every fixture.

Separate:

- Query support absent.
- Support present below threshold.
- Conflict.
- Incomplete execution.
- Remaining unprocessed tasks.
- Eviction or retention effects.

Task-queue exhaustion is not by itself proof of complete reasoning over all possible knowledge.

## 7.3 Threshold policy

Preserve the Cycle 15 experimental display thresholds for the primary comparison unless a pre-registered change is justified before final evaluation.

Always report raw native truth values and returned statements.

Do not lower confidence thresholds to claim that a missing derivation has been repaired.

Use the operational baseline's own thresholds when reporting its frozen comparison.

Do not compare thresholded results from different policies without disclosure.

## 7.4 Provenance and proof status

Retain:

- Exact native input program.
- Initial facts and rules.
- All stamp assignments.
- Rule/checkpoint identities.
- Selected-task output.
- Returned beliefs and answer channels.
- Native process receipt.
- Budgets and runtime hashes.
- Diagnostic replay results.

Do not invent a complete fired-rule tree.

A revalidated proof witness is distinct from an execution trace.

Do not count cached answer retrieval as fresh native derivation.

## 7.5 Measurements

Benchmark:

- One-cell baseline.
- Two-cell recursive arm.
- Two-cell finite arm.
- Learned finite arm.
- Negative obstruction.
- Unknown occupancy.
- Representative scoped versus distractor-rich input.

Measure cold inference, cached retrieval, and full proof reconstruction separately.

Record native processes, selected tasks, retained beliefs, wall time, memory, and proof bytes.

Ten repetitions per small headline workload are sufficient as a target; disclose when fewer are feasible.

Do not require a speedup. Correctness and explanatory value take priority.

## 7.6 Storage discipline

Reuse the compact proof infrastructure.

Keep source, tests, compact examples, summaries, and manifests in Git.

Keep bulk experimental outputs outside the tracked working tree.

Do not repeatedly embed identical native programs and proof subgraphs in every report.

Register a storage ceiling and record actual usage.

Create local checksum-verified evidence packs if needed. Do not upload them.

**Deliverables:** Budget study, benchmark report, native receipts, and storage manifest.

---

# C16-08 — Integration, Preservation, and Consolidated Delivery

## Objective

Deliver a small usable experiment with exact boundaries.

## 8.1 Suggested implementation layout

Adapt to existing conventions:

    research/cycle16/
        experiments.py
        evidence_audit.py
        corpus.py
        cli.py

    knowledge/cycle16/
        recursive.metta
        finite_two.metta
        schemas.json

    training/cycle16_paths.py
    evaluation/cycle16_paths.py

    tests/test_cycle16_native_reuse.py
    tests/test_cycle16_finite_paths.py
    tests/test_cycle16_occupancy.py
    tests/test_cycle16_learning.py

Reuse Cycle 15's adapter rather than copying it unnecessarily.

Do not alter historical loaders or models merely to make new checkpoint structures compatible.

## 8.2 Experimental interface

Provide an opt-in interface that accepts:

- Observed state.
- Attacker and target.
- Optional supplied move.
- Knowledge arm.
- Checkpoint.
- Inference budgets.
- Proof mode.

Return:

- Target semantics.
- Raw observations and scope identity.
- Knowledge/checkpoint identity.
- `Clear`, `Attack`, and optional exposure support.
- Contrary support.
- Classification.
- Unknown and incomplete reasons.
- Native stamps.
- Proof status.
- Budget usage.

Do not add a best-move or strategic-score field.

Provide actual CLI commands for:

1. Reproducing the minimal stamp failure.
2. Comparing R and F.
3. Running the nine occupancy cases.
4. Replaying learned support.
5. Running preservation checks.

Document commands only after implementation.

## 8.3 Operational preservation

Preserve:

- Accepted legal checkpoint bytes.
- Operational source and runtime hashes.
- Established legal classifications and native proof parity.
- All 287 negative controls.
- All 27 history controls.
- Both known en-passant recoveries.
- All 76 controlled legal holdouts.
- Historical files and scientific receipts.
- Existing APIs.

Run the complete source-bound preservation suite at final acceptance.

The prior full legal comparison covered 206 shards and 584,112 candidate rows. Use its actual manifest and commands rather than recreating an approximate substitute.

If evidence or dependencies are unavailable, report which gates could not be executed. Do not claim complete acceptance from targeted tests alone.

## 8.4 Boundary tests

Verify that:

- Evaluation-oracle access can be disabled during inference.
- Test labels cannot update training.
- The finite template is chosen by native matching, not host path-length branching.
- Unknown cells never become empty facts.
- No source or state identity leaks across requests.
- No extra rule copies or fresh stamps evade overlap.
- Rule files contain declarative data rather than executable adjudication.
- Native errors produce incomplete outcomes, not negative predictions.

## 8.5 Required reports

Produce:

    docs/cycle16/engineering-report.md
    docs/cycle16/package-matrix.md
    docs/cycle16/research-registration.md
    docs/cycle16/reuse-counterexample.md
    docs/cycle16/finite-paths.md
    docs/cycle16/learning-and-transfer.md
    docs/cycle16/evidence-semantics.md
    docs/cycle16/performance-and-proofs.md
    docs/cycle16/reproduction.md
    docs/cycle16/architecture-decision.md

Each package must report separately:

- Engineering completion.
- Research outcome.
- Evidence location.
- Remaining limitation.

---

## 7. Acceptance Gates

### Mandatory engineering gates

1. Native runtime and calculus unchanged.
2. Operational legality preserved.
3. No host-side clearance or attack adjudicator.
4. No descriptor-key fallback.
5. No forged, stripped, or per-firing evidence stamps.
6. Relative domain knowledge remains coordinate-independent.
7. Unknown and incomplete states remain distinct.
8. Native input/output provenance retained.
9. Checkpoint replay and ancestry handling verified.
10. No remote write.

### Finite-composition research gate

Demonstrate a two-cell positive consequence from raw observations through native derivation, if supported.

Required controls:

- Each essential emptiness premise removed separately.
- Finite rule removed.
- Relevant blocker introduced.
- State binding changed.
- Unfamiliar entities supplied.

A direct diagnostic operator call does not pass this gate.

### Learning research gate

Show native revision of the registered rule and its effect on held-out support.

Report whether the effect changes classification, only confidence, or neither.

Do not claim structure learning from supplied templates.

### Transfer research gate

Report unseen entities, locations, source episodes, and coarse geometry separately.

Do not count transformed variants or attacker-kind substitutions as independent geometry evidence.

### Generic-reuse research gate

Claim generic reuse only if the unchanged native system actually supports it with honest provenance and appropriate counterexamples.

Finite unrolling does not pass this gate.

---

## 8. Research Targets

| Area | Target |
|---|---|
| Failure localization | Minimal symbolic and chess counterexamples |
| Main comparison | Recursive versus finite two-cell encoding |
| Occupancy coverage | All nine E/O/U combinations |
| Native interventions | Rule, premise, state, role, blocker, and ancestry controls |
| Learning | Native revision with explicit conditional admission |
| Held-out episodes | Aim for at least 24, with honest group accounting |
| Provenance | Stable rule and training stamps throughout |
| Preservation | Complete established legal gates |
| Scope | No new preference campaign or automatic move selection |

No target authorizes lowering thresholds, altering native semantics, or filtering unsuccessful cases from the report.

A negative research result is acceptable when it precisely identifies the unsupported step.

---

## 9. Authorization and Execution Contract

Authorized:

- Local source changes.
- Pinned read-only source inspection.
- Existing evidence restoration.
- Native experiments.
- Small controlled corpus generation.
- Training and evaluation.
- Tests, reports, benchmarks, and local commits.

Not authorized:

- GitHub push.
- Pull requests or releases.
- Artifact uploads.
- External deployment.
- Upstream changes.
- New evidence-policy implementations.
- New native inference operators.
- Legal checkpoint changes.
- Strategic move selection.
- Deleting or rewriting historical evidence.

Previous pushes do not authorize a push for this cycle.

Complete all feasible packages without milestone-by-milestone approval.

If one experiment fails, preserve it and continue independent work.

Stop only for genuinely blocking dependencies or actions outside this authorization.

---

## 10. Final Codex Response

Return:

1. Starting and ending commits.
2. Branch and working-tree state.
3. Local commit list.
4. Confirmation that no remote write occurred.
5. Eight-package completion matrix.
6. Minimal recursive failure and implicated stamp overlap.
7. Recursive versus finite two-cell results.
8. All nine occupancy outcomes.
9. Clear, attack, and exposure results separately.
10. Supplied versus learned rule effects.
11. Transfer and ancestry-grouping results.
12. Duplicate, diamond, cycle, and shared-training controls.
13. Budget and ordering sensitivity.
14. Raw-proof versus reconstructed-witness scope.
15. Performance and storage measurements.
16. Legal preservation and historical-file verification.
17. Clean reproduction scope.
18. Known limitations.
19. Evidence-policy decision.
20. Recommended next experiment.

Every major claim must point to executable evidence.

Do not summarize “all packages delivered” as “all research questions solved.”

---

## 11. Next-Cycle Decision

Use the result to choose a focused follow-up.

### Finite two-cell reasoning works reliably

Consider a separately registered bounded path family, or one additional consequence family.

Do not assume that extending finite encodings establishes generic recursion.

### Learned support exposes additional overlap failures

Prioritize the distinction between shared model uncertainty and repeated observation evidence.

Prepare an authorization request for a precisely specified research change, not an undocumented patch.

### The finite representation does not work

Keep the problem minimal and resolve the exact missing binding, semantic, confidence, or execution condition.

Do not return to broad preference learning as a substitute.

### Generic reuse becomes defensible under existing mechanisms

Test additional path lengths and evidence-sharing structures before making a general claim.

Preserve the previous runtime and failure cases as regression evidence.

---

## Final Objective

Cycle 16 must make one boundary precise:

**Can native PLN combine the raw observations for a two-cell path without falsifying independence or bypassing its evidence guard?**

The desired result is an inspectable native derivation—or a minimal, reproducible explanation of why it remains unsupported.

A finite template may be useful. A reusable recursive rule may require different evidence semantics. Those are distinct findings.

Keep that distinction explicit.

**Relative facts describe the environment. Declarative rules express the hypotheses. Native PLN performs the supported inference. Provenance records what the conclusion actually depends on.**