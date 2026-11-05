#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash scripts/bootstrap.sh --dependencies-only
.venv/bin/python -m scripts.cycle3_deliver "$@"
