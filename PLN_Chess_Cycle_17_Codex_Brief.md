# PLN Chess — Cycle 17 Consolidated Engineering Brief

## Shared Learned Evidence and Composable Native Inference

**Repository:** https://github.com/machieke/pln-chess
**Starting commit:** `63fbf4a198d15cc27c8ad15865be84bfdb871c28`
**Starting branch:** `cycle16-native-path-composition`
**Delivery branch:** `cycle17-shared-evidence-semantics`
**Operational baseline:** Unchanged accepted Cycle 12 legal checkpoint
**Execution:** One consolidated autonomous engineering assignment
**Delivery:** Implementation, native experiments, mathematical reference tests, evidence, documentation, tests, commits, and a verified GitHub push

**Explicit publication authorization:**
Commit the completed work and push the delivery branch to the existing
`machieke/pln-chess` repository. Do not stop at local commits.

This authorization does not permit force-pushing, changing the default branch,
merging into master, publishing releases, deploying services, changing upstream
PLN, or modifying the accepted operational model.

---

## 1. Mission

Cycle 17 must investigate whether separately learned relational rules can compose
through the existing native PLN reasoner without misrepresenting shared evidence.

The primary question is:

> Can the learned two-cell clearance rule and a learned terminal attack rule
> compose when their registered training ancestry is genuinely disjoint, and
> how does behavior change when that ancestry overlaps?

The second question is:

> What information and mathematical assumptions would be required to support
> shared uncertain knowledge without counting repeated observations as new evidence?

These are separate investigations.

The first is an executable native-PLN experiment using the unchanged runtime.

The second is an isolated semantics study. It may include exact mathematical
reference calculations, but it must not introduce a replacement inference
operator or feed reference calculations into chess inference.

Do not expand path lengths, resume broad preference learning, or implement
autonomous move selection.

---

## 2. Starting Evidence and Scope

Cycle 16 reported:

- Native binding of reusable rules and shared roles.
- A supplied finite two-cell rule deriving clearance and attack.
- Learned clearance composed successfully with supplied terminal rules.
- Learned clearance combined with learned downstream rules remained blocked
  when their training ancestry overlapped.
- A retained witness identified eleven overlapping training-game stamps.
- Recursive reuse remained blocked by the repeated rule's own stamp.
- The operational legal checkpoint and native calculus remained unchanged.

The finite experiment's held-out panel contained 72 dependent endpoints from
24 source games. The supplied finite and learned-clearance arms classified all
72 correctly. The shared learned-chain arm classified 42 negatives and left
30 positives unknown.

These are repository-reported results. Reproduce the relevant evidence before
using it as a baseline.

### Preserve the target definition

The chess target remains occupancy-constrained sliding influence.

It is not:

- Full legal capture eligibility.
- General move legality.
- Universal king safety.
- Strategic preference.
- Optimal move choice.

Keep `Clear`, `Attack`, `NoAttack`, and optional role-correct exposure separate.

A negative attack result does not prove negative clearance or king safety.

---

## 3. Required Source Review

Read:

    docs/cycle16/engineering-report.md
    docs/cycle16/evidence-semantics.md
    docs/cycle16/learning-and-transfer.md
    docs/cycle16/reuse-counterexample.md
    docs/cycle16/architecture-decision.md
    docs/cycle16/reproduction.md

    artifacts/cycle16/supplement/shared-training-witness.json
    knowledge/cycle16/finite_two.metta

    research/cycle15/native_reasoner.py
    research/cycle15/knowledge.py
    vendor/pln/lib_pln.metta
    configs/runtime-lock.json

Discover the actual Cycle 16 training, corpus, checkpoint, evaluation, and
acceptance paths from the checkout.

Do not substitute guessed filenames or inferred experiment results.

Preserve the runtime pins:

- PLN: `4405956947c4b53c7ff01bd565aa3b114bc970a1`
- PeTTa: `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`

Verify the source hashes against the actual runtime lock.

---

## 4. Non-Negotiable Boundaries

### Native experiments

- Keep the native inference calculus and evidence guard unchanged.
- Preserve native schema binding and derivation.
- Do not strip, rename, salt, or regenerate evidence identities to avoid overlap.
- Do not assign fresh rule evidence per application.
- Do not clone the recursive rule under different names.
- Do not replace clearance or attack inference with a host adjudicator.
- Do not use direct operator diagnostics as a fallback production answer.
- Preserve missing, conflicting, unsupported, and incomplete outcomes separately.

### Learning

