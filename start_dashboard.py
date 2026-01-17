#!/usr/bin/env python3
"""
Start the ROBOAi Web Dashboard
Runs the Flask web server for the trading dashboard
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from roboai.api.web_api import app, socketio
from roboai.utils import get_logger

logger = get_logger("WebServer")

def main():
    """Start the web server"""
    print("=" * 70)
    print("  ROBOAi Trading Platform - Web Dashboard")
    print("=" * 70)
    print()
    print("  🌐 Dashboard URL: http://localhost:5000")
    print("  📊 Access the trading dashboard in your web browser")
    print()
    print("  Features:")
    print("  • Toggle between Paper and Live trading modes")
    print("  • Switch between Algo AI and Manual strategies")
    print("  • Real-time P&L monitoring")
    print("  • View active positions and recent trades")
    print("  • Configure advanced trading strategies")
    print()
    print("  Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    try:
        # Run with SocketIO support
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\nShutting down web server...")
        logger.info("Web server stopped")
    except Exception as e:
        logger.error(f"Error starting web server: {e}")
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
