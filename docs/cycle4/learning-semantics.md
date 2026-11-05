# Learning, dependence and decision semantics

The curriculum reuses only the 1,906 eligible Cycle 3 training records. Frozen test rows never enter training. All local, attack and condition labels are supplied at the training boundary; the production inference function receives only an observed position, model and budgets.

| Target | Training supervision | Scope |
|---|---|---|
| LocalAdmissibility | Auxiliary reference pseudo-legality; a positive legal observation also entails local support | Joint categorical baseline, excludes global king safety |
| GeometryObserved | Positive pseudo-legal or legal examples | Independent observation-conditioned support; negative legality is not assigned to geometry |
| Obstruction | Training-only auxiliary label for an individual ray cell and mover class | One-cell witness, independent of blocker distance and complete ray pattern |
| DestinationConflict | Training-only occupancy/kind label | Friendly destination or king capture observations |
| BoundaryConflict | Training-only boundary label | Destination existence observation |
| Attack | Reference successor/origin/transit attack labels in observation-role groups | Every opponent-to-king frame is sensed; no production attack adjudicator |
| Attack → exposure | Separate exposure-role contact groups | Empirical conditional, not a hard-coded axiom |
| Exposure → NotLegal | Separate legality-role contact groups | Empirical conditional, not a hard-coded veto |
| Condition → NotLegal | Dedicated source-group pools selected from training labels | Antecedent observations in those groups are withheld from that condition's learning |

Constraint bridge pools are selected deterministically by a hash ordering of eligible **training** groups. Their complete membership is in the dataset. Attack, exposure and illegality contact pools preserve the Cycle 3 partition. Every chain checks source-group intersection before applying another edge. Native truth functions themselves do not enforce stamps.

Each hypothesis starts with the existing weak `(0.5, 0.05)` prior. Native revision updates positive and negative channels separately. These channels share provenance and are never fused as independent evidence. A source group, or an explicitly declared transformation ancestor, contributes at most once to a hypothesis. Later correlated observations remain in the ledger; exclusions are counted and hashed and are reconstructible by replay. Independent conflicting observations remain in both supporting and contradicting evidence lists. Retraction removes declared source groups before deterministic replay.

This policy relies on truthful source-group and transformation-lineage declarations. It does not infer statistical independence from visual differences. In particular, different positions from one game remain one bootstrap cluster and should be one training group.

Native negation converts a supported `Not LegalMove` chain into a low-strength `LegalMove` TV. Native confidence choice selects among already supported negative conclusions of the same proposition. The local-positive projection is not inserted as a competing global-safety theorem. This semantic separation explains why a previously conflicting movement/attack case can now become supported illegal without pretending that the local movement evidence was false.

If an applicable attack conditional has mixed independent support and counterevidence in the indecisive strength band, the positive presentation abstains. If attack support exists but its chain is missing, dependent or too weak, it also abstains. All raw TVs and losing evidence remain inspectable. No custom host-side probability or confidence arithmetic combines premises.

Default display thresholds remain strength ≥0.8 for support, ≤0.2 for contradiction, and confidence ≥0.25. Conservative and coverage-oriented ablations were declared in `configs/cycle4.json` before final holdout evaluation. Validation-only empirical calibration never alters native TVs or classification thresholds.

Positive output is still **native-partial**. It says the learned local projection supports the move under its observation category; it does not establish a universal theorem that all legal-move conditions hold. Negative output can have a complete native unary constraint chain. Historical flags remain observations. The temporal API checks supplied structural transitions and records their source and uncertainty; it does not certify historical move legality.
