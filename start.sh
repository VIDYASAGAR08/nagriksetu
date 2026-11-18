#!/usr/bin/env bash

# ==============================================================================
# NagrikSetu (नागरिक सेतु) — One-Click Development & Demonstration Launcher
# Starts:
#   1. NagrikSetu Central Portal (FastAPI Port 8000 & React Port 5173)
#   2. School & Education Microservice (FastAPI Port 8001 & React Port 5174)
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
SCHOOL_DIR="$PROJECT_ROOT/School service"

# Colors for terminal output
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
AMBER='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${AMBER}   🇮🇳  NagrikSetu (नागरिक सेतु) — Multi-Service Platform Launcher  ${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# 1. Check Python & Virtualenv for Main Backend
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

# 4. Check School Frontend node_modules
if [ -d "$SCHOOL_DIR/frontend" ] && [ ! -d "$SCHOOL_DIR/frontend/node_modules" ]; then
    echo -e "${CYAN}📦 Installing School service frontend npm dependencies...${NC}"
    cd "$SCHOOL_DIR/frontend"
    npm install
    cd "$PROJECT_ROOT"
fi

# 5. Cleanup any orphaned processes on ports 8000, 8001, 5173, and 5174
echo -e "${BLUE}🔍 Checking ports 8000, 8001, 5173, and 5174...${NC}"
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8001 | xargs kill -9 2>/dev/null || true
lsof -ti :5173 | xargs kill -9 2>/dev/null || true
lsof -ti :5174 | xargs kill -9 2>/dev/null || true

# 6. Start Main FastAPI Backend (Port 8000)
echo -e "${GREEN}🚀 Starting NagrikSetu Main Backend on http://127.0.0.1:8000...${NC}"
cd "$BACKEND_DIR"
PYTHONPATH=. "$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 7. Start School Microservice Backend (Port 8001)
if [ -d "$SCHOOL_DIR/backend" ]; then
    echo -e "${GREEN}🚀 Starting School & Education Microservice on http://127.0.0.1:8001...${NC}"
    cd "$SCHOOL_DIR/backend"
    DATABASE_PATH="$SCHOOL_DIR/backend/data/nagriksetu.db" JWT_SECRET_KEY="nagriksetu_jwt_secret_dev_key_2026" "$BACKEND_DIR/.venv/bin/uvicorn" main:app --port 8001 &
    SCHOOL_BACKEND_PID=$!
fi

# Wait for backends
sleep 1.5

# 8. Start Main Frontend (Port 5173)
echo -e "${GREEN}🚀 Starting NagrikSetu Central Portal on http://localhost:5173...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

# 9. Start School Service Frontend (Port 5174)
if [ -d "$SCHOOL_DIR/frontend" ]; then
    echo -e "${GREEN}🚀 Starting School Service Frontend on http://localhost:5174...${NC}"
    cd "$SCHOOL_DIR/frontend"
    npm run dev &
    SCHOOL_FRONTEND_PID=$!
fi

cd "$PROJECT_ROOT"

# Trap Ctrl+C (SIGINT/SIGTERM) to kill child processes cleanly
cleanup() {
    echo -e "\n${AMBER}🛑 Shutting down NagrikSetu services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $SCHOOL_BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    kill $SCHOOL_FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped safely.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN}   ✓ ALL NAGRIKSETU PLATFORMS ARE LIVE & INTEGRATED!   ${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}"
echo -e "  🌐 ${BOLD}Central Portal & Website:${NC}    http://localhost:5173"
echo -e "  🎓 ${BOLD}Integrated School Directory:${NC}  http://localhost:5173/education"
echo -e "  🏫 ${BOLD}School & Admissions Portal:${NC}   http://localhost:5174"
echo -e "  ⚙️  ${BOLD}Central API Docs (Swagger):${NC}  http://127.0.0.1:8000/docs"
echo -e "  ⚙️  ${BOLD}School Service API Docs:${NC}     http://127.0.0.1:8001/docs"
echo -e "\n${AMBER}Press Ctrl+C in this terminal at any time to stop all services.${NC}\n"

wait
