# Cycle 3 native PLN audit and decision

The production source and runtime pins are unchanged from Cycle 2. `configs/runtime-lock.json` pins PLN commit `4405956947c4b53c7ff01bd565aa3b114bc970a1`, PeTTa commit `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`, source hashes, and SWI-Prolog 10.0.1. No Python truth-value formula substitutes for native execution.

Run `.venv/bin/pln-chess cycle3 --action audit`. `artifacts/cycle3/native-probes.json` contains actual outputs, source signature locations, the earlier regression probes, and the full runtime manifest. Its `.metta` sibling reproduces the added raw probes after adjusting the import path for the checkout. The Python audit constructs that path automatically.

| Mechanism | Executed result | Use |
|---|---|---|
| Truth_Revision | Finite confidence evidence revises the same proposition | Learning, one contribution per declared dependence group |
| Truth_ModusPonens / `\|-` | Grounding, variable binding, nested implications and unary chains execute | Conditional movement and exposure |
| Truth_Negation | Complement with native confidence behavior | Negative-legality alternative |
| BestConfidenceCandidate | Chooses one alternative; stronger local evidence can defeat a counter | Arbitration, never evidence fusion |
| Truth_Induction + Truth_w2c | Executes with explicit finite measured marginals | Experimental controlled variant |
| Deduction / inheritance | Earlier numerical and grounded probes reproduced | Audit only; no missing marginals invented |
| Equivalence, inversion, abduction, similarity | Earlier verified numeric probes retained | Experimental audit only |
| StampDisjoint | Shared stamps return false; separate stamps true | Dependence audit; Truth_* functions do not automatically enforce it |
| A and B → And(A,B) | Empty result | Unsupported |
| And(A,B) → A or B | Empty result | Unsupported |
| Supplied And(A,B), And(A,B)→C | Native MP returns C | Joint **sensor observation**, not conjunction construction |
| A and Not(A) | No automatic contradictory-proposition revision | Separate channels and abstention |
| Zero-confidence revision / confidence-one revision | Empty/undefined result | Zero evidence skipped; finite revision confidence required |

The explicit joint-sensor probe returns C with TV `(0.9, 0.7128000000000001)`. The nested conditional example returns `(0.9, 0.6351048000000001)`. Neither proves the independence or conjunction of separately observed chess conditions. Low-confidence MP executes and stays weak; zero-strength MP returns strength 0.02 with zero confidence, demonstrating why a zero-confidence output must not be interpreted as a decisive fact.

The existing native inheritance-induction wrapper passes marginal roles in an order that differs from the direct formula's intended target/common/outcome roles. Cycle 3 retains direct `Truth_Induction` calls with recorded counts and explicit arguments. The model never silently repairs an upstream operator.

Decision: keep the existing pinned runtime, native conditional layers and unary chains. Reject invented conjunction, host confidence multiplication, Boolean legality composition and an engine legality gate. Cycle 2's separately pinned MIT-licensed upstream branch experiments remain archived in `artifacts/cycle2/upstream-audit.json`; no newly audited drop-in implementation is claimed or adopted. Genuine conjunction remains a research limitation rather than an engineering completion claim.
