#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Activate venv
source .venv/bin/activate

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting Enrollment Service on ${HOST:-0.0.0.0}:${PORT:-8000}..."
uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --reload
