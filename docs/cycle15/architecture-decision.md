# Architecture decision

Choose **Outcome 2: native binding works; raw chess consequence remains partial**.

Native execution and shared-role binding are demonstrated on the pinned runtime.
The reasoner applies supplied reusable implications and can derive a local
occupancy-constrained attack and role-correct exposure without Python selecting
the conclusion. Native revision changes learned rule beliefs, and those beliefs
support unfamiliar one-cell configurations. The intended architecture has a
working limited instance.

The central unresolved boundary is composition over longer empty paths. Reusing
the same recursive rule creates overlapping evidence stamps, so the existing
native guard blocks the next combination. More steps and larger queues do not
resolve the retained generous counterexample. This is a semantic/evidence-reuse
question, not evidence that the board is obstructed.

On 48 held-out structural roots, connected inference answers 52 of 96 endpoints
correctly and abstains on 44. Its positive recall is 8.33%. The frozen conditional
baseline answers all 96 correctly. There is no demonstrated accuracy advantage,
rule-structure discovery, arbitrary-ray generalization or general legal-move
reasoning. All admitted learning evidence is positive conditional support; noisy
supervision and empirical calibration remain open.

The next experiment should isolate **repeated reusable-rule evidence on a
two-intermediate-cell path**. Keep the native runtime unchanged and compare a
fully disclosed, bounded two-cell supplied template with the recursive template,
using identical raw observations, stable rule stamps and explicit ancestry.
The former would test a finite domain encoding, not solve generic recursion.
If a generic evidence policy change is required, it needs separate authorization
and an upstream design review. Do not mint fresh rule evidence or add a hidden
host clearance test to force success.

Retain the existing operational conditional implementation and accepted legal
model. Keep Cycle 15 opt-in. Broader preference work, persistent native state and
another consequence family should follow a focused resolution of this boundary.

Evidence: [native matrix](../../artifacts/cycle15/capabilities/matrix.json),
[recursive failure](../../artifacts/cycle15/representative/reused-recursive-rule.json),
[generous chess failure](../../artifacts/cycle15/representative/long-path-generous.json),
[matched results](../../artifacts/cycle15/evaluation/summary.json),
[held-out learning effect](../../artifacts/cycle15/supplement/heldout-learning-effect.json),
and [equal field counts](../../artifacts/cycle15/supplement/information/field-information-loss.json).
