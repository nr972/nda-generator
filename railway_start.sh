#!/usr/bin/env bash
#
# Railway deployment startup — runs both API and Streamlit in one container.
#

set -e

mkdir -p data/generated

# Start API server in background
uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT:-8000}" &

# Wait for API to be ready
for i in $(seq 1 30); do
    if curl -s "http://127.0.0.1:${API_PORT:-8000}/health" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Start Streamlit frontend (foreground — Railway monitors this process)
exec streamlit run frontend/app.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
