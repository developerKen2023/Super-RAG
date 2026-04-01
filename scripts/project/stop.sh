#!/bin/bash
echo "============================================"
echo "Stopping Agentic RAG Masterclass"
echo "============================================"

# Kill processes using port 8000 (Backend)
echo ""
echo "Killing processes on port 8000 (Backend)..."
if command -v lsof &> /dev/null; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    netstat -ano | grep :8000 | grep LISTEN | awk '{print $5}' | xargs kill -9 2>/dev/null || true
fi

# Kill processes using port 5173 (Frontend)
echo "Killing processes on port 5173 (Frontend)..."
if command -v lsof &> /dev/null; then
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    netstat -ano | grep :5173 | grep LISTEN | awk '{print $5}' | xargs kill -9 2>/dev/null || true
fi

# Kill uvicorn and node processes
echo "Killing uvicorn and node processes..."
pkill -9 uvicorn 2>/dev/null || true
pkill -9 node 2>/dev/null || true

echo ""
echo "============================================"
echo "All services stopped."
echo "============================================"
