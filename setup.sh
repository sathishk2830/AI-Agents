#!/bin/bash

# TP Creator - Quick Start Script for macOS/Linux

echo ""
echo "==========================================="
echo "  TP Creator - Intelligence Test Plan Agent"
echo "==========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

python3 --version
node --version

echo "✓ Python and Node.js found"
echo ""

# Setup backend
echo "Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✓ Backend dependencies installed"
echo ""

# Setup frontend
echo "Setting up Frontend..."
cd ../frontend
npm install
echo "✓ Frontend dependencies installed"
echo ""

echo "==========================================="
echo "  Setup Complete!"
echo "==========================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m uvicorn main:app --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "API Docs: http://localhost:8000/docs"
echo ""
