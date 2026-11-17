# Native reuse counterexample

The repeated extension cannot compose the two empty cells in the unchanged
native derivation. [Minimal results](../../artifacts/cycle16/minimal/minimal.json)
and [chess interventions](../../artifacts/cycle16/interventions/interventions.json)
retain the actual returned premises and separately executed guard diagnostics.
Run `python -m research.cycle16 minimal --out /path/to/new/minimal`.

The symbolic initial facts are `State(audit_state)`, `Empty(audit_c1,audit_state)`
and `Empty(audit_c2,audit_state)`. The supplied initialization and extension
rules retain `rule_empty-tail` and `rule_extend-empty` on every application.
Native derivation returns:

| Statement | Confidence | Native stamps |
| --- | ---: | --- |
| `PathEmpty(Nil,state)` | .9405 | state observation, empty-tail |
| `PathEmpty(Cons(c2,Nil),state)` | .88454025 | c2 observation, state observation, empty-tail, extend-empty |
| `PathEmpty(tail,state) -> PathEmpty(Cons(c1,tail),state)` | .9405 | c1 observation, extend-empty |

The latter two premises overlap **only on `rule_extend-empty`**. Native
`StampDisjoint` returns false. The second extension is absent from returned
beliefs under 128 steps and 256/512 queue parameters. Both relevant premises
are available, so this particular failure is not explained by missing binding,
missing observations, low confidence, timeout, or an unavailable intermediate.
The equivalent raw chess path produces the same overlap.

The native statement-level `|-` operation is directional: modus ponens expects
the premise first and implication second. The first retained diagnostic called
the reverse order and returned no structural result. The final diagnostic
retains both orders: the correct order produces the proposed second extension
with confidence .8319101051250001. This is an **unguarded structural witness**,
not an answer from `PLN.Derive`. It shows that the statements match and that
the actual guard rejects them. The exposed trace does not prove the scheduler
attempted this specific pair; no such event is invented.

[Dependency controls](../../artifacts/cycle16/dependencies/dependencies.json)
separate assumptions rather than relabel real observations:

| Control | Result |
| --- | --- |
| Shared rule stamp only | Guard false; absent conclusion |
| Shared environmental stamp | Guard false; absent conclusion |
| Shared training stamp | Guard false; absent conclusion |
| Explicitly disjoint synthetic inputs | Guard true; conclusion derives |
| Diamond from one common observation | Join absent |
| Same join with independently supplied branches | Join derives |
| Replayed identical input | Same .9801 answer and stamps as one delivery |
| Circular A → B → A | Original A remains .99; no confidence increase |

Replay retains an extra duplicate input entry in the returned belief collection;
its support does not increase. The circular case can return a lower-confidence
descendant with the original observation in its ancestry, but cannot revise it
as independent evidence. These small examples delimit the tested guard; they
are not a proof against every possible cycle. All synthetic stamps are namespaced.

The [learned-chain witness](../../artifacts/cycle16/supplement/shared-training-witness.json)
adds a real-data counterpart: clearance and the terminal partial implication
share eleven training-game stamps. Both statements are returned, the guard is
false, and direct native structural matching would return attack at
.8128120084615383. That value never enters experimental predictions. The first
ground-only lookup in the budget report returned null because the actual
terminal statement still has a target variable; the supplementary audit preserves
that result and checks the returned variable-bearing statement instead.
