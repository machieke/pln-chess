# Blocker-move consequences

The target is **occupancy-constrained sliding influence**, including influence
on a friendly occupied destination. It is not legal capture eligibility or full
move legality. The evaluation-only reference uses python-chess `Board.attacks`
for the specified attacker. Unknown relevant occupancy or missing query entities
has no binary reference label.

Stage A supplies an explicitly marked attack premise and asks for exposure of
the original actor's king. The native chain also requires the correct target
kind, target owner, attacker owner, actor and state. It succeeds for the actor's
king and abstains for the tested ordinary target or friendly attacker. This is
not credited as deriving attack from occupancy.

Stage B removes that premise. Native inference derives an attack across one
empty intervening cell, and can continue to the correctly bound exposure result.
It derives `NoAttack` when a specified ray member is occupied. All relevant
premises remain explicit. The [Stage A transcript](../../artifacts/cycle15/representative/stage-a-actor-king.json),
[Stage B exposure](../../artifacts/cycle15/representative/stage-b-exposure.json),
and [one-cell learned attack](../../artifacts/cycle15/representative/learned-baseline.json)
retain exact programs and outputs.

| Required scenario | Observed distinction |
| --- | --- |
| Sole blocker leaves a one-cell path | Negative before; positive after |
| Blocker moves along a longer ray | Negative support remains |
| Second blocker remains | Negative support remains |
| Unknown relevant cell | Unknown; missing observation is not empty |
| Unrelated move | Blocked relationship remains negative |
| Attacker removed | Invalid query domain and no attack support |
| Target removed or replaced under another identity | Original target query has no support |
| Renaming or translation | One-cell result preserved |
| Ordinary versus actor's king; friendly source | Attack and exposure remain distinct |
| Stale state facts | Correctly indexed facts do not change state |
| Competing occupancy, low-level audit | Positive and contrary support both exposed |

The [intervention receipt](../../artifacts/cycle15/diagnostics/interventions.json)
contains every dependent scenario. The public state API rejects conflicting
occupancy before reasoning; the low-level audit intentionally injects it to
test conflict visibility.

## Composition boundary

Longer empty paths are unsupported in the tested grammar. Extending an already
derived empty tail would reuse the recursive rule's stamp, which overlaps the
tail's ancestry. The native guard rejects that combination. The same limitation
appears in the [minimal recursive-chain probe](../../artifacts/cycle15/representative/reused-recursive-rule.json).
The [generous chess run](../../artifacts/cycle15/representative/long-path-generous.json)
also fails to produce attack support. This is not replaced by Python clearance.

Removing `clear-one` alone does not remove the independent one-cell derivation
through empty-tail initialization and one extension. Removing the essential
emptiness observation or the sole applicable terminal attack rule does remove
support. Reports identify surviving support instead of demanding an unjustified
classification flip.

The host compares before/after endpoint results. The native system has not
derived a truth value for “the supplied move created the attack.”
