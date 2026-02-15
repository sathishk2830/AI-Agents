@echo off
REM TP Creator - Launch Script for Windows
REM This script starts both backend and frontend servers, then opens the browser

echo.
echo ============================================
echo   TP Creator - Intelligence Test Plan Agent
echo   LAUNCH SCRIPT (Windows)
echo ============================================
echo.

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Node.js and Python found
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  WARNING: .env file not found!
    echo.
    echo Please copy .env-example to .env and configure:
    echo   - JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN
    echo   - GROK_API_KEY (or configure local Ollama)
    echo.
    echo Continue anyway? (Y/N)
    set /p choice="Choice: "
    if /i not "%choice%"=="Y" exit /b 1
    echo.
)

echo Starting TP Creator application...
echo.

REM Start backend
echo 📦 Starting Backend (FastAPI)...
cd backend
if not exist venv (
    echo   Creating virtual environment...
    python -m venv venv
)

REM Install dependencies silently
echo   Installing dependencies...
venv\Scripts\pip install -q -r requirements.txt 2>nul

REM Start backend in new window
start "TP Creator - Backend" cmd /k "venv\Scripts\python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo   ✅ Backend started (port 8000)
echo.

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting Frontend (React)...
cd ..\frontend

REM Install dependencies if needed
if not exist node_modules (
    echo   Installing npm packages...
    call npm install -q
)

REM Start frontend in new window
start "TP Creator - Frontend" cmd /k "npm start"
echo   ✅ Frontend started (port 3000)
echo.

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

REM Open browser
echo 🌐 Opening browser...
start http://localhost:3000

echo.
echo ============================================
echo   TP Creator is Running!
echo ============================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 📡 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Next Steps:
echo 1. Go to Settings (⚙️) and configure:
echo    - Jira credentials
echo    - LLM provider (Grok or Ollama)
echo 2. Go to Dashboard (📊) and generate test plans!
echo.
echo To stop:
echo - Close the backend and frontend command windows
echo.
pause
