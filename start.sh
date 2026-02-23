#!/usr/bin/env bash
#
# NDA Generator — One-command startup
# Launches both the API server and the web frontend.
# Usage: ./start.sh
#

set -e

cd "$(dirname "$0")"

API_PORT=8000
FRONTEND_PORT=8501
API_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Shutting down..."
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
    [ -n "$API_PID" ] && kill "$API_PID" 2>/dev/null
    wait 2>/dev/null
    echo "Stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)

# Install dependencies if needed
if ! "$PYTHON" -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies (first run only)..."
    "$PYTHON" -m pip install -e ".[dev]" --quiet
fi

# Create data directories
mkdir -p data/generated

# Start API server in background
echo "Starting API server on port $API_PORT..."
"$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$API_PORT" &
API_PID=$!

# Wait for API to be ready
echo "Waiting for API..."
for i in $(seq 1 30); do
    if curl -s "http://127.0.0.1:$API_PORT/health" >/dev/null 2>&1; then
        echo "API is ready."
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "Error: API failed to start."
        cleanup
    fi
    sleep 1
done

# Start Streamlit frontend
echo "Starting frontend on port $FRONTEND_PORT..."
echo ""
echo "============================================"
echo "  NDA Generator is running!"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  API docs: http://localhost:$API_PORT/docs"
echo "  Press Ctrl+C to stop"
echo "============================================"
echo ""

"$PYTHON" -m streamlit run frontend/app.py \
    --server.port "$FRONTEND_PORT" \
    --server.address 127.0.0.1 \
    --server.headless false &
FRONTEND_PID=$!

# Wait for either process to exit
wait
