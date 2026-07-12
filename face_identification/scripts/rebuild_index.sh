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

echo "Triggering FAISS index rebuild from database..."
python -c "
import asyncio
from app.database.engine import AsyncSessionLocal
from app.faiss.manager import FAISSManager

async def main():
    async with AsyncSessionLocal() as session:
        success, size = await FAISSManager().rebuild(session)
        if success:
            print(f'Success: FAISS index rebuilt. Size: {size}')
        else:
            print('Failed or empty database.')

asyncio.run(main())
"
