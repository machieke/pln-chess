#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export TMPDIR="${TMPDIR:-/dev/shm}"
export PYTHONDONTWRITEBYTECODE=1
export C7_OUT="${C7_OUT:-$PWD/artifacts/cycle7}"
mkdir -p "$C7_OUT/logs"
uv run --no-project --python 3.12.12 python - <<'PY'
import json,os,subprocess
from pathlib import Path
p=Path(os.environ['C7_OUT'])/'bootstrap-context.json'
p.write_text(json.dumps({'fresh_venv':not Path('.venv').exists(),'fresh_runtime':not Path('.runtime').exists(),
 'initial_clean_checkout':not subprocess.check_output(['git','status','--porcelain'],text=True).strip(),
 'source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()},indent=2)+'\n')
PY
bash scripts/bootstrap.sh --dependencies-only > "$C7_OUT/logs/bootstrap.txt" 2>&1
.venv/bin/python - <<'PY'
import os
from pathlib import Path
from pln_chess.common import read_json,write_json
p=Path(os.environ['C7_OUT'])/'bootstrap-context.json';r=read_json(p);r['bootstrap_passed']=True;write_json(p,r)
PY
.venv/bin/python -m scripts.cycle7_run > "$C7_OUT/logs/driver.txt" 2>&1