- Use native revision for rule truth values.
- Preserve real source ancestry across rules and checkpoints.
- Keep rule structure supplied and explicitly documented.
- Do not claim structure discovery.
- Unknown observations are not negative labels.
- Unsatisfied antecedents do not automatically contradict a conditional.
- Test labels and reference-engine results cannot enter inference facts.

### Architecture

- Learned domain knowledge remains piece-relative.
- Absolute coordinates are environmental/provenance data, not learned constants.
- Keep all experiments outside the accepted operational path.
- Do not change the legal checkpoint or operational defaults.
- Do not add preference learning, search, or move selection.

### Mathematical laboratory

Host-side exact arithmetic is allowed only in an isolated research-reference
module. Its results are not native PLN truth values, learned chess parameters,
or replacement inference outputs.

A different evidence policy may be specified and evaluated conceptually.
It must not be implemented in the native runtime during this cycle.

### Publication

Commit and push the completed experimental branch.

Do not force-push, merge into master, publish releases, or upload bulk evidence
without separate authorization.

---

## 5. Claims That Must Remain Separate

Report these claims independently:

1. **Execution:** The native reasoner applies the registered statements.
2. **Learning:** Native revision changes the targeted rule parameters.
3. **Recorded provenance separation:** The two learned rules have no shared
   registered training ancestry.
4. **Native composability:** Their learned statements combine successfully.
5. **Statistical independence:** A stronger assumption not established merely
   by different source IDs or nonoverlapping stamp sets.
6. **Generic rule reuse:** Repeated use of one recursive rule, which remains a
   separate problem.
7. **Shared-evidence semantics:** A defensible interpretation of combining
   uncertain knowledge estimated from overlapping observations.

A successful disjoint-training chain does not establish claims 5, 6, or 7.

“Both targeted rules learned” does not mean every supplied chess template,
geometric convention, or observation-trust assumption was learned.

---

## 6. Execution Order

Complete eight packages in one consolidated run.

1. Preserve and register.
2. Reproduce the real shared-training failure.
3. Construct matched shared/disjoint training arms.
4. Run native composition, overlap, and removal experiments.
5. Build the isolated mathematical reference laboratory.
6. Assess evidence semantics and architecture options.
7. Verify preservation, proof integrity, and resource use.
8. Package, commit, push, and verify remote delivery.

Do not acquire a large new external corpus.

Use existing licensed sources where sufficient. Keep synthetic controls explicitly
separate from naturally sourced episodes.

If the native disjoint chain fails, first localize that failure. Do not assume
the intended outcome and proceed as though it succeeded.

---

# C17-01 — Baseline Preservation and Registered Study

## Objective

Establish a reproducible starting point and freeze the experimental comparisons.

Verify:

- Starting commit and ancestry.
- Clean or explicitly accounted-for working-tree state.
- Runtime and vendor hashes.
- Accepted legal checkpoint file hash and semantic identity.
- Cycle 16 knowledge structure and checkpoints.
- Relevant evidence manifests.
- Remote repository identity.

Do not destructively reset unrelated work.

Create the delivery branch from the pinned baseline, or resume an existing branch
only after verifying its ancestry and ownership of the changes.

### Baseline fixtures

Reproduce:

- Supplied finite two-cell positive result.
- Learned-clearance/supplied-terminal result.
- Shared learned-chain failure.
- The eleven-stamp witness.
- Recursive rule-reuse failure.
- Representative negative and unknown occupancy cases.
- Duplicate, diamond, and cycle controls.

Restore externalized evidence using existing verified mechanisms when required.
Do not fabricate omitted baseline evidence.

### Study registration

Create:

    docs/cycle17/research-registration.md

Register:

- Primary hypotheses.
- Target rule pair.
- Training-set construction.
- Ancestry definitions.
- Per-rule sample sizes.
- Development and test groups.
- Overlap conditions.
- Truth-value and threshold policies.
- Budget ladder.
- Mathematical reference cases.
- Resource and storage ceilings.
- Failure-localization criteria.
- Publication plan.

Historical test cases are regression evidence, not untouched new evaluations.

**Deliverables:** Baseline receipt, registration, frozen manifests, and identified
gaps in baseline reproduction.

---

# C17-02 — Preserve and Localize the Real Learned-Chain Failure

## Objective

Keep the actual Cycle 16 failure central to the study.

Do not replace it with only a convenient synthetic example.

For the retained witness, record:

- The learned clearance statement.
- The terminal attack partial implication.
- Their native truth values.
- Their rule identities.
- All contributing observation and training stamps.
- Their exact stamp intersection.
- Native structural matching result.
- Native guard result.
- Final derivation outcome.

Distinguish:

