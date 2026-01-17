#!/bin/bash
# ROBOAi Trading Platform - Stop Script for Linux/Mac

echo "================================================================"
echo "          ROBOAi Trading Platform - Stopping"
echo "================================================================"
echo ""

echo "Looking for ROBOAi processes..."
echo ""

# Find processes running roboai.main
PIDS=$(ps aux | grep "roboai.main" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "No ROBOAi processes found running."
else
    for PID in $PIDS; do
        echo "Stopping ROBOAi process $PID..."
        kill -SIGTERM $PID 2>/dev/null
        
        # Wait for graceful shutdown
        sleep 2
        
        # Check if still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "Process $PID did not stop, forcing..."
            kill -SIGKILL $PID 2>/dev/null
        fi
        
        echo "Process $PID stopped."
    done
fi

echo ""
echo "================================================================"
echo "          ROBOAi Trading Platform - Stopped"
echo "================================================================"
