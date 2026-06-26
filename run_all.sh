#!/usr/bin/env bash
# Reproduce the full analysis pipeline (Python).
set -euo pipefail
cd "$(dirname "$0")"
echo "[1/2] Cleaning raw export -> tidy CSV ..."
python3 python/01_clean_data.py
echo "[2/2] Running descriptive analysis + figures ..."
python3 python/02_analyse.py
echo "Done. See figures/ and outputs/."