1. Statements exist and structurally match.
2. The guard admits or rejects their combination.
3. The scheduler actually produces the desired conclusion.
4. The conclusion crosses a registered display threshold.

A diagnostic direct statement-level inference can establish structural possibility.
It does not establish that the guarded native process returned the answer.

### Failure categories

Classify each missing result as one or more of:

- Missing statement.
- Role/state mismatch.
- Shared rule identity.
- Shared training ancestry.
- Shared environmental evidence.
- Confidence below threshold.
- Queue eviction or remaining tasks.
- Timeout or malformed execution.
- Unsupported query domain.

Do not attribute every unknown result to provenance overlap.

Preserve exact programs and native outputs.

**Deliverables:** Real-case failure receipt, minimal reproducer, and cause taxonomy.

---

# C17-03 — Matched Shared and Disjoint Training Design

## Objective

Test whether the unchanged reasoner can compose both learned empirical links
when their registered training sources do not overlap.

Use `clear-two` and one terminal attack rule as the primary pair.

Start with the rook rule because the historical witness has adequate rook support.
Bishop and queen remain secondary capability checks unless independently supported
training strata are available.

## 3.1 Construct two registered training groups

Create two disjoint ancestry sets:

    G_A
    G_B

Aim for at least twelve eligible root episodes in each set.

Use the same registered eligibility rules and balance observable geometry,
occupancy, and source characteristics where practical.

Each episode must be eligible for the targeted conditional evidence. Preserve
the exact admission logic.

Choose groups before running the new final inference evaluation.

Do not create disjointness by:

- Renaming one game.
- Reassigning a transformed copy.
- Splitting one episode's descendants between groups.
- Replacing ancestry with a checkpoint-specific hash.
- Removing shared ancestors from the ledger.

Report repeated openings and other plausible dependence that source grouping
does not eliminate.

## 3.2 Crossed training design

Fit these four native-learned combinations:

| Arm | Clearance training | Terminal-rule training |
|---|---|---|
| S-AA | G_A | G_A |
| S-BB | G_B | G_B |
| D-AB | G_A | G_B |
| D-BA | G_B | G_A |

This reciprocal design helps distinguish an overlap effect from a fortunate
choice of one training subset.

Keep per-rule admitted sample counts and observation-confidence policy matched
where the real data permit.

Report both:

- Number of samples per rule.
- Number of unique source episodes across the pair.

A shared arm and a disjoint arm cannot simultaneously have identical per-rule
counts and identical total unique-source counts. Do not conceal that difference.

## 3.3 Required anchors

Also retain:

- The original Cycle 16 shared-chain checkpoint.
- Supplied-clearance/supplied-terminal control.
- Learned-clearance/supplied-terminal control.
- Untrained-prior control.
- Rule-removal controls.

Do not silently substitute a supplied terminal rule in the disjoint learned arm.

List every rule actually used in the successful chain and identify whether its
structure, truth value, and observation trust were supplied or learned.

## 3.4 Truth-value comparability

Compare raw native rule parameters before comparing final answers.

With equally weighted positive admissions, some arms may naturally have identical
rule truth values despite different ancestry.

When that occurs, preserve it as a strong matched diagnostic.

Do not manually overwrite truth values to manufacture equality.

If rule parameters differ, report the confounding and include parameter-sensitive
analysis. Do not claim that ancestry alone explains an outcome without support.

## 3.5 Data admission and labels

A blocked path does not contradict an implication whose antecedent requires both
cells to be empty.

For the terminal rule, document how the training antecedent is established.
Evaluation-side checks are permitted for evidence preparation but may not inject
`Clear` into held-out inference.

Unknown or invalid observations remain excluded or separately classified.

All-positive admitted outcomes must be disclosed. They do not establish
negative-example learning or robustness to noisy supervision.

**Deliverables:** Group manifests, four learned model pairs, native revision
traces, admission/exclusion receipts, and parameter comparisons.

---

# C17-04 — Composition, Overlap Sweep, and Transfer Controls

## Objective

Evaluate whether provenance overlap predicts the native composition boundary,
without changing the guard or forging evidence.

## 4.1 Stagewise queries

For every arm, query separately:

    Clear(attacker, target, shape, state)
    Attack(attacker, target, state)

Evaluate optional correctly bound exposure only as a separate secondary result.

Do not let successful clearance count as successful downstream composition.

Record both positive and contrary channels.

## 4.2 Controlled overlap sweep

After the reciprocal primary arms, run a bounded overlap study.

Keep clearance training fixed to G_A. Construct terminal-rule training sets with
the same registered sample count and actual overlap levels such as:

    0 shared sources
    1 shared source
    approximately half shared sources
    all shared sources

