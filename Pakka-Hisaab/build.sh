#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "from backend.db import ensure_database; c=ensure_database(); print('SQLite ready'); c.close()"
