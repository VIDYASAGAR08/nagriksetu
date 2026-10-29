#!/usr/bin/env bash
# ==============================================================================
# CivicAdmin Platform - Demonstration Launcher
# Starts both the FastAPI Backend and Vite React Frontend
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "  CivicAdmin Citizen Services Platform - Launcher"
echo "============================================================"

# 1. Check Python virtual environment
if [ ! -d "backend/.venv" ]; then
    echo "Creating Python virtual environment in backend/.venv..."
    python3 -m venv backend/.venv
    backend/.venv/bin/pip install -r backend/requirements.txt
fi

# 2. Check Database initialization
if [ ! -f "backend/civic_admin.db" ]; then
    echo "Seeding initial development database..."
    cd backend
    .venv/bin/python -m app.seed
    cd ..
fi

# 3. Kill any lingering process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 4. Start FastAPI Backend in background
echo "Starting FastAPI Backend on http://127.0.0.1:8000..."
cd "$DIR/backend"
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd "$DIR"

# Wait for backend to be ready
echo "Waiting for backend readiness probe..."
sleep 2

# 5. Start Vite Frontend
echo "Starting Vite Frontend on http://localhost:5173..."
cd "$DIR/frontend"

cleanup() {
    echo ""
    echo "Shutting down CivicAdmin servers..."
    kill $BACKEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM EXIT

npm run dev