Select membership by a frozen deterministic policy.

Each shared observation keeps its real identity across rules.

Every distinct source must correspond to an actual different registered episode,
not a new label for old evidence.

This intervention changes the actual admitted training sets. It is not a
stamp-deletion experiment.

Record native learned parameters and overlap for each arm.

Do not assume a gradual effect: the current guard may create a sharp admissibility
boundary. Test rather than encode that expectation.

## 4.3 Held-out evaluation

Aim for at least six development roots and twenty-four new held-out source roots.

Use one primary query per source episode, with dependent occupancy variants.

Exclude training and development ancestry from final testing.

Retain the historical Cycle 16 panel as a separate regression panel.

Avoid selecting only the first common opening arrangement. Use a preregistered
stratified policy over available relative directions, positions, and game phases.

Do not manufacture broad geometry independence in a narrow two-cell problem.

Report novelty separately for:

- Source episodes.
- Entity bindings.
- Endpoint locations.
- Coarse relative geometry.
- Query ancestry.
- Underlying collection or publisher.

Where evidence is insufficient for a target, report the shortfall.

## 4.4 Occupancy controls

Preserve all nine E/O/U combinations:

- EE may support the positive influence target.
- EO, OE, OO, OU, and UO contain a known obstruction.
- EU, UE, and UU remain unresolved unless separately justified evidence exists.

Do not infer king safety from `NoAttack`.

Use state, role, renaming, translation, and relevant-blocker interventions.

## 4.5 Removal and replay controls

Require:

- Remove the learned clearance rule.
- Remove the learned terminal rule.
- Remove either necessary emptiness premise.
- Replace one learned rule by its untrained prior.
- Remove one source group and perform an actual native refit.
- Replay identical training evidence.
- Replay identical inference facts.
- Supply contradictory low-level evidence in a separate audit.
- Break a shared role or state binding.

Preserve surviving independent derivations when they exist.

## 4.6 Metrics

Report numerators and denominators for:

- Clearance derivation.
- Attack derivation.
- Correct positive support.
- Correct negative support.
- Unknown.
- Conflicting.
- Incomplete.
- Below-threshold support.
- Overlap-rejected matched statements.

Before/after states and occupancy variants do not enlarge the independent root
count.

Do not claim generalization from identical endpoint locations merely because
entity identifiers changed.

**Deliverables:** Stagewise comparison, overlap sweep, held-out evaluation,
interventions, and complete failure census.

---

# C17-05 — Isolated Mathematical Reference Laboratory

## Objective

Specify what “shared uncertain knowledge” could mean and identify what the
current representation does not determine.

This laboratory is not a new PLN inference implementation.

Its outputs must remain outside:

- Native chess inference.
- Rule checkpoints.
- Operational truth values.
- Display classifications.
- Production caches.

Use a module boundary that production code cannot import.

Exact finite enumeration or rational arithmetic is preferred for small examples.
Monte Carlo is unnecessary for the primary cases.

## 5.1 Define the quantities

Distinguish:

- A rule's logical structure.
- An uncertain parameter associated with that rule.
- Training observations informing that parameter.
- Current environmental observations.
- Distinct uses of a parameter.
- Repeated use of the same observed event.
- A proof application's identity.
- The conclusion whose predictive uncertainty is being assessed.

Do not automatically interpret native `(strength, confidence)` as a Beta
distribution or a full Bayesian posterior.

Any illustrative interpretation must be explicitly stated and must not be
presented as the semantics already implemented by the native runtime.

## 5.2 Same marginals, different joint dependence

Construct exact reference models with two binary uncertain parameters whose
marginals are each 1/2.

Compare:

- Independent parameters.
- Perfectly positively associated parameters.
- Perfectly negatively associated parameters.

The joint success event can differ even though the marginal means are identical.

Use this as an identifiability test:

> Do the retained native truth values and flat provenance stamps specify the
> joint information required for the proposed inference?

Do not claim that these toy parameters are measured chess-rule probabilities.

## 5.3 Reusing one uncertain parameter

Use a separate finite example:

    theta is 1/4 or 3/4, each with probability 1/2.

Under a stated model of two conditionally independent applications sharing theta:

    joint success = E[theta^2] = 5/16.

Under a different model with independently redrawn parameters:

    joint success = E[theta]^2 = 1/4.

These are different assumptions, not interchangeable formulas.

Also distinguish both from repeating the very same event, where:

    E AND E = E.

Do not use any of these reference results as a replacement PLN formula.

## 5.4 Observation reuse and posterior reuse

