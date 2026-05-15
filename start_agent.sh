#!/usr/bin/env bash
set -euo pipefail

# Starts the Python tiny-model service and the Node web UI together.
# Use on a local computer, Codespaces, Replit shell, or a VPS.

PYTHON_PORT="${PYTHON_PORT:-8081}"
WEB_PORT="${PORT:-8080}"
export PYTHON_SERVICE_URL="${PYTHON_SERVICE_URL:-http://127.0.0.1:${PYTHON_PORT}}"

cleanup() {
  if [[ -n "${PY_PID:-}" ]]; then kill "$PY_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT

PORT="$PYTHON_PORT" python python-service/app.py &
PY_PID=$!

echo "Started Python service on port ${PYTHON_PORT} (pid ${PY_PID})"
echo "Starting web UI on port ${WEB_PORT}"
PORT="$WEB_PORT" node server/server.js
