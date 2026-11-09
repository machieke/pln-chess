#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${C9_OUT:?Set C9_OUT to a fresh output directory outside this checkout}"
export C9_OUT
export TMPDIR=/dev/shm
export PYTHONPATH="$PWD/src:$PWD"
mkdir -p "$C9_OUT"
if [[ -e .venv || -e .runtime ]]; then
  echo 'Use a clean checkout without .venv or .runtime for the clean bootstrap gate.' >&2
  exit 2
fi
git diff --exit-code > "$C9_OUT/bootstrap-initial-diff.txt"
git diff --cached --exit-code >> "$C9_OUT/bootstrap-initial-diff.txt"
git status --porcelain=v1 > "$C9_OUT/bootstrap-initial-status.txt"
bash scripts/bootstrap.sh --dependencies-only > "$C9_OUT/bootstrap.txt" 2>&1
.venv/bin/python - <<'PY'
import os,subprocess,sys
from pathlib import Path
from pln_chess.common import ROOT,write_json
from pln_chess.pln import Runtime
out=Path(os.environ['C9_OUT'])
status=(out/'bootstrap-initial-status.txt').read_text()
# External output directories keep a fresh checkout fully clean. A pre-existing
# committed artifacts directory is also supported for replay comparisons.
assert not status.strip(),status
write_json(out/'bootstrap-context.json',dict(fresh_venv=True,fresh_runtime=True,initial_clean_checkout=True,
    bootstrap_passed=True,source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    python=sys.version,runtime=Runtime().manifest,output=str(out),
    dependency_lock_sha256=__import__('hashlib').sha256((ROOT/'requirements-dev.lock').read_bytes()).hexdigest()))
PY
.venv/bin/python -m scripts.cycle9_run
