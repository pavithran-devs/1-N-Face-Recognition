#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"
VENV_DIR="${VENV_PATH:-$HOME/.venvs/face_identification}"
source "$VENV_DIR/bin/activate"
echo "Formatting with black..."
black app/ tests/ streamlit_app/
echo "Fixing with ruff..."
ruff check --fix app/ tests/ streamlit_app/