Demonstrate the difference between:

- Conditioning once on a dataset and using the resulting uncertain knowledge
  in several predictions.
- Applying the same observation's likelihood twice as if two independent
  observations had occurred.
- Learning two parameters from a common dataset under a model that couples them.
- Learning two parameters under an explicitly factorized model.

Shared data do not imply a particular correlation automatically.
Disjoint record IDs do not prove statistical independence.

Record the actual assumptions in each case.

## 5.5 Required control structures

Include reference tests for:

- Duplicate observation.
- Same parameter used twice.
- Two parameters learned from shared observations.
- Disjoint evidence under a stated factorization assumption.
- Diamond-shaped dependence.
- Circular derivation without new external evidence.
- Unequal premise uncertainty.
- A deliberately false hypothesis.
- Missing dependence information.

Where a conclusion is not identified by the supplied information, return bounds
or “not identified under these assumptions,” not an invented point estimate.

## 5.6 Comparison with native behavior

Compare the native outcome and reference outcome without asserting they must
match numerically.

Classify differences as:

- Different intended semantics.
- Different retained information.
- Conservative admissibility restriction.
- Insufficiently specified confidence interpretation.
- Potential implementation issue supported by a minimal counterexample.

Do not declare the native calculus mathematically wrong merely because it differs
from an independently chosen reference model.

**Deliverables:** Executable reference cases, assumptions manifest, exact results,
and a strict import-boundary test.

---

# C17-06 — Evidence Representation and Architecture Decision

## Objective

Produce an implementation-ready problem specification without implementing a
new guard or truth-value calculus.

## 6.1 Diagnostic provenance model

Represent, for analysis only:

    schema_id
    parameter_generation_id
    training_observation_ids
    training_ancestry_groups
    environmental_observation_ids
    application_id
    parent_derivations

Map these categories to the existing native stamps without changing them.

Application IDs are trace identities, not independent evidence.

Distinct schema IDs do not prove independent training support.

## 6.2 Explain the native results

Answer:

- Does D-AB compose?
- Does D-BA compose?
- Do shared arms reproduce the overlap failure?
- Is clearance still derived when attack is blocked?
- Does one overlapping source suffice to affect admissibility?
- Are any differences caused by unequal native rule parameters?
- Do environmental stamps or auxiliary rules introduce additional overlap?
- Does the recursive-rule failure remain even under disjoint training?

Do not assume the disjoint chain will succeed. Report other failures precisely.

## 6.3 Evaluate architectural options

### Option A — Retain strict disjointness

Describe what can be achieved under the current policy.

Report the cost of requiring separate training support for composable rules and
why this is not automatically a satisfactory general learning architecture.

### Option B — Separate provenance roles

Specify how schema identity, parameter uncertainty, and observation evidence
could be represented distinctly.

State what this representation would and would not solve.

Do not imply that typed provenance alone supplies correct correlated inference.

### Option C — Richer uncertainty/dependence semantics

Identify the additional joint information, approximation assumptions, or bounds
that a future inference mechanism would require.

Describe mathematical and engineering obligations.

No implementation is authorized here.

## 6.4 Requirements for a future proposal

Any proposed policy change must address:

- Repeated uncertain parameters.
- Shared environmental observations.
- Duplicate delivery.
- Common-ancestor diamonds.
- Cycles without new evidence.
- Conflicting observations.
- Revision versus application.
- Probability and confidence interpretation.
- Computational cost.
- Backward compatibility.
- Evidence that must be retained for auditing.

Do not propose “ignore rule stamps” as a complete solution.

**Deliverables:** Diagnostic provenance schema, semantics specification,
counterexamples, and a clear recommendation.

---

# C17-07 — Preservation, Proof Integrity, and Performance

## Objective

Protect the working learner and make the research reproducible.

## 7.1 Native boundaries

Preserve:

- Native source hashes.
- `PLN.Derive` and `PLN.Query`.
- `StampDisjoint`.
- Existing statement rules.
- Native revision and truth-value formulas.
- Stable rule and training identities.

No fallback to host clearance or direct numerical answer construction.

Run inference with evaluation-oracle access disabled.

## 7.2 Proof scope

Retain:

- Exact native input program.
- Initial facts and rules.
- Model and runtime identities.
- Native selected-task output.
- Returned beliefs and stamps.
- Query answers.
- Guard diagnostics.
- Process receipts.
- Training and ancestry manifests.

Distinguish an observed execution trace from a post-hoc native-revalidated witness.

Do not fabricate a complete fired-rule tree.

## 7.3 Budget controls

Use the registered small, medium, and generous budgets.

