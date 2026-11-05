# Baseline and provenance

The authoritative starting commit is `d5cfcb126acc9c3e5da669744d661e6895fb9303` on `master`, synchronized with `origin/master`. The only initial user change was the new Cycle 5 brief; it was preserved. The earlier push instruction completed before this cycle. This brief explicitly authorizes local commits and forbids pushing.

The [startup receipt](../../artifacts/cycle5/baseline-start.json) locks runtime, environment, working-tree state and protected file hashes. All 194 existing tests passed before implementation. The frozen 40-position, 24-position adversarial, older eight-game and C4 twelve-game splits were rerun. Every candidate classification, raw TV and native proof digest matched C4. [Versioned baseline results](../../artifacts/cycle5/baseline.json) include in-board metrics, per-family breakdowns and calibration with the earlier validation mapping.

The runtime remains the unchanged `vendor/pln/lib_pln.metta` at PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`, SHA-256 `cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`, with PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`, SWI-Prolog 10.0.1 and Python 3.12.12. Dependency and backend hashes are checked at runtime. No alternative Python inference path exists.

| Concern | Actual implementation |
|---|---|
| C4 observations and local categories | [ontology](../../src/pln_chess/cycle4/ontology.py) |
| C4 native negative chains | [inference](../../src/pln_chess/cycle4/inference.py) |
| Learning and dependence | [C4 model](../../src/pln_chess/cycle4/model.py), [append-only ledger](../../src/pln_chess/evidence/__init__.py) |
| Native arithmetic and cache | [runtime](../../src/pln_chess/pln/runtime.py), [session](../../src/pln_chess/cycle3/native.py) |
| Historical scope | [C4 history](../../src/pln_chess/cycle4/history.py) |
| Evaluation and benchmark | [evaluation](../../evaluation/cycle4.py), [fresh-process benchmark](../../evaluation/cycle4_benchmark.py) |
| API and inspector | [API](../../src/pln_chess/api/__init__.py), [inspector](../../src/pln_chess/cli/web.py) |

Earlier artifact files are never rewritten. Source compatibility is verified by retaining the original tests; old manifests describe their corresponding historical commits, not later edited source trees.
