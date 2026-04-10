#!/bin/bash

# QuotMate Backend Startup Script

echo "🚀 Starting QuotMate Backend API..."

# Change to backend directory
cd "$(dirname "$0")"

# Determine virtual environment directory (.venv takes priority over venv)
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
else
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Copy .env.example to .env and configure it."
fi

# Set WeasyPrint library path for macOS
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# Verify WeasyPrint dependencies (optional check)
if ! ls /opt/homebrew/lib/libcairo.* >/dev/null 2>&1; then
    echo "⚠️  Warning: WeasyPrint system libraries may not be installed!"
    echo "Install with: brew install cairo pango gdk-pixbuf libffi gobject-introspection glib"
fi

# Start the FastAPI server
echo "📡 Starting server on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔍 ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

./$VENV_DIR/bin/uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0 --port 8000
