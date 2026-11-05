# Native PLN capability audit

The selected implementation is [trueagi-io/PLN](https://github.com/trueagi-io/PLN/tree/4405956947c4b53c7ff01bd565aa3b114bc970a1), main commit `4405956947c4b53c7ff01bd565aa3b114bc970a1` (2026-03-15). Its exact, unmodified MIT-licensed `lib_pln.metta` is vendored. It runs through [PeTTa](https://github.com/trueagi-io/PeTTa/tree/ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f), main commit `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f` (2026-10-28), on SWI-Prolog 10.0.1 and CPython 3.12.12. PeTTa supplies the native MeTTa space; Hyperon Python/AtomSpace is not required. Full hashes are in `configs/runtime-lock.json`.

The old OpenCog C++/URE implementation is [marked superseded](https://github.com/opencog/pln). The [experimental repository](https://github.com/trueagi-io/pln-experimental) directs users to this maintained implementation. The experimental conjunction work inspected consists of formula investigations, not a drop-in verified rule for this runtime. No old or untested formula was transplanted.

| Capability | Exact signature / native symbol | Vendored source | Behavior / executed check | Status |
|---|---|---|---|---|
| Modus ponens | `(|- (A TVa) ((Implication A B) TVab))` | `vendor/pln/lib_pln.metta:216`, `Truth_ModusPonens:124` | `(0.8,0.9)` and `(0.9,0.8)` → `(0.724,0.5184)` | Verified; production |
| Revision | `(|- (A TV1) (A TV2))` | line 211; `Truth_Revision:136` | Opposite observations `(1,.5)`, `(0,.5)` → `(.5,2/3)` | Verified; production |
| Negation elimination | `(|- ((Not A) TV))` | line 284; `Truth_Negation:147` | `(.9,.8)` → `(.1,.8)` | Verified; production |
| Deduction | `(|- ((Inheritance A B) TVab) ((Inheritance B C) TVbc))` | line 236; `Truth_Deduction:84` | Requires `(STV A/B/C)` marginals; consistency failure returns `(1,0)` | Verified audit; not chess composition |
| Inheritance | Same deduction/induction link type; `SyllogisticRuleGuard` | lines 232–251 | Grounded `(Inheritance A C)` produced by native `|-` | Verified audit |
| Induction | `(|- ((Inheritance C A) TVca) ((Inheritance C B) TVcb))` | line 246; `Truth_Induction:102` | Five-TV formula plus native rule smoke; explicit population marginals required | Verified audit; chess rule discovery not integrated |
| Evidence overlap | `(StampDisjoint stamps1 stamps2)` | line 335 | `(e1 e2)` vs `(e2 e3)` → false | Verified; ledger uses conservative group exclusion |
| Evidence choice | `(BestConfidenceCandidate ((TV stamp) ...))` | line 412 | Selects highest confidence; ties preserve earlier positive-confidence candidate | Verified; production; no combining shared evidence |
| Evidence weight conversion | `(Truth_w2c weight)` | line 75 | `3` → `.75` | Verified audit |
| Multi-premise conjunction | No core `|- A B → And(A,B)` | whole audited core | Executable `(collapse (|- (A ...) (B ...)))` returns `()` | **Blocked** |
| Confidence-1 revision | `(Truth_Revision (stv 1 1) ...)` | lines 71,136 | No result: division by zero avoided through native empty | Unsupported domain; bridge rejects |
| All-zero-confidence choice | `(BestConfidenceCandidate (((stv .5 0) (e))))` | lines 409–413 | No selected TV; initial empty candidate has rank zero | No-evidence observations remain unknown |
| Abduction, similarity, equivalence, inversion | Present native symbols | core | Source-inspected but not required by production | Not claimed verified |
| Automatic generalization/search | No application-level chess learner | n/a | Revision learns fixed typed categorical hypotheses; no synthesis | Not implemented |

Run `pln-chess runtime-audit` or `pytest tests/test_native.py -q`. Actual stdout and exact invocations are saved in `artifacts/runtime-audit.json`. Variable pattern binding is exercised by native `|-` rules on relational atoms; the application grounds candidates before scheduling.

The native modus ponens implementation has a fixed `.02` background strength and confidence that depends on premise/implication strengths. Strength and confidence are separate. Native revision converts confidence to evidence weight with `c/(1-c)` and back with `w/(w+1)`; the bridge never implements these formulas in Python. Each observation has confidence `.5`; priors have strength `.5`, confidence `.05`. These are disclosed modeling choices, not learned chess rules.

The upstream `examples/Direct.metta` folds modus ponens across several inputs. We deliberately do not interpret that as conjunction: its asymmetry and `.02` background do not supply verified AND semantics. Nested implications also do not solve this gap. The reduced model uses a joint categorical sensory proposition rather than claiming its fields were logically conjoined by PLN. This capability gate constrains every coverage claim.
