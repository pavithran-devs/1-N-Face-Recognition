#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

source .venv/bin/activate

echo "Running tests with coverage..."
pytest tests/ -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    "$@"