Separate overlap failure from:

- Unprocessed tasks.
- Eviction.
- Timeout.
- Missing marginal assumptions.
- Low-confidence results.
- Malformed input/output.

Use generous diagnostics only for localized failures.

Do not raise budgets until an expected answer appears and then omit lower-budget
failures.

## 7.4 Preservation gates

Verify the accepted legal checkpoint remains byte-identical.

Preserve:

- 206 legal shards and 584,112 candidate-row classifications/proofs.
- 287 negative evidence-removal controls.
- 27 history controls.
- Both known en-passant recoveries.
- 76 controlled legal holdouts.
- Historical source, checkpoints, and evidence.
- Existing public APIs.

Use the actual registered preservation tools and manifests.

Run targeted checks during development and the complete source-bound suite once
the final executable research source is frozen.

If a gate cannot run, report it as blocked. Do not substitute a smoke test and
claim full acceptance.

## 7.5 Performance and resources

Benchmark:

- Shared-chain inference.
- Disjoint-chain inference.
- Recursive control.
- Negative and unknown occupancy.
- Representative distractor-rich inputs.
- Stored-answer retrieval.
- Full proof reconstruction.

Report cold inference separately from cached retrieval.

Track wall time, native processes, selected tasks, retained beliefs, memory,
proof bytes, and evidence size.

Keep reference-laboratory cost separate from native inference.

## 7.6 Reproduction

A clean checkout must be able to reproduce the minimal shared/disjoint experiment
using small checked-in fixtures and checkpoints, without downloading all historic
bulk evidence.

Full historical verification may require separate restored evidence. Document it
as a distinct reproduction level.

**Deliverables:** Acceptance matrix, boundary tests, native receipts, benchmark
results, and clean-reproduction instructions.

---

# C17-08 — Delivery, Commit, Push, and Remote Verification

## Objective

Deliver a reviewable GitHub branch, not merely a local completion message.

## 8.1 Required implementation organization

Adapt to repository conventions:

    research/cycle17/
        study.py
        provenance.py
        reference_models.py
        cli.py

    training/cycle17_shared_evidence.py
    evaluation/cycle17_shared_evidence.py
    tests/test_cycle17_*.py

Reuse the existing native adapter and declarative rules where possible.

Do not create an alternative probabilistic engine inside the reference module.

## 8.2 Required reports

Produce:

    docs/cycle17/engineering-report.md
    docs/cycle17/package-matrix.md
    docs/cycle17/research-registration.md
    docs/cycle17/shared-chain-baseline.md
    docs/cycle17/training-design.md
    docs/cycle17/composition-results.md
    docs/cycle17/reference-semantics.md
    docs/cycle17/evidence-policy-decision.md
    docs/cycle17/performance-and-proofs.md
    docs/cycle17/reproduction.md
    docs/cycle17/publication.md

Include small machine-readable summaries, checkpoints, representative native
programs, outputs, model comparisons, and evidence manifests.

The principal finding must be inspectable from the pushed repository.

Do not leave every decisive witness available only through an absolute path on
the development machine.

## 8.3 Engineering status versus research outcome

For each package report:

- Implementation status.
- Executed verification.
- Research result.
- Unresolved limitations.
- Supporting artifact paths.

Negative research findings are still to be committed and pushed.

Do not label experimental code as an accepted operational model.

---

## 7. Commit and Push Requirements

### Authorization

You are explicitly authorized and instructed to:

1. Create local implementation commits.
2. Commit reports, tests, compact evidence, and manifests.
3. Push the completed research branch to `machieke/pln-chess`.
4. Verify the remote branch SHA.

No additional permission request is required for that branch push.

### Branch safety

Use:

    cycle17-shared-evidence-semantics

Confirm the branch descends from:

    63fbf4a198d15cc27c8ad15865be84bfdb871c28

Do not reset an existing branch containing unrelated work.

If the intended branch already exists remotely, inspect it first. Continue only
when the update is a safe fast-forward of the intended work.

Otherwise use a clearly named new branch with a documented suffix.

Never use:

    git push --force
    git push --force-with-lease
    git push --mirror
    git push --all

Do not push to master or change the default branch.

Do not create a release, upload large assets, or merge a pull request.

### Verify the remote repository

Inspect both fetch and push URLs.

The authorized destination is exactly:

    machieke/pln-chess

An SSH or HTTPS URL for that repository is acceptable.

Check multiple push URLs and URL rewrites. Do not publish to an unrelated mirror
or fork merely because it is called `origin`.

Do not print credentials or token-bearing URLs in reports.

---

## 8. Publication Size and Evidence Policy

