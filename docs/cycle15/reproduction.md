# Reproduction

Use Python 3.12.12 and the unchanged pinned runtime from
[configs/runtime-lock.json](../../configs/runtime-lock.json). Existing dependency
installation is sufficient; `bash scripts/bootstrap.sh` is the repository's
bootstrap entry point when needed. No runtime upgrade is part of this cycle.
Run these commands from the repository root with `.venv/bin/python`.

## Small native demonstrations

```bash
.venv/bin/python -m research.cycle15 microcase --out /tmp/c15-microcase
.venv/bin/python -m research.cycle15 blocker --out /tmp/c15-blocker
```

Both commands create a compact summary and a content-hashed complete result.
The blocker command reports a negative before-state and positive after-state for
a supplied displacement across one intervening cell. It does not select a move.
The endpoint comparison is a host diagnostic.

The Python interface is:

```python
from research.cycle15.queries import infer_consequence

result = infer_consequence(
    observed_state, supplied_candidate, target_relation,
    knowledge_checkpoint=None, budgets=None, proof_mode="full",
)
```

The [CLI source](../../research/cycle15/__main__.py) contains a complete valid
input. Call `infer_state` for an individual endpoint or an explicitly marked
Stage A diagnostic. Rule files are independently parsed by
[knowledge.py](../../research/cycle15/knowledge.py).

## Research reproduction

Use a new external output directory; immutable runs should not be overwritten.

```bash
TASK_OUT=/path/to/new/cycle15-evidence
.venv/bin/python -m evaluation.cycle15_capabilities --out "$TASK_OUT/capabilities"
.venv/bin/python -m training.cycle15_consequences --out "$TASK_OUT/learning"
.venv/bin/python -m evaluation.cycle15_consequences \
  --out "$TASK_OUT/evaluation" --checkpoint "$TASK_OUT/learning/model.json" --workers 2
.venv/bin/python -m evaluation.cycle15_diagnostics \
  --out "$TASK_OUT/diagnostics" --checkpoint "$TASK_OUT/learning/model.json"
.venv/bin/python -m scripts.cycle15_information --out "$TASK_OUT/supplement/information"
.venv/bin/python -m scripts.cycle15_supplement --out "$TASK_OUT/supplement" \
  --evaluation-root "$TASK_OUT/evaluation" --checkpoint "$TASK_OUT/learning/model.json"
.venv/bin/python -m scripts.cycle15_query_audit --part query --out "$TASK_OUT/supplement/query-audit"
.venv/bin/python -m scripts.cycle15_query_audit --part chain --out "$TASK_OUT/supplement/query-audit"
.venv/bin/python -m scripts.cycle15_partition_audit \
  --results "$TASK_OUT/evaluation/results.json" --out "$TASK_OUT/supplement/partition-audit.json"
.venv/bin/python -m evaluation.cycle15_performance --out "$TASK_OUT/performance"
.venv/bin/python -m pytest -q tests/test_cycle15_*.py
```

The capability runner retrieves the pinned upstream Smokes source only if its
local copy is absent; it adapts imports and retains both versions. Production
inference itself performs no network access. Evaluation requires the existing
frozen field model already in Git. The corpus is deterministic and generated
locally; no external preference collection is needed.

Resume only an unchanged evaluation directory with its same model. Choose a new
directory after source changes. Run provenance contains timestamps, paths and
process measurements, so refitting creates a new ledger identity; compare
learned parameters, ancestry, native answers and stamps, not timing-bearing file
hashes across separate executions.

## Full legal preservation

The expensive preservation driver requires a clean source checkout and the
existing historical evidence. Read [Cycle 14 publication](../cycle14/publication.md)
before restoring any missing data. Local verified Cycle 14 packs may be used;
no original-history download is necessary for these source inspections.

```bash
.venv/bin/python -m scripts.cycle15_preservation \
  --out /path/to/new/preservation \
  --source /path/to/clean/source-checkout --workers 4
```

This executes all 206 legal jobs, all controls, the full test suite and exact
canonical native proof comparison. It does not synthesize acceptance from old
summaries. Historical evidence is read-only; all generated output is external.

The delivered acceptance checkout uses verified existing runtime/virtualenv
links and read-only links to externalized historical evidence. It is not claimed
to be a new dependency installation. Separately, a fresh Git source archive
reproduces the native capabilities, model parameters and CLI demonstration
within the explicitly recorded scope.

## Local evidence packs

Large outputs are retained locally at
`/home/purplezky/cycle15-evidence-20261117`. They are not uploaded or added to Git.
The final [evidence manifest](../../publication/cycle15/manifest.json) records
every packaged path, size, content hash and local pack. To restore a copied pack
set into a new directory:

```bash
.venv/bin/python -m scripts.cycle15_evidence restore \
  --root /path/to/restored-evidence \
  --packs /path/to/cycle15-packs --manifest publication/cycle15/manifest.json
.venv/bin/python -m scripts.cycle15_evidence verify \
  --root /path/to/restored-evidence --manifest publication/cycle15/manifest.json
```

The tool checks each pack and each file, rejects path traversal/symlink
destinations, and never replaces different existing evidence. Paths inside raw
receipts retain their original source-bound location; resolve them relative to
the manifest's `original_local_root` when inspecting a restored copy. Historical
receipts are not rewritten for relocation. Compact representative native proofs,
checkpoints and summaries remain directly inspectable in Git.
