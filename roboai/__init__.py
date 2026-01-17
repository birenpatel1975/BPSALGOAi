"""ROBOAi Trading Platform - Main Package"""

__version__ = "1.0.0"
__author__ = "Biren Patel"
__description__ = "AI-powered algorithmic trading platform for NSE F&O"

# Package initialization
import sys
import os

# Ensure Python 3.10+
if sys.version_info < (3, 10):
    raise RuntimeError("ROBOAi requires Python 3.10 or higher")

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
