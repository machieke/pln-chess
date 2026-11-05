#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v uv >/dev/null; then
  echo 'Install uv (https://docs.astral.sh/uv/getting-started/installation/) then rerun bootstrap.' >&2
  exit 2
fi
if ! command -v swipl >/dev/null; then
  echo 'BLOCKED: install SWI-Prolog 10.0.1 with Janus and PCRE, then rerun bootstrap.' >&2
  exit 2
fi
pln_swi_version=$(swipl --version)
if [[ "$pln_swi_version" != 'SWI-Prolog version 10.0.1 for x86_64-linux' ]]; then
  echo 'BLOCKED: audited native runtime requires SWI-Prolog 10.0.1 with Janus and PCRE. Install that version and rerun. No Python inference fallback is provided.' >&2
  exit 2
fi
uv venv --python 3.12.12 --allow-existing .venv
uv pip sync --python .venv/bin/python requirements-dev.lock
uv pip install --python .venv/bin/python --no-deps -e .
if [ ! -f .runtime/petta/run.sh ]; then
  mkdir -p .runtime
  git clone https://github.com/trueagi-io/PeTTa.git .runtime/petta
  git -C .runtime/petta checkout --detach ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f
fi
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
.venv/bin/python scripts/deliver.py
