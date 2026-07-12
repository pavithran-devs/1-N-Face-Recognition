#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"
VENV_DIR="${VENV_PATH:-$HOME/.venvs/face_identification}"
source "$VENV_DIR/bin/activate"

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "Starting Streamlit face identification UI on port 8501..."
streamlit run streamlit_app/Home.py --server.port 8501
