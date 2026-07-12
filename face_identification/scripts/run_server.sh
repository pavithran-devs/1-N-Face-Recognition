#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Activate venv
VENV_DIR="${VENV_PATH:-$HOME/.venvs/face_identification}"
source "$VENV_DIR/bin/activate"

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

PORT="${PORT:-8001}"
HOST="${HOST:-0.0.0.0}"

echo "Starting Face Identification Service on $HOST:$PORT..."
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
