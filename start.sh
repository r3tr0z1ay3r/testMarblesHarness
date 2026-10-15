#!/usr/bin/env bash
set -e

# Determine directory where script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment in .venv..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if uvicorn and fastapi are installed, install dependencies if missing
if ! python -c "import uvicorn, fastapi" &> /dev/null; then
    echo "📥 Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"

echo "===================================================="
echo "🚀 FastAPI In-Memory CRUD Server"
echo "🌐 URL:         http://${HOST}:${PORT}"
echo "📖 Swagger UI:  http://${HOST}:${PORT}/docs"
echo "📑 ReDoc:       http://${HOST}:${PORT}/redoc"
echo "💓 Health:      http://${HOST}:${PORT}/health"
echo "===================================================="

python -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload "$@"
