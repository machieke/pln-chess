# Finite two-cell composition

The supplied finite declaration produces **Clear, Attack and role-correct king
exposure** from raw two-cell occupancy. Removing it restores the recursive
arm's unknown result. This establishes native applicability and bounded finite
composition, not generic recursion. The new declaration is the only structural
difference between the complete R and F knowledge files.

```metta
(Rule clear-two (Implication (RayPath $a $t (Cons $c1 (Cons $c2 Nil)) $shape $s) (Implication (Empty $c1 $s) (Implication (Empty $c2 $s) (Clear $a $t $shape $s)))))
```

[The manifest](../../knowledge/cycle16/manifest.json) binds both full knowledge
files and their structure identities. All eleven historical declarations are
byte-preserved in the recursive file; the finite file adds the twelfth rule.
The historical loader and its twelve-template bound are unchanged. Native
matching chooses applicability; Python loads the whole knowledge file for every
path length. Cell names are local structural roles, never absolute rule coordinates.

[The minimal comparison](../../artifacts/cycle16/minimal/minimal.json) uses
identical observations and terminal rules across R, F and F-minus:

| Arm | Clear | Attack | King exposure |
| --- | --- | --- | --- |
| R | Unknown | Unknown | Unknown |
| F | Positive, c=.92178405 | Positive, c=.866937899025 | Positive, c=.7911382323851379 |
| F-minus | Unknown | Unknown | Unknown |

Every stage is an independent native derivation from the same complete raw
inputs. A stage's host-returned answer is never injected into the next stage.
The king fixture binds original actor, target kind and owner, opposing attacker
owner, and state. A friendly occupied destination still receives influence;
it does not imply legal capture.

[All 27 occupancy runs](../../artifacts/cycle16/occupancy/occupancy.json) agree
across orthogonal rooks, diagonal bishops and orthogonal queens:

| First cell | Second cell | Attack | Clear / exposure |
| --- | --- | --- | --- |
| E | E | Positive | Positive / positive in the correct king fixture |
| E | O | Negative | Unknown / unknown |
| O | E | Negative | Unknown / unknown |
| O | O | Negative | Unknown / unknown |
| O | U | Negative | Unknown / unknown |
| U | O | Negative | Unknown / unknown |
| E | U | Unknown | Unknown / unknown |
| U | E | Unknown | Unknown / unknown |
| U | U | Unknown | Unknown / unknown |

Negative attack is separate `NoAttack` support; it is not a native `NotClear`
or `NotKingExposed` theorem. For O/U, all reference completions are obstructed.
For E/U, U/E and U/U, the evaluation-only completion set contains both possible
labels. No hidden completion is selected as ground truth. Multiple obstruction
routes keep the shared rule stamp, rather than being revised as independent.

[Interventions](../../artifacts/cycle16/interventions/interventions.json) remove
each sole emptiness premise, remove `clear-two`, change one premise's state, or
change the structural ray's attacker. Each removes attack support. Lowering
the rule confidence to .2 lowers attack confidence to .1825132419, still above
the registered .1 display threshold. The low-level competing-occupancy audit
reports both positive and negative channels as conflicting. The public API
rejects duplicate occupancy, duplicate unknown cells and known/unknown collisions.

[Structural controls](../../artifacts/cycle16/structural/structural.json) retain
the expected distinctions: a sole departing blocker changes negative to positive;
moving it along the ray or leaving a second blocker preserves negative support;
an unrelated move does not clear the path. Missing or replaced query entities
produce invalid domains and unknown support, not negative conclusions. Ordinary
targets, friendly targets and the wrong actor suppress exposure while preserving
attack. Renaming, translation, reflection and consistent owner swapping preserve
the tested result. Correctly indexed stale facts do not satisfy a different state.

The [stronger same-entity state controls](../../artifacts/cycle16/supplement/role-state-controls.json)
mix before/after facts for identical entities. Omitting an after-state emptiness
premise still removes support despite the same cell being explicitly empty in
the before state. A wrong ray target removes attack; a friendly attacker
preserves influence but cannot establish the tested exposure conclusion.

Zero- and one-intervening-cell controls still work through existing knowledge.
The three-cell empty path remains unknown even with generous budgets: `clear-two`
does not match it. No three-cell template was introduced. Before/after comparison
is a host diagnostic; no native theorem that a move “created” an attack is claimed.