Prevent another oversized push.

### Keep in ordinary Git

- Source and tests.
- Domain/schema declarations.
- Dependency and runtime manifests.
- Reports and compact result tables.
- Small experimental checkpoints.
- Decisive native witnesses.
- Reproduction commands.
- Bulk-artifact hashes and availability information.

### Keep outside ordinary Git

- Native environments and dependency caches.
- Full repeated historical proof exports.
- Large databases.
- Bulk benchmark output.
- Multi-gigabyte transcript archives.
- Duplicated evidence packs.

Use existing content-addressed evidence tooling where practical.

No new release upload or paid storage is authorized.

Retain bulk evidence locally with a checksum manifest and offline restoration
instructions. State clearly which artifacts are not remotely available.

### Project publication budgets

Use these conservative project budgets for new Cycle 17 Git content:

- No newly introduced blob larger than 10 MiB.
- Aim for at most 100 MiB of new unique Git blob content across the entire
  Cycle 17 commit range.

These are project budgets, not claims about platform limits.

Audit all new reachable blobs, not merely the current working tree. A large file
added in an earlier unpublished commit still matters after deletion from the tip.

Check for secrets, private data, temporary paths, and accidental dependency
vendoring before committing.

Do not blanket-ignore all artifacts: the minimal scientific evidence must remain
reviewable.

### If the size gate fails

Preserve the local evidence.

Correct only the new, unpublished Cycle 17 history as necessary, with a backup
and documented source mapping.

Do not rewrite already published historical commits.

Revalidate source/evidence identities after repackaging.

Do not repeatedly retry an oversized push without addressing the identified
cause.

---

## 9. Required Publication Procedure

Use the following sequence after the final code and evidence checks.

### Step 1 — Commit the intended work

Stage only reviewed source, tests, documentation, compact artifacts, and manifests.

Create meaningful commits. There is no required commit count.

Verify:

    git status --short
    git log --oneline <starting-commit>..HEAD

The final working tree should be clean apart from explicitly documented ignored
local evidence outputs.

### Step 2 — Run publication preflight

Verify:

- Correct repository.
- Correct branch.
- No unrelated changes.
- No secret-bearing files.
- New-blob size inventory.
- Source-bound acceptance scope.
- Report links.
- Minimal reproducer availability.
- No unsupported claim that bulk local artifacts were uploaded.

A dry-run push can be useful but is not proof of publication.

### Step 3 — Push the explicit branch

After confirming `origin` points to the authorized repository:

```bash
set -euo pipefail

BRANCH="cycle17-shared-evidence-semantics"

test "$(git branch --show-current)" = "$BRANCH"
test -z "$(git status --porcelain)"

LOCAL_HEAD="$(git rev-parse HEAD)"

git push --set-upstream origin "HEAD:refs/heads/${BRANCH}"

REMOTE_HEAD="$(
  git ls-remote --exit-code origin "refs/heads/${BRANCH}" |
  awk 'NR == 1 { print $1 }'
)"

test -n "$REMOTE_HEAD"
test "$LOCAL_HEAD" = "$REMOTE_HEAD"

printf 'Verified publication: %s %s\n' "$BRANCH" "$REMOTE_HEAD"
```

If a documented alternate branch was required, use its actual name consistently.

Do not assume this command block replaces the earlier remote-identity and
size checks.

### Step 4 — Independently verify availability

Query the branch against the canonical repository or GitHub API and confirm
the same SHA.

Confirm that the engineering report and minimal reproducer are accessible at
that commit.

Do not confuse an existing remote-tracking reference with a new remote check.

### Step 5 — Report publication honestly

A push is complete only after the remote ref matches the final local commit.

If authentication, network access, repository policy, or size prevents pushing:

- Preserve all local work.
- Record the exact error.
- State “committed locally; push blocked.”
- Do not claim “pushed.”

Do not bypass authentication or branch protection.

Record the final remote-verification receipt outside the tracked checkout or
in the final delivery response. Avoid creating an endless sequence of commits
solely to record each commit's own final SHA.

---

## 10. Acceptance and Decision Gates

### Mandatory engineering gates

1. Operational checkpoint and source remain protected.
2. Native runtime and guard unchanged.
3. Actual provenance preserved.
4. No host answer fallback.
5. Reference mathematics remains isolated.
6. Shared/disjoint models are separately versioned.
7. Evidence replay and removals are auditable.
8. Minimal experiments reproduce from the published branch.
9. Reports distinguish engineering completion from research success.
10. Commit and remote-push status are verified and accurately reported.

### Research gates

#### Native learned-chain gate

