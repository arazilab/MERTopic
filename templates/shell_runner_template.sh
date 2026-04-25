#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip

# Add stage-specific dependencies here.
# python -m pip install openai python-dotenv tqdm pandas pyarrow

# Run a stage-specific script here.
# python scripts/example_stage.py
