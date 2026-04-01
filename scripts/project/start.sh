#!/bin/bash
echo "============================================"
echo "Starting Agentic RAG Masterclass"
echo "============================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[Cleanup] Killing existing processes..."
echo "--------------------------------------"

# Kill processes using port 8000 (Backend)
if command -v lsof &> /dev/null; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    # Fallback for Windows Git Bash with netstat
    netstat -ano | grep :8000 | grep LISTEN | awk '{print $5}' | xargs kill -9 2>/dev/null || true
fi

# Kill processes using port 5173 (Frontend)
if command -v lsof &> /dev/null; then
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    netstat -ano | grep :5173 | grep LISTEN | awk '{print $5}' | xargs kill -9 2>/dev/null || true
fi

echo "Cleanup done."
echo ""

# Start Backend
echo "[1/2] Starting Backend on port 8000..."
echo "--------------------------------------"
cd "$SCRIPT_DIR/../../backend"
./venv/Scripts/uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Start Frontend
echo ""
echo "[2/2] Starting Frontend on port 5173..."
echo "--------------------------------------"
cd "$SCRIPT_DIR/../../frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

cd "$SCRIPT_DIR"

echo ""
echo "============================================"
echo "Both services are starting!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait
