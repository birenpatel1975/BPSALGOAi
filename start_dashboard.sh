#!/bin/bash
# ROBOAi Web Dashboard - Start Script for Linux/Mac

echo "================================================================"
echo "      ROBOAi Trading Platform - Web Dashboard"
echo "================================================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "[1/2] Activating virtual environment..."
source venv/bin/activate

# Start the web dashboard
echo "[2/2] Starting web dashboard..."
echo ""
echo "Dashboard will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "================================================================"
echo ""

python start_dashboard.py
