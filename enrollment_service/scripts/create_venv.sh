#!/bin/bash
set -e

echo "Creating Python virtual environment..."

# Check if Python 3.14 is available
if ! command -v python3.14 &> /dev/null; then
    echo "Error: python3.14 not found"
    exit 1
fi

# Create venv
python3.14 -m venv .venv

echo "Virtual environment created at .venv/"
echo "Activate with: source .venv/bin/activate"
