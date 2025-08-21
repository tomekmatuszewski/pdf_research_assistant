#!/bin/bash
set -e

./.venv/bin/python backend/injest.py

exec ./.venv/bin/uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload