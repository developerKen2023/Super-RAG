@echo off
echo ============================================
echo Starting Agentic RAG Masterclass
echo ============================================

cd /d "%~dp0"

echo.
echo [Cleanup] Killing existing processes...
echo ----------------------------------------

:: Kill processes using port 8000 (Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing backend process PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

:: Kill processes using port 5173 (Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing frontend process PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

:: Also kill known process names
taskkill /IM uvicorn.exe /F >nul 2>&1
taskkill /IM node.exe /F >nul 2>&1

echo Cleanup done.
echo.

echo [1/2] Starting Backend on port 8000...
echo ----------------------------------------
start "Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\uvicorn app.main:app --reload --port 8000"

echo.
echo [2/2] Starting Frontend on port 5173...
echo ----------------------------------------
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ============================================
echo Both services are starting!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo ============================================
echo.
echo Press any key to exit this window...
pause > nul
