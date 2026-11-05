#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export TMPDIR="${TMPDIR:-/dev/shm}"
export PYTHONDONTWRITEBYTECODE=1
export C6_OUT="${C6_OUT:-$PWD/artifacts/cycle6}"
mkdir -p "$C6_OUT/logs"
# Record whether this invocation really starts without either dependency tree.
uv run --no-project --python 3.12.12 python - <<'PY'
import json,os,subprocess
from pathlib import Path
p=Path(os.environ['C6_OUT'])/'bootstrap-context.json'
p.write_text(json.dumps({'fresh_venv':not Path('.venv').exists(),'fresh_runtime':not Path('.runtime').exists(),
 'initial_clean_checkout':not subprocess.check_output(['git','status','--porcelain'],text=True).strip(),
 'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},indent=2)+'\n')
PY
bash scripts/bootstrap.sh --dependencies-only > "$C6_OUT/logs/bootstrap.txt" 2>&1
.venv/bin/python -m pytest -q > "$C6_OUT/pytest.txt" 2>&1
.venv/bin/python -m scripts.cycle6_baseline --out "$C6_OUT" > "$C6_OUT/logs/baseline.txt" 2>&1
.venv/bin/python -m scripts.cycle6_deliver --stage all > "$C6_OUT/logs/delivery.txt" 2>&1
.venv/bin/python -m scripts.cycle6_verify > "$C6_OUT/logs/verification.txt" 2>&1
.venv/bin/python -m evaluation.cycle6_reporting
