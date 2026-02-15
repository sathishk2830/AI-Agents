#!/bin/bash

# TP Creator - Launch Script for macOS/Linux
# This script starts both backend and frontend servers, then opens the browser

echo ""
echo "==========================================="
echo "  TP Creator - Intelligence Test Plan Agent"
echo "  LAUNCH SCRIPT (macOS/Linux)"
echo "==========================================="
echo ""

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "✓ Node.js and Python found"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo ""
    echo "Please copy .env-example to .env and configure:"
    echo "  - JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN"
    echo "  - GROK_API_KEY (or configure local Ollama)"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo ""
fi

echo "Starting TP Creator application..."
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start backend
echo "📦 Starting Backend (FastAPI)..."
cd "$SCRIPT_DIR/backend"

if [ ! -d venv ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

echo "   Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

# Start backend in background
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   ✅ Backend started (port 8000, PID: $BACKEND_PID)"
echo ""

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend (React)..."
cd "$SCRIPT_DIR/frontend"

if [ ! -d node_modules ]; then
    echo "   Installing npm packages..."
    npm install -q
fi

# Start frontend in background
npm start &
FRONTEND_PID=$!
echo "   ✅ Frontend started (port 3000, PID: $FRONTEND_PID)"
echo ""

# Wait for frontend to start
sleep 5

# Open browser
echo "🌐 Opening browser..."
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:3000
fi

echo ""
echo "==========================================="
echo "   TP Creator is Running!"
echo "==========================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "📡 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Next Steps:"
echo "1. Go to Settings (⚙️) and configure:"
echo "   - Jira credentials"
echo "   - LLM provider (Grok or Ollama)"
echo "2. Go to Dashboard (📊) and generate test plans!"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for either process to exit
wait -n
EXITED=$?

echo ""
echo "One of the processes exited. Cleaning up..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null

exit $EXITED