At least one registered arm composes both learned targeted links, or the failure
is localized with a minimal witness.

Do not substitute a supplied terminal rule.

#### Overlap gate

Compare real shared and disjoint training support under matched protocols.

Do not fake overlap changes through identifier edits.

#### Semantics gate

Demonstrate what the reference examples identify and what marginal information
alone leaves undetermined.

Do not claim a new sound PLN evidence policy unless its assumptions and proof
obligations are actually established.

#### Generic-reuse gate

Retain recursive reuse as a separate unresolved or demonstrated outcome.

Disjoint training between two rules does not solve repeated use of one rule.

---

## 11. Research Targets

| Area | Target |
|---|---|
| Primary training | Two registered groups with at least 12 eligible roots each |
| Crossed study | S-AA, S-BB, D-AB, D-BA |
| Overlap study | Zero, one, partial, and full shared ancestry |
| Final evaluation | At least 24 held-out roots where feasible |
| Occupancy | All nine E/O/U cases retained |
| Dependence controls | Duplicate, shared observation, shared training, diamond, and cycle |
| Mathematical reference | Exact finite examples with explicit assumptions |
| Native calculus | Unchanged |
| Legal preservation | Complete established gates |
| Publication | Committed, pushed, and remote SHA verified |

These are targets, not permission to relabel dependent samples as independent.

A failed research hypothesis is acceptable. An undocumented inference workaround
or false publication claim is not.

---

## 12. Final Architecture Decision

Choose the evidence-supported conclusion.

### A. Disjoint learned chains work; shared chains remain blocked

This establishes a bounded native route under registered disjoint support.

Explain its limitations and whether a shared-evidence representation study is
justified next.

### B. Disjoint learned chains also fail

Localize residual overlap, binding, confidence, or resource limitations.

Do not jump directly to a generic evidence-policy change.

### C. Shared uncertainty is not identified by existing retained information

State what joint information or assumptions would be required.

Recommend an isolated future proposal only; do not implement it.

### D. A defensible semantic proposal is specified

Provide its assumptions, counterexamples, verification requirements, and migration
impact for explicit authorization.

Do not activate it during this cycle.

No outcome authorizes autonomous chess move selection.

---

## 13. Final Codex Response

Include:

1. Starting and ending commit hashes.
2. Actual branch name.
3. Working-tree status and commit list.
4. Verified remote SHA and publication status.
5. Eight-package matrix.
6. Baseline shared-chain reproduction.
7. Shared/disjoint training-group audit.
8. Raw rule parameters and ancestry overlap by arm.
9. Clearance and attack results separately.
10. Held-out positives, negatives, unknowns, conflicts, and incomplete requests.
11. Overlap-sweep and removal outcomes.
12. Mathematical reference findings and assumptions.
13. Generic-recursion status.
14. Native proof and reference-laboratory separation.
15. Legal preservation and complete test scope.
16. Performance and storage accounting.
17. Public versus locally retained evidence.
18. Clean-reproduction status.
19. Known limitations.
20. Recommended next experiment.

Link the published engineering report, package matrix, reproduction guide, and
decisive compact witnesses.

Do not use “fully learned chess reasoning” when only the two targeted conditional
parameters were learned.

Do not use “independent evidence” merely because stamps are disjoint.

Do not use “pushed” without remote verification.

---

## 14. Reference Sources

Pinned repository references:

- `docs/cycle16/evidence-semantics.md`
- `docs/cycle16/learning-and-transfer.md`
- `docs/cycle16/architecture-decision.md`
- `artifacts/cycle16/supplement/shared-training-witness.json`
- `vendor/pln/lib_pln.metta`
- `configs/runtime-lock.json`

Publication references:

https://git-scm.com/docs/git-push
https://git-scm.com/docs/git-ls-remote
https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

Use the repository's pinned native implementation as the executable source of
truth. Documentation review does not authorize runtime upgrades.

---

## Final Objective

Cycle 17 must establish whether learned relational knowledge can compose under
honest, explicitly characterized evidence arrangements.

The project needs to distinguish:

- Reusing a rule.
- Reusing an uncertain parameter.
- Reusing a training observation.
- Reusing current environmental evidence.
- Counting a proof application as if it were new information.

The native experiments should identify what works under the current guard.
The isolated reference laboratory should clarify what a future shared-evidence
mechanism would have to mean.

Preserve this principle:

**Knowledge may be reused. Evidence must not be invented. Dependence must be
represented or explicitly assumed—not erased to obtain a desired answer.**

Complete the research package, commit it, push the dedicated branch, and verify
that the final commit is available remotely.