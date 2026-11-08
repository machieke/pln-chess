# Relative promotion transitions and curriculum

Schema 8 preserves an immutable schema-7 source checkpoint and adds a separate
ledger of promotion transition evidence. The accepted source remains available
as `C8-frozen`; all original checkpoints and historical reports are protected by
the baseline hash manifest. No learned rule contains an absolute square constant.

`PromotionBoundary`, owner-relative displacement, destination occupancy and kind,
choice, resulting piece and existing post-transition exposure frames are separate
typed observations. The learned local key contains the mover type, absolute file
**displacement magnitude** (not file identity), owner-forward displacement,
owner-relative distance to the promotion boundary at both endpoints, destination
existence/occupancy/type, promotion choice, resulting type and operation.
White/Black orientation and file reflection share this representation. A legal
file translation preserves it when no board edge is crossed. Vertical pawn
translations generally change boundary semantics and are not claimed symmetries.

These are host board observations with explicit source IDs. The local target is
pseudo-legal transition eligibility; global legality and post-move exposure are
separate offline labels. Existing native attack/exposure constraints remain in
force. An observation does not itself decide legality, and the new key does not
prove global king safety.

The registered learner disables C7's lossy level-1/2 backoff, retains exact learned
categories, and considers a promotion rule only for an unresolved complete
observation. It preserves prior supported decisions and specific local
counterevidence. A matched hypothesis is projected into the existing C6 native
pipeline, with both the learned and grounded rule IDs retained. Native revision,
modus ponens, negation and selection execute their existing formulas. There is
no Python TV formula, new native operator, or production reference-engine gate.
Strict and experimental modes do not execute the new operational promotion pass.

Training counts at most one unambiguous observation per source group and rule;
shared transformation ancestry cannot add confidence. Zero-confidence or
incomplete observations cannot train a rule. Conflicting labels within one group
are excluded rather than counted as independent votes. Full exclusions, raw
native revision expressions and returned STVs are retained in the training
ledger. Retraction reconstructs the learner from surviving evidence.

The seeded dataset has five partitions: training, validation, combination
holdout, adversarial and independent games. Complete scenario pairs cover both
owners and all four promotion choices, empty/friendly/opponent destinations,
blocked advances, pins, discovered exposure and check evasion. Missing destination
observations are actually applied to `Position`, rather than merely tagged in the
report. Labels are not artificially forced to a 50/50 balance.

Constructed training families are isolated or have one attack ray. Validation,
combination and adversarial configurations add respectively two, three and four
pieces. Their complete configuration family IDs are disjoint. Added pieces may
be remote; the family partition does **not** establish that every extra piece
interacts causally with the promotion. Atomic transition categories intentionally
recur across these families. Color mirrors remain in one split and share a source
group; they are not independently acquired observations. The data generator
excludes cross-split exact, symmetry and translation-lineage duplicates.

The game families are separately seeded queen-pawn training, English validation,
and Caro-Kann/Scandinavian test games. These are synthetic legal random games,
not external human-game evidence. The complete game histories, seeds, exclusions,
family definitions, class counts, source groups and overlap audit are in
[`datasets/dataset.json`](../../artifacts/cycle8/datasets/dataset.json) and
[`datasets/audit.json`](../../artifacts/cycle8/datasets/audit.json).

Ablations remove promotion training, destination context, choice/resulting-piece
context, and dependence safeguards. The destination ablation masks occupancy and
piece type; the choice ablation pools choice and resulting type. The dependence
ablation disables deduplication and runtime overlap guards while preserving real
IDs. The no-promotion-training arm keeps the C7 exact-only learner and was
registered as a possible conservative fallback **before** C8 outcomes. Destructive
ablations are never eligible for promotion. The observed effects, including null
results, belong in the evaluation report rather than being presumed beneficial.
