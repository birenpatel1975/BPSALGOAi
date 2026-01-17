#!/bin/bash
# ROBOAi Trading Platform - Start Script for Linux/Mac

echo "================================================================"
echo "          ROBOAi Trading Platform - Starting"
echo "================================================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "[1/3] Activating virtual environment..."
source venv/bin/activate

# Check if config exists
if [ ! -f "config.yaml" ]; then
    echo "[WARNING] config.yaml not found!"
    echo "Creating from example..."
    cp config.example.yaml config.yaml
    echo "[INFO] Please edit config.yaml before using live trading."
    echo ""
fi

# Display mode
echo "[2/3] Checking configuration..."
python -c "from roboai.utils import get_config; c = get_config(); print(f'Trading Mode: {c.get(\"trading.mode\")}')" 2>/dev/null || echo "[WARNING] Could not read config"
echo ""

# Start the platform
echo "[3/3] Starting ROBOAi Trading Platform..."
echo "Press Ctrl+C to stop the platform"
echo ""
echo "================================================================"
echo ""

python -m roboai.main

# Platform stopped
echo ""
echo "================================================================"
echo "          ROBOAi Trading Platform - Stopped"
echo "================================================================"
