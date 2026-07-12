#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Activate venv
source .venv/bin/activate

# Install streamlit deps if not already present
pip install --quiet streamlit requests pandas

echo "Starting Streamlit UI at http://localhost:8501"
streamlit run streamlit_ui/Home.py \
    --server.port 8501 \
    --server.headless false \
    --browser.gatherUsageStats false
