#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  bash build.sh
fi
python_bin=".venv/bin/python"
command -v xdg-open >/dev/null 2>&1 && xdg-open http://127.0.0.1:8000 >/dev/null 2>&1 &
"$python_bin" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
