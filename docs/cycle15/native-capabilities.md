# Native capabilities

The pinned native reasoner passes both the absent-conclusion and reusable-binding
gates. The strongest demonstrated classification is **native-schema-binding**.
Python supplies sentences and queries; native statement matching chooses rules
and binds variables. There is no host grounding loop or descriptor fallback in
the experimental adapter.

[The 41-case matrix](../../artifacts/cycle15/capabilities/matrix.json) is executable
with `python -m evaluation.cycle15_capabilities --out /path/to/capabilities`.
The [adapter](../../research/cycle15/native_reasoner.py) retains the exact program,
stdout/stderr, selected tasks, returned beliefs, native-selected answer channels,
runtime identity and per-process resource measurements. Small complete examples
are in [representative evidence](../../artifacts/cycle15/representative/).

| Capability | Observed result |
| --- | --- |
| Retrieval, absent one-rule and two-rule conclusions | Supported |
| Shared-variable curried implications | Supported; swapping the shared target removes support |
| Unfamiliar entities and irrelevant inputs | Supported within the tested budgets |
| Missing sole premise or rule | No support found |
| Independent versus shared-stamp revision | Independent evidence revises; shared evidence cannot revise together |
| Diamond with common ancestry stamp | Join unavailable; independently supplied branches can join |
| Repeated recursive rule in a longer chain | Unavailable when the next firing overlaps the rule's own stamp |
| Separate positive and contrary channels | Both exposed as conflicting |
| Variable query | No answer in the tested form, despite ground conclusions being available |
| Missing deduction marginals | No deduction; explicit synthetic marginal assumptions enable the audit case |
| Equal-confidence answers | The earlier retained candidate wins; reversing input order can change it |

The [one-rule](../../artifacts/cycle15/representative/one-rule.json),
[two-rule](../../artifacts/cycle15/representative/two-rules.json),
[shared-role](../../artifacts/cycle15/representative/shared-role.json) and
[swapped-role](../../artifacts/cycle15/representative/swapped-role.json) transcripts
contain the actual inputs and outputs. A selected task is directly observed.
Its evidence stamp is native-returned. Neither is a full fired-rule tree.
No reconstructed witness chooses a production answer.

## Exact APIs and boundaries

The primary call is:

```metta
(PLN.Derive Tasks Beliefs 1 maxsteps taskqueuesize beliefqueuesize)
```

The adapter then applies the library's own `BestConfidenceCandidate` expression
to exact query matches in those returned beliefs, separately for positive and
contrary propositions. Direct Query compatibility uses:

```metta
(PLN.Query Tasks Beliefs term maxsteps taskqueuesize beliefqueuesize)
```

Sentences have the exact form `(Sentence (proposition (stv strength confidence))
(stamp-items))`. No new `|-` clause, truth formula, helper adjudicator or generic
logical operator is introduced. Knowledge files are parsed as declarative data.

Query performs bounded forward derivation, then answer selection; no backward
chaining is demonstrated. Steps start at one and stop when the counter exceeds
the maximum. Zero steps preserves the initial belief collection. `LimitSize`
returns a collection strictly smaller than its size argument: capacity one
empties it. Zero capacities are rejected by the adapter because the pinned
implementation would not terminate its limiter. Queues can evict conclusions;
remaining tasks and eviction invalidate a saturation claim. Empty results mean
no support under the reported budget, not falsity.

Native schemas are printed with renamed variables. The final telemetry compares
statements modulo variable renaming, preserving repeated-role structure. The
earlier raw receipts remain immutable; the supplementary proof audit recomputes
their derived-statement counts without changing programs, answers or stamps.

## Compatibility and runtime

The [upstream smoke receipt](../../artifacts/cycle15/capabilities/upstream-smoke.json)
records the original hash and passing Edward/cancerous assertion from pinned
[Smokes.metta](https://github.com/trueagi-io/PLN/blob/4405956947c4b53c7ff01bd565aa3b114bc970a1/examples/Smokes.metta).
Only its first three import declarations were replaced by a local pinned import.
The assertion is not used to claim every friend-chain construct was exercised.

PLN is `4405956947c4b53c7ff01bd565aa3b114bc970a1`, with vendored SHA-256
`cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`.
PeTTa is `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`; every locked file is verified.
Python is 3.12.12 and SWI-Prolog is 10.0.1. The unchanged
[runtime lock](../../configs/runtime-lock.json) is authoritative.
