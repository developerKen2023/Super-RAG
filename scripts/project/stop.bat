@echo off
echo ============================================
echo Stopping Agentic RAG Masterclass
echo ============================================

echo.
echo Killing processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Killing processes on port 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Killing uvicorn and node processes...
taskkill /IM uvicorn.exe /F >nul 2>&1
taskkill /IM node.exe /F >nul 2>&1

echo.
echo ============================================
echo All services stopped.
echo ============================================
pause
