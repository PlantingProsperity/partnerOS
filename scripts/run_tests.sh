#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d .venv ]]; then
  echo "❌ .venv not found. Run: bash scripts/bootstrap_venv.sh"
  exit 1
fi

source .venv/bin/activate

python -m unittest discover -s tests -v
