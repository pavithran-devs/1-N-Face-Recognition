#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"
source .venv/bin/activate
echo "Formatting with black..."
black app/ tests/
echo "Fixing with ruff..."
ruff check --fix app/ tests/
