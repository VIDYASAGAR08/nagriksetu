#!/usr/bin/env bash

# ==============================================================================
# NagrikSetu (नागरिक सेतु) — One-Click Development & Demonstration Launcher
# Starts both FastAPI Backend (Port 8000) and React Vite Frontend (Port 5173)
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for terminal output
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
AMBER='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${AMBER}   🇮🇳  NagrikSetu (नागरिक सेतु) — Administrative Platform Launcher  ${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# 1. Check Python & Virtualenv
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${AMBER}⚠️ Python virtual environment not found. Creating .venv in backend/...${NC}"
    python3 -m venv "$BACKEND_DIR/.venv"
    "$BACKEND_DIR/.venv/bin/pip" install --upgrade pip
    "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

# 2. Check Database & Seed if missing
if [ ! -f "$BACKEND_DIR/civic_admin.db" ]; then
    echo -e "${CYAN}🌱 Initializing and seeding demo database with administrative records...${NC}"
    cd "$BACKEND_DIR"
    PYTHONPATH=. "$BACKEND_DIR/.venv/bin/python" -m app.seed
    cd "$PROJECT_ROOT"
fi

# 3. Check Frontend node_modules
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${CYAN}📦 Installing frontend npm dependencies...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_ROOT"
fi

# 4. Cleanup any orphaned processes on port 8000 and 5173
echo -e "${BLUE}🔍 Checking ports 8000 and 5173...${NC}"
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :5173 | xargs kill -9 2>/dev/null || true

# 5. Start Backend Process
echo -e "${GREEN}🚀 Starting FastAPI Backend on http://127.0.0.1:8000...${NC}"
cd "$BACKEND_DIR"
PYTHONPATH=. "$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend health
sleep 1.5

# 6. Start Frontend Process
echo -e "${GREEN}🚀 Starting Vite Frontend on http://localhost:5173...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

cd "$PROJECT_ROOT"

# Trap Ctrl+C (SIGINT/SIGTERM) to kill child processes cleanly
cleanup() {
    echo -e "\n${AMBER}🛑 Shutting down NagrikSetu services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped safely.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN}   ✓ NAGRIKSETU PLATFORM IS LIVE AND READY FOR DEMONSTRATION!   ${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}"
echo -e "  🌐 ${BOLD}Citizen Portal & Website:${NC}  http://localhost:5173"
echo -e "  ⚙️  ${BOLD}FastAPI Backend Docs:${NC}      http://127.0.0.1:8000/docs"
echo -e "  📊 ${BOLD}Database Inspection Tool:${NC}  python3 backend/inspect_db.py"
echo -e "\n${BOLD}${CYAN}Demo Credentials:${NC}"
echo -e "  • ${BOLD}National Administrator:${NC}   admin@civicportal.gov / AdminPass123!@#"
echo -e "  • ${BOLD}Scoped District Admin:${NC}    admin.bengaluru@nagriksetu.gov.in / AdminPass123!@#"
echo -e "  • ${BOLD}Registered Citizen:${NC}       aarav.sharma@example.com / CitizenPass123!@"
echo -e "\n${AMBER}Press Ctrl+C in this terminal at any time to stop both servers.${NC}\n"

# Keep script waiting for Ctrl+C
wait
