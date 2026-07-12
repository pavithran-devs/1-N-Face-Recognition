#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Ensure .venv exists
if [ ! -d ".venv" ]; then
    echo "No .venv found. Run scripts/create_venv.sh first."
    exit 1
fi

# Activate
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-dev.txt

# Copy .env if not present
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Create exports directory
mkdir -p exports

echo ""
echo "Installation complete!"
echo "Next: Create the database and run migrations:"
echo "  createdb -U postgres enrollment_db"
echo "  alembic upgrade head"
