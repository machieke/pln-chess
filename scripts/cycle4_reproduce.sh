#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export TMPDIR="${TMPDIR:-/dev/shm}"
bash scripts/bootstrap.sh --dependencies-only
.venv/bin/python -m scripts.cycle4_deliver "$@"
