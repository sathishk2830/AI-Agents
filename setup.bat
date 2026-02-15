@echo off
REM TP Creator - Quick Start Script for Windows

echo.
echo ============================================
echo   TP Creator - Intelligence Test Plan Agent
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✓ Python and Node.js found
echo.

REM Setup backend
echo Setting up Backend...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo ✓ Backend dependencies installed
echo.

REM Setup frontend
echo Setting up Frontend...
cd ..\frontend
call npm install
echo ✓ Frontend dependencies installed
echo.

echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To start the application:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python -m uvicorn main:app --reload
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm start
echo.
echo Then open http://localhost:3000 in your browser
echo.
echo API Docs: http://localhost:8000/docs
echo.
pause
