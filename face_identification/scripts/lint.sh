#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"
VENV_DIR="${VENV_PATH:-$HOME/.venvs/face_identification}"
source "$VENV_DIR/bin/activate"
echo "Running ruff check..."
ruff check app/ tests/ streamlit_app/
